# app/components/workflow/header.py
"""Header del Workflow Builder"""
import reflex as rx
from app.states.workflow_state import WorkflowState
from app.components.shared.design_tokens import GRADIENT_PRIMARY, TRANSITION_DEFAULT
from app.components.shared import stat_pill

def workflow_header() -> rx.Component:
    """Header con nombre, stats y acciones"""
    return rx.hstack(
        # Left: Name + Status
        rx.hstack(
            rx.icon("workflow", size=24, class_name="text-blue-400"),
            rx.vstack(
                rx.input(
                    value=WorkflowState.current_workflow_name,
                    on_change=WorkflowState.set_workflow_name,
                    class_name="text-lg font-bold text-white bg-transparent border-none focus:outline-none w-48",
                    placeholder="Workflow name..."
                ),
                rx.hstack(
                    rx.badge(
                        WorkflowState.current_workflow_status,
                        color_scheme=rx.cond(
                            WorkflowState.current_workflow_status == "active",
                            "green",
                            rx.cond(
                                WorkflowState.current_workflow_status == "paused",
                                "yellow",
                                "gray"
                            )
                        ),
                        size="1"
                    ),
                    stat_pill("nodes", WorkflowState.node_count.to_string(), "blue"),
                    stat_pill("connections", WorkflowState.edge_count.to_string(), "cyan"),
                    spacing="2"
                ),
                spacing="0",
                align_items="start"
            ),
            spacing="3",
            align_items="center"
        ),
        
        rx.spacer(),
        
        # Right: Actions
        rx.hstack(
            rx.button(
                rx.hstack(rx.icon("folder-open", size=16), rx.text("Open"), spacing="2"),
                variant="ghost",
                on_click=WorkflowState.toggle_workflow_list,
                class_name=TRANSITION_DEFAULT
            ),
            rx.button(
                rx.hstack(rx.icon("file-plus", size=16), rx.text("New"), spacing="2"),
                variant="ghost",
                on_click=WorkflowState.new_workflow,
                class_name=TRANSITION_DEFAULT
            ),
            rx.button(
                rx.hstack(rx.icon("play", size=16), rx.text("Test"), spacing="2"),
                variant="outline",
                color_scheme="yellow",
                on_click=WorkflowState.test_workflow_execution,
                class_name=TRANSITION_DEFAULT
            ),
            rx.button(
                rx.hstack(rx.icon("save", size=16), rx.text("Save"), spacing="2"),
                variant="solid",
                color_scheme="blue",
                on_click=WorkflowState.save_workflow,
                class_name=TRANSITION_DEFAULT
            ),
            rx.cond(
                WorkflowState.current_workflow_status == "active",
                rx.button(
                    rx.hstack(rx.icon("pause", size=16), rx.text("Pause"), spacing="2"),
                    variant="outline",
                    color_scheme="yellow",
                    on_click=WorkflowState.pause_workflow
                ),
                rx.button(
                    rx.hstack(rx.icon("zap", size=16), rx.text("Activate"), spacing="2"),
                    variant="solid",
                    class_name=f"{GRADIENT_PRIMARY} text-white",
                    on_click=WorkflowState.activate_workflow
                )
            ),
            rx.button(
                rx.hstack(rx.icon("home", size=16), rx.text("Monitor"), spacing="2"),
                variant="ghost",
                on_click=rx.redirect("/")
            ),
            spacing="2"
        ),
        
        class_name="w-full p-4 border-b border-white/10 bg-[#12121a]",
        align_items="center"
    )