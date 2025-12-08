# app/components/monitor/context_menu.py
"""Floating contextual menu when equipment is selected"""
import reflex as rx
from app.states.monitor_state import MonitorState
from app.components.shared.design_tokens import (
    GLASS_PANEL_PREMIUM, TRANSITION_DEFAULT, SHADOW_XL
)
from app.components.shared import gradient_separator, icon_button, section_label

def floating_context_menu() -> rx.Component:
    """Menú flotante inferior derecha con props y acciones"""
    return rx.cond(
        MonitorState.selected_object_name != "",
        rx.vstack(
            # HEADER
            rx.hstack(
                rx.icon("box", size=16, class_name="text-orange-400"),
                rx.text(
                    MonitorState.selected_object_name,
                    class_name="font-bold text-white text-sm truncate"
                ),
                rx.spacer(),
                icon_button("x", on_click=MonitorState.clear_selection, size=14),
                width="100%",
                align_items="center"
            ),
            
            gradient_separator(),
            
            # TABS: Main / Actions
            rx.cond(
                MonitorState.menu_mode == "main",
                properties_view(),
                actions_view()
            ),
            
            spacing="3",
            class_name=f"{GLASS_PANEL_PREMIUM} absolute bottom-6 right-6 p-4 rounded-xl {SHADOW_XL} z-50 w-80 max-w-[90vw]"
        ),
        rx.fragment()
    )

def properties_view() -> rx.Component:
    """Vista de propiedades del equipo"""
    return rx.vstack(
        # Stats Grid
        rx.grid(
            rx.vstack(
                rx.text("TEMP", class_name="text-[10px] text-slate-400 font-bold"),
                rx.text(
                    f"{MonitorState.equipment_temp}°C",
                    class_name="text-sm font-mono text-slate-100"
                ),
                spacing="1"
            ),
            rx.vstack(
                rx.text("PRESS", class_name="text-[10px] text-slate-400 font-bold"),
                rx.text(
                    f"{MonitorState.equipment_pressure}",
                    class_name="text-sm font-mono text-slate-100"
                ),
                spacing="1"
            ),
            rx.vstack(
                rx.text("STATUS", class_name="text-[10px] text-slate-400 font-bold"),
                rx.badge(MonitorState.equipment_status, size="1", color_scheme="green"),
                spacing="1"
            ),
            columns="3",
            width="100%",
            gap="2"
        ),
        
        gradient_separator(),
        
        # Actions
        rx.vstack(
            rx.button(
                rx.hstack(
                    rx.cond(
                        MonitorState.is_expanded,
                        rx.icon("minimize-2", size=18),
                        rx.icon("maximize-2", size=18)
                    ),
                    rx.vstack(
                        rx.text(
                            rx.cond(MonitorState.is_expanded, "Restore", "Focus Mode"),
                            class_name="font-bold"
                        ),
                        rx.text("Graph Context", class_name="text-[10px] opacity-80"),
                        align_items="start",
                        spacing="0"
                    ),
                    spacing="2"
                ),
                variant="solid",
                color_scheme=rx.cond(MonitorState.is_expanded, "indigo", "gray"),
                size="3",
                width="100%",
                on_click=MonitorState.toggle_expand,
                class_name=TRANSITION_DEFAULT
            ),
            
            rx.button(
                rx.hstack(
                    rx.icon("zap", size=16),
                    rx.text("Quick Actions"),
                    spacing="2"
                ),
                variant="soft",
                size="2",
                width="100%",
                on_click=MonitorState.set_menu_mode("actions"),
                class_name=TRANSITION_DEFAULT
            ),
            spacing="2",
            width="100%"
        ),
        
        spacing="3",
        width="100%"
    )

def actions_view() -> rx.Component:
    """Vista de acciones rápidas"""
    return rx.vstack(
        section_label("ACTIONS"),
        
        rx.grid(
            rx.button(
                rx.vstack(
                    rx.icon("git-branch-plus", size=18),
                    rx.text("New Workflow", size="1"),
                    spacing="1"
                ),
                variant="outline",
                class_name="h-16 text-blue-400 hover:bg-blue-500/10",
                on_click=MonitorState.create_workflow_for_selection
            ),
            rx.button(
                rx.vstack(
                    rx.icon("send", size=18),
                    rx.text("Send", size="1"),
                    spacing="1"
                ),
                variant="outline",
                class_name="h-16 hover:bg-white/5",
                on_click=lambda: MonitorState.handle_quick_action("SEND")
            ),
            rx.button(
                rx.vstack(
                    rx.icon("file-text", size=18),
                    rx.text("Report", size="1"),
                    spacing="1"
                ),
                variant="outline",
                class_name="h-16 hover:bg-white/5",
                on_click=lambda: MonitorState.handle_quick_action("REPORT")
            ),
            rx.button(
                rx.vstack(
                    rx.icon("octagon", size=18),
                    rx.text("STOP", size="1"),
                    spacing="1"
                ),
                variant="outline",
                class_name="h-16 text-rose-400 hover:bg-rose-500/10",
                on_click=lambda: MonitorState.handle_quick_action("STOP")
            ),
            columns="2",
            gap="2",
            width="100%"
        ),
        
        rx.button(
            rx.hstack(
                rx.icon("arrow-left", size=14),
                rx.text("Back"),
                spacing="2"
            ),
            variant="ghost",
            size="1",
            width="100%",
            on_click=MonitorState.set_menu_mode("main")
        ),
        
        width="100%",
        spacing="3"
    )