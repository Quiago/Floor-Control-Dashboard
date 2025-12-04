# app/states/workflow_state.py
"""
Workflow Builder State - FIXED VERSION v2

The key insight is that ReactFlow in controlled mode requires careful handling:
1. ReactFlow sends position changes during drag with `dragging: true`
2. At drag end, it sends `dragging: false` WITHOUT position data
3. We should NOT update state during drag - only track final position

The original bug was caused by constantly rebuilding the nodes array during drag,
which caused React/ReactFlow to lose track of the internal drag state.
"""
import reflex as rx
from typing import List, Dict, Any, Optional
import random

class WorkflowState(rx.State):
    """Workflow builder state"""
    
    # --- STATE DATA ---
    # Start with a test node to verify ReactFlow works
    nodes: List[Dict[str, Any]] = [
        {
            'id': 'initial_1',
            'type': 'default',
            'data': {'label': 'Initial Test Node'},
            'position': {'x': 100, 'y': 100},
            'draggable': True
        }
    ]
    edges: List[Dict[str, Any]] = []
    
    # Equipment library mock
    equipment_library: List[Dict] = [
        {'id': 'eq1', 'label': 'Robot Arm V1', 'type': 'robot', 'sensors': []}
    ]

    # --- DRAG AND DROP STATE ---
    dragged_type: str = ""
    dragged_is_action: bool = False
    
    # UI State
    show_equipment_panel: bool = True
    selected_node_id: str = ""
    
    # Counter for unique IDs
    _node_counter: int = 0
    
    def load_equipment(self):
        print("DEBUG: Loaded initial equipment")
    
    # --- DEFINITIONS ---
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

    @rx.var
    def is_dragging(self) -> bool:
        """Check if we're currently dragging from the toolbox"""
        return self.dragged_type != ""

    # --- DRAG AND DROP HANDLERS ---

    @rx.event
    def start_drag(self, category_key: str, is_action: bool):
        """Called when mousedown on a toolbox button"""
        print(f"DEBUG: Start Drag -> {category_key}, is_action={is_action}")
        self.dragged_type = category_key
        self.dragged_is_action = is_action

    @rx.event
    def cancel_drag(self):
        """Cancel the current drag operation"""
        print("DEBUG: Drag cancelled")
        self.dragged_type = ""
        self.dragged_is_action = False

    @rx.event
    def handle_drop(self, x: float, y: float):
        """Called when mouse is released on the canvas"""
        if not self.dragged_type:
            print("DEBUG: handle_drop called but no dragged_type")
            return
        
        print(f"DEBUG: Dropping {self.dragged_type} at ({x}, {y})")

        # Get canvas-relative coordinates
        SIDEBAR_WIDTH = 256
        HEADER_HEIGHT = 64
        
        drop_x = max(0, x - SIDEBAR_WIDTH)
        drop_y = max(0, y - HEADER_HEIGHT)

        # Generate unique ID
        self._node_counter += 1
        new_id = f"node_{self._node_counter}_{random.randint(100, 999)}"
        
        # Find category info
        category = next(
            (c for c in self.category_definitions if c['key'] == self.dragged_type), 
            None
        )
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
        
        self.nodes = [*self.nodes, new_node]
        
        print(f"DEBUG: Created node {new_id}, total nodes: {len(self.nodes)}")
        print(f"DEBUG: Node position: ({drop_x}, {drop_y})")
        
        # Clear drag state
        self.dragged_type = ""
        self.dragged_is_action = False

    # --- REACTFLOW EVENT HANDLERS ---

    @rx.event
    def on_nodes_change(self, node_changes: List[Dict[str, Any]]):
        """
        Handle ReactFlow node changes.
        
        CRITICAL: In controlled mode, we MUST update node positions for drag to work.
        ReactFlow sends position changes, and we must reflect them in state.
        """
        if not node_changes:
            return
        
        # Build a dict of position updates
        position_updates: Dict[str, Dict[str, float]] = {}
        ids_to_remove: List[str] = []
        
        for change in node_changes:
            change_type = change.get("type", "")
            node_id = change.get("id", "")
            
            if change_type == "position":
                position = change.get("position")
                if position:
                    position_updates[node_id] = position
                        
            elif change_type == "select":
                if change.get("selected", False):
                    self.selected_node_id = node_id
                    
            elif change_type == "remove":
                ids_to_remove.append(node_id)
        
        # Apply position updates by creating a new list
        if position_updates:
            new_nodes = []
            for node in self.nodes:
                if node["id"] in position_updates:
                    # Create new node dict with updated position
                    updated_node = {**node, "position": position_updates[node["id"]]}
                    new_nodes.append(updated_node)
                else:
                    new_nodes.append(node)
            self.nodes = new_nodes
        
        # Handle removals
        if ids_to_remove:
            self.nodes = [n for n in self.nodes if n["id"] not in ids_to_remove]

    @rx.event
    def on_connect(self, new_edge: Dict):
        """Handle new edge connections"""
        if not new_edge:
            return
            
        source = new_edge.get("source", "")
        target = new_edge.get("target", "")
        
        if not source or not target:
            return
            
        edge_id = f"e{source}-{target}"
        
        # Remove existing edge with same id if exists
        filtered_edges = [e for e in self.edges if e["id"] != edge_id]
        
        # Add new edge
        new_edge_data = {
            "id": edge_id,
            "source": source,
            "target": target,
            "animated": True
        }
        
        # CRITICAL: Use reassignment for proper reactivity
        self.edges = [*filtered_edges, new_edge_data]
        print(f"DEBUG: Created edge {edge_id}")
        
    @rx.event
    def on_edges_change(self, edge_changes: List[Dict[str, Any]]):
        """Handle edge changes"""
        if not edge_changes:
            return
            
        ids_to_remove = set()
        
        for change in edge_changes:
            if change.get("type") == "remove":
                ids_to_remove.add(change.get("id", ""))
        
        if ids_to_remove:
            self.edges = [e for e in self.edges if e["id"] not in ids_to_remove]
            print(f"DEBUG: Removed {len(ids_to_remove)} edges")

    # --- UI HELPERS ---
    
    @rx.event
    def toggle_equipment_panel(self):
        self.show_equipment_panel = not self.show_equipment_panel

    @rx.event
    def clear_workflow(self):
        """Clear all nodes and edges"""
        self.nodes = []
        self.edges = []
        self.selected_node_id = ""
        print("DEBUG: Workflow cleared")

    @rx.event
    def close_config_menu(self):
        self.selected_node_id = ""
        
    @rx.event
    def configure_equipment_node(self, node_id: str, equipment_id: str):
        """Configure a node with specific equipment"""
        pass

    @rx.event
    def add_test_node(self):
        """Debug helper to add a test node"""
        self._node_counter += 1
        test_node = {
            'id': f"test_{self._node_counter}",
            'type': 'default',
            'data': {'label': f'Test Node {self._node_counter}'},
            'position': {'x': 100 + (self._node_counter * 50), 'y': 100},
            'draggable': True
        }
        self.nodes = [*self.nodes, test_node]
        print(f"DEBUG: Added test node, total: {len(self.nodes)}")