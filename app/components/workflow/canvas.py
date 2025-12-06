# app/components/workflow/canvas.py
"""Canvas principal con ReactFlow"""
import reflex as rx
from typing import Any, Dict
from reflex.components.radix.themes.layout.box import Box
from app.reactflow import react_flow, background, controls
from app.states.workflow_state import WorkflowState
from app.components.shared.design_tokens import TRANSITION_DEFAULT

class DropZone(Box):
    """Box que captura coordenadas del mouse"""
    def get_event_triggers(self) -> Dict[str, Any]:
        return {
            **super().get_event_triggers(),
            "on_mouse_up": lambda e: [e.clientX, e.clientY],
        }

drop_zone = DropZone.create

def workflow_canvas() -> rx.Component:
    """Canvas principal con ReactFlow"""
    return rx.box(
        react_flow(
            background(color="#374151", gap=16, size=1, variant="dots"),
            controls(),
            nodes_draggable=True,
            nodes_connectable=True,
            on_connect=lambda e0: WorkflowState.on_connect(e0),
            on_nodes_change=lambda e0: WorkflowState.on_nodes_change(e0),
            on_edges_change=lambda e0: WorkflowState.on_edges_change(e0),
            nodes=WorkflowState.nodes,
            edges=WorkflowState.edges,
            fit_view=True,
            class_name="bg-[#0a0a0f] w-full h-full",
            style={"width": "100%", "height": "100%"}
        ),
        drop_overlay(),
        drag_indicator(),
        class_name="flex-1 h-full w-full relative overflow-hidden",
        id="workflow-canvas"
    )

def drop_overlay() -> rx.Component:
    """Overlay cuando se arrastra"""
    return rx.cond(
        WorkflowState.is_dragging,
        drop_zone(
            rx.box(
                rx.vstack(
                    rx.icon("download", size=32, class_name="text-emerald-400 opacity-50"),
                    rx.text(
                        "Release to drop here",
                        class_name="text-sm text-emerald-400 opacity-75"
                    ),
                    class_name="items-center justify-center"
                ),
                class_name="absolute inset-0 flex items-center justify-center pointer-events-none"
            ),
            class_name=f"absolute inset-0 bg-emerald-500/5 border-2 border-dashed border-emerald-500/30 z-40 cursor-copy {TRANSITION_DEFAULT}",
            on_mouse_up=WorkflowState.handle_drop,
            on_mouse_leave=WorkflowState.cancel_drag,
        ),
        rx.fragment()
    )

def drag_indicator() -> rx.Component:
    """Indicador de drag activo"""
    return rx.cond(
        WorkflowState.is_dragging,
        rx.box(
            rx.hstack(
                rx.icon("mouse-pointer-click", size=16, class_name="text-emerald-400 animate-pulse"),
                rx.text(
                    f"Dragging: {WorkflowState.dragged_type}",
                    class_name="text-sm text-emerald-400 font-medium"
                ),
                spacing="2"
            ),
            class_name="fixed bottom-24 left-1/2 transform -translate-x-1/2 bg-gray-900/90 backdrop-blur border border-emerald-500 px-4 py-2 rounded-full shadow-lg z-[100]"
        ),
        rx.fragment()
    )