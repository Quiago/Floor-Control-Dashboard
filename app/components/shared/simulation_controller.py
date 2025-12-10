# app/components/shared/simulation_controller.py
"""
Simulation Controller Component - DOM elements for ticker and chatbot integration.

Provides:
- Hidden tick button for JavaScript to click (for simulation ticker)
- State element with data attributes for JavaScript to read
- Chatbot integration via global variable polling
"""
import reflex as rx
from app.states.simulation_state import SimulationState
from app.states.monitor_state import MonitorState


# JavaScript for simulation ticker
SIMULATION_TICKER_SCRIPT = """
(function() {
    var ticker = null;
    var lastRunning = 'false';

    // Check simulation state periodically
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
    console.log('[Simulation] Ticker loaded');
})();
"""


def simulation_controller() -> rx.Component:
    """
    Simulation controller DOM elements - ticker for monitor page.

    Provides the JavaScript ticker that calls simulation_tick periodically.
    """
    return rx.fragment(
        # JavaScript ticker
        rx.script(SIMULATION_TICKER_SCRIPT),

        # Hidden tick button - JavaScript clicks this to trigger simulation_tick
        rx.button(
            "tick",
            id="sim-tick-btn",
            on_click=SimulationState.simulation_tick,
            style={"display": "none"}
        ),

        # Simulation state element - JavaScript reads these data attributes
        rx.box(
            id="sim-state",
            data_running=SimulationState.simulation_running.to_string(),
            data_speed=SimulationState.simulation_speed.to_string(),
            style={"display": "none"}
        ),
    )
