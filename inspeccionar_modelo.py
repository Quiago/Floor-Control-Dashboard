from pygltflib import GLTF2

# Cambia esto por la ruta real de tu archivo en assets
RUT_MODELO = "assets/pharmaceutical_manufacturing_machinery.glb"

def analizar_modelo():
    print(f"📂 Cargando: {RUT_MODELO}...")
    try:
        gltf = GLTF2().load(RUT_MODELO)
    except FileNotFoundError:
        print("❌ Error: No encuentro el archivo. Verifica la ruta.")
        return

    #print("\n--- 🎨 MATERIALES (Colores/Texturas) ---")
    ## Estos son los nombres que detecta el script JS de interacción
    #for i, mat in enumerate(gltf.materials):
    #    print(f"ID {i}: {mat.name}")

    print("\n--- 🧩 NODOS/MESHES (Las piezas geométricas) ---")
    # Estas son las piezas reales. Si ves muchas aquí pero pocos materiales,
    # es que comparten material.
    for i, node in enumerate(gltf.nodes):
        if node.name:
            # Buscamos qué mesh usa este nodo
            mesh_info = f"(Mesh ID: {node.mesh})" if node.mesh is not None else "(Es un grupo/contenedor)"
            print(f"Nodo {i}: '{node.name}' {mesh_info}")

if __name__ == "__main__":
    analizar_modelo()