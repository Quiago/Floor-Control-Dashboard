# app/components/monitor/alert_feed.py
"""Feed de alertas en tiempo real - Uses isolated SimulationState"""
import reflex as rx
from app.states.simulation_state import SimulationState
from app.components.shared import section_label

def alert_feed_panel() -> rx.Component:
    """Panel lateral derecho con stream de alertas"""
    return rx.vstack(
        # Header (always render both badges, toggle with CSS)
        rx.hstack(
            rx.icon("activity", size=16, class_name="text-blue-500"),
            rx.text(
                "Live Monitor",
                class_name="text-xs font-bold text-gray-400 uppercase"
            ),
            rx.spacer(),
            # Simulation ON badge + stop button (shown when running)
            rx.hstack(
                rx.badge("SIMULATION ON", color_scheme="green", variant="solid", size="1"),
                rx.button(
                    rx.icon("square", size=12),
                    variant="ghost",
                    color_scheme="red",
                    size="1",
                    on_click=SimulationState.stop_simulation,
                    class_name="h-6 px-2"
                ),
                spacing="2",
                class_name=rx.cond(
                    SimulationState.simulation_running,
                    "",
                    "hidden"
                )
            ),
            # MONITORING badge (shown when not running)
            rx.badge(
                "MONITORING",
                color_scheme="gray",
                variant="outline",
                size="1",
                class_name=rx.cond(
                    SimulationState.simulation_running,
                    "hidden",
                    ""
                )
            ),
            class_name="w-full p-3 border-b border-gray-800 bg-gray-900/50 items-center"
        ),
        
        # Sensor Data (always rendered, hidden with CSS to maintain hook order)
        rx.vstack(
            section_label("Real-Time Sensors"),
            rx.vstack(
                rx.foreach(SimulationState.current_sensor_values, sensor_value_row),
                class_name="w-full space-y-2 p-2 max-h-[120px] overflow-y-auto"
            ),
            class_name=rx.cond(
                SimulationState.simulation_running,
                "w-full border-b border-gray-800/50",
                "w-full border-b border-gray-800/50 hidden"
            )
        ),
        
        # Alert Stream (always render both, toggle visibility with CSS)
        rx.vstack(
            section_label("Alert Stream"),
            # Alert list (shown when there are alerts)
            rx.vstack(
                rx.foreach(
                    SimulationState.alert_feed,
                    alert_item
                ),
                id="alert-stream",
                class_name=rx.cond(
                    SimulationState.alert_feed.length() > 0,
                    "flex-1 overflow-y-auto w-full p-2 space-y-1 max-h-[calc(100vh-400px)]",
                    "flex-1 overflow-y-auto w-full p-2 space-y-1 max-h-[calc(100vh-400px)] hidden"
                )
            ),
            # Empty state (shown when no alerts)
            rx.vstack(
                rx.icon("bell-off", size=24, class_name="text-gray-600"),
                rx.text("No alerts yet", class_name="text-xs text-gray-500"),
                rx.text("Alerts appear when thresholds exceeded", class_name="text-[10px] text-gray-600"),
                spacing="2",
                align_items="center",
                class_name=rx.cond(
                    SimulationState.alert_feed.length() > 0,
                    "py-8 hidden",
                    "py-8"
                )
            ),
            width="100%",
            spacing="2"
        ),
        
        class_name="w-full h-full bg-gray-900 rounded-lg border border-gray-800 overflow-hidden"
    )


def sensor_value_row(item: rx.Var[dict]) -> rx.Component:
    """Row showing a single sensor value with dynamic styling."""
    return rx.hstack(
        # Equipment & sensor
        rx.vstack(
            rx.text(item['equipment'], class_name="text-[10px] text-gray-500 truncate"),
            rx.text(item['key'], class_name="text-xs font-medium text-gray-300 uppercase"),
            spacing="0",
            align_items="start",
            class_name="w-24 shrink-0"
        ),
        
        # Value with conditional styling
        rx.text(
            item['value'],
            class_name=rx.cond(
                item['is_alert'],
                "text-lg font-bold text-rose-400 font-mono w-16 text-right animate-pulse",
                "text-lg font-bold text-white font-mono w-16 text-right"
            )
        ),
        
        # Progress bar
        rx.box(
            rx.box(
                class_name=rx.cond(
                    item['status'] == 'alert',
                    "h-full bg-rose-500 rounded-full transition-all",
                    rx.cond(
                        item['status'] == 'warning',
                        "h-full bg-amber-500 rounded-full transition-all",
                        "h-full bg-emerald-500 rounded-full transition-all"
                    )
                ),
                style={"width": item['progress_pct'].to_string() + "%"}
            ),
            class_name="flex-1 h-2 bg-gray-700 rounded-full overflow-hidden"
        ),
        
        # Threshold value
        rx.text(
            item['threshold'],
            class_name="text-xs text-amber-400/80 font-mono w-12 text-right shrink-0"
        ),
        
        spacing="3",
        align_items="center",
        class_name=rx.cond(
            item['is_alert'],
            "w-full p-2 rounded bg-rose-900/30 border border-rose-500/30 animate-pulse",
            "w-full p-2 rounded bg-gray-800/30 hover:bg-gray-800/50"
        )
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