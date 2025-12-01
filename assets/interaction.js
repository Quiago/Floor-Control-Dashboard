import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

// --- LOGGER DEBUG HELPER ---
function logDebug(step, message, data = "") {
    console.log(`%c[Paso ${step}] ${message}`, "color: #00ffff; font-weight: bold; background: #003333; padding: 2px 5px; border-radius: 3px;", data);
}

function logError(step, message, error) {
    console.error(`%c[ERROR Paso ${step}] ${message}`, "color: #ff0000; font-weight: bold;", error);
}

// --- BRIDGE: JS -> PYTHON ---
function sendToReflex(data) {
    const input = document.getElementById('bridge-input');
    if (input) {
        logDebug("5", "Enviando datos a Python...", data);
        const nativeInputValueSetter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        nativeInputValueSetter.call(input, data);
        input.dispatchEvent(new Event('input', { bubbles: true }));
    } else {
        logError("5", "No se encontró el input puente #bridge-input");
    }
}

// --- INIT ---
window.addEventListener('DOMContentLoaded', () => {
    logDebug("1", "DOM Cargado. Buscando <model-viewer>...");
    
    let attempts = 0;
    const checkExist = setInterval(function() {
       attempts++;
       const modelViewer = document.querySelector("model-viewer");
       
       if (modelViewer) {
          logDebug("2", "Etiqueta <model-viewer> encontrada.", modelViewer);
          clearInterval(checkExist);
          setupDiagnostics(modelViewer); 
          setupSmartRaycaster(modelViewer);
       } else if (attempts > 50) { // 5 segundos timeout
           logError("1", "Timeout: No se encontró <model-viewer>.");
           clearInterval(checkExist);
       }
    }, 100);
});

// --- DIAGNÓSTICOS DE CARGA ---
function setupDiagnostics(viewer) {
    viewer.addEventListener('load', () => {
        logDebug("3", "✅ Modelo 3D cargado (Evento 'load').");
        const rect = viewer.getBoundingClientRect();
        logDebug("3.1", "Dimensiones:", `Ancho: ${rect.width}px, Alto: ${rect.height}px`);
        if (rect.height === 0) logError("3.1", "⚠️ Altura 0px. Revisa CSS en app.py.");
    });

    viewer.addEventListener('error', (err) => {
        logError("3", "❌ Falló la carga del .glb", err);
    });
}

// --- RAYCASTER ---
function setupSmartRaycaster(viewer) {
    viewer.addEventListener('click', (event) => {
        logDebug("4", "Click detectado.");

        const symbols = Object.getOwnPropertySymbols(viewer);
        let internalContext = null;

        for (const sym of symbols) {
            const val = viewer[sym];
            if (val && val.camera && val.scene) {
                internalContext = val;
                break;
            }
        }

        if (!internalContext) {
            logError("4", "No se pudo acceder a la escena Three.js.");
            return;
        }

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
            logDebug("4.2", "Intersección:", meaningfulGroup.name);
            flashHierarchy(meaningfulGroup);
            sendToReflex(meaningfulGroup.name);
        } else {
            logDebug("4.2", "Click en vacío.");
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