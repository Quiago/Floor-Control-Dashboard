# app/components/monitor/chat_panel.py
"""Panel de chat con Nexus AI"""
import reflex as rx
from app.states.monitor_state import MonitorState
from app.components.shared.design_tokens import GRADIENT_PRIMARY, TRANSITION_DEFAULT

def chat_panel() -> rx.Component:
    """Panel de chat AI (35% ancho derecho)"""
    return rx.vstack(
        # Header
        rx.hstack(
            rx.icon("bot", class_name="text-emerald-400"),
            rx.text("Nexus AI", class_name="font-bold text-white"),
            class_name="p-4 border-b border-gray-800 bg-gray-900"
        ),
        
        # Messages
        rx.vstack(
            rx.foreach(MonitorState.chat_history, chat_message),
            class_name="flex-1 p-4 overflow-y-auto"
        ),
        
        # Input
        rx.form(
            rx.hstack(
                rx.input(
                    placeholder="Command...",
                    value=MonitorState.chat_input,
                    on_change=MonitorState.set_chat_input,
                    class_name="bg-gray-800 border-gray-700 text-sm flex-1",
                    name="chat_msg"
                ),
                rx.button(
                    rx.icon("send", size=16),
                    type="submit",
                    class_name=f"{GRADIENT_PRIMARY} {TRANSITION_DEFAULT}"
                ),
                spacing="2",
                width="100%"
            ),
            on_submit=MonitorState.send_message,
            class_name="p-3 border-t border-gray-800 w-full"
        ),
        
        class_name="h-full bg-gray-950 rounded-lg border border-gray-800",
        width="100%"
    )

def chat_message(msg: rx.Var[dict]) -> rx.Component:
    """Mensaje individual del chat"""
    return rx.box(
        rx.text(msg["text"], class_name="text-sm text-gray-200"),
        class_name=f"bg-gray-800 p-2 rounded-lg mb-2 {TRANSITION_DEFAULT}"
    )