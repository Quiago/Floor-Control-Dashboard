# app/pages/monitor.py
"""Monitor Page - Vista principal de monitoreo"""
import reflex as rx
from app.states.monitor_state import MonitorState
from app.states.workflow_state import WorkflowState
from app.states.simulation_state import SimulationState
from app.components.monitor.model_viewer import model_viewer_3d
from app.components.monitor.context_menu import floating_context_menu
from app.components.monitor.knowledge_graph import knowledge_graph_panel
from app.components.monitor.sensor_dashboard import live_sensor_dashboard
from app.components.monitor.alert_feed import alert_feed_panel
from app.components.monitor.chat_panel import chat_panel
from app.components.shared.design_tokens import COLORS
from app.components.shared.simulation_controller import simulation_controller
from app.components.shared.state_bridge import state_bridge

def monitor_header() -> rx.Component:
    """Header with navigation and simulation status"""
    return rx.hstack(
        rx.hstack(
            rx.icon("activity", size=24, class_name="text-blue-400"),
            rx.heading("Nexus Monitor", size="6", class_name="text-slate-100"),
            spacing="3",
            align_items="center"
        ),
        rx.spacer(),
        # Simulation status indicator (visibility controlled by JS)
        rx.badge(
            rx.hstack(
                rx.box(class_name="w-2 h-2 bg-emerald-500 rounded-full animate-pulse"),
                rx.text(f"SIMULATION ACTIVE • Tick #{SimulationState.simulation_tick_count}"),
                spacing="2"
            ),
            id="sim-status-active",
            color_scheme="green",
            variant="solid",
            size="1",
            class_name="hidden"  # JS will toggle this
        ),
        rx.button(
            rx.hstack(
                rx.icon("workflow", size=16),
                rx.text("Workflow Builder"),
                spacing="2"
            ),
            variant="solid",
            color_scheme="blue",
            on_click=rx.redirect("/workflow-builder"),
        ),
        class_name="w-full px-4 py-3 border-b border-slate-700/50 bg-slate-900/80 backdrop-blur-sm",
        align_items="center",
        spacing="3"
    )

def monitor_page() -> rx.Component:
    """Monitor Page - Vista principal"""
    return rx.box(
        # Simulation controller (ticker + state elements)
        simulation_controller(),
        
        rx.vstack(
            monitor_header(),
            
            # Main Layout
            rx.grid(
                # LEFT: 3D Model + Alert Feed
                rx.grid(
                    # 3D Model (60%)
                    rx.box(
                        model_viewer_3d(),
                        floating_context_menu(),
                        knowledge_graph_panel(),
                        class_name="w-full h-full relative"
                    ),
                    
                    # Bottom Panel (40%)
                    alert_feed_panel(),
                    
                    rows="60% 40%",
                    gap="4",
                    height="100%"
                ),
                
                # RIGHT: Chat Panel (35%)
                chat_panel(),
                
                grid_template_columns="65% 35%",
                height="calc(100vh - 60px)",
                gap="4",
                class_name="p-4 w-full"
            ),
            
            spacing="0",
            class_name=f"bg-[{COLORS['bg_primary']}] min-h-screen w-full"
        ),
        on_mount=WorkflowState.load_equipment
    )