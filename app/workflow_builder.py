# app/workflow_builder.py
"""
Fixed Workflow Builder with proper drag-drop implementation.

The key fixes:
1. Use a custom component to properly capture mouse coordinates
2. Proper event handling that doesn't conflict with ReactFlow
3. Use ReactFlow's native pane click for drop positioning
"""
from typing import Any, Dict
import reflex as rx
from reflex.components.radix.themes.layout.box import Box
from app.reactflow import react_flow, background, controls
from app.states.workflow_state import WorkflowState


class DropZone(Box):
    """
    A custom Box component that captures mouse coordinates on mouse up.
    This fixes the EventFnArgMismatchError by properly defining the event signature.
    """
    
    def get_event_triggers(self) -> Dict[str, Any]:
        return {
            **super().get_event_triggers(),
            # Define on_mouse_up to extract clientX and clientY from the event
            "on_mouse_up": lambda e: [e.clientX, e.clientY],
        }


# Create the component factory
drop_zone = DropZone.create


def workflow_header() -> rx.Component:
    """Header with navigation and save button"""
    return rx.hstack(
        rx.hstack(
            rx.icon("workflow", size=24, class_name="text-blue-400"),
            rx.heading("Workflow Builder", size="6", class_name="text-white"),
            spacing="3"
        ),
        rx.spacer(),
        rx.hstack(
            # Debug button to test node creation
            rx.button(
                rx.hstack(rx.icon("plus", size=16), rx.text("Test Add"), spacing="2"),
                variant="outline",
                color_scheme="green",
                on_click=WorkflowState.add_test_node
            ),
            rx.button(
                rx.hstack(rx.icon("home", size=16), rx.text("Monitor"), spacing="2"),
                variant="ghost",
                on_click=rx.redirect("/")
            ),
            rx.button(
                rx.hstack(rx.icon("save", size=16), rx.text("Save"), spacing="2"),
                variant="solid",
                color_scheme="blue"
            ),
            spacing="2"
        ),
        class_name="w-full p-4 border-b border-gray-800 bg-gray-900"
    )


def get_icon(icon_name: rx.Var[str]) -> rx.Component:
    """Get icon component by name"""
    return rx.match(
        icon_name,
        ("scan", rx.icon("scan", size=18)),
        ("box", rx.icon("box", size=18)),
        ("circle-dot", rx.icon("circle-dot", size=18)),
        ("package", rx.icon("package", size=18)),
        ("arrow-right", rx.icon("arrow-right", size=18)),
        ("circle", rx.icon("circle", size=18)),
        ("zap", rx.icon("zap", size=18)),
        ("message-circle", rx.icon("message-circle", size=18)),
        ("mail", rx.icon("mail", size=18)),
        ("bell", rx.icon("bell", size=18)),
        rx.icon("circle-help", size=18)
    )


def category_button(category: rx.Var[dict]) -> rx.Component:
    """
    Draggable category button.
    
    Uses mousedown to start drag and tracks via state.
    The actual drop is handled by the canvas area.
    """
    return rx.box(
        rx.button(
            rx.hstack(
                get_icon(category['icon']),
                rx.text(category['name'], size="2"),
                spacing="2"
            ),
            variant="outline",
            class_name=rx.cond(
                WorkflowState.is_dragging,
                "w-full border-gray-700 justify-start opacity-50 cursor-grabbing pointer-events-none",
                "w-full border-gray-700 hover:bg-blue-900/20 hover:border-blue-500 justify-start cursor-grab"
            ),
            type="button",
        ),
        class_name="w-full select-none",
        # Start drag on mousedown
        on_mouse_down=WorkflowState.start_drag(
            category['key'], 
            category['type'] == 'action'
        ),
    )


def equipment_panel() -> rx.Component:
    """Left sidebar with draggable equipment categories"""
    return rx.cond(
        WorkflowState.show_equipment_panel,
        rx.vstack(
            rx.hstack(
                rx.text("TOOLBOX", class_name="text-xs font-bold text-gray-400 uppercase"),
                rx.spacer(),
                rx.button(
                    rx.icon("x", size=14),
                    variant="ghost",
                    size="1",
                    on_click=WorkflowState.toggle_equipment_panel
                ),
                width="100%"
            ),
            rx.box(
                rx.vstack(
                    rx.text("EQUIPMENT", class_name="text-[10px] text-gray-500 font-bold uppercase mb-2"),
                    rx.text(
                        rx.cond(
                            WorkflowState.is_dragging,
                            "Release on canvas to drop",
                            "Click and drag to canvas"
                        ),
                        class_name=rx.cond(
                            WorkflowState.is_dragging,
                            "text-[9px] text-green-400 mb-2 italic font-bold",
                            "text-[9px] text-gray-600 mb-2 italic"
                        )
                    ),
                    rx.foreach(WorkflowState.equipment_categories, category_button),
                    rx.separator(class_name="my-4 bg-gray-700"),
                    rx.text("ACTIONS", class_name="text-[10px] text-gray-500 font-bold uppercase mb-2"),
                    rx.foreach(WorkflowState.action_categories, category_button),
                    spacing="2",
                    width="100%"
                ),
                class_name="flex-1 overflow-y-auto",
                height="calc(100vh - 180px)"
            ),
            rx.vstack(
                rx.separator(class_name="bg-gray-700"),
                rx.button(
                    rx.hstack(rx.icon("trash-2", size=14), rx.text("Clear"), spacing="2"),
                    variant="ghost",
                    class_name="w-full text-red-400 hover:bg-red-900/20",
                    on_click=WorkflowState.clear_workflow
                ),
                spacing="2",
                width="100%"
            ),
            class_name="w-64 h-full bg-gray-900 border-r border-gray-800 flex flex-col p-4",
            spacing="0"
        ),
        rx.button(
            rx.icon("panel-left", size=16),
            variant="ghost",
            class_name="absolute top-20 left-4 z-50 bg-gray-900 border border-gray-700 hover:bg-gray-800",
            on_click=WorkflowState.toggle_equipment_panel
        )
    )


def config_menu() -> rx.Component:
    """Configuration menu for selected node"""
    return rx.cond(
        WorkflowState.selected_node_id != "",
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.text("Node Configuration", class_name="text-sm font-bold text-white"),
                    rx.spacer(),
                    rx.button(
                        rx.icon("x", size=14),
                        variant="ghost",
                        size="1",
                        on_click=WorkflowState.close_config_menu
                    ),
                    width="100%"
                ),
                rx.text(f"Selected: {WorkflowState.selected_node_id}", class_name="text-xs text-gray-400"),
                rx.separator(class_name="my-2 bg-gray-700"),
                rx.text("Configuration options will appear here", class_name="text-xs text-gray-500"),
                spacing="2",
                width="100%"
            ),
            class_name="absolute top-20 right-4 bg-gray-900 p-4 border border-gray-700 rounded-lg z-50 w-64"
        ),
        rx.fragment()
    )


def drag_indicator() -> rx.Component:
    """Visual indicator when dragging"""
    return rx.cond(
        WorkflowState.is_dragging,
        rx.box(
            rx.hstack(
                rx.icon("mouse-pointer-click", size=16, class_name="text-green-400"),
                rx.text(f"Dragging: {WorkflowState.dragged_type}", class_name="text-sm text-green-400"),
                spacing="2"
            ),
            class_name="fixed bottom-4 left-1/2 transform -translate-x-1/2 bg-gray-900 border border-green-500 px-4 py-2 rounded-full shadow-lg z-[100]"
        ),
        rx.fragment()
    )


def drop_overlay() -> rx.Component:
    """
    Overlay that captures the drop event when dragging.
    Uses our custom DropZone component that properly captures mouse coordinates.
    """
    return rx.cond(
        WorkflowState.is_dragging,
        drop_zone(
            # Visual feedback for drop zone
            rx.box(
                rx.vstack(
                    rx.icon("download", size=32, class_name="text-blue-400 opacity-50"),
                    rx.text("Release to drop here", class_name="text-sm text-blue-400 opacity-75"),
                    class_name="items-center justify-center"
                ),
                class_name="absolute inset-0 flex items-center justify-center pointer-events-none"
            ),
            class_name="absolute inset-0 bg-blue-500/5 border-2 border-dashed border-blue-500/30 z-40 cursor-copy",
            # Capture mouseup with coordinates using our custom component
            on_mouse_up=WorkflowState.handle_drop,
            on_mouse_leave=WorkflowState.cancel_drag,
        ),
        rx.fragment()
    )


def workflow_canvas() -> rx.Component:
    """
    Main canvas area with ReactFlow.
    """
    return rx.box(
        # ReactFlow component - controlled mode
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
            
            class_name="bg-gray-950 w-full h-full",
            style={"width": "100%", "height": "100%"}
        ),
        # Drop overlay
        drop_overlay(),
        # Config menu
        config_menu(),
        
        class_name="flex-1 h-full w-full relative overflow-hidden",
        id="workflow-canvas"
    )


def workflow_builder() -> rx.Component:
    """Main workflow builder page"""
    return rx.vstack(
        workflow_header(),
        rx.hstack(
            equipment_panel(),
            workflow_canvas(),
            spacing="0",
            class_name="flex-1 w-full h-full relative"
        ),
        drag_indicator(),
        spacing="0",
        class_name="h-screen w-full bg-black select-none",
        on_mount=WorkflowState.load_equipment,
    )