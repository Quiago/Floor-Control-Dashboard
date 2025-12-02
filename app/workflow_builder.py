"""
Workflow Builder Page - Full screen canvas for creating automation workflows
"""
import reflex as rx
from app.reactflow import react_flow, background, controls, minimap
from typing import Any, Dict, List
from collections import defaultdict
import random


# Initial nodes for demo
initial_nodes = [
    {
        'id': '1',
        'type': 'input',
        'data': {'label': 'Temperature Sensor'},
        'position': {'x': 250, 'y': 25},
    },
    {
        'id': '2',
        'data': {'label': 'Check Threshold'},
        'position': {'x': 250, 'y': 125},
    },
    {
        'id': '3',
        'type': 'output',
        'data': {'label': 'Send Alert'},
        'position': {'x': 250, 'y': 250},
    },
]

initial_edges = [
    {'id': 'e1-2', 'source': '1', 'target': '2', 'animated': True},
    {'id': 'e2-3', 'source': '2', 'target': '3', 'animated': True},
]


class WorkflowState(rx.State):
    """State for workflow builder"""
    
    nodes: List[Dict[str, Any]] = initial_nodes
    edges: List[Dict[str, Any]] = initial_edges
    
    @rx.event
    def add_sensor_node(self):
        """Add a new sensor node"""
        new_id = str(len(self.nodes) + 1)
        x = random.randint(50, 700)
        y = random.randint(50, 500)
        
        new_node = {
            'id': new_id,
            'type': 'default',
            'data': {'label': f'Sensor {new_id}'},
            'position': {'x': x, 'y': y},
            'draggable': True,
        }
        self.nodes.append(new_node)
    
    @rx.event
    def add_action_node(self):
        """Add a new action node"""
        new_id = str(len(self.nodes) + 1)
        x = random.randint(50, 700)
        y = random.randint(50, 500)
        
        new_node = {
            'id': new_id,
            'type': 'output',
            'data': {'label': f'Action {new_id}'},
            'position': {'x': x, 'y': y},
            'draggable': True,
        }
        self.nodes.append(new_node)
    
    @rx.event
    def add_condition_node(self):
        """Add a new condition node"""
        new_id = str(len(self.nodes) + 1)
        x = random.randint(50, 700)
        y = random.randint(50, 500)
        
        new_node = {
            'id': new_id,
            'type': 'default',
            'data': {'label': f'Condition {new_id}'},
            'position': {'x': x, 'y': y},
            'draggable': True,
        }
        self.nodes.append(new_node)
    
    @rx.event
    def clear_workflow(self):
        """Clear all nodes and edges"""
        self.nodes = []
        self.edges = []
    
    @rx.event
    def on_connect(self, new_edge):
        """Handle new edge connection"""
        # Check if edge already exists
        for i, edge in enumerate(self.edges):
            if edge["id"] == f"e{new_edge['source']}-{new_edge['target']}":
                del self.edges[i]
                break
        
        # Add new edge
        self.edges.append({
            "id": f"e{new_edge['source']}-{new_edge['target']}",
            "source": new_edge["source"],
            "target": new_edge["target"],
            "animated": True,
        })
    
    @rx.event
    def on_nodes_change(self, node_changes: List[Dict[str, Any]]):
        """Handle node position changes during dragging"""
        map_id_to_new_position = defaultdict(dict)
        
        # Store new positions
        for change in node_changes:
            if change["type"] == "position" and change.get("dragging") == True:
                map_id_to_new_position[change["id"]] = change["position"]
        
        # Update node positions
        for i, node in enumerate(self.nodes):
            if node["id"] in map_id_to_new_position:
                new_position = map_id_to_new_position[node["id"]]
                self.nodes[i]["position"] = new_position
    
    @rx.event
    def on_edges_change(self, edge_changes: List[Dict[str, Any]]):
        """Handle edge changes"""
        # Handle edge deletions
        for change in edge_changes:
            if change["type"] == "remove":
                edge_id = change["id"]
                self.edges = [e for e in self.edges if e["id"] != edge_id]


def workflow_header() -> rx.Component:
    """Header with navigation and actions"""
    return rx.hstack(
        rx.hstack(
            rx.icon("workflow", size=24, class_name="text-blue-400"),
            rx.heading("Workflow Builder", size="6", class_name="text-white"),
            spacing="3",
            align_items="center"
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.hstack(
                    rx.icon("home", size=16),
                    rx.text("Monitor"),
                    spacing="2"
                ),
                variant="ghost",
                on_click=rx.redirect("/"),
                class_name="text-gray-300 hover:text-white"
            ),
            rx.button(
                rx.hstack(
                    rx.icon("save", size=16),
                    rx.text("Save"),
                    spacing="2"
                ),
                variant="solid",
                color_scheme="blue",
            ),
            spacing="2"
        ),
        class_name="w-full p-4 border-b border-gray-800 bg-gray-900",
        align_items="center"
    )


def workflow_toolbox() -> rx.Component:
    """Sidebar toolbox with node types"""
    return rx.vstack(
        rx.text("TOOLBOX", class_name="text-xs font-bold text-gray-400 uppercase mb-3"),
        
        # Sensor Nodes
        rx.vstack(
            rx.text("TRIGGERS", class_name="text-[10px] text-gray-500 font-bold mb-1"),
            rx.button(
                rx.vstack(
                    rx.icon("scan-eye", size=24, class_name="text-cyan-400"),
                    rx.text("Sensor", size="2"),
                    spacing="1"
                ),
                variant="outline",
                class_name="w-full h-20 border-gray-700 hover:bg-cyan-900/20 hover:border-cyan-500",
                on_click=WorkflowState.add_sensor_node
            ),
            spacing="2",
            width="100%"
        ),
        
        # Condition Nodes
        rx.vstack(
            rx.text("LOGIC", class_name="text-[10px] text-gray-500 font-bold mb-1 mt-3"),
            rx.button(
                rx.vstack(
                    rx.icon("git-branch", size=24, class_name="text-yellow-400"),
                    rx.text("Condition", size="2"),
                    spacing="1"
                ),
                variant="outline",
                class_name="w-full h-20 border-gray-700 hover:bg-yellow-900/20 hover:border-yellow-500",
                on_click=WorkflowState.add_condition_node
            ),
            spacing="2",
            width="100%"
        ),
        
        # Action Nodes
        rx.vstack(
            rx.text("ACTIONS", class_name="text-[10px] text-gray-500 font-bold mb-1 mt-3"),
            rx.button(
                rx.vstack(
                    rx.icon("zap", size=24, class_name="text-green-400"),
                    rx.text("Action", size="2"),
                    spacing="1"
                ),
                variant="outline",
                class_name="w-full h-20 border-gray-700 hover:bg-green-900/20 hover:border-green-500",
                on_click=WorkflowState.add_action_node
            ),
            spacing="2",
            width="100%"
        ),
        
        rx.separator(class_name="my-3 bg-gray-700"),
        
        # Clear button
        rx.button(
            rx.hstack(
                rx.icon("trash-2", size=14),
                rx.text("Clear All"),
                spacing="2"
            ),
            variant="ghost",
            class_name="w-full text-red-400 hover:bg-red-900/20",
            on_click=WorkflowState.clear_workflow
        ),
        
        class_name="w-64 h-full bg-gray-900 p-4 border-r border-gray-800",
        spacing="2"
    )


def workflow_canvas() -> rx.Component:
    """Main ReactFlow canvas"""
    return rx.box(
        react_flow(
            background(color="#1f2937", gap=16, size=1, variant="dots"),
            controls(),
            minimap(class_name="bg-gray-800"),
            nodes_draggable=True,
            nodes_connectable=True,
            on_connect=lambda e0: WorkflowState.on_connect(e0),
            on_nodes_change=lambda e0: WorkflowState.on_nodes_change(e0),
            on_edges_change=lambda e0: WorkflowState.on_edges_change(e0),
            nodes=WorkflowState.nodes,
            edges=WorkflowState.edges,
            fit_view=True,
            class_name="bg-gray-950"
        ),
        class_name="flex-1 h-full"
    )


def workflow_builder() -> rx.Component:
    """Main workflow builder page"""
    return rx.vstack(
        workflow_header(),
        rx.hstack(
            workflow_toolbox(),
            workflow_canvas(),
            spacing="0",
            class_name="flex-1 w-full h-full"
        ),
        spacing="0",
        class_name="h-screen w-full bg-black"
    )