# app/workflow_builder.py
from typing import Dict, Any
import reflex as rx
from app.reactflow import react_flow, background, controls, minimap
from app.states.workflow_state import WorkflowState


def workflow_header() -> rx.Component:
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
                rx.hstack(rx.icon("home", size=16), rx.text("Monitor"), spacing="2"),
                variant="ghost",
                on_click=rx.redirect("/"),
                class_name="text-gray-300 hover:text-white"
            ),
            rx.button(
                rx.hstack(rx.icon("save", size=16), rx.text("Save"), spacing="2"),
                variant="solid",
                color_scheme="blue"
            ),
            spacing="2"
        ),
        class_name="w-full p-4 border-b border-gray-800 bg-gray-900",
        align_items="center"
    )

# --- ICON HELPER ---
def get_icon(icon_name: rx.Var[str]) -> rx.Component:
    """Helper to render dynamic icons safely using rx.match"""
    return rx.match(
        icon_name,
        ("scan", rx.icon("scan", size=16, class_name="text-blue-400")),
        ("box", rx.icon("box", size=16, class_name="text-blue-400")),
        ("circle-dot", rx.icon("circle-dot", size=16, class_name="text-blue-400")),
        ("package", rx.icon("package", size=16, class_name="text-blue-400")),
        ("arrow-right", rx.icon("arrow-right", size=16, class_name="text-blue-400")),
        ("circle", rx.icon("circle", size=16, class_name="text-blue-400")),
        ("zap", rx.icon("zap", size=16, class_name="text-blue-400")),
        rx.icon("circle-help", size=16, class_name="text-blue-400")
    )


def equipment_category(category: Any) -> rx.Component:
    """Equipment category section"""
    # FIX: Cast category to dict to ensure key access works
    category = category.to(dict)
    
    return rx.vstack(
        rx.hstack(
            get_icon(category['icon']),
            rx.text(category['name'], size="2", class_name="font-semibold text-gray-300"),
            rx.badge(category['count'], size="1", variant="soft", color_scheme="blue"),
            spacing="2",
            align_items="center",
            class_name="mb-2"
        ),
        
        rx.vstack(
            rx.foreach(
                # FIX: Ensure 'equipment' is treated as a list
                category['equipment'].to(list),
                
                # FIX: 'eq' is untyped, so we must cast it to dict to access ['label'] and ['id']
                lambda eq: rx.button(
                    rx.vstack(
                        get_icon(category['icon']),
                        rx.text(eq.to(dict)['label'], size="1", class_name="text-center truncate w-full"),
                        spacing="1",
                        width="100%"
                    ),
                    variant="outline",
                    class_name="w-full h-14 border-gray-700 hover:bg-blue-900/20 hover:border-blue-500 text-gray-300",
                    on_click=WorkflowState.add_equipment_node(eq.to(dict)['id'])
                )
            ),
            spacing="2",
            width="100%"
        ),
        
        spacing="2",
        width="100%",
        class_name="mb-4"
    )


def equipment_panel() -> rx.Component:
    """Equipment library panel"""
    return rx.cond(
        WorkflowState.show_equipment_panel,
        rx.vstack(
            rx.hstack(
                rx.text("EQUIPMENT", class_name="text-xs font-bold text-gray-400 uppercase"),
                rx.spacer(),
                rx.button(
                    rx.icon("x", size=14),
                    variant="ghost",
                    size="1",
                    on_click=WorkflowState.toggle_equipment_panel,
                    class_name="text-gray-400 hover:text-white"
                ),
                width="100%",
                class_name="mb-3"
            ),
            
            rx.box(
                rx.vstack(
                    rx.foreach(
                        # FIX: Explicitly cast the state var to list
                        WorkflowState.equipment_by_category.to(list),
                        equipment_category
                    ),
                    
                    rx.separator(class_name="my-3 bg-gray-700"),
                    
                    rx.vstack(
                        rx.text("ACTIONS", class_name="text-[10px] text-gray-500 font-bold uppercase mb-2"),
                        rx.button(
                            rx.vstack(
                                rx.icon("zap", size=16, class_name="text-green-400"),
                                rx.text("Send Alert", size="1"),
                                spacing="1"
                            ),
                            variant="outline",
                            class_name="w-full h-14 border-gray-700 hover:bg-green-900/20 text-gray-300",
                            on_click=WorkflowState.add_action_node
                        ),
                        spacing="2",
                        width="100%"
                    ),
                    
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
            
            class_name="w-72 h-full bg-gray-900 border-r border-gray-800 flex flex-col p-4",
            spacing="0"
        ),
        rx.button(
            rx.icon("panel-left", size=16),
            variant="ghost",
            class_name="absolute top-20 left-4 z-50 bg-gray-900 border border-gray-700 hover:bg-gray-800",
            on_click=WorkflowState.toggle_equipment_panel
        )
    )


def workflow_canvas() -> rx.Component:
    return rx.box(
        react_flow(
            background(
                color="#374151",
                gap=16,
                size=1,
                variant="dots"
            ),
            controls(),
            minimap(
                node_color="#4b5563",
                mask_color="#1f2937",
                class_name="!bg-gray-900 !border !border-gray-700"
            ),
            nodes_draggable=True,
            nodes_connectable=True,
            on_connect=WorkflowState.on_connect,
            on_nodes_change=WorkflowState.on_nodes_change,
            on_edges_change=WorkflowState.on_edges_change,
            nodes=WorkflowState.nodes,
            edges=WorkflowState.edges,
            fit_view=True,
            class_name="bg-gray-950"
        ),
        class_name="flex-1 h-full"
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