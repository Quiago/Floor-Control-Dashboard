import * as THREE from 'https://unpkg.com/three@0.160.0/build/three.module.js';

window.addEventListener('DOMContentLoaded', () => {
    const checkExist = setInterval(function() {
       const modelViewer = document.querySelector("model-viewer");
       if (modelViewer) {
          console.log("✅ Sistema de Precisión (Three.js) Activado");
          clearInterval(checkExist);
          setupSmartRaycaster(modelViewer);
       }
    }, 100);
});

function setupSmartRaycaster(viewer) {
    viewer.addEventListener('click', (event) => {
        // 1. Acceder a la escena interna (Truco avanzado)
        const symbols = Object.getOwnPropertySymbols(viewer);
        const sceneSymbol = symbols.find(s => s.description === 'scene');
        const scene = viewer[sceneSymbol];

        if (!scene) {
            console.warn("⚠️ No se pudo acceder a la escena interna.");
            return;
        }

        // 2. Preparar el Raycaster
        const raycaster = new THREE.Raycaster();
        const pointer = new THREE.Vector2();
        
        // Calcular posición del mouse normalizada (-1 a +1)
        const rect = viewer.getBoundingClientRect();
        pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
        pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;

        // Necesitamos la cámara interna también
        // model-viewer suele exponerla en una propiedad interna o podemos buscarla en la escena
        // Un truco es buscar el primer objeto tipo 'PerspectiveCamera' en la escena del visor
        let camera = null;
        scene.traverse((obj) => {
            if (obj.isPerspectiveCamera && !camera) {
                camera = obj;
            }
        });

        if (!camera) {
            console.error("No se encontró la cámara interna.");
            return;
        }

        // 3. Disparar el rayo
        raycaster.setFromCamera(pointer, camera);
        
        // Buscamos intersecciones con el modelo
        const intersects = raycaster.intersectObjects(scene.children, true);

        if (intersects.length > 0) {
            // El primer objeto es el más cercano (con el que chocó el click)
            const hitObject = intersects[0].object;
            console.log("🎯 Impacto directo en Mesh:", hitObject.name);

            // 4. MAGIA: Subir por la jerarquía hasta encontrar un nombre útil
            // Si le damos al 'Object_2853', subimos a su padre hasta ver 'LabDemo...'
            const componentName = findMeaningfulName(hitObject);
            
            console.log("📦 COMPONENTE DETECTADO:", componentName);
            
            // Efecto Visual: Flash en el objeto detectado
            flashObject(hitObject);
            
            // Aquí enviaríamos a Reflex o mostraríamos alerta
            // window.alert(`Seleccionaste: ${componentName}`);
        }
    });
}

// Función recursiva para buscar el nombre del "Padre" importante
function findMeaningfulName(obj) {
    // Si el objeto no tiene padre o es la escena, paramos
    if (!obj.parent || obj.parent.type === 'Scene') return obj.name;

    // Lista de nombres "basura" o genéricos que queremos ignorar
    // Puedes agregar aquí 'Object_', 'geo_', 'Tube', etc.
    const isGeneric = obj.name.includes('Object_') || 
                      obj.name.includes('geo_') || 
                      obj.name.startsWith('Node');

    // Si el nombre actual parece útil (no es genérico), lo devolvemos
    // Ajusta esta lógica según tus nombres reales (ej: si contiene 'LabDemo')
    if (!isGeneric && obj.name.length > 2) {
        return obj.name;
    }

    // Si no, seguimos subiendo al padre
    return findMeaningfulName(obj.parent);
}

function flashObject(mesh) {
    if (!mesh.material) return;
    
    // Clonamos el material para no afectar a los otros objetos iguales
    // Esto soluciona tu problema de "selección múltiple"
    const originalMaterial = mesh.material;
    const flashMaterial = originalMaterial.clone();
    
    flashMaterial.color.setHex(0xff0000); // Rojo brillante
    // flashMaterial.emissive.setHex(0xff0000); // Opcional: brillo propio
    
    mesh.material = flashMaterial;

    setTimeout(() => {
        mesh.material = originalMaterial;
        // Liberar memoria del material clonado
        flashMaterial.dispose();
    }, 400);
}