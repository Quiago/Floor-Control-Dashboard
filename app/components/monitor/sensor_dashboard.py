"""Dashboard de sensores en vivo durante simulación"""
import reflex as rx
from app.states.workflow_state import WorkflowState
from app.components.shared.design_tokens import GLASS_PANEL, TRANSITION_DEFAULT
from app.components.shared import status_dot

def live_sensor_dashboard() -> rx.Component:
    """Dashboard con gauges de sensores activos"""
    return rx.cond(
        WorkflowState.simulation_running,
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    status_dot(running=True, color="emerald"),
                    rx.text(
                        "LIVE MONITORING",
                        class_name="text-sm font-bold text-emerald-400 uppercase tracking-wider"
                    ),
                    rx.badge(
                        f"Tick #{WorkflowState.simulation_tick_count}",
                        color_scheme="blue",
                        size="1"
                    ),
                    spacing="3",
                    align_items="center"
                ),
                
                # Sensor Gauges
                rx.cond(
                    WorkflowState.current_sensor_values.length() > 0,
                    rx.hstack(
                        rx.foreach(WorkflowState.current_sensor_values, sensor_gauge),
                        spacing="4",
                        class_name="overflow-x-auto py-2 w-full"
                    ),
                    rx.hstack(
                        rx.icon("loader-2", size=20, class_name="animate-spin text-blue-400"),
                        rx.text("Initializing sensors...", class_name="text-sm text-gray-400"),
                        spacing="2",
                        class_name="py-4"
                    )
                ),
                
                spacing="3",
                class_name="w-full"
            ),
            class_name=f"bg-[#0a0a0f]/80 border-b border-white/10 px-4 py-3 {TRANSITION_DEFAULT}"
        ),
        rx.fragment()
    )

def sensor_gauge(item: rx.Var[dict]) -> rx.Component:
    """Gauge individual de sensor"""
    return rx.vstack(
        # Equipment name
        rx.text(
            item['equipment'],
            class_name="text-[10px] text-gray-500 truncate w-full text-center font-medium"
        ),
        
        # Sensor type
        rx.text(
            item['key'],
            class_name="text-xs font-medium text-gray-300 uppercase tracking-wide"
        ),
        
        # Value
        rx.text(
            item['value'],
            class_name="text-2xl font-bold text-white font-mono"
        ),
        
        # Threshold
        rx.hstack(
            rx.text("Threshold:", class_name="text-[10px] text-gray-500"),
            rx.text(
                item['threshold'],
                class_name="text-[10px] text-amber-400 font-mono font-bold"
            ),
            spacing="1"
        ),
        
        # Progress bar
        rx.box(
            rx.box(
                class_name="h-full bg-gradient-to-r from-emerald-500 via-amber-500 to-rose-500 rounded-full transition-all duration-500"
            ),
            class_name="w-full h-2 bg-gray-800 rounded-full overflow-hidden"
        ),
        
        spacing="1",
        class_name=f"{GLASS_PANEL} p-4 rounded-xl min-w-[150px]"
    )