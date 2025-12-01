import reflex as rx
from app.states.nexus_state import NexusState

# --- COMPONENTES UI ---

def properties_view() -> rx.Component:
    """Vista Principal: Propiedades y Navegación"""
    return rx.vstack(
        # Grid de datos
        rx.grid(
            rx.vstack(
                rx.text("TEMP", class_name="text-[10px] text-gray-400 font-bold"),
                rx.text(f"{NexusState.selected_object_props['temperature']}°C", class_name="text-sm font-mono text-white"),
                spacing="1"
            ),
            rx.vstack(
                rx.text("PRESS", class_name="text-[10px] text-gray-400 font-bold"),
                rx.text(f"{NexusState.selected_object_props['pressure']}", class_name="text-sm font-mono text-white"),
                spacing="1"
            ),
            rx.vstack(
                rx.text("STATUS", class_name="text-[10px] text-gray-400 font-bold"),
                rx.badge(NexusState.selected_object_props['status'], 
                         color_scheme=rx.cond(NexusState.selected_object_props['status'] == "Optimal", "green", "red"),
                         size="1"),
                spacing="1"
            ),
            columns="3",
            width="100%",
            gap="2"
        ),
        # Botonera Principal (Quick Actions & Expand)
        rx.hstack(
            rx.button(
                rx.hstack(rx.icon("zap", size=14), rx.text("Quick Actions")),
                variant="surface", color_scheme="blue", size="2", width="100%",
                on_click=NexusState.set_menu_mode("actions")
            ),
            rx.button(
                rx.cond(
                    NexusState.is_expanded,
                    rx.icon("minimize-2", size=16), # Icono colapsar
                    rx.icon("maximize-2", size=16)  # Icono expandir
                ),
                variant="solid", 
                color_scheme=rx.cond(NexusState.is_expanded, "red", "gray"),
                size="2",
                on_click=NexusState.toggle_expand,
                title="Isolate/Expand Component View"
            ),
            width="100%",
            spacing="2"
        ),
        spacing="3",
        width="100%"
    )

def actions_view() -> rx.Component:
    """Vista Secundaria: Botones de Acción Rápida"""
    return rx.vstack(
        rx.text("PROTOCOL EXECUTION", class_name="text-[10px] text-gray-500 font-bold mb-1"),
        rx.grid(
            rx.button(
                rx.vstack(rx.icon("send", size=18), rx.text("Send Data", size="1")),
                variant="outline", class_name="h-16 border-gray-700 hover:bg-blue-900/20",
                on_click=NexusState.handle_quick_action("SEND")
            ),
            rx.button(
                rx.vstack(rx.icon("file-text", size=18), rx.text("Report", size="1")),
                variant="outline", class_name="h-16 border-gray-700 hover:bg-blue-900/20",
                on_click=NexusState.handle_quick_action("REPORT")
            ),
            rx.button(
                rx.vstack(rx.icon("octagon", size=18), rx.text("STOP", size="1")),
                variant="outline", class_name="h-16 border-red-900/50 text-red-400 hover:bg-red-900/20 hover:border-red-500",
                on_click=NexusState.handle_quick_action("STOP")
            ),
            columns="3",
            gap="2",
            width="100%"
        ),
        rx.button(
            rx.hstack(rx.icon("arrow-left", size=14), rx.text("Back to Properties")),
            variant="ghost", size="1", width="100%", class_name="mt-2 text-gray-400",
            on_click=NexusState.set_menu_mode("main")
        ),
        width="100%"
    )

def floating_context_menu() -> rx.Component:
    """Menú flotante dinámico"""
    return rx.cond(
        NexusState.selected_object_name,
        rx.vstack(
            # Header común
            rx.hstack(
                rx.icon("box", size=16, class_name="text-orange-400"),
                rx.text(NexusState.selected_object_name, class_name="font-bold text-white text-sm"),
                rx.spacer(),
                rx.button(
                    rx.icon("x", size=14),
                    variant="ghost", size="1",
                    on_click=NexusState.clear_selection,
                    class_name="hover:bg-red-500/20 text-gray-400 hover:text-red-400 rounded-full p-1"
                ),
                width="100%", align_items="center"
            ),
            rx.separator(class_name="my-2 bg-gray-700"),
            
            # Contenido Dinámico (Propiedades o Acciones)
            rx.cond(
                NexusState.menu_mode == "main",
                properties_view(),
                actions_view()
            ),
            
            class_name="absolute bottom-6 right-6 bg-gray-900/95 backdrop-blur-md p-4 rounded-xl border border-gray-600 shadow-2xl z-50 w-80 animate-in slide-in-from-bottom-4 fade-in duration-300"
        ),
        rx.fragment()
    )

def controls_guide() -> rx.Component:
    return rx.hstack(
        rx.hstack(rx.icon("mouse-pointer-2", size=14), rx.text("Rotate (L)", class_name="text-[10px]")),
        rx.divider(orientation="vertical", class_name="h-3 bg-gray-600"),
        rx.hstack(rx.icon("move", size=14), rx.text("Pan (R)", class_name="text-[10px]")),
        rx.divider(orientation="vertical", class_name="h-3 bg-gray-600"),
        rx.hstack(rx.icon("zoom-in", size=14), rx.text("Zoom", class_name="text-[10px]")),
        class_name="absolute top-4 left-4 bg-gray-900/80 backdrop-blur px-3 py-1.5 rounded-full border border-gray-700 text-gray-300 shadow-lg z-40 items-center gap-3 select-none pointer-events-none"
    )

def main_layout() -> rx.Component:
    return rx.grid(
        rx.grid(
            rx.box(
                rx.html("""
                    <model-viewer
                        src="/pharmaceutical_manufacturing_machinery.glb"
                        camera-orbit="45deg 55deg 2.5m" 
                        camera-controls autoplay
                        shadow-intensity="1"
                        loading="eager"
                        style="width: 100%; height: 100%; min-height: 500px; display: block; background-color: #111827;"
                    >
                         <div slot="poster" style="color: white; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%);">
                             Cargando Digital Twin...
                        </div>
                    </model-viewer>
                """),
                
                # Input JS -> Python (Selección)
                rx.el.input(id="bridge-input", class_name="hidden", on_change=NexusState.handle_3d_selection),
                
                # NUEVO: Input Python -> JS (Comandos como isolate/restore)
                rx.el.input(id="command-input", class_name="hidden", value=NexusState.js_command),
                
                controls_guide(),
                floating_context_menu(),
                class_name="w-full h-full relative rounded-lg overflow-hidden border border-gray-800 bg-gray-900 shadow-lg flex flex-col",
            ),
            rx.vstack(
                rx.hstack(
                    rx.icon("activity", size=16, class_name="text-blue-500"),
                    rx.text("Active Workflows", class_name="text-xs font-bold text-gray-400 uppercase tracking-wider"),
                    class_name="w-full p-3 border-b border-gray-800 bg-gray-900/50"
                ),
                rx.vstack(
                    rx.foreach(
                        NexusState.workflow_steps,
                        lambda step: rx.hstack(
                            rx.text(step["title"], class_name="text-sm text-gray-300"),
                            rx.spacer(),
                            rx.badge(step["status"], variant="outline"),
                            class_name="w-full p-2 bg-gray-800/30 rounded border border-gray-700/50"
                        )
                    ),
                    class_name="w-full p-3 gap-2 overflow-y-auto"
                ),
                class_name="w-full h-full bg-gray-900 rounded-lg border border-gray-800 overflow-hidden"
            ),
            rows="60% 40%", gap="4", height="100%", width="100%"
        ),
        rx.vstack(
            rx.hstack(
                rx.icon("bot", class_name="text-green-400"),
                rx.text("Nexus AI", class_name="font-bold text-white"),
                class_name="p-4 border-b border-gray-800 w-full bg-gray-900"
            ),
            rx.vstack(
                rx.foreach(NexusState.chat_history, lambda msg: rx.box(
                    rx.text(msg["text"], class_name="text-sm text-gray-200"),
                    class_name=rx.cond(msg["role"] == "system", "bg-gray-800 p-2 rounded-lg border-l-2 border-blue-500 mb-2", "bg-blue-900/30 p-2 rounded-lg border-l-2 border-green-500 mb-2 ml-4")
                )),
                class_name="flex-1 w-full p-4 overflow-y-auto"
            ),
            rx.hstack(
                rx.input(placeholder="Command...", value=NexusState.chat_input, on_change=NexusState.set_chat_input, class_name="bg-gray-800 border-gray-700 text-sm", width="100%"),
                rx.button(rx.icon("send", size=16), on_click=NexusState.send_message),
                class_name="p-3 border-t border-gray-800 w-full bg-gray-900 gap-2"
            ),
            class_name="h-full bg-gray-950 rounded-lg border border-gray-800 overflow-hidden"
        ),
        grid_template_columns="65% 35%", height="100vh", width="100%", gap="4", class_name="p-4 bg-black"
    )

def index() -> rx.Component:
    return rx.box(main_layout(), class_name="bg-black min-h-screen", width="100%")

app = rx.App(
    theme=rx.theme(appearance="dark"),
    head_components=[
        rx.el.script(src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js", type="module"),
        rx.el.script(src="/interaction.js", type="module"),
    ],
)
app.add_page(index, route="/")