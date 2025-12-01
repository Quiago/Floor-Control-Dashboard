import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

// --- LOGGER ---
function logDebug(step, message, data = "") {
    console.log(`%c[Paso ${step}] ${message}`, "color: #00ffff; font-weight: bold; background: #003333; padding: 2px 5px; border-radius: 3px;", data);
}
function logError(step, message, error) {
    console.error(`%c[ERROR Paso ${step}] ${message}`, "color: #ff0000; font-weight: bold;", error);
}

// --- BRIDGE: JS -> PYTHON (Enviar selección) ---
function sendToReflex(data) {
    const input = document.getElementById('bridge-input');
    if (input) {
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeInputValueSetter.call(input, data);
        input.dispatchEvent(new Event('input', { bubbles: true }));
    }
}

// --- INIT ---
let globalModelViewer = null;

window.addEventListener('DOMContentLoaded', () => {
    const checkExist = setInterval(function() {
       const modelViewer = document.querySelector("model-viewer");
       if (modelViewer) {
          logDebug("Init", "Model Viewer encontrado.");
          clearInterval(checkExist);
          globalModelViewer = modelViewer;
          setupSmartRaycaster(modelViewer);
          setupCommandListener(modelViewer);
       }
    }, 200);
});

// --- COMMAND LISTENER (PYTHON -> JS) ---
function setupCommandListener(viewer) {
    const commandInput = document.getElementById('command-input');
    
    if (!commandInput) {
        logError("Init", "No se encontró #command-input");
        return;
    }

    // Polling suave para detectar cambios en el comando desde Python
    let lastCommand = "";
    setInterval(() => {
        if (commandInput.value !== lastCommand) {
            lastCommand = commandInput.value;
            handleCommand(lastCommand, viewer);
        }
    }, 200);
}

function handleCommand(command, viewer) {
    if (!command) return;
    
    logDebug("CMD", `Comando recibido: ${command}`);
    
    // --- CORRECCIÓN CRÍTICA AQUÍ ---
    // Eliminamos la línea que causaba el crash: viewer.model.children[0]
    // Usamos EXCLUSIVAMENTE la técnica de Symbols que sabemos que funciona.
    
    const symbols = Object.getOwnPropertySymbols(viewer);
    let threeScene = null;
    
    for (const sym of symbols) {
        const val = viewer[sym];
        if (val && val.scene && val.scene.isScene) {
            threeScene = val.scene;
            break;
        }
    }
    
    if (!threeScene) {
        logError("CMD", "No se pudo acceder a la escena interna de Three.js");
        return;
    }

    if (command === "restore") {
        // MOSTRAR TODO
        threeScene.traverse((child) => {
            if (child.isMesh) child.visible = true;
        });
        // Opcional: Resetear cámara si es necesario
        // viewer.cameraOrbit = "45deg 55deg 2.5m"; 
    } 
    else if (command.startsWith("isolate:")) {
        // AISLAR OBJETO
        const targetName = command.split(":")[1];
        logDebug("CMD", `Aislando objeto: ${targetName}`);
        
        // 1. Ocultar TODO primero
        threeScene.traverse((child) => {
            if (child.isMesh) child.visible = false;
        });

        // 2. Buscar el objeto objetivo y mostrarlo (junto con sus hijos)
        // Necesitamos una búsqueda recursiva robusta
        let targetObj = null;
        threeScene.traverse((child) => {
            if (child.name === targetName) {
                targetObj = child;
            }
        });

        if (targetObj) {
            // Mostrar el objeto y todos sus descendientes
            targetObj.traverse((child) => {
                if (child.isMesh) child.visible = true;
            });
            logDebug("CMD", "Objeto aislado correctamente.");
        } else {
            logError("CMD", `No se encontró el objeto: ${targetName}`);
        }
    }
}


// --- RAYCASTER (Lógica existente) ---
function setupSmartRaycaster(viewer) {
    viewer.addEventListener('click', (event) => {
        const symbols = Object.getOwnPropertySymbols(viewer);
        let internalContext = null;
        for (const sym of symbols) {
            const val = viewer[sym];
            if (val && val.camera && val.scene) { internalContext = val; break; }
        }
        if (!internalContext) return;

        const camera = internalContext.camera;
        const scene = internalContext.scene;
        const raycaster = new THREE.Raycaster();
        const pointer = new THREE.Vector2();
        const rect = viewer.getBoundingClientRect();
        
        pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(pointer, camera);
        const intersects = raycaster.intersectObjects(scene.children, true);

        if (intersects.length > 0) {
            const hitObject = intersects[0].object;
            const meaningfulGroup = findMeaningfulGroup(hitObject);
            flashHierarchy(meaningfulGroup);
            sendToReflex(meaningfulGroup.name);
        } else {
            // Clic en vacío -> Deseleccionar
            sendToReflex("");
        }
    });
}

function findMeaningfulGroup(obj) {
    if (!obj.parent || obj.parent.type === 'Scene') return obj;
    const junkNames = ['Object_', 'geo_', 'Tube', 'Node', 'Mesh', 'root', 'Scene', 'default'];
    const isJunk = junkNames.some(junk => obj.name.includes(junk));
    if (!isJunk && obj.name.length > 2) return obj;
    return findMeaningfulGroup(obj.parent);
}

function flashHierarchy(group) {
    group.traverse((child) => {
        if (child.isMesh && child.material) flashMesh(child);
    });
}

function flashMesh(mesh) {
    if (mesh.userData.isFlashing) return;
    mesh.userData.isFlashing = true;
    const originalMaterial = mesh.material;
    const flashMaterial = originalMaterial.clone();
    flashMaterial.color.setHex(0xffaa00);
    flashMaterial.emissive.setHex(0x331100);
    mesh.material = flashMaterial;
    setTimeout(() => {
        mesh.material = originalMaterial;
        if(flashMaterial) flashMaterial.dispose();
        mesh.userData.isFlashing = false;
    }, 600);
}