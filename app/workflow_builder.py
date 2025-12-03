# app/workflow_builder.py
from typing import Any, Dict
import reflex as rx
from app.reactflow import react_flow, background, controls
from app.states.workflow_state import WorkflowState

# --- IMPORTACIÓN CRÍTICA PARA ARREGLAR EL EVENTO ---
# Importamos la clase Box base para poder modificar sus eventos
from reflex.components.radix.themes.layout.box import Box

class DropZoneBox(Box):
    """
    Un Box especial que permite capturar coordenadas en on_mouse_up.
    Esto arregla el error 'EventFnArgMismatchError'.
    """
    def get_event_triggers(self) -> Dict[str, Any]:
        return {
            **super().get_event_triggers(),
            # SOBRESCRIBIMOS EL EVENTO:
            # Le decimos a Reflex que capture clientX y clientY del evento JS
            "on_mouse_up": lambda e: [e.clientX, e.clientY],
        }

def workflow_header() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.icon("workflow", size=24, class_name="text-blue-400"),
            rx.heading("Workflow Builder", size="6", class_name="text-white"),
            spacing="3"
        ),
        rx.spacer(),
        rx.hstack(
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
    # Usamos rx.el.div para los botones arrastrables
    return rx.el.div(
        rx.button(
            rx.hstack(
                get_icon(category['icon']),
                rx.text(category['name'], size="2"),
                spacing="2"
            ),
            variant="outline",
            class_name="w-full border-gray-700 hover:bg-blue-900/20 hover:border-blue-500 justify-start pointer-events-none",
        ),
        class_name="w-full cursor-pointer active:scale-95 transition-transform",
        # Inicia el drag en el estado
        on_mouse_down=WorkflowState.start_drag(
            category['key'], 
            category['type'] == 'action'
        )
    )

def equipment_panel() -> rx.Component:
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
                    rx.text("Drag to canvas", class_name="text-[9px] text-gray-600 mb-2 italic"),
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
    return rx.cond(
        WorkflowState.selected_node_id != "",
        rx.box(
            rx.text("Configuration Menu Placeholder"),
            class_name="absolute top-20 right-4 bg-gray-900 p-4 border border-gray-700 rounded z-50"
        ),
        rx.fragment()
    )

def workflow_canvas() -> rx.Component:
    # USAMOS NUESTRO DropZoneBox EN LUGAR DE rx.box
    return DropZoneBox.create(
        react_flow(
            background(color="#374151", gap=16, size=1, variant="dots"),
            controls(),
            
            nodes_draggable=True,
            nodes_connectable=True,
            
            # Eventos nativos de ReactFlow
            on_connect=WorkflowState.on_connect,
            on_nodes_change=WorkflowState.on_nodes_change,
            on_edges_change=WorkflowState.on_edges_change,
            
            nodes=WorkflowState.nodes,
            edges=WorkflowState.edges,
            fit_view=True,
            
            class_name="bg-gray-950 w-full h-full",
            style={"width": "100%", "height": "100%"}
        ),
        config_menu(),
        
        # AHORA ESTO FUNCIONARÁ
        # Porque DropZoneBox define que on_mouse_up acepta argumentos
        on_mouse_up=WorkflowState.handle_drop,
        
        class_name="flex-1 h-full w-full relative"
    )

def workflow_builder() -> rx.Component:
    return rx.vstack(
        workflow_header(),
        rx.hstack(
            equipment_panel(),
            workflow_canvas(),
            spacing="0",
            class_name="flex-1 w-full h-full relative"
        ),
        spacing="0",
        class_name="h-screen w-full bg-black",
        on_mount=WorkflowState.load_equipment
    )