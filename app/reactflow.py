# app/reactflow.py
"""
ReactFlow wrapper for Reflex - CONTROLLED MODE.

IMPORTANT: Using reactflow@11.10.1 because version 11.11.3+ has a bug
where nodes disappear when position is updated in controlled mode.
See: https://github.com/xyflow/xyflow/issues/4287
"""
import reflex as rx
from typing import Any, Dict, List


class ReactFlowLib(rx.Component):
    """Base component for ReactFlow library."""
    # Pin to 11.10.1 - later versions have the disappearing nodes bug
    library = "reactflow@11.10.1"
    
    def _get_custom_code(self) -> str:
        """Import ReactFlow's CSS styles"""
        return """import 'reactflow/dist/style.css';"""


class ReactFlow(ReactFlowLib):
    """Main ReactFlow component - controlled mode"""
    
    tag = "ReactFlow"
    
    # CONTROLLED mode props
    nodes: rx.Var[List[Dict[str, Any]]]
    edges: rx.Var[List[Dict[str, Any]]]
    
    # View props
    fit_view: rx.Var[bool]
    
    # Interaction props
    nodes_draggable: rx.Var[bool]
    nodes_connectable: rx.Var[bool]
    
    # Event handlers
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


react_flow = ReactFlow.create
background = Background.create
controls = Controls.create