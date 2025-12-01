import reflex as rx
from app.states.nexus_state import NexusState

# ... (chat_message se mantiene igual) ...
def chat_message(msg: dict) -> rx.Component:
    return rx.hstack(
        #rx.text(msg["time"], class_name="text-xs text-gray-500 font-mono min-w-[60px] shrink-0"),
        rx.text(msg["role"], class_name=rx.cond(msg["role"] == "Assistant", "text-xs font-bold text-blue-400 uppercase tracking-wide w-16 shrink-0", "text-xs font-bold text-green-400 uppercase tracking-wide w-16 shrink-0")),
        rx.text(msg["text"], class_name="text-sm text-gray-200 flex-1 break-words"),
        class_name="w-full items-start gap-3 py-1 px-2 hover:bg-gray-800/50 rounded transition-colors",
    )

def qa(question: str, answer: str) -> rx.Component:
    return rx.box(
        rx.box(question, text_align="right"),
        rx.box(answer, text_align="left"),
        margin_y="1em",
    )

def chat() -> rx.Component:
    qa_pairs = [
        (
            "What is Reflex?",
            "A way to build web apps in pure Python!",
        ),
        (
            "What can I make with it?",
            "Anything from a simple website to a complex web app!",
        ),
    ]
    return rx.box(
        *[
            qa(question, answer)
            for question, answer in qa_pairs
        ]
    )
# ... (context_menu se mantiene igual) ...
def context_menu() -> rx.Component:
    return rx.vstack(
        rx.text(NexusState.selected_component, class_name="text-xs text-gray-500 font-mono mb-1 px-2 border-b border-gray-700 pb-1 w-full"),
        rx.el.button(rx.hstack(rx.icon("maximize", size=14), rx.text("Expand View")), class_name="w-full flex items-center gap-2 px-2 py-1.5 hover:bg-blue-600/20 hover:text-blue-400 rounded text-sm transition-colors text-left", on_click=NexusState.open_expanded_view),
        rx.el.button(rx.hstack(rx.icon("chart-bar", size=14), rx.text("Properties")), class_name="w-full flex items-center gap-2 px-2 py-1.5 hover:bg-blue-600/20 hover:text-blue-400 rounded text-sm transition-colors text-left", on_click=NexusState.open_properties),
        rx.el.button(rx.hstack(rx.icon("zap", size=14), rx.text("Quick Actions")), class_name="w-full flex items-center gap-2 px-2 py-1.5 hover:bg-yellow-600/20 hover:text-yellow-400 rounded text-sm transition-colors text-left", on_click=NexusState.menu_action_quick),
        class_name="absolute bg-gray-900 border border-gray-700 rounded-lg shadow-2xl p-1 w-48 backdrop-blur-md",
        style={"left": NexusState.context_menu_x, "top": NexusState.context_menu_y, "z-index": "100"},
        display=rx.cond(NexusState.context_menu_open, "flex", "none"),
        on_mouse_leave=NexusState.close_context_menu,
    )

# ... (properties_panel y expanded_view_overlay se mantienen igual) ...
def properties_panel() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.hstack(rx.text("Status Summary", class_name="text-xs font-bold uppercase text-gray-400"), rx.spacer(), rx.el.button(rx.icon("x", size=14), on_click=NexusState.close_properties, class_name="text-gray-500 hover:text-white"), class_name="w-full items-center mb-2"),
            rx.text(NexusState.selected_component, class_name="text-lg font-semibold text-white mb-4"),
            rx.grid(rx.text("Health", class_name="text-sm text-gray-400"), rx.text("98%", class_name="text-sm text-green-400 font-mono text-right"), rx.text("Temp", class_name="text-sm text-gray-400"), rx.text("45°C", class_name="text-sm text-yellow-400 font-mono text-right"), cols="2", gap="2", class_name="w-full"),
            rx.button("Run Diagnostics", size="2", class_name="w-full mt-4 bg-gray-800 hover:bg-gray-700 border border-gray-600"),
            class_name="p-4",
        ),
        class_name="absolute bottom-4 right-4 w-64 bg-gray-900/90 border border-gray-700 rounded-lg shadow-xl backdrop-blur-md z-40 transition-all duration-300",
        display=rx.cond(NexusState.properties_panel_open, "block", "none"),
    )

def expanded_view_overlay() -> rx.Component:
    return rx.center(
        rx.vstack(
            rx.hstack(rx.icon("box", size=32, class_name="text-blue-500"), rx.heading(NexusState.selected_component, size="6"), rx.spacer(), rx.button("Close View", on_click=NexusState.exit_expanded_view, variant="outline"), class_name="w-full items-center gap-4 mb-8"),
            rx.text("Detailed breakdown view.", class_name="text-gray-500"),
            class_name="bg-gray-950 border border-gray-800 p-12 rounded-xl shadow-2xl w-3/4 h-3/4 max-w-4xl"
        ),
        class_name="absolute inset-0 bg-black/80 z-[60] backdrop-blur-sm",
        display=rx.cond(NexusState.is_expanded_view, "flex", "none")
    )

# --- MONITOR TAB ---

def monitor_tab() -> rx.Component:
    return rx.grid(
        rx.vstack(
            rx.box(
                # 1. PUENTE DE DATOS
                rx.el.input(
                    id="nexus-3d-bridge",
                    class_name="hidden",
                    on_change=NexusState.handle_3d_click
                ),
                
                # 2. MODELO 3D (Versión Corregida)
                rx.box(
                    as_=rx.Var.create("'model-viewer'"),
                    key="static-model-viewer",
                    src="/pharmaceutical_manufacturing_machinery.glb",
                    alt="Digital Twin",
                    custom_attrs={
                        "camera-orbit": "45deg 55deg 2.5m",
                        "bounds": "tight",
                        #"autoplay": "true",
                        "touch-action": "pan-y",
                        # ESTA LÍNEA ES LA SOLUCIÓN AL ERROR DE CONSOLA:
                        "camera-controls": rx.cond(NexusState.camera_active, "true", None)
                    },
                    width="100%",
                    height="100%",
                    position="absolute",
                    top="0",
                    left="0",
                    z_index="0",
                ),
                
                # 3. ESCUDO (Cierra el menú al hacer click fuera)
                rx.cond(
                    NexusState.context_menu_open,
                    rx.box(
                        class_name="absolute inset-0 z-10 cursor-default",
                        on_click=NexusState.close_context_menu,
                        # Un fondo transparente muy sutil ayuda a depurar si el escudo está activo
                        bg="transparent" 
                    )
                ),

                # 4. UI FLOTANTE
                rx.el.button(
                    rx.icon("triangle-alert", class_name="text-white h-6 w-6"),
                    class_name="absolute top-4 right-4 p-3 rounded-full bg-red-600 shadow-lg z-20 transition-opacity",
                    style={"opacity": rx.cond(NexusState.is_alert_active, "1", "0.3")},
                ),
                
                context_menu(), 
                properties_panel(),
                expanded_view_overlay(),
                
                class_name="relative w-full h-[75%] bg-gray-900 rounded-lg border border-gray-700 shadow-md isolate overflow-hidden",
            ),
            
            # --- CHAT UI (Sin cambios) ---
            rx.vstack(
                rx.hstack(
                    rx.hstack(rx.icon("bot", size=18, class_name="text-blue-400"), rx.text("Nexus AI Assistant", class_name="text-sm font-semibold text-white"), class_name="items-center gap-2"),
                    rx.el.button(rx.hstack(rx.icon("play", size=12, class_name="text-white"), rx.text("RUN SIMULATION", class_name="text-[10px] font-bold"), class_name="items-center gap-1"), on_click=NexusState.start_simulation, class_name="bg-blue-600 hover:bg-blue-500 text-white px-3 py-1.5 rounded transition-colors shadow-sm"),
                    class_name="w-full justify-between items-center px-4 py-3 border-b border-gray-700 bg-gray-800 shrink-0",
                ),
                #rx.vstack(rx.foreach(NexusState.chat_history, chat_message), class_name="flex-1 w-full overflow-y-auto p-4 space-y-2 bg-gray-900/50 scroll-smooth"),
                rx.vstack(chat(), class_name="flex-1 w-full overflow-y-auto p-4 space-y-2 bg-gray-900/50 scroll-smooth"),
                rx.hstack(
                    rx.el.input(placeholder="Type command...", on_change=NexusState.set_chat_input, class_name="flex-1 bg-gray-900 text-white text-sm rounded-md px-4 py-2 outline-none border border-gray-700 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-all placeholder:text-gray-600", default_value=NexusState.chat_input),
                    rx.el.button(rx.icon("send-horizontal", size=16, class_name="text-white"), on_click=NexusState.send_message, class_name="bg-blue-600 hover:bg-blue-500 p-2.5 rounded-md transition-colors shadow-sm items-center flex justify-center"),
                    class_name="w-full p-3 border-t border-gray-700 bg-gray-800 gap-3 shrink-0",
                ),
                height="25%",
                class_name="w-full bg-gray-800 rounded-lg border border-gray-700 shadow-lg overflow-hidden",
            ),
            class_name="h-full gap-4",
        ),
        # --- PANEL DERECHO (Sin cambios) ---
        rx.vstack(
            rx.hstack(rx.icon("activity", size=18, class_name="text-blue-500"), rx.text("Live Workflows", class_name="text-sm font-bold text-gray-100 uppercase tracking-wider"), class_name="w-full items-center gap-2 mb-2 px-1"),
            rx.vstack(
                rx.foreach(NexusState.workflow_steps, lambda step: rx.el.div(rx.hstack(rx.text(step["title"], class_name="font-medium text-gray-200 text-sm"), rx.el.span(step["status"], class_name=rx.cond(step["status"] == "active", "bg-green-500/10 text-green-400 border-green-500/20", "bg-gray-700/30 text-gray-500 border-gray-700/30") + " text-[10px] px-2 py-0.5 rounded border uppercase font-bold"), class_name="justify-between items-start w-full gap-2"), rx.hstack(rx.icon("clock", size=12, class_name="text-gray-600"), rx.text(step["time"], class_name="text-[10px] text-gray-500 font-mono"), class_name="items-center gap-1.5 mt-2"), class_name="bg-gray-800/40 p-3 rounded-lg w-full border border-gray-700 hover:border-gray-600 transition-colors")),
                class_name="w-full space-y-2 overflow-y-auto pr-1",
            ),
            class_name="h-full bg-gray-900/30 rounded-lg p-3 border border-gray-800/50",
        ),
        grid_template_columns="3fr 1fr",
        width="100%",
        height="90vh",
        gap="4",
    )

# ... (builder_tab, index, app igual) ...
def builder_tab() -> rx.Component:
    return rx.hstack(
        rx.vstack(
            rx.text("Toolbox", class_name="text-sm font-bold text-gray-400 uppercase tracking-wider mb-4 px-1"),
            rx.el.button(rx.icon("scan-eye", size=16, class_name="mr-2 text-purple-400"), "Add Sensor", class_name="w-full flex items-center text-left px-3 py-2.5 bg-gray-800 text-gray-300 text-sm rounded hover:bg-gray-700 transition-colors border border-gray-700"),
            rx.el.button(rx.icon("zap", size=16, class_name="mr-2 text-yellow-400"), "Add Action", class_name="w-full flex items-center text-left px-3 py-2.5 bg-gray-800 text-gray-300 text-sm rounded hover:bg-gray-700 transition-colors border border-gray-700"),
            rx.el.button(rx.icon("git-branch", size=16, class_name="mr-2 text-blue-400"), "Add Condition", class_name="w-full flex items-center text-left px-3 py-2.5 bg-gray-800 text-gray-300 text-sm rounded hover:bg-gray-700 transition-colors border border-gray-700"),
            class_name="w-64 bg-gray-900/50 h-full p-4 border-r border-gray-800 gap-3",
        ),
        rx.box(
            rx.vstack(rx.icon("layout-template", size=48, class_name="text-gray-800 mb-4"), rx.text("Workflow Canvas", class_name="text-gray-600 font-medium text-lg"), rx.text("Drag and drop items from the toolbox to build automation", class_name="text-gray-700 text-sm"), class_name="items-center justify-center h-full"),
            class_name="flex-1 h-full bg-gray-950 p-8 rounded-lg m-4 border-2 border-dashed border-gray-800/50 flex items-center justify-center",
        ),
        class_name="h-[90vh] w-full",
    )

def index() -> rx.Component:
    return rx.el.main(
        rx.tabs.root(
            rx.tabs.list(
                rx.tabs.trigger("Monitor & Control", value="monitor", class_name="data-[state=active]:text-blue-400 data-[state=active]:border-b-2 data-[state=active]:border-blue-400 text-gray-400 px-4 py-2 hover:text-gray-200 transition-colors text-sm font-medium"),
                rx.tabs.trigger("Automation Builder", value="builder", class_name="data-[state=active]:text-blue-400 data-[state=active]:border-b-2 data-[state=active]:border-blue-400 text-gray-400 px-4 py-2 hover:text-gray-200 transition-colors text-sm font-medium"),
                class_name="mb-6 border-b border-gray-800 flex gap-4",
            ),
            rx.tabs.content(monitor_tab(), value="monitor", class_name="w-full outline-none"),
            rx.tabs.content(builder_tab(), value="builder", class_name="w-full outline-none"),
            value=NexusState.active_tab,
            on_change=NexusState.set_tab,
            class_name="w-full max-w-[1600px] mx-auto",
        ),
        class_name="min-h-screen bg-gray-950 text-white p-6 font-['Inter'] selection:bg-blue-500/30",
    )

app = rx.App(
    theme=rx.theme(appearance="light"),
    head_components=[
        rx.el.script(type="module", src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js"),
        rx.el.script(src="/interaction.js", type="module"),
        rx.el.link(href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap", rel="stylesheet"),
    ],
)
app.add_page(index, route="/")