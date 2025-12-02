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

// === GLOBAL STATE ===
let globalModelViewer = null;
let isInitialized = false;

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
    // Check if already has listener to avoid duplicates
    if (viewer._hasRaycaster) {
        log("Raycaster already setup, skipping");
        return;
    }
    
    viewer._hasRaycaster = true;
    
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
    
    // Check if already has listener to avoid duplicates
    if (commandInput._hasListener) {
        log("Command listener already setup, skipping");
        return;
    }
    
    commandInput._hasListener = true;
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
        
        scene.traverse((child) => {
            if (child.isMesh) child.visible = false;
        });
        
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
            scene.traverse((child) => {
                if (child.isMesh) child.visible = true;
            });
        }
    }
}

// === INITIALIZATION (SPA-COMPATIBLE) ===
function initializeModelViewer() {
    const viewer = document.querySelector("model-viewer");
    
    if (!viewer) {
        return; // Model viewer not in DOM yet
    }
    
    // Check if this viewer is already initialized
    if (viewer === globalModelViewer && isInitialized) {
        return; // Already initialized
    }
    
    // New viewer detected or first time
    log("Model Viewer found - initializing");
    globalModelViewer = viewer;
    isInitialized = true;
    
    setupSmartRaycaster(viewer);
    setupCommandListener(viewer);
    
    log("✓ Raycaster ready");
    log("✓ Commands ready");
}

// === CONTINUOUS CHECK FOR MODEL VIEWER (SPA NAVIGATION SUPPORT) ===
// This runs continuously to handle SPA navigation where model-viewer
// gets unmounted and remounted when navigating between pages
function startContinuousCheck() {
    setInterval(() => {
        const viewer = document.querySelector("model-viewer");
        
        // If viewer exists but is different from current, reinitialize
        if (viewer && viewer !== globalModelViewer) {
            log("New model viewer detected (navigation), reinitializing...");
            isInitialized = false;
            initializeModelViewer();
        }
        // If viewer disappeared, reset state
        else if (!viewer && globalModelViewer) {
            log("Model viewer unmounted");
            globalModelViewer = null;
            isInitialized = false;
        }
        // If viewer exists and matches, try to initialize if not done
        else if (viewer && !isInitialized) {
            initializeModelViewer();
        }
    }, 500); // Check every 500ms
}

// === START ON LOAD ===
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        log("Initializing...");
        initializeModelViewer();
        startContinuousCheck();
    });
} else {
    // Document already loaded (happens in SPAs)
    log("Initializing (already loaded)...");
    initializeModelViewer();
    startContinuousCheck();
}