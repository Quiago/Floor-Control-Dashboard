# app/components/monitor/knowledge_graph.py
"""Panel lateral con info de grafo de conocimiento"""
import reflex as rx
from app.states.monitor_state import MonitorState
from app.components.shared.design_tokens import GLASS_STRONG, SHADOW_XL, COLORS
from app.components.shared import gradient_separator, section_label

def knowledge_graph_panel() -> rx.Component:
    """Panel izquierdo expandible con RUL + deps"""
    return rx.cond(
        MonitorState.is_expanded,
        rx.vstack(
            # Header
            rx.hstack(
                rx.icon("network", class_name="text-blue-400"),
                rx.text(
                    "Knowledge Graph",
                    class_name="font-bold text-blue-100 uppercase text-xs tracking-wider"
                ),
                spacing="2",
                class_name="mb-2"
            ),
            
            # RUL Chart + Info
            rx.hstack(
                rul_chart(MonitorState.equipment_rul),
                rx.vstack(
                    rx.badge(
                        MonitorState.equipment_line,
                        variant="outline",
                        color_scheme="blue"
                    ),
                    rx.text(
                        MonitorState.equipment_product,
                        class_name="text-xs text-white"
                    ),
                    align_items="start",
                    spacing="1"
                ),
                class_name=f"w-full bg-[{COLORS['bg_elevated']}] p-3 rounded-lg border {COLORS['border_default']}"
            ),
            
            # Sensors
            section_label("SENSORS"),
            rx.flex(
                rx.foreach(
                    MonitorState.equipment_sensors,
                    lambda s: rx.badge(
                        s,
                        variant="soft",
                        color_scheme="cyan",
                        size="1",
                        class_name="m-1"
                    )
                ),
                wrap="wrap"
            ),
            
            gradient_separator(),
            
            # Dependencies
            rx.grid(
                rx.vstack(
                    section_label("DEPENDS ON"),
                    rx.foreach(
                        MonitorState.equipment_depends_on,
                        lambda d: rx.hstack(
                            rx.icon("arrow-up", size=10, class_name="text-rose-400"),
                            rx.text(d, size="1"),
                            spacing="1"
                        )
                    ),
                    spacing="1",
                    align_items="start"
                ),
                rx.vstack(
                    section_label("AFFECTS"),
                    rx.foreach(
                        MonitorState.equipment_affects,
                        lambda a: rx.hstack(
                            rx.icon("arrow-down", size=10, class_name="text-emerald-400"),
                            rx.text(a, size="1"),
                            spacing="1"
                        )
                    ),
                    spacing="1",
                    align_items="start"
                ),
                columns="2",
                class_name=f"bg-[{COLORS['bg_elevated']}]/30 p-2 rounded border {COLORS['border_subtle']}"
            ),
            
            spacing="4",
            class_name=f"{GLASS_STRONG} absolute top-4 left-4 bottom-16 w-80 p-4 rounded-xl {SHADOW_XL} z-40"
        ),
        rx.fragment()
    )

def rul_chart(percentage: rx.Var[int]) -> rx.Component:
    """Circular RUL chart"""
    circumference = 2 * 3.1416 * 40
    
    return rx.box(
        rx.html(f"""
            <svg width="100" height="100" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                <circle cx="50" cy="50" r="40" stroke="#1f2937" stroke-width="8" fill="transparent" />
                <circle cx="50" cy="50" r="40" stroke="currentColor" stroke-width="8" fill="transparent" 
                        stroke-dasharray="{circumference}" 
                        stroke-dashoffset="{{circumference * (1 - (percentage / 100))}}" 
                        stroke-linecap="round" 
                        class="{{percentage > 50 ? 'text-emerald-500' : percentage > 20 ? 'text-amber-500' : 'text-rose-500'}} transition-all duration-1000" />
            </svg>
        """.replace("{{circumference", "{circumference").replace("percentage", str(percentage))),
        rx.vstack(
            rx.text("RUL", class_name="text-[10px] text-gray-400 font-bold"),
            rx.text(f"{percentage}%", class_name="text-xl font-mono text-white font-bold"),
            class_name="absolute inset-0 flex items-center justify-center pointer-events-none"
        ),
        class_name="relative w-[100px] h-[100px]"
    )