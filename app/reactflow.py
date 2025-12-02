"""
Reactflow wrapper for Reflex.
Based on reactflow library for building node-based workflows.
"""
import reflex as rx
from typing import Any, Dict, List


class ReactFlowLib(rx.Component):
    """Base component for reactflow library"""
    library = "reactflow"
    
    def _get_custom_code(self) -> str:
        return """import 'reactflow/dist/style.css';"""


class ReactFlow(ReactFlowLib):
    """Main ReactFlow canvas component"""
    tag = "ReactFlow"
    
    # Node and edge data
    nodes: rx.Var[List[Dict[str, Any]]]
    edges: rx.Var[List[Dict[str, Any]]]
    
    # Display options
    fit_view: rx.Var[bool]
    nodes_draggable: rx.Var[bool]
    nodes_connectable: rx.Var[bool]
    nodes_focusable: rx.Var[bool]
    
    # Event handlers
    on_nodes_change: rx.EventHandler[lambda e0: [e0]]
    on_edges_change: rx.EventHandler[lambda e0: [e0]]
    on_connect: rx.EventHandler[lambda e0: [e0]]


class Background(ReactFlowLib):
    """Background pattern for ReactFlow"""
    tag = "Background"
    
    color: rx.Var[str]
    gap: rx.Var[int]
    size: rx.Var[int]
    variant: rx.Var[str]


class Controls(ReactFlowLib):
    """Navigation controls for ReactFlow"""
    tag = "Controls"


class MiniMap(ReactFlowLib):
    """Minimap overview for ReactFlow"""
    tag = "MiniMap"


# Create convenience functions
react_flow = ReactFlow.create
background = Background.create
controls = Controls.create
minimap = MiniMap.create