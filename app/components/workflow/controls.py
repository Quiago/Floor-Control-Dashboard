# app/components/workflow/controls.py
"""Controles de simulación en barra inferior - Uses SimulationState and WorkflowState"""
import reflex as rx
from app.states.simulation_state import SimulationState
from app.states.workflow_state import WorkflowState
from app.components.shared.design_tokens import GRADIENT_PRIMARY, GRADIENT_DANGER, TRANSITION_DEFAULT
from app.components.shared import status_dot

# JavaScript for simulation ticker
SIMULATION_SCRIPT = """
(function() {
    var ticker = null;
    var lastRunning = 'false';
    
    function checkSim() {
        var stateEl = document.getElementById('sim-state');
        var tickBtn = document.getElementById('sim-tick-btn');
        if (!stateEl || !tickBtn) return;
        
        var running = stateEl.getAttribute('data-running');
        var speed = parseInt(stateEl.getAttribute('data-speed') || '2') * 1000;
        
        if (running === 'true' && lastRunning === 'false') {
            console.log('[Simulation] Starting ticker, interval:', speed);
            ticker = setInterval(function() {
                var btn = document.getElementById('sim-tick-btn');
                if (btn) btn.click();
            }, speed);
        }
        
        if (running === 'false' && lastRunning === 'true') {
            console.log('[Simulation] Stopping ticker');
            if (ticker) {
                clearInterval(ticker);
                ticker = null;
            }
        }
        
        lastRunning = running;
    }
    
    setInterval(checkSim, 500);
    console.log('[Simulation] Controller loaded');
})();
"""


def simulation_controls() -> rx.Component:
    """Barra inferior con controles"""
    return rx.vstack(
        # Hidden elements for JS
        rx.script(SIMULATION_SCRIPT),
        rx.button(
            "tick",
            id="sim-tick-btn",
            on_click=SimulationState.simulation_tick,
            style={"display": "none"}
        ),
        rx.box(
            id="sim-state",
            data_running=SimulationState.simulation_running.to_string(),
            data_speed=SimulationState.simulation_speed.to_string(),
            style={"display": "none"}
        ),
        
        # Controls bar
        rx.hstack(
            # Status
            rx.hstack(
                rx.cond(
                    SimulationState.simulation_running,
                    rx.hstack(
                        status_dot(running=True, color="emerald"),
                        rx.text(
                            "SIMULATION ACTIVE",
                            class_name="text-xs font-bold text-emerald-400 uppercase tracking-wide"
                        ),
                        rx.text(
                            f"Tick #{SimulationState.simulation_tick_count}",
                            class_name="text-xs text-gray-500 font-mono"
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
                        value=SimulationState.simulation_speed.to_string(),
                        on_change=SimulationState.set_simulation_speed,
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
                    on_click=SimulationState.trigger_manual_alert,
                    class_name=TRANSITION_DEFAULT
                ),
                
                # Start/Stop
                rx.cond(
                    SimulationState.simulation_running,
                    rx.button(
                        rx.hstack(
                            rx.icon("square", size=14),
                            rx.text("Stop"),
                            spacing="2"
                        ),
                        variant="solid",
                        class_name=f"{GRADIENT_DANGER} text-white",
                        size="2",
                        on_click=SimulationState.stop_simulation
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
                        # Pass workflow data to SimulationState
                        on_click=lambda: SimulationState.start_simulation(
                            WorkflowState.nodes,
                            WorkflowState.edges
                        )
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