import reflex as rx
from app.states.nexus_state import NexusState
from app.workflow_builder import workflow_builder
from app.workflow_builder import live_sensor_dashboard
from app.states.workflow_state import WorkflowState

# Initialize data directory for SQLite
from pathlib import Path
Path("data").mkdir(exist_ok=True)

# --- RUL CHART ---
def rul_chart(percentage: int) -> rx.Component:
    circumference = 2 * 3.1416 * 40
    stroke_dashoffset = circumference * (1 - (percentage / 100))
    color = rx.cond(percentage > 50, "text-green-500", rx.cond(percentage > 20, "text-yellow-500", "text-red-500"))
    return rx.box(
        rx.html(f"""
            <svg width="100" height="100" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                <circle cx="50" cy="50" r="40" stroke="#1f2937" stroke-width="8" fill="transparent" />
                <circle cx="50" cy="50" r="40" stroke="currentColor" stroke-width="8" fill="transparent" 
                        stroke-dasharray="{circumference}" stroke-dashoffset="{stroke_dashoffset}" 
                        stroke-linecap="round" class="{color} transition-all duration-1000" />
            </svg>
        """),
        rx.vstack(
            rx.text("RUL", class_name="text-[10px] text-gray-400 font-bold"),
            rx.text(f"{percentage}%", class_name="text-xl font-mono text-white font-bold"),
            class_name="absolute inset-0 flex items-center justify-center pointer-events-none"
        ),
        class_name="relative w-[100px] h-[100px]"
    )

# --- KNOWLEDGE GRAPH PANEL ---
def knowledge_graph_panel() -> rx.Component:
    return rx.cond(
        NexusState.is_expanded,
        rx.vstack(
            rx.hstack(
                rx.icon("network", class_name="text-blue-400"),
                rx.text("Knowledge Graph", class_name="font-bold text-blue-100 uppercase text-xs tracking-wider"),
                class_name="mb-2 items-center gap-2"
            ),
            rx.hstack(
                rul_chart(NexusState.equipment_rul),
                rx.vstack(
                    rx.badge(NexusState.equipment_line, variant="outline", color_scheme="blue"),
                    rx.text(NexusState.equipment_product, class_name="text-xs text-white"),
                    align_items="start", spacing="1"
                ),
                class_name="w-full bg-gray-800/50 p-3 rounded-lg border border-gray-700"
            ),
            rx.text("SENSORS", class_name="text-[10px] text-gray-500 font-bold mt-2"),
            rx.flex(
                rx.foreach(NexusState.equipment_sensors, lambda s: rx.badge(s, variant="soft", color_scheme="cyan", size="1", class_name="m-1")),
                wrap="wrap"
            ),
            rx.separator(class_name="bg-gray-700 my-1"),
            rx.grid(
                rx.vstack(
                    rx.text("DEPENDS ON", class_name="text-[10px] text-gray-500 font-bold"),
                    rx.foreach(NexusState.equipment_depends_on, lambda d: rx.hstack(rx.icon("arrow-up", size=10, class_name="text-red-400"), rx.text(d, size="1"))),
                    spacing="1"
                ),
                rx.vstack(
                    rx.text("AFFECTS", class_name="text-[10px] text-gray-500 font-bold"),
                    rx.foreach(NexusState.equipment_affects, lambda a: rx.hstack(rx.icon("arrow-down", size=10, class_name="text-green-400"), rx.text(a, size="1"))),
                    spacing="1"
                ),
                columns="2", class_name="bg-gray-800/30 p-2 rounded border border-gray-700/50"
            ),
            class_name="absolute top-4 left-4 bottom-16 w-80 bg-gray-900/95 backdrop-blur-xl p-4 rounded-xl border border-gray-600 shadow-2xl z-40"
        ),
        rx.fragment()
    )

def properties_view() -> rx.Component:
    return rx.vstack(
        rx.grid(
            rx.vstack(rx.text("TEMP", class_name="text-[10px] text-gray-400 font-bold"), rx.text(f"{NexusState.equipment_temp}°C", class_name="text-sm font-mono text-white"), spacing="1"),
            rx.vstack(rx.text("PRESS", class_name="text-[10px] text-gray-400 font-bold"), rx.text(f"{NexusState.equipment_pressure}", class_name="text-sm font-mono text-white"), spacing="1"),
            rx.vstack(rx.text("STATUS", class_name="text-[10px] text-gray-400 font-bold"), rx.badge(NexusState.equipment_status, size="1"), spacing="1"),
            columns="3", width="100%", gap="2"
        ),
        rx.separator(class_name="my-1 bg-gray-700"),
        rx.vstack(
            rx.button(
                rx.hstack(
                    rx.cond(NexusState.is_expanded, rx.icon("minimize-2", size=18), rx.icon("maximize-2", size=18)),
                    rx.vstack(
                        rx.text(rx.cond(NexusState.is_expanded, "Restore", "Focus Mode"), class_name="font-bold"),
                        rx.text("Graph Context", class_name="text-[10px] opacity-80"),
                        align_items="start", spacing="0"
                    )
                ),
                variant="solid",
                color_scheme=rx.cond(NexusState.is_expanded, "indigo", "gray"),
                size="3", width="100%",
                on_click=NexusState.toggle_expand
            ),
            rx.button(rx.hstack(rx.icon("zap", size=16), rx.text("Quick Actions")), variant="soft", size="2", width="100%", on_click=NexusState.set_menu_mode("actions")),
            spacing="2", width="100%"
        ),
        spacing="3", width="100%"
    )

def actions_view() -> rx.Component:
    return rx.vstack(
        rx.text("ACTIONS", class_name="text-[10px] text-gray-500 font-bold mb-1"),
        rx.grid(
            rx.button(
                rx.vstack(rx.icon("git-branch-plus", size=18), rx.text("New Workflow", size="1")),
                variant="outline", class_name="h-16 text-blue-400",
                on_click=NexusState.create_workflow_for_selection
            ),
            rx.button(rx.vstack(rx.icon("send", size=18), rx.text("Send", size="1")), variant="outline", class_name="h-16", on_click=lambda: NexusState.handle_quick_action("SEND")),
            rx.button(rx.vstack(rx.icon("file-text", size=18), rx.text("Report", size="1")), variant="outline", class_name="h-16", on_click=lambda: NexusState.handle_quick_action("REPORT")),
            rx.button(rx.vstack(rx.icon("octagon", size=18), rx.text("STOP", size="1")), variant="outline", class_name="h-16 text-red-400", on_click=lambda: NexusState.handle_quick_action("STOP")),
            columns="3", gap="2", width="100%"
        ),
        rx.button(rx.hstack(rx.icon("arrow-left", size=14), rx.text("Back")), variant="ghost", size="1", width="100%", on_click=NexusState.set_menu_mode("main")),
        width="100%"
    )

def floating_context_menu() -> rx.Component:
    return rx.cond(
        NexusState.selected_object_name != "",
        rx.vstack(
            rx.hstack(
                rx.icon("box", size=16, class_name="text-orange-400"),
                rx.text(NexusState.selected_object_name, class_name="font-bold text-white text-sm"),
                rx.spacer(),
                rx.button(rx.icon("x", size=14), variant="ghost", size="1", on_click=NexusState.clear_selection),
                width="100%"
            ),
            rx.separator(class_name="my-2 bg-gray-700"),
            rx.cond(NexusState.menu_mode == "main", properties_view(), actions_view()),
            class_name="absolute bottom-6 right-6 bg-gray-900/95 backdrop-blur-md p-4 rounded-xl border border-gray-600 shadow-2xl z-50 w-80"
        ),
        rx.fragment()
    )

def controls_guide() -> rx.Component:
    return rx.cond(
        ~NexusState.is_expanded,
        rx.hstack(
            rx.hstack(rx.icon("mouse-pointer-2", size=14), rx.text("Rotate", class_name="text-[10px]")),
            rx.divider(orientation="vertical", class_name="h-3 bg-gray-600"),
            rx.hstack(rx.icon("move", size=14), rx.text("Pan", class_name="text-[10px]")),
            class_name="absolute top-4 left-4 bg-gray-900/80 backdrop-blur px-3 py-1.5 rounded-full border border-gray-700 text-gray-300 shadow-lg z-40"
        ),
        rx.fragment()
    )

# --- MAIN LAYOUT (NO TABS - SINGLE VIEW) ---
def monitor_header() -> rx.Component:
    """Header with navigation to workflow builder"""
    return rx.hstack(
        rx.hstack(
            rx.icon("activity", size=24, class_name="text-blue-400"),
            rx.heading("Nexus Monitor", size="6", class_name="text-white"),
            spacing="3",
            align_items="center"
        ),
        rx.spacer(),
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
        class_name="w-full px-4 py-3 border-b border-gray-800 bg-gray-900",
        align_items="center"
    )

def index() -> rx.Component:
    return rx.box(
        rx.vstack(
            monitor_header(),
            rx.grid(
            rx.grid(
                rx.box(
                    rx.html("""
                        <model-viewer
                            src="/pharmaceutical_manufacturing_machinery.glb"
                            camera-orbit="45deg 55deg 2.5m" camera-controls autoplay shadow-intensity="1"
                            style="width: 100%; height: 100%; min-height: 500px; display: block; background: #111827;">
                            <div slot="poster" style="color: white; text-align: center; padding-top: 50%;">Loading...</div>
                        </model-viewer>
                    """),
                    rx.el.input(id="bridge-input", class_name="hidden", on_change=NexusState.handle_3d_selection),

                    # LOGIC MOVED TO FRONTEND TO AVOID SERIALIZATION ERRORS
                    rx.el.input(
                        id="command-input",
                        class_name="hidden",
                        read_only=True,
                        value=rx.cond(
                            WorkflowState.latest_alert_equipment != "",
                            "alert:" + WorkflowState.latest_alert_equipment,
                            NexusState.js_command
                        )
                    ),
                    controls_guide(),
                    floating_context_menu(),
                    knowledge_graph_panel(),
                    class_name="w-full h-full relative rounded-lg overflow-hidden border border-gray-800 bg-gray-900"
                ),
                # --- PANEL INFERIOR IZQUIERDO MEJORADO ---
                rx.vstack(
                    rx.hstack(
                        rx.icon("activity", size=16, class_name="text-blue-500"),
                        rx.text("Live Monitor", class_name="text-xs font-bold text-gray-400 uppercase"),
                        rx.spacer(),
                        rx.cond(
                            WorkflowState.simulation_running,
                            rx.badge("SIMULATION ON", color_scheme="green", variant="solid", size="1"),
                            rx.badge("MONITORING", color_scheme="gray", variant="outline", size="1")
                        ),
                        class_name="w-full p-3 border-b border-gray-800 bg-gray-900/50 items-center"
                    ),

                    # 1. Dashboard de Sensores (Solo visible si corre simulación)
                    live_sensor_dashboard(),

                    # 2. Feed de Alertas (Siempre visible)
                    rx.vstack(
                        rx.text("Alert Stream", class_name="text-[10px] font-bold text-gray-500 uppercase px-2 pt-2"),
                        rx.vstack(
                            rx.foreach(
                                WorkflowState.alert_feed,
                                lambda a: rx.hstack(
                                    rx.box(class_name=rx.cond(a['severity']=='critical', "w-1 h-full bg-red-500", "w-1 h-full bg-yellow-500")),
                                    rx.text(f"{a['equipment']}: {a['sensor']} > {a['threshold']}", class_name="text-xs text-gray-300"),
                                    rx.spacer(),
                                    rx.text(a['timestamp'], class_name="text-[10px] text-gray-600 font-mono"),
                                    class_name="w-full bg-gray-800/30 p-2 rounded border border-gray-700/30 items-center"
                                )
                            ),
                            class_name="flex-1 overflow-y-auto w-full p-2 space-y-1 max-h-[150px]"
                        ),
                        width="100%", spacing="2"
                    ),
                    class_name="w-full h-full bg-gray-900 rounded-lg border border-gray-800 overflow-hidden"
                ),
                # -------------------------------------------
                rows="60% 40%", gap="4", height="100%"
            ),
            rx.vstack(
                rx.hstack(rx.icon("bot", class_name="text-green-400"), rx.text("Nexus AI", class_name="font-bold text-white"), class_name="p-4 border-b border-gray-800 bg-gray-900"),
                rx.vstack(rx.foreach(NexusState.chat_history, lambda m: rx.box(rx.text(m["text"], class_name="text-sm text-gray-200"), class_name="bg-gray-800 p-2 rounded-lg mb-2")), class_name="flex-1 p-4 overflow-y-auto"),
                rx.form(
                    rx.hstack(
                        rx.input(placeholder="Command...", value=NexusState.chat_input, on_change=NexusState.set_chat_input, class_name="bg-gray-800 border-gray-700 text-sm", width="100%", name="chat_msg"),
                        rx.button(rx.icon("send", size=16), type="submit"),
                        class_name="gap-2"
                    ),
                    on_submit=NexusState.send_message,
                    class_name="p-3 border-t border-gray-800 w-full"
                ),
                class_name="h-full bg-gray-950 rounded-lg border border-gray-800",
                width="100%"
            ),
            grid_template_columns="65% 35%", height="calc(100vh - 60px)", gap="4", class_name="p-4", width="100%"
        ),
            spacing="0",
            class_name="bg-black min-h-screen w-full"
        ),
        # CARGA INICIAL CRÍTICA
        on_mount=WorkflowState.load_equipment
    )

app = rx.App(
    theme=rx.theme(appearance="dark"),
    head_components=[
        rx.el.script(src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js", type="module"),
        rx.el.script(src="/interaction.js", type="module"),
    ],
)
app.add_page(index, route="/")
app.add_page(workflow_builder, route="/workflow-builder")