# app/reactflow.py (UPDATED - fix React Flow warnings)
import reflex as rx
from typing import Any, Dict, List


class ReactFlowLib(rx.Component):
    """Base component for reactflow library"""
    library = "reactflow"
    lib_dependencies = ["reactflow@11.11.0"]
    
    def _get_custom_code(self) -> str:
        return """import 'reactflow/dist/style.css';"""


class ReactFlow(ReactFlowLib):
    """Main ReactFlow canvas component"""
    tag = "ReactFlow"
    
    nodes: rx.Var[List[Dict[str, Any]]]
    edges: rx.Var[List[Dict[str, Any]]]
    
    fit_view: rx.Var[bool] = True
    nodes_draggable: rx.Var[bool] = True
    nodes_connectable: rx.Var[bool] = True
    nodes_focusable: rx.Var[bool] = True
    
    on_nodes_change: rx.EventHandler[lambda e0: [e0]]
    on_edges_change: rx.EventHandler[lambda e0: [e0]]
    on_connect: rx.EventHandler[lambda e0: [e0]]


class Background(ReactFlowLib):
    """Background pattern for ReactFlow"""
    tag = "Background"
    
    color: rx.Var[str] = "#374151"
    gap: rx.Var[int] = 16
    size: rx.Var[int] = 1
    variant: rx.Var[str] = "dots"


class Controls(ReactFlowLib):
    """Navigation controls for ReactFlow"""
    tag = "Controls"


class MiniMap(ReactFlowLib):
    """Minimap overview for ReactFlow"""
    tag = "MiniMap"
    
    node_color: rx.Var[str] = "#4b5563"
    mask_color: rx.Var[str] = "#1f2937"
    zoom_able: rx.Var[bool] = True
    pan_able: rx.Var[bool] = True


react_flow = ReactFlow.create
background = Background.create
controls = Controls.create
minimap = MiniMap.create