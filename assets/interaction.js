import * as THREE from 'https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js';

// === LOGGER ===
const log = (msg, data = "") => console.log(`%c[Nexus] ${msg}`, "color: #00d9ff; font-weight: bold;", data);
const error = (msg, err) => console.error(`%c[Nexus ERROR] ${msg}`, "color: #ff0000; font-weight: bold;", err);

// === BRIDGE: JS -> PYTHON ===
function sendToReflex(data) {
    const input = document.getElementById('bridge-input');
    if (input) {
        const setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
        setter.call(input, data);
        input.dispatchEvent(new Event('input', { bubbles: true }));
    }
}

// === GLOBAL ===
let globalModelViewer = null;

// === INIT ===
window.addEventListener('DOMContentLoaded', () => {
    log("Initializing...");
    
    const checkModelViewer = setInterval(() => {
        const viewer = document.querySelector("model-viewer");
        if (viewer) {
            log("✓ Model Viewer found");
            clearInterval(checkModelViewer);
            globalModelViewer = viewer;
            
            // Setup immediately (don't wait for load event)
            setupSmartRaycaster(viewer);
            setupCommandListener(viewer);
            log("✓ Raycaster ready");
            log("✓ Commands ready");
        }
    }, 200);
});

// === GET THREE.JS SCENE ===
function getThreeScene(viewer) {
    const symbols = Object.getOwnPropertySymbols(viewer);
    for (const sym of symbols) {
        const val = viewer[sym];
        if (val && val.scene && val.scene.isScene) {
            return val.scene;
        }
    }
    return null;
}

// === RAYCASTER (Equipment Selection) ===
function setupSmartRaycaster(viewer) {
    viewer.addEventListener('click', (event) => {
        try {
            const symbols = Object.getOwnPropertySymbols(viewer);
            let camera = null;
            let scene = null;
            
            for (const sym of symbols) {
                const val = viewer[sym];
                if (val && val.camera && val.scene) {
                    camera = val.camera;
                    scene = val.scene;
                    break;
                }
            }
            
            if (!camera || !scene) {
                error("Raycaster: Camera or scene not ready yet");
                return;
            }
            
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
                log(`Selected: ${meaningfulGroup.name}`);
                flashHierarchy(meaningfulGroup);
                sendToReflex(meaningfulGroup.name);
            } else {
                log("Deselected (empty space)");
                sendToReflex("");
            }
        } catch (err) {
            error("Raycaster error", err);
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
        if (flashMaterial) flashMaterial.dispose();
        mesh.userData.isFlashing = false;
    }, 600);
}

// === COMMAND LISTENER (PYTHON -> JS) ===
function setupCommandListener(viewer) {
    const commandInput = document.getElementById('command-input');
    
    if (!commandInput) {
        error("Command input not found: #command-input");
        return;
    }
    
    let lastCommand = "";
    
    setInterval(() => {
        const currentCommand = commandInput.value;
        if (currentCommand && currentCommand !== lastCommand) {
            lastCommand = currentCommand;
            handleCommand(currentCommand, viewer);
        }
    }, 200);
}

function handleCommand(command, viewer) {
    log(`CMD received: ${command}`);
    
    const scene = getThreeScene(viewer);
    if (!scene) {
        error("Cannot access Three.js scene");
        return;
    }
    
    if (command === "restore") {
        scene.traverse((child) => {
            if (child.isMesh) child.visible = true;
        });
        log("✓ View restored");
    } 
    else if (command.startsWith("isolate:")) {
        const targetName = command.split(":")[1];
        log(`Isolating: ${targetName}`);
        
        // Hide everything first
        scene.traverse((child) => {
            if (child.isMesh) child.visible = false;
        });
        
        // Find target and show it + children
        let targetObj = null;
        scene.traverse((child) => {
            if (child.name === targetName) {
                targetObj = child;
            }
        });
        
        if (targetObj) {
            targetObj.traverse((child) => {
                if (child.isMesh) child.visible = true;
            });
            log(`✓ Isolated: ${targetName}`);
        } else {
            error(`Target not found: ${targetName}`);
            // Restore if not found
            scene.traverse((child) => {
                if (child.isMesh) child.visible = true;
            });
        }
    }
}