# app/states/workflow_state.py
import reflex as rx
from typing import List, Dict, Any
from collections import defaultdict
from app.extractors.glb_parser import load_equipment_from_glb


class WorkflowState(rx.State):
    """Workflow builder state with equipment from GLB"""
    
    equipment_library: List[Dict] = []
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    
    show_equipment_panel: bool = True
    
    @rx.var
    def equipment_by_category(self) -> List[Dict]:
        """Group equipment by category - returns list of category dicts"""
        categories = defaultdict(list)
        
        category_map = {
            'analyzer': {'name': 'Quality Analyzers', 'icon': 'scan'},
            'robot': {'name': 'Robotic Systems', 'icon': 'box'},
            'centrifuge': {'name': 'Centrifuges', 'icon': 'circle-dot'},
            'storage': {'name': 'Storage Units', 'icon': 'package'},
            'conveyor': {'name': 'Conveyors', 'icon': 'arrow-right'},
            'other': {'name': 'Other Equipment', 'icon': 'circle'}
        }
        
        for eq in self.equipment_library:
            eq_type = eq['type'] if eq['type'] in category_map else 'other'
            categories[eq_type].append(eq)
        
        result = []
        for cat_key in ['analyzer', 'robot', 'centrifuge', 'storage', 'conveyor', 'other']:
            if cat_key in categories and categories[cat_key]:
                result.append({
                    'key': cat_key,
                    'name': category_map[cat_key]['name'],
                    'icon': category_map[cat_key]['icon'],
                    'equipment': categories[cat_key],
                    'count': len(categories[cat_key])
                })
        
        return result
    
    def load_equipment(self):
        """Load equipment from GLB file"""
        self.equipment_library = load_equipment_from_glb()
    
    @rx.event
    def add_equipment_node(self, equipment_id: str):
        """Add equipment from library to canvas"""
        equipment = next((eq for eq in self.equipment_library if eq['id'] == equipment_id), None)
        if not equipment:
            return
        
        node_id = f"eq_{len(self.nodes) + 1}"
        x_offset = (len(self.nodes) % 3) * 250
        y_offset = (len(self.nodes) // 3) * 150
        
        self.nodes.append({
            'id': node_id,
            'type': 'default',
            'data': {
                'label': equipment['label'],
                'equipment_id': equipment['id'],
                'equipment_type': equipment['type'],
                'sensors': equipment['sensors']
            },
            'position': {'x': 300 + x_offset, 'y': 100 + y_offset}
        })
    
    @rx.event
    def add_action_node(self):
        """Add action node"""
        node_id = f"action_{len(self.nodes) + 1}"
        x_offset = (len(self.nodes) % 3) * 250
        y_offset = (len(self.nodes) // 3) * 150
        
        self.nodes.append({
            'id': node_id,
            'type': 'output',
            'data': {'label': 'Send Alert'},
            'position': {'x': 300 + x_offset, 'y': 100 + y_offset}
        })
    
    @rx.event
    def clear_workflow(self):
        self.nodes = []
        self.edges = []
    
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