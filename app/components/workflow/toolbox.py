# app/components/workflow/toolbox.py
"""Sidebar with draggable tools"""
import reflex as rx
from app.states.workflow_state import WorkflowState
from app.components.shared.design_tokens import GLASS_PANEL_PREMIUM, TRANSITION_DEFAULT
from app.components.shared import section_label, icon_button

def get_icon(icon_name: rx.Var[str], size: int = 16) -> rx.Component:
    """Get icon by name"""
    return rx.match(
        icon_name,
        ("scan", rx.icon("scan", size=size)),
        ("box", rx.icon("box", size=size)),
        ("circle-dot", rx.icon("circle-dot", size=size)),
        ("package", rx.icon("package", size=size)),
        ("arrow-right", rx.icon("arrow-right", size=size)),
        ("globe", rx.icon("globe", size=size)),
        ("message-circle", rx.icon("message-circle", size=size)),
        ("mail", rx.icon("mail", size=size)),
        ("bell", rx.icon("bell", size=size)),
        rx.icon("circle-help", size=size)
    )

def category_button(category: rx.Var[dict]) -> rx.Component:
    """Botón draggable de categoría"""
    return rx.box(
        rx.button(
            rx.hstack(
                # Icon with gradient background
                rx.box(
                    get_icon(category['icon'], size=18),
                    class_name=f"p-2 rounded bg-gradient-to-br from-{category['color']}-500/20 to-{category['color']}-600/10"
                ),
                rx.text(category['name'], size="2", class_name="font-medium"),
                spacing="2"
            ),
            variant="ghost",
            class_name=rx.cond(
                WorkflowState.is_dragging,
                f"w-full justify-start opacity-50 cursor-grabbing pointer-events-none {TRANSITION_DEFAULT}",
                f"w-full justify-start cursor-grab hover:bg-slate-700/40 border border-transparent hover:border-slate-600/40 {TRANSITION_DEFAULT}"
            ),
            type="button",
        ),
        class_name="w-full select-none",
        on_mouse_down=WorkflowState.start_drag(
            category['key'],
            category['type'] == 'action'
        ),
    )

def equipment_panel() -> rx.Component:
    """Panel lateral izquierdo"""
    return rx.cond(
        WorkflowState.show_equipment_panel,
        rx.vstack(
            # Header
            rx.hstack(
                rx.text(
                    "TOOLBOX",
                    class_name="text-xs font-bold text-slate-400 uppercase tracking-wider"
                ),
                rx.spacer(),
                icon_button("x", WorkflowState.toggle_equipment_panel, size=14),
                width="100%"
            ),
            
            # Content
            rx.box(
                rx.vstack(
                    # Equipment
                    section_label("EQUIPMENT"),
                    rx.text(
                        rx.cond(
                            WorkflowState.is_dragging,
                            "Release on canvas to drop",
                            "Click and drag to canvas"
                        ),
                        class_name=rx.cond(
                            WorkflowState.is_dragging,
                            "text-[9px] text-green-400 mb-2 italic font-bold",
                            "text-[9px] text-slate-500 mb-2 italic"
                        )
                    ),
                    rx.foreach(WorkflowState.equipment_categories, category_button),
                    
                    rx.box(class_name="h-px w-full bg-gradient-to-r from-transparent via-slate-500/30 to-transparent my-4"),
                    
                    # Actions
                    section_label("ACTIONS"),
                    rx.foreach(WorkflowState.action_categories, category_button),
                    
                    spacing="2",
                    width="100%"
                ),
                class_name="flex-1 overflow-y-auto",
                height="calc(100vh - 350px)"
            ),
            
            # Footer
            rx.vstack(
                rx.box(class_name="h-px w-full bg-gradient-to-r from-transparent via-slate-500/30 to-transparent"),
                rx.button(
                    rx.hstack(
                        rx.icon("trash-2", size=14),
                        rx.text("Clear All"),
                        spacing="2"
                    ),
                    variant="ghost",
                    class_name="w-full text-rose-400 hover:bg-rose-900/20",
                    on_click=WorkflowState.clear_workflow
                ),
                spacing="2",
                width="100%"
            ),
            
            class_name=f"w-64 h-full {GLASS_PANEL_PREMIUM} border-r border-slate-600/40 flex flex-col p-4",
            spacing="0"
        ),
        rx.button(
            rx.icon("panel-left", size=16),
            variant="ghost",
            class_name=f"absolute top-20 left-4 z-50 {GLASS_PANEL_PREMIUM} border border-slate-600/40 hover:bg-slate-700/50",
            on_click=WorkflowState.toggle_equipment_panel
        )
    )