# app/workflow_builder.py
"""
Enhanced Workflow Builder with Configuration UI and Live Simulation.
"""
from typing import Any, Dict
import reflex as rx
from reflex.components.radix.themes.layout.box import Box
from app.reactflow import react_flow, background, controls
from app.states.workflow_state import WorkflowState


# ===========================================
# CUSTOM COMPONENTS
# ===========================================

class DropZone(Box):
    """Custom Box that captures mouse coordinates on mouse up."""
    
    def get_event_triggers(self) -> Dict[str, Any]:
        return {
            **super().get_event_triggers(),
            "on_mouse_up": lambda e: [e.clientX, e.clientY],
        }

drop_zone = DropZone.create


def get_icon(icon_name: rx.Var[str], size: int = 16) -> rx.Component:
    """Get icon component by name using rx.match."""
    return rx.match(
        icon_name,
        ("scan", rx.icon("scan", size=size)),
        ("box", rx.icon("box", size=size)),
        ("circle-dot", rx.icon("circle-dot", size=size)),
        ("package", rx.icon("package", size=size)),
        ("arrow-right", rx.icon("arrow-right", size=size)),
        ("globe", rx.icon("globe", size=size)),
        ("message-circle", rx.icon("message-circle", size=size)),
        ("mail", rx.icon("mail", size=size)),
        ("bell", rx.icon("bell", size=size)),
        ("cpu", rx.icon("cpu", size=size)),
        rx.icon("circle-help", size=size)
    )


# ===========================================
# HEADER
# ===========================================

def workflow_header() -> rx.Component:
    """Header with workflow name, status, and actions."""
    return rx.hstack(
        rx.hstack(
            rx.icon("workflow", size=24, class_name="text-blue-400"),
            rx.vstack(
                rx.input(
                    value=WorkflowState.current_workflow_name,
                    on_change=WorkflowState.set_workflow_name,
                    class_name="text-lg font-bold text-white bg-transparent border-none focus:outline-none w-48",
                    placeholder="Workflow name..."
                ),
                rx.hstack(
                    rx.badge(
                        WorkflowState.current_workflow_status,
                        color_scheme=rx.cond(
                            WorkflowState.current_workflow_status == "active",
                            "green",
                            rx.cond(
                                WorkflowState.current_workflow_status == "paused",
                                "yellow",
                                "gray"
                            )
                        ),
                        size="1"
                    ),
                    rx.text(f"{WorkflowState.node_count} nodes", class_name="text-xs text-white-500"),
                    rx.text(f"{WorkflowState.edge_count} connections", class_name="text-xs text-white-500"),
                    spacing="2"
                ),
                spacing="0",
                align_items="start"
            ),
            spacing="3",
            align_items="center"
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.hstack(rx.icon("folder-open", size=16), rx.text("Open"), spacing="2"),
                variant="ghost",
                on_click=WorkflowState.toggle_workflow_list
            ),
            rx.button(
                rx.hstack(rx.icon("file-plus", size=16), rx.text("New"), spacing="2"),
                variant="ghost",
                on_click=WorkflowState.new_workflow
            ),
            rx.button(
                rx.hstack(rx.icon("play", size=16), rx.text("Test"), spacing="2"),
                variant="outline",
                color_scheme="yellow",
                on_click=WorkflowState.test_workflow_execution
            ),
            rx.button(
                rx.hstack(rx.icon("save", size=16), rx.text("Save"), spacing="2"),
                variant="solid",
                color_scheme="blue",
                on_click=WorkflowState.save_workflow
            ),
            rx.cond(
                WorkflowState.current_workflow_status == "active",
                rx.button(
                    rx.hstack(rx.icon("pause", size=16), rx.text("Pause"), spacing="2"),
                    variant="outline",
                    color_scheme="yellow",
                    on_click=WorkflowState.pause_workflow
                ),
                rx.button(
                    rx.hstack(rx.icon("zap", size=16), rx.text("Activate"), spacing="2"),
                    variant="solid",
                    color_scheme="green",
                    on_click=WorkflowState.activate_workflow
                )
            ),
            rx.button(
                rx.hstack(rx.icon("home", size=16), rx.text("Monitor"), spacing="2"),
                variant="ghost",
                on_click=rx.redirect("/")
            ),
            spacing="2"
        ),
        class_name="w-full p-4 border-b border-gray-800 bg-gray-900",
        align_items="center"
    )


# ===========================================
# TOOLBOX
# ===========================================

def category_button(category: rx.Var[dict]) -> rx.Component:
    """Draggable category button."""
    return rx.box(
        rx.button(
            rx.hstack(
                get_icon(category['icon'], size=18),
                rx.text(category['name'], size="2"),
                spacing="2"
            ),
            variant="outline",
            class_name=rx.cond(
                WorkflowState.is_dragging,
                "w-full border-gray-700 justify-start opacity-50 cursor-grabbing pointer-events-none",
                "w-full border-gray-700 hover:bg-blue-900/20 hover:border-blue-500 justify-start cursor-grab"
            ),
            type="button",
        ),
        class_name="w-full select-none",
        on_mouse_down=WorkflowState.start_drag(
            category['key'], 
            category['type'] == 'action'
        ),
    )


def equipment_panel() -> rx.Component:
    """Left sidebar with draggable equipment categories"""
    return rx.cond(
        WorkflowState.show_equipment_panel,
        rx.vstack(
            rx.hstack(
                rx.text("TOOLBOX", class_name="text-xs font-bold text-white-400 uppercase"),
                rx.spacer(),
                rx.button(
                    rx.icon("x", size=14),
                    variant="ghost",
                    size="1",
                    on_click=WorkflowState.toggle_equipment_panel
                ),
                width="100%"
            ),
            rx.box(
                rx.vstack(
                    rx.text("EQUIPMENT", class_name="text-[10px] text-white-500 font-bold uppercase mb-2"),
                    rx.text(
                        rx.cond(
                            WorkflowState.is_dragging,
                            "Release on canvas to drop",
                            "Click and drag to canvas"
                        ),
                        class_name=rx.cond(
                            WorkflowState.is_dragging,
                            "text-[9px] text-green-400 mb-2 italic font-bold",
                            "text-[9px] text-white-600 mb-2 italic"
                        )
                    ),
                    rx.foreach(WorkflowState.equipment_categories, category_button),
                    rx.separator(class_name="my-4 bg-gray-700"),
                    rx.text("ACTIONS", class_name="text-[10px] text-white-500 font-bold uppercase mb-2"),
                    rx.foreach(WorkflowState.action_categories, category_button),
                    spacing="2",
                    width="100%"
                ),
                class_name="flex-1 overflow-y-auto",
                height="calc(100vh - 350px)"
            ),
            rx.vstack(
                rx.separator(class_name="bg-gray-700"),
                rx.button(
                    rx.hstack(rx.icon("trash-2", size=14), rx.text("Clear All"), spacing="2"),
                    variant="ghost",
                    class_name="w-full text-red-400 hover:bg-red-900/20",
                    on_click=WorkflowState.clear_workflow
                ),
                spacing="2",
                width="100%"
            ),
            class_name="w-64 h-full bg-gray-900 border-r border-gray-800 flex flex-col p-4",
            spacing="0"
        ),
        rx.button(
            rx.icon("panel-left", size=16),
            variant="ghost",
            class_name="absolute top-20 left-4 z-50 bg-gray-900 border border-gray-700 hover:bg-gray-800",
            on_click=WorkflowState.toggle_equipment_panel
        )
    )


# ===========================================
# CONFIGURATION PANEL
# ===========================================

def sensor_select_option(sensor: rx.Var[Dict]) -> rx.Component:
    return rx.select.item(
        rx.hstack(
            rx.text(sensor['name']),
            rx.text(f"({sensor['unit']})", class_name="text-white-500 text-xs"),
            spacing="2"
        ),
        value=sensor['id']
    )


def operator_select_option(op: rx.Var[Dict]) -> rx.Component:
    return rx.select.item(op['label'], value=op['value'])


def severity_button(sev: rx.Var[Dict]) -> rx.Component:
    return rx.button(
        sev['label'],
        variant=rx.cond(
            WorkflowState.config_severity == sev['value'],
            "solid",
            "outline"
        ),
        color_scheme=sev['color'],
        size="1",
        on_click=WorkflowState.set_config_severity(sev['value'])
    )


def equipment_config_form() -> rx.Component:
    return rx.vstack(
        # --- NUEVO SELECTOR DE EQUIPO ESPECÍFICO ---
        rx.vstack(
            rx.text("Target Equipment (3D Asset)", class_name="text-xs text-white-400 font-bold uppercase"),
            rx.select.root(
                rx.select.trigger(placeholder="Select specific machine...", class_name="w-full"),
                rx.select.content(
                    # Iteramos sobre los equipos extraídos del GLB
                    rx.foreach(
                        WorkflowState.available_equipment,
                        lambda eq: rx.select.item(eq["label"], value=eq["name"]) 
                    )
                ),
                value=WorkflowState.config_specific_equipment_id,
                on_change=WorkflowState.set_config_specific_equipment_id,
            ),
            spacing="1",
            width="100%"
        ),
        rx.vstack(
            rx.text("Sensor", class_name="text-xs text-white-400 font-bold uppercase"),
            rx.select.root(
                rx.select.trigger(placeholder="Select sensor...", class_name="w-full"),
                rx.select.content(
                    rx.foreach(WorkflowState.selected_node_sensors, sensor_select_option)
                ),
                value=WorkflowState.config_sensor_type,
                on_change=WorkflowState.set_config_sensor_type,
            ),
            spacing="1",
            width="100%"
        ),
        rx.hstack(
            rx.vstack(
                rx.text("Condition", class_name="text-xs text-white-400 font-bold uppercase"),
                rx.select.root(
                    rx.select.trigger(class_name="w-full"),
                    rx.select.content(
                        rx.foreach(WorkflowState.operator_options, operator_select_option)
                    ),
                    value=WorkflowState.config_operator,
                    on_change=WorkflowState.set_config_operator,
                ),
                spacing="1",
                width="50%"
            ),
            rx.vstack(
                rx.text("Threshold", class_name="text-xs text-white-400 font-bold uppercase"),
                rx.input(
                    type="number",
                    value=WorkflowState.config_threshold,
                    on_change=WorkflowState.set_config_threshold,
                    class_name="w-full bg-gray-800 border-gray-700"
                ),
                spacing="1",
                width="50%"
            ),
            spacing="2",
            width="100%"
        ),
        rx.vstack(
            rx.text("Alert Severity", class_name="text-xs text-white-400 font-bold uppercase"),
            rx.hstack(
                rx.foreach(WorkflowState.severity_options, severity_button),
                spacing="2"
            ),
            spacing="1",
            width="100%"
        ),
        spacing="4",
        width="100%"
    )


def action_config_form() -> rx.Component:
    return rx.vstack(
        rx.cond(
            WorkflowState.selected_node_category == "whatsapp",
            rx.vstack(
                rx.text("Phone Number", class_name="text-xs text-white-400 font-bold uppercase"),
                rx.input(
                    placeholder="+1234567890",
                    value=WorkflowState.config_phone_number,
                    on_change=WorkflowState.set_config_phone_number,
                    class_name="w-full bg-gray-800 border-gray-700"
                ),
                spacing="1",
                width="100%"
            ),
            rx.fragment()
        ),
        rx.cond(
            WorkflowState.selected_node_category == "email",
            rx.vstack(
                rx.text("Email Address", class_name="text-xs text-white-400 font-bold uppercase"),
                rx.input(
                    placeholder="alert@company.com",
                    value=WorkflowState.config_email,
                    on_change=WorkflowState.set_config_email,
                    class_name="w-full bg-gray-800 border-gray-700"
                ),
                spacing="1",
                width="100%"
            ),
            rx.fragment()
        ),
        rx.cond(
            WorkflowState.selected_node_category == "webhook",
            rx.vstack(
                rx.text("Webhook URL", class_name="text-xs text-white-400 font-bold uppercase"),
                rx.input(
                    placeholder="https://api.example.com/webhook",
                    value=WorkflowState.config_webhook_url,
                    on_change=WorkflowState.set_config_webhook_url,
                    class_name="w-full bg-gray-800 border-gray-700"
                ),
                spacing="1",
                width="100%"
            ),
            rx.fragment()
        ),
        rx.vstack(
            rx.text("Alert Severity", class_name="text-xs text-white-400 font-bold uppercase"),
            rx.hstack(
                rx.foreach(WorkflowState.severity_options, severity_button),
                spacing="2"
            ),
            spacing="1",
            width="100%"
        ),
        spacing="4",
        width="100%"
    )


def config_panel() -> rx.Component:
    return rx.cond(
        WorkflowState.show_config_panel,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.vstack(
                        rx.text("Configure Node", class_name="text-sm font-bold text-white"),
                        rx.text(WorkflowState.selected_node_category, class_name="text-xs text-white-400 capitalize"),
                        spacing="0",
                        align_items="start"
                    ),
                    rx.spacer(),
                    rx.badge(
                        rx.cond(WorkflowState.selected_node_is_configured, "Configured", "Not configured"),
                        color_scheme=rx.cond(WorkflowState.selected_node_is_configured, "green", "gray"),
                        size="1"
                    ),
                    rx.button(rx.icon("x", size=14), variant="ghost", size="1", on_click=WorkflowState.close_config_panel),
                    width="100%",
                    align_items="start"
                ),
                rx.separator(class_name="my-2 bg-gray-700"),
                rx.cond(WorkflowState.selected_node_is_action, action_config_form(), equipment_config_form()),
                rx.separator(class_name="my-2 bg-gray-700"),
                rx.button(
                    rx.hstack(rx.icon("check", size=16), rx.text("Save Configuration"), spacing="2"),
                    variant="solid",
                    color_scheme="blue",
                    class_name="w-full",
                    on_click=WorkflowState.save_node_config
                ),
                spacing="3",
                width="100%"
            ),
            class_name="absolute top-20 right-4 bg-gray-900/95 backdrop-blur p-4 border border-gray-700 rounded-lg z-50 w-80"
        ),
        rx.fragment()
    )


# ===========================================
# DIALOGS
# ===========================================

def workflow_list_item(workflow: rx.Var[Dict]) -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text(workflow['name'], class_name="text-sm font-medium text-white"),
            rx.hstack(
                rx.badge(workflow['status'], size="1"),
                rx.text(workflow['updated_at'], class_name="text-[10px] text-white-500"),
                spacing="2"
            ),
            spacing="0",
            align_items="start"
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(rx.icon("folder-open", size=14), variant="ghost", size="1", on_click=WorkflowState.load_workflow(workflow['id'])),
            rx.button(rx.icon("trash-2", size=14), variant="ghost", size="1", color_scheme="red", on_click=WorkflowState.delete_workflow(workflow['id'])),
            spacing="1"
        ),
        class_name="w-full p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800",
        width="100%"
    )


def workflow_list_dialog() -> rx.Component:
    return rx.cond(
        WorkflowState.show_workflow_list,
        rx.box(
            rx.box(class_name="fixed inset-0 bg-black/50 z-40", on_click=WorkflowState.toggle_workflow_list),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text("Saved Workflows", class_name="text-lg font-bold text-white"),
                        rx.spacer(),
                        rx.button(rx.icon("x", size=16), variant="ghost", on_click=WorkflowState.toggle_workflow_list),
                        width="100%"
                    ),
                    rx.separator(class_name="my-2 bg-gray-700"),
                    rx.cond(
                        WorkflowState.saved_workflows.length() > 0,
                        rx.vstack(rx.foreach(WorkflowState.saved_workflows, workflow_list_item), spacing="2", width="100%"),
                        rx.text("No saved workflows yet", class_name="text-white-500 text-sm py-8 text-center")
                    ),
                    spacing="2",
                    width="100%"
                ),
                class_name="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-gray-900 p-6 border border-gray-700 rounded-xl z-50 w-[500px]"
            )
        ),
        rx.fragment()
    )


def test_result_item(result: rx.Var[Dict]) -> rx.Component:
    return rx.hstack(
        rx.icon(
            rx.cond(result['would_trigger'], "alert-circle", "check-circle"),
            size=16,
            class_name=rx.cond(result['would_trigger'], "text-red-400", "text-green-400")
        ),
        rx.vstack(
            rx.text(result['trigger_node'], class_name="text-sm text-white"),
            rx.text(f"{result['sensor']}: {result['current_value']} {result['operator']} {result['threshold']}", class_name="text-xs text-white-400"),
            spacing="0",
            align_items="start"
        ),
        rx.spacer(),
        rx.badge(
            rx.cond(result['would_trigger'], "Would trigger", "OK"),
            color_scheme=rx.cond(result['would_trigger'], "red", "green"),
            size="1"
        ),
        class_name="w-full p-2 bg-gray-800/50 rounded",
        width="100%"
    )


def test_results_dialog() -> rx.Component:
    return rx.cond(
        WorkflowState.test_mode,
        rx.box(
            rx.box(class_name="fixed inset-0 bg-black/50 z-40", on_click=WorkflowState.close_test_mode),
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("flask-conical", size=20, class_name="text-yellow-400"),
                        rx.text("Test Results", class_name="text-lg font-bold text-white"),
                        rx.spacer(),
                        rx.button(rx.icon("x", size=16), variant="ghost", on_click=WorkflowState.close_test_mode),
                        width="100%",
                        align_items="center"
                    ),
                    rx.separator(class_name="my-2 bg-gray-700"),
                    rx.cond(
                        WorkflowState.test_results.length() > 0,
                        rx.vstack(rx.foreach(WorkflowState.test_results, test_result_item), spacing="2", width="100%"),
                        rx.text("No triggers configured", class_name="text-white-500 text-sm py-4")
                    ),
                    spacing="2",
                    width="100%"
                ),
                class_name="fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 bg-gray-900 p-6 border border-gray-700 rounded-xl z-50 w-[500px]"
            )
        ),
        rx.fragment()
    )


# ===========================================
# CANVAS
# ===========================================

def drag_indicator() -> rx.Component:
    return rx.cond(
        WorkflowState.is_dragging,
        rx.box(
            rx.hstack(
                rx.icon("mouse-pointer-click", size=16, class_name="text-green-400"),
                rx.text(f"Dragging: {WorkflowState.dragged_type}", class_name="text-sm text-green-400"),
                spacing="2"
            ),
            class_name="fixed bottom-24 left-1/2 transform -translate-x-1/2 bg-gray-900 border border-green-500 px-4 py-2 rounded-full shadow-lg z-[100]"
        ),
        rx.fragment()
    )


def drop_overlay() -> rx.Component:
    return rx.cond(
        WorkflowState.is_dragging,
        drop_zone(
            rx.box(
                rx.vstack(
                    rx.icon("download", size=32, class_name="text-blue-400 opacity-50"),
                    rx.text("Release to drop here", class_name="text-sm text-blue-400 opacity-75"),
                    class_name="items-center justify-center"
                ),
                class_name="absolute inset-0 flex items-center justify-center pointer-events-none"
            ),
            class_name="absolute inset-0 bg-blue-500/5 border-2 border-dashed border-blue-500/30 z-40 cursor-copy",
            on_mouse_up=WorkflowState.handle_drop,
            on_mouse_leave=WorkflowState.cancel_drag,
        ),
        rx.fragment()
    )


def workflow_canvas() -> rx.Component:
    return rx.box(
        react_flow(
            background(color="#374151", gap=16, size=1, variant="dots"),
            controls(),
            nodes_draggable=True,
            nodes_connectable=True,
            on_connect=lambda e0: WorkflowState.on_connect(e0),
            on_nodes_change=lambda e0: WorkflowState.on_nodes_change(e0),
            on_edges_change=lambda e0: WorkflowState.on_edges_change(e0),
            nodes=WorkflowState.nodes,
            edges=WorkflowState.edges,
            fit_view=True,
            class_name="bg-gray-950 w-full h-full",
            style={"width": "100%", "height": "100%"}
        ),
        drop_overlay(),
        config_panel(),
        class_name="flex-1 h-full w-full relative overflow-hidden",
        id="workflow-canvas"
    )


# ===========================================
# LIVE SENSOR DISPLAY
# ===========================================

def sensor_gauge(item: rx.Var[Dict]) -> rx.Component:
    """Single sensor gauge showing live value."""
    return rx.vstack(
        rx.text(item['equipment'], class_name="text-[10px] text-white-500 truncate w-full text-center"),
        rx.text(item['key'], class_name="text-xs font-medium text-white-300 uppercase"),
        rx.text(item['value'], class_name="text-2xl font-bold text-white font-mono"),
        rx.hstack(
            rx.text("Threshold:", class_name="text-[10px] text-white-500"),
            rx.text(item['threshold'], class_name="text-[10px] text-yellow-400 font-mono"),
            spacing="1"
        ),
        rx.box(
            rx.box(class_name="h-full bg-gradient-to-r from-green-500 via-yellow-500 to-red-500 rounded-full"),
            class_name="w-full h-2 bg-gray-700 rounded-full overflow-hidden"
        ),
        spacing="1",
        class_name="p-4 bg-gray-800 rounded-xl border border-gray-700 min-w-[150px]"
    )


def live_sensor_dashboard() -> rx.Component:
    """Dashboard showing live sensor values when simulation is running."""
    return rx.cond(
        WorkflowState.simulation_running,
        rx.box(
            rx.vstack(
                rx.hstack(
                    rx.box(class_name="w-3 h-3 bg-green-500 rounded-full animate-pulse"),
                    rx.text("LIVE MONITORING", class_name="text-sm font-bold text-green-400 uppercase"),
                    rx.badge(f"Tick #{WorkflowState.simulation_tick_count}", color_scheme="blue", size="1"),
                    spacing="3",
                    align_items="center"
                ),
                rx.cond(
                    WorkflowState.current_sensor_values.length() > 0,
                    rx.hstack(
                        rx.foreach(WorkflowState.current_sensor_values, sensor_gauge),
                        spacing="4",
                        class_name="overflow-x-auto py-2"
                    ),
                    rx.hstack(
                        rx.icon("loader-2", size=20, class_name="animate-spin text-blue-400"),
                        rx.text("Initializing sensors...", class_name="text-sm text-white-400"),
                        spacing="2",
                        class_name="py-4"
                    )
                ),
                spacing="3",
                class_name="w-full"
            ),
            class_name="bg-gray-900/80 border-b border-gray-800 px-4 py-3"
        ),
        rx.fragment()
    )


# ===========================================
# SIMULATION CONTROLS
# ===========================================

def simulation_controls() -> rx.Component:
    """Bottom bar with simulation controls and JavaScript interval trigger."""
    return rx.vstack(
        live_sensor_dashboard(),
        rx.hstack(
            rx.hstack(
                rx.cond(
                    WorkflowState.simulation_running,
                    rx.hstack(
                        rx.box(class_name="w-3 h-3 bg-green-500 rounded-full animate-pulse"),
                        rx.text("SIMULATION ACTIVE", class_name="text-xs font-bold text-green-400 uppercase"),
                        spacing="2"
                    ),
                    rx.hstack(
                        rx.box(class_name="w-3 h-3 bg-gray-600 rounded-full"),
                        rx.text("SIMULATION STOPPED", class_name="text-xs font-bold text-white-500 uppercase"),
                        spacing="2"
                    )
                ),
                align_items="center"
            ),
            rx.spacer(),
            rx.hstack(
                rx.hstack(
                    rx.text("Interval:", class_name="text-xs text-white-400"),
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
                rx.button(
                    rx.hstack(rx.icon("zap", size=14), rx.text("Test Alert"), spacing="2"),
                    variant="outline",
                    color_scheme="yellow",
                    size="1",
                    on_click=WorkflowState.trigger_manual_alert
                ),
                rx.cond(
                    WorkflowState.simulation_running,
                    rx.button(
                        rx.hstack(rx.icon("square", size=14), rx.text("Stop"), spacing="2"),
                        variant="solid",
                        color_scheme="red",
                        size="2",
                        on_click=WorkflowState.stop_simulation
                    ),
                    rx.button(
                        rx.hstack(rx.icon("play", size=14), rx.text("Start Simulation"), spacing="2"),
                        variant="solid",
                        color_scheme="green",
                        size="2",
                        on_click=WorkflowState.start_simulation
                    )
                ),
                spacing="3"
            ),
            class_name="w-full px-4 py-3",
            align_items="center"
        ),
        # Hidden button that JavaScript will click
        rx.button(
            "tick",
            id="sim-tick-btn",
            on_click=WorkflowState.simulation_tick,
            style={"display": "none"}
        ),
        # Data attributes for JavaScript to read simulation state
        rx.box(
            id="sim-state",
            data_running=WorkflowState.simulation_running.to_string(),
            data_speed=WorkflowState.simulation_speed.to_string(),
            style={"display": "none"}
        ),
        spacing="0",
        class_name="w-full border-t border-gray-800 bg-gray-900"
    )


# ===========================================
# ALERT FEED
# ===========================================

def alert_feed_item(alert: rx.Var[Dict]) -> rx.Component:
    return rx.hstack(
        rx.box(class_name="w-1 h-full min-h-[40px] bg-red-500 rounded-l"),
        rx.vstack(
            rx.hstack(
                rx.text(alert['timestamp'], class_name="text-[10px] text-white-500 font-mono"),
                rx.badge(alert['action_type'], size="1", color_scheme="blue"),
                spacing="2"
            ),
            rx.text(alert['equipment'], class_name="text-xs font-medium text-white"),
            rx.text(f"{alert['sensor']}: {alert['value']} / {alert['threshold']}", class_name="text-[10px] text-white-400"),
            spacing="0",
            align_items="start",
            class_name="py-1"
        ),
        class_name="w-full bg-gray-800/50 rounded overflow-hidden",
        spacing="0"
    )


def alert_feed_panel() -> rx.Component:
    return rx.cond(
        WorkflowState.show_alert_feed,
        rx.vstack(
            rx.hstack(
                rx.hstack(
                    rx.icon("bell", size=16, class_name="text-yellow-400"),
                    rx.text("Alert Feed", class_name="text-sm font-bold text-white"),
                    spacing="2"
                ),
                rx.spacer(),
                rx.hstack(
                    rx.button(rx.icon("trash-2", size=12), variant="ghost", size="1", on_click=WorkflowState.clear_alert_feed),
                    rx.button(rx.icon("x", size=12), variant="ghost", size="1", on_click=WorkflowState.toggle_alert_feed),
                    spacing="1"
                ),
                width="100%"
            ),
            rx.separator(class_name="bg-gray-700"),
            rx.cond(
                WorkflowState.alert_feed.length() > 0,
                rx.vstack(
                    rx.foreach(WorkflowState.alert_feed, alert_feed_item),
                    spacing="2",
                    width="100%",
                    class_name="overflow-y-auto max-h-[calc(100vh-350px)]"
                ),
                rx.vstack(
                    rx.icon("inbox", size=32, class_name="text-white-700"),
                    rx.text("No alerts yet", class_name="text-xs text-white-600"),
                    class_name="items-center justify-center py-8"
                )
            ),
            spacing="3",
            class_name="w-64 h-full bg-gray-900 border-l border-gray-800 p-3"
        ),
        rx.button(
            rx.hstack(
                rx.icon("bell", size=16),
                rx.cond(
                    WorkflowState.alert_feed.length() > 0,
                    rx.badge(WorkflowState.alert_feed.length(), color_scheme="red", size="1"),
                    rx.fragment()
                ),
                spacing="2"
            ),
            variant="ghost",
            class_name="absolute top-20 right-4 z-50 bg-gray-900 border border-gray-700",
            on_click=WorkflowState.toggle_alert_feed
        )
    )


# ===========================================
# TOAST
# ===========================================

def toast_notification() -> rx.Component:
    return rx.cond(
        WorkflowState.show_toast,
        rx.box(
            rx.hstack(
                rx.text(WorkflowState.toast_message, class_name="text-sm text-white"),
                rx.button(rx.icon("x", size=14), variant="ghost", size="1", on_click=WorkflowState.hide_toast),
                spacing="3",
                align_items="center"
            ),
            class_name="fixed bottom-24 left-1/2 transform -translate-x-1/2 bg-gray-800 border border-gray-700 px-4 py-3 rounded-lg shadow-lg z-[200]"
        ),
        rx.fragment()
    )


# ===========================================
# SIMULATION JAVASCRIPT
# ===========================================

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


# ===========================================
# MAIN PAGE
# ===========================================

def workflow_builder() -> rx.Component:
    """Main workflow builder page"""
    return rx.box(
        # Load simulation controller
        rx.script(SIMULATION_SCRIPT),
        
        rx.vstack(
            workflow_header(),
            rx.hstack(
                equipment_panel(),
                workflow_canvas(),
                alert_feed_panel(),
                spacing="0",
                class_name="flex-1 w-full h-full relative"
            ),
            simulation_controls(),
            spacing="0",
            class_name="h-screen w-full"
        ),
        drag_indicator(),
        workflow_list_dialog(),
        test_results_dialog(),
        toast_notification(),
        class_name="bg-black select-none",
        on_mount=WorkflowState.load_equipment,
    )