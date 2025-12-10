# app/components/monitor/chat_panel.py
"""Enhanced AI Chat Panel with LangGraph agent integration."""
import reflex as rx
from app.states.agent_state import AgentState
from app.components.shared.design_tokens import (
    GRADIENT_PRIMARY, TRANSITION_DEFAULT, GLASS_PANEL_PREMIUM, INPUT_FIELD
)


def chat_panel() -> rx.Component:
    """AI Chat Panel with enhanced UI and agent integration."""
    return rx.vstack(
        # Header
        rx.hstack(
            rx.hstack(
                rx.icon("bot", class_name="text-blue-400"),
                rx.text("Nexus AI", class_name="font-bold text-slate-100"),
                spacing="2"
            ),
            rx.spacer(),
            rx.hstack(
                rx.button(
                    rx.icon("trash-2", size=14),
                    variant="ghost",
                    size="1",
                    on_click=AgentState.clear_chat,
                    class_name="text-slate-400 hover:text-red-400"
                ),
                spacing="1"
            ),
            class_name="p-3 border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-sm",
            width="100%"
        ),
        
        # Messages Area
        rx.box(
            rx.vstack(
                rx.foreach(AgentState.chat_history, chat_message),
                
                # Thinking indicator (always rendered, hidden with CSS)
                thinking_indicator(
                    class_name=rx.cond(
                        AgentState.is_thinking,
                        "",
                        "hidden"
                    )
                ),

                # Workflow approval buttons (always rendered, hidden with CSS)
                workflow_approval_buttons(
                    class_name=rx.cond(
                        AgentState.awaiting_approval,
                        "",
                        "hidden"
                    )
                ),
                
                spacing="3",
                width="100%",
                align_items="stretch"
            ),
            class_name="flex-1 p-4 overflow-y-auto min-h-0",
            id="chat-messages"
        ),
        
        # Input Area
        rx.form(
            rx.hstack(
                rx.input(
                    placeholder="Ask about equipment, sensors, or create workflows...",
                    value=AgentState.chat_input,
                    on_change=AgentState.set_chat_input,
                    class_name=f"{INPUT_FIELD} flex-1 text-sm",
                    name="chat_msg",
                    disabled=AgentState.is_thinking
                ),
                rx.button(
                    rx.cond(
                        AgentState.is_thinking,
                        rx.icon("loader-circle", size=16, class_name="animate-spin"),
                        rx.icon("send", size=16)
                    ),
                    type="submit",
                    disabled=AgentState.is_thinking,
                    class_name=f"{GRADIENT_PRIMARY} {TRANSITION_DEFAULT} px-3"
                ),
                spacing="2",
                width="100%"
            ),
            on_submit=AgentState.send_message,
            class_name="p-3 border-t border-slate-700/50 w-full"
        ),
        
        class_name=f"h-full {GLASS_PANEL_PREMIUM} rounded-xl overflow-hidden flex flex-col",
        width="100%"
    )


def chat_message(msg: rx.Var[dict]) -> rx.Component:
    """Individual chat message with role-based styling."""
    return rx.box(
        rx.hstack(
            # Avatar
            rx.cond(
                msg["role"] == "user",
                rx.box(
                    rx.icon("user", size=14, class_name="text-slate-300"),
                    class_name="w-7 h-7 rounded-full bg-slate-700 flex items-center justify-center shrink-0"
                ),
                rx.box(
                    rx.icon("bot", size=14, class_name="text-blue-300"),
                    class_name="w-7 h-7 rounded-full bg-blue-600/30 flex items-center justify-center shrink-0"
                )
            ),
            
            # Message content
            # NOTE: Using rx.text instead of rx.markdown to avoid React hooks order error
            # rx.markdown uses useContext internally which breaks when used inside rx.foreach
            rx.vstack(
                rx.text(
                    msg["content"],
                    class_name=rx.cond(
                        msg["role"] == "user",
                        "text-sm text-slate-200 whitespace-pre-wrap",
                        "text-sm text-slate-100 whitespace-pre-wrap"
                    )
                ),
                rx.text(
                    msg["time"],
                    class_name="text-[10px] text-slate-500"
                ),
                spacing="1",
                align_items="start",
                class_name="flex-1 min-w-0"
            ),
            
            spacing="3",
            align_items="start",
            width="100%"
        ),
        class_name=rx.cond(
            msg["role"] == "user",
            f"bg-slate-800/50 p-3 rounded-lg border border-slate-700/30 {TRANSITION_DEFAULT}",
            f"bg-slate-900/50 p-3 rounded-lg border border-blue-500/20 {TRANSITION_DEFAULT}"
        ),
        width="100%"
    )


def thinking_indicator(class_name: str = "") -> rx.Component:
    """Animated thinking indicator."""
    return rx.hstack(
        rx.box(
            rx.icon("bot", size=14, class_name="text-blue-300"),
            class_name="w-7 h-7 rounded-full bg-blue-600/30 flex items-center justify-center shrink-0 animate-pulse"
        ),
        rx.hstack(
            rx.box(class_name="w-2 h-2 bg-blue-400 rounded-full animate-bounce"),
            rx.box(class_name="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:0.1s]"),
            rx.box(class_name="w-2 h-2 bg-blue-400 rounded-full animate-bounce [animation-delay:0.2s]"),
            spacing="1"
        ),
        rx.text("Thinking...", class_name="text-xs text-slate-400"),
        spacing="3",
        align_items="center",
        class_name=f"bg-slate-900/50 p-3 rounded-lg border border-blue-500/20 {class_name}"
    )


def workflow_approval_buttons(class_name: str = "") -> rx.Component:
    """Buttons for approving or rejecting a pending workflow."""
    return rx.hstack(
        rx.button(
            rx.hstack(
                rx.icon("check", size=16),
                rx.text("Approve & Activate"),
                spacing="2"
            ),
            variant="solid",
            color_scheme="green",
            on_click=AgentState.approve_workflow,
            class_name=TRANSITION_DEFAULT
        ),
        rx.button(
            rx.hstack(
                rx.icon("x", size=16),
                rx.text("Cancel"),
                spacing="2"
            ),
            variant="outline",
            color_scheme="red",
            on_click=AgentState.reject_workflow,
            class_name=TRANSITION_DEFAULT
        ),
        spacing="2",
        class_name=f"p-3 bg-slate-800/50 rounded-lg border border-orange-500/30 {class_name}"
    )