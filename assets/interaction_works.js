import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';

window.addEventListener('DOMContentLoaded', () => {
    const checkExist = setInterval(function() {
       const modelViewer = document.querySelector("model-viewer");
       if (modelViewer) {
          console.log("✅ Sistema de Raycasting Grupal Activado");
          clearInterval(checkExist);
          setupSmartRaycaster(modelViewer);
       }
    }, 100);
});

function setupSmartRaycaster(viewer) {
    viewer.addEventListener('click', (event) => {
        // 1. ACCESO A LA ESCENA INTERNA
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
            console.error("❌ No se pudo acceder al contexto interno.");
            return;
        }

        const camera = internalContext.camera;
        const scene = internalContext.scene;

        // 2. RAYCASTER
        const raycaster = new THREE.Raycaster();
        const pointer = new THREE.Vector2();
        const rect = viewer.getBoundingClientRect();
        pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        raycaster.setFromCamera(pointer, camera);
        const intersects = raycaster.intersectObjects(scene.children, true);

        if (intersects.length > 0) {
            const hitObject = intersects[0].object;
            
            // 3. BUSCAR AL PADRE IMPORTANTE (EL GRUPO COMPLETO)
            // En lugar de quedarnos solo con el nombre, devolvemos el OBJETO entero
            const meaningfulGroup = findMeaningfulGroup(hitObject);
            
            console.log(`🎯 Impacto en: ${hitObject.name}`); 
            console.log(`📦 Grupo Seleccionado: ${meaningfulGroup.name}`);
            
            // 4. FLASH GRUPAL (La mejora UX)
            // Recorremos todos los hijos del grupo encontrado y los iluminamos
            flashHierarchy(meaningfulGroup);
            
            // Aquí conectarías con Reflex enviando el nombre del grupo
            sendToReflex(meaningfulGroup.name);
        }
    });
}

// Busca el objeto padre que tenga un nombre "con sentido"
function findMeaningfulGroup(obj) {
    // Si llegamos a la Escena raíz o no hay padre, devolvemos el objeto original
    // (para evitar iluminar toda la fábrica si tocamos el suelo)
    if (!obj.parent || obj.parent.type === 'Scene') return obj;

    // Filtros de nombres "basura"
    const junkNames = ['Object_', 'geo_', 'Tube', 'Node', 'Mesh', 'root'];
    const isJunk = junkNames.some(junk => obj.name.includes(junk));

    // Si el nombre es útil (ej: "Analyzer_10"), ¡ESTE ES EL GRUPO!
    if (!isJunk && obj.name.length > 3) {
        return obj;
    }

    // Si no, seguimos subiendo al abuelo
    return findMeaningfulGroup(obj.parent);
}

// Función recursiva que pinta todo lo que esté debajo del grupo
function flashHierarchy(group) {
    // .traverse recorre el objeto y todos sus hijos, nietos, etc.
    group.traverse((child) => {
        if (child.isMesh && child.material) {
            flashMesh(child);
        }
    });
}

function flashMesh(mesh) {
    // Evitamos flashear si ya está flasheando (para no buguear el color)
    if (mesh.userData.isFlashing) return;
    mesh.userData.isFlashing = true;

    const originalMaterial = mesh.material;
    
    // Clonamos para no afectar a otros objetos fuera de este grupo
    const flashMaterial = originalMaterial.clone();
    flashMaterial.color.setHex(0xff0000); // ROJO
    // flashMaterial.emissive.setHex(0x550000); // Brillo opcional
    
    mesh.material = flashMaterial;

    setTimeout(() => {
        mesh.material = originalMaterial;
        flashMaterial.dispose();
        mesh.userData.isFlashing = false;
    }, 5000); // 5000ms de flash
}