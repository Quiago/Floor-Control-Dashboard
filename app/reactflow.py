# app/reactflow.py
"""
ReactFlow wrapper for Reflex.

Based on the official Reflex documentation example.
Uses rx.Component (not NoSSRComponent) as per the working example.
"""
import reflex as rx
from typing import Any, Dict, List


class ReactFlowLib(rx.Component):
    """
    Base component for ReactFlow library.
    
    Note: Using rx.Component as per the working Reflex example.
    ReactFlow handles its own client-side rendering internally.
    """
    library = "reactflow@11.10.1"
    
    def _get_custom_code(self) -> str:
        """Import ReactFlow's CSS styles"""
        return """import 'reactflow/dist/style.css';"""


class ReactFlow(ReactFlowLib):
    """Main ReactFlow component"""
    
    tag = "ReactFlow"
    
    # Data props
    nodes: rx.Var[List[Dict[str, Any]]]
    edges: rx.Var[List[Dict[str, Any]]]
    
    # View props
    fit_view: rx.Var[bool]
    
    # Interaction props
    nodes_draggable: rx.Var[bool]
    nodes_connectable: rx.Var[bool]
    nodes_focusable: rx.Var[bool]
    
    # Event handlers - use the exact pattern from the docs
    on_nodes_change: rx.EventHandler[lambda e0: [e0]]
    on_edges_change: rx.EventHandler[lambda e0: [e0]]
    on_connect: rx.EventHandler[lambda e0: [e0]]


class Background(ReactFlowLib):
    """Background component for ReactFlow"""
    
    tag = "Background"
    
    color: rx.Var[str]
    gap: rx.Var[int]
    size: rx.Var[int]
    variant: rx.Var[str]


class Controls(ReactFlowLib):
    """Controls component for ReactFlow"""
    
    tag = "Controls"


# Create component factory functions
react_flow = ReactFlow.create
background = Background.create
controls = Controls.create

