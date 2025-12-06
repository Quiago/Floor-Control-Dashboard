# app/pages/workflow_builder.py
"""Workflow Builder Page - Refactorizado con nuevo diseño"""
import reflex as rx
from app.states.workflow_state import WorkflowState
from app.components.workflow import (workflow_header, equipment_panel,
                                    workflow_canvas, config_panel,
                                    simulation_controls,
                                    workflow_list_dialog,
                                    test_results_dialog)
from app.components.shared.design_tokens import COLORS

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
            console.log('[Simulation] Starting ticker, speed:', speed);
            if (ticker) clearInterval(ticker);
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

def workflow_builder_page() -> rx.Component:
    """Workflow Builder - Vista completa"""
    return rx.box(
        rx.script(SIMULATION_SCRIPT),
        
        rx.vstack(
            workflow_header(),
            
            rx.hstack(
                equipment_panel(),
                workflow_canvas(),
                spacing="0",
                class_name="flex-1 w-full h-full relative"
            ),
            
            simulation_controls(),
            
            spacing="0",
            class_name="h-screen w-full"
        ),
        
        config_panel(),
        workflow_list_dialog(),
        test_results_dialog(),
        
        class_name=f"bg-[{COLORS['bg_primary']}] select-none",
        on_mount=WorkflowState.load_equipment,
    )