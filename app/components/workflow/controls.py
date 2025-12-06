# app/components/workflow/controls.py
"""Controles de simulación en barra inferior"""
import reflex as rx
from app.states.workflow_state import WorkflowState
from app.components.shared.design_tokens import GRADIENT_PRIMARY, GRADIENT_DANGER, TRANSITION_DEFAULT
from app.components.shared import status_dot

def simulation_controls() -> rx.Component:
    """Barra inferior con controles"""
    return rx.vstack(
        # Hidden elements for JS
        rx.button(
            "tick",
            id="sim-tick-btn",
            on_click=WorkflowState.simulation_tick,
            style={"display": "none"}
        ),
        rx.box(
            id="sim-state",
            data_running=WorkflowState.simulation_running.to_string(),
            data_speed=WorkflowState.simulation_speed.to_string(),
            style={"display": "none"}
        ),
        
        # Controls bar
        rx.hstack(
            # Status
            rx.hstack(
                rx.cond(
                    WorkflowState.simulation_running,
                    rx.hstack(
                        status_dot(running=True, color="emerald"),
                        rx.text(
                            "SIMULATION ACTIVE",
                            class_name="text-xs font-bold text-emerald-400 uppercase tracking-wide"
                        ),
                        spacing="2"
                    ),
                    rx.hstack(
                        status_dot(running=False),
                        rx.text(
                            "SIMULATION STOPPED",
                            class_name="text-xs font-bold text-gray-500 uppercase tracking-wide"
                        ),
                        spacing="2"
                    )
                ),
                align_items="center"
            ),
            
            rx.spacer(),
            
            # Actions
            rx.hstack(
                # Speed selector
                rx.hstack(
                    rx.text("Interval:", class_name="text-xs text-gray-400"),
                    rx.select.root(
                        rx.select.trigger(class_name="w-28 h-8 text-xs"),
                        rx.select.content(
                            rx.select.item("Fast (1s)", value="1"),
                            rx.select.item("Normal (2s)", value="2"),
                            rx.select.item("Slow (5s)", value="5"),
                        ),
                        value=WorkflowState.simulation_speed.to_string(),
                        on_change=WorkflowState.set_simulation_speed,
                        size="1"
                    ),
                    spacing="2",
                    align_items="center"
                ),
                
                # Test Alert
                rx.button(
                    rx.hstack(
                        rx.icon("zap", size=14),
                        rx.text("Test Alert"),
                        spacing="2"
                    ),
                    variant="outline",
                    color_scheme="yellow",
                    size="1",
                    on_click=WorkflowState.trigger_manual_alert,
                    class_name=TRANSITION_DEFAULT
                ),
                
                # Start/Stop
                rx.cond(
                    WorkflowState.simulation_running,
                    rx.button(
                        rx.hstack(
                            rx.icon("square", size=14),
                            rx.text("Stop"),
                            spacing="2"
                        ),
                        variant="solid",
                        class_name=f"{GRADIENT_DANGER} text-white",
                        size="2",
                        on_click=WorkflowState.stop_simulation
                    ),
                    rx.button(
                        rx.hstack(
                            rx.icon("play", size=14),
                            rx.text("Start Simulation"),
                            spacing="2"
                        ),
                        variant="solid",
                        class_name=f"{GRADIENT_PRIMARY} text-white",
                        size="2",
                        on_click=WorkflowState.start_simulation
                    )
                ),
                
                spacing="3"
            ),
            
            class_name="w-full px-4 py-3",
            align_items="center"
        ),
        
        spacing="0",
        class_name="w-full border-t border-white/10 bg-[#12121a]"
    )