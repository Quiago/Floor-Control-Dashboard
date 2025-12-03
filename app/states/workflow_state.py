# app/states/workflow_state.py
import reflex as rx
from typing import List, Dict, Any, Optional
from collections import defaultdict
from app.extractors.glb_parser import load_equipment_from_glb


class WorkflowState(rx.State):
    """Workflow builder state"""
    
    equipment_library: List[Dict] = []
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    
    show_equipment_panel: bool = True
    selected_node_id: str = ""
    config_menu_position: Dict[str, float] = {}
    
    def load_equipment(self):
        self.equipment_library = load_equipment_from_glb()
    
    @rx.var
    def category_definitions(self) -> List[Dict]:
        """Equipment and action categories"""
        return [
            {'key': 'analyzer', 'name': 'Analyzers', 'icon': 'scan', 'type': 'equipment'},
            {'key': 'robot', 'name': 'Robots', 'icon': 'box', 'type': 'equipment'},
            {'key': 'centrifuge', 'name': 'Centrifuges', 'icon': 'circle-dot', 'type': 'equipment'},
            {'key': 'storage', 'name': 'Storage', 'icon': 'package', 'type': 'equipment'},
            {'key': 'conveyor', 'name': 'Conveyors', 'icon': 'arrow-right', 'type': 'equipment'},
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
    
    @rx.event
    def add_category_node(self, category_key: str, is_action: bool):
        node_id = f"node_{len(self.nodes) + 1}"
        x_offset = (len(self.nodes) % 3) * 250
        y_offset = (len(self.nodes) // 3) * 150
        
        category = next((c for c in self.category_definitions if c['key'] == category_key), None)
        
        self.nodes.append({
            'id': node_id,
            'type': 'default',
            'data': {
                'label': category['name'] if category else category_key,
                'category': category_key,
                'is_action': is_action,
                'configured': False,
                'equipment_id': None,
                'config': {}
            },
            'position': {'x': 300 + x_offset, 'y': 100 + y_offset}
        })
    
    @rx.event
    def select_node(self, node_id: str):
        self.selected_node_id = node_id
    
    @rx.event
    def close_config_menu(self):
        self.selected_node_id = ""
    
    @rx.event
    def configure_equipment_node(self, node_id: str, equipment_id: str):
        for i, node in enumerate(self.nodes):
            if node['id'] == node_id:
                equipment = next((eq for eq in self.equipment_library if eq['id'] == equipment_id), None)
                if equipment:
                    self.nodes[i]['data']['equipment_id'] = equipment_id
                    self.nodes[i]['data']['label'] = equipment['label']
                    self.nodes[i]['data']['configured'] = True
                    self.nodes[i]['data']['sensors'] = equipment['sensors']
                break
    
    @rx.event
    def configure_sensor_threshold(self, node_id: str, sensor_id: str, threshold_low: float, threshold_high: float):
        for i, node in enumerate(self.nodes):
            if node['id'] == node_id:
                if 'thresholds' not in self.nodes[i]['data']['config']:
                    self.nodes[i]['data']['config']['thresholds'] = {}
                self.nodes[i]['data']['config']['thresholds'][sensor_id] = {
                    'low': threshold_low,
                    'high': threshold_high
                }
                break
    
    @rx.event
    def configure_action_node(self, node_id: str, action_type: str, config: Dict):
        for i, node in enumerate(self.nodes):
            if node['id'] == node_id:
                self.nodes[i]['data']['configured'] = True
                self.nodes[i]['data']['config'] = config
                break
    
    @rx.event
    def clear_workflow(self):
        self.nodes = []
        self.edges = []
        self.selected_node_id = ""
    
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
    def on_nodes_change(self, node_changes: List[Dict[str, Any]]):
        map_id_to_new_position = defaultdict(dict)
        
        for change in node_changes:
            if change["type"] == "position" and change.get("dragging"):
                map_id_to_new_position[change["id"]] = change["position"]
            elif change["type"] == "select" and change.get("selected"):
                self.selected_node_id = change["id"]
        
        for i, node in enumerate(self.nodes):
            if node["id"] in map_id_to_new_position:
                self.nodes[i]["position"] = map_id_to_new_position[node["id"]]
    
    @rx.event
    def on_edges_change(self, edge_changes: List[Dict[str, Any]]):
        for change in edge_changes:
            if change["type"] == "remove":
                self.edges = [e for e in self.edges if e["id"] != change["id"]]
    
    @rx.event
    def toggle_equipment_panel(self):
        self.show_equipment_panel = not self.show_equipment_panel