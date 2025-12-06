# app/components/monitor/alert_feed.py
"""Feed de alertas en tiempo real"""
import reflex as rx
from app.states.workflow_state import WorkflowState
from app.components.shared import section_label

def alert_feed_panel() -> rx.Component:
    """Panel lateral derecho con stream de alertas"""
    return rx.vstack(
        # Header
        rx.hstack(
            rx.icon("activity", size=16, class_name="text-blue-500"),
            rx.text(
                "Live Monitor",
                class_name="text-xs font-bold text-gray-400 uppercase"
            ),
            rx.spacer(),
            rx.cond(
                WorkflowState.simulation_running,
                rx.badge("SIMULATION ON", color_scheme="green", variant="solid", size="1"),
                rx.badge("MONITORING", color_scheme="gray", variant="outline", size="1")
            ),
            class_name="w-full p-3 border-b border-gray-800 bg-gray-900/50 items-center"
        ),
        
        # Alert Stream
        rx.vstack(
            section_label("Alert Stream"),
            rx.vstack(
                rx.foreach(
                    WorkflowState.alert_feed,
                    alert_item
                ),
                class_name="flex-1 overflow-y-auto w-full p-2 space-y-1 max-h-[calc(100vh-400px)]"
            ),
            width="100%",
            spacing="2"
        ),
        
        class_name="w-full h-full bg-gray-900 rounded-lg border border-gray-800 overflow-hidden"
    )

def alert_item(alert: rx.Var[dict]) -> rx.Component:
    """Item individual de alerta"""
    return rx.hstack(
        # Severity indicator
        rx.box(
            class_name=rx.cond(
                alert['severity'] == 'critical',
                "w-1 h-full bg-rose-500",
                "w-1 h-full bg-amber-500"
            )
        ),
        
        # Content
        rx.vstack(
            rx.hstack(
                rx.text(
                    alert['timestamp'],
                    class_name="text-[10px] text-gray-500 font-mono"
                ),
                rx.badge(alert['severity'], size="1", color_scheme=rx.cond(
                    alert['severity'] == 'critical', "red", "yellow"
                )),
                spacing="2"
            ),
            rx.text(
                f"{alert['equipment']}: {alert['sensor']} > {alert['threshold']}",
                class_name="text-xs text-gray-300"
            ),
            spacing="0",
            align_items="start",
            class_name="flex-1"
        ),
        
        class_name="w-full bg-gray-800/30 p-2 rounded border border-gray-700/30 items-center hover:bg-gray-800/50 transition-colors"
    )