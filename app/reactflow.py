# app/reactflow.py
import reflex as rx
from typing import Any, Dict, List

class ReactFlowLib(rx.Component):
    """Componente base para la librería reactflow."""
    library = "reactflow"
    lib_dependencies = ["reactflow@11.11.0"]
    
    def _get_custom_code(self) -> str:
        return """import 'reactflow/dist/style.css';"""

class ReactFlow(ReactFlowLib):
    tag = "ReactFlow"
    
    # Props de datos
    nodes: rx.Var[List[Dict[str, Any]]]
    edges: rx.Var[List[Dict[str, Any]]]
    fit_view: rx.Var[bool]
    
    # Props de configuración
    nodes_draggable: rx.Var[bool]
    nodes_connectable: rx.Var[bool]
    nodes_focusable: rx.Var[bool]
    
    # Eventos estándar (Serializamos el evento para evitar errores de ciclo)
    on_nodes_change: rx.EventHandler[lambda e0: [e0]]
    on_edges_change: rx.EventHandler[lambda e0: [e0]]
    on_connect: rx.EventHandler[lambda e0: [e0]]
    
    # Eventos de panel (Opcionales, pero los definimos seguros por si acaso)
    on_pane_click: rx.EventHandler[lambda e: [e.clientX, e.clientY]]
    on_pane_mouse_move: rx.EventHandler[lambda e: [e.clientX, e.clientY]]

class Background(ReactFlowLib):
    tag = "Background"
    color: rx.Var[str] = "#374151"
    gap: rx.Var[int] = 16
    size: rx.Var[int] = 1
    variant: rx.Var[str] = "dots"

class Controls(ReactFlowLib):
    tag = "Controls"

# Instancias
react_flow = ReactFlow.create
background = Background.create
controls = Controls.create