# app/states/workflow_state.py
import reflex as rx
from typing import List, Dict, Any, Optional
import random

class WorkflowState(rx.State):
    """Workflow builder state"""
    
    # --- ESTADO DE DATOS ---
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    
    # Mock de librería de equipos
    equipment_library: List[Dict] = [
        {'id': 'eq1', 'label': 'Robot Arm V1', 'type': 'robot', 'sensors': []}
    ]

    # --- ESTADO DE DRAG AND DROP ---
    dragged_type: str = ""
    dragged_is_action: bool = False
    
    # UI State
    show_equipment_panel: bool = True
    selected_node_id: str = ""
    
    def load_equipment(self):
        print("DEBUG: Loaded initial equipment")
    
    # --- DEFINICIONES ---
    @rx.var
    def category_definitions(self) -> List[Dict]:
        return [
            {'key': 'analyzer', 'name': 'Analyzers', 'icon': 'scan', 'type': 'equipment'},
            {'key': 'robot', 'name': 'Robots', 'icon': 'box', 'type': 'equipment'},
            {'key': 'centrifuge', 'name': 'Centrifuges', 'icon': 'circle-dot', 'type': 'equipment'},
            {'key': 'storage', 'name': 'Storage', 'icon': 'package', 'type': 'equipment'},
            {'key': 'whatsapp', 'name': 'WhatsApp', 'icon': 'message-circle', 'type': 'action'},
            {'key': 'email', 'name': 'Email', 'icon': 'mail', 'type': 'action'},
            {'key': 'alert', 'name': 'System Alert', 'icon': 'bell', 'type': 'action'}
        ]
    
    @rx.var
    def equipment_categories(self) -> List[Dict]:
        return [c for c in self.category_definitions if c['type'] == 'equipment']
    
    @rx.var
    def action_categories(self) -> List[Dict]:
        return [c for c in self.category_definitions if c['type'] == 'action']
    
    @rx.var
    def selected_node(self) -> Optional[Dict]:
        if not self.selected_node_id:
            return None
        return next((n for n in self.nodes if n['id'] == self.selected_node_id), None)

    @rx.var
    def equipment_for_selected_category(self) -> List[Dict]:
        if not self.selected_node:
            return []
        category = self.selected_node['data'].get('category')
        return [eq for eq in self.equipment_library if eq['type'] == category]

    # --- MANEJADORES DE DRAG AND DROP ---

    @rx.event
    def start_drag(self, category_key: str, is_action: bool):
        """Se llama cuando haces click/hold en el botón del menú"""
        print(f"DEBUG: Start Drag -> {category_key}")
        self.dragged_type = category_key
        self.dragged_is_action = is_action

    @rx.event
    def handle_drop(self, x: float, y: float):
        """Se llama cuando sueltas el mouse en CUALQUIER lugar del canvas"""
        if not self.dragged_type:
            return
        
        print(f"DEBUG: Dropping {self.dragged_type} at ({x}, {y})")

        # Ajuste de coordenadas (Offset del sidebar y header)
        # Ajusta estos valores si el mouse no cuadra con el nodo
        drop_x = x - 300 
        drop_y = y - 80 

        new_id = f"node_{random.randint(1000, 9999)}"
        category = next((c for c in self.category_definitions if c['key'] == self.dragged_type), None)
        label = category['name'] if category else self.dragged_type

        new_node = {
            'id': new_id,
            'type': 'default',
            'data': {
                'label': label,
                'category': self.dragged_type,
                'is_action': self.dragged_is_action,
                'configured': False,
                'config': {}
            },
            'position': {'x': drop_x, 'y': drop_y},
            'draggable': True
        }
        
        self.nodes.append(new_node)
        
        # Limpiar estado
        self.dragged_type = ""

    # --- MANEJADORES DE REACT FLOW ---

    @rx.event
    def on_nodes_change(self, node_changes: List[Dict[str, Any]]):
        """Maneja movimientos y selección de nodos sin borrarlos"""
        map_id_to_new_position = {}
        ids_to_remove = []

        for change in node_changes:
            if change["type"] == "position" and "position" in change and change.get("dragging"):
                if change["position"]:
                    map_id_to_new_position[change["id"]] = change["position"]
            elif change["type"] == "select" and change.get("selected"):
                self.selected_node_id = change["id"]
            elif change["type"] == "remove":
                ids_to_remove.append(change["id"])

        if not map_id_to_new_position and not ids_to_remove:
            return

        new_nodes_list = []
        for node in self.nodes:
            if node["id"] in ids_to_remove:
                continue
            
            if node["id"] in map_id_to_new_position:
                updated_node = node.copy()
                updated_node["position"] = map_id_to_new_position[node["id"]]
                new_nodes_list.append(updated_node)
            else:
                new_nodes_list.append(node)
        
        self.nodes = new_nodes_list

    @rx.event
    def on_connect(self, new_edge):
        edge_id = f"e{new_edge['source']}-{new_edge['target']}"
        self.edges = [e for e in self.edges if e["id"] != edge_id]
        self.edges.append({
            "id": edge_id,
            "source": new_edge["source"],
            "target": new_edge["target"],
            "animated": True
        })
        
    @rx.event
    def on_edges_change(self, edge_changes: List[Dict[str, Any]]):
        for change in edge_changes:
            if change["type"] == "remove":
                self.edges = [e for e in self.edges if e["id"] != change["id"]]

    # --- UI HELPERS ---
    @rx.event
    def toggle_equipment_panel(self):
        self.show_equipment_panel = not self.show_equipment_panel

    @rx.event
    def clear_workflow(self):
        self.nodes = []
        self.edges = []
        self.selected_node_id = ""

    @rx.event
    def close_config_menu(self):
        self.selected_node_id = ""
        
    @rx.event
    def configure_equipment_node(self, node_id: str, equipment_id: str):
        pass