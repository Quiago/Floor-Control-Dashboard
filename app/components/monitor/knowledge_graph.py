# app/components/monitor/knowledge_graph.py
"""Knowledge Graph panel with interactive dependency visualization"""
import reflex as rx
from app.states.monitor_state import MonitorState
from app.components.shared.design_tokens import (
    GLASS_PANEL_PREMIUM, SHADOW_XL, COLORS, TRANSITION_DEFAULT, GRAPH_COLORS
)
from app.components.shared import gradient_separator, section_label, dependency_node

def knowledge_graph_panel() -> rx.Component:
    """Left expandable panel with RUL + interactive dependency graph - always rendered, hidden with CSS"""
    return rx.vstack(
            # Header
            rx.hstack(
                rx.icon("network", class_name="text-blue-400"),
                rx.text(
                    "Knowledge Graph",
                    class_name="font-bold text-blue-200 uppercase text-xs tracking-wider"
                ),
                rx.spacer(),
                rx.badge("LIVE", color_scheme="green", size="1"),
                spacing="2",
                width="100%",
                class_name="mb-2"
            ),
            
            # RUL Chart + Equipment Info
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
                        class_name="text-xs text-slate-200"
                    ),
                    rx.hstack(
                        rx.icon("activity", size=12, class_name="text-green-400"),
                        rx.text("Optimal", class_name="text-[10px] text-green-400"),
                        spacing="1"
                    ),
                    align_items="start",
                    spacing="1"
                ),
                class_name="w-full bg-slate-800/60 p-3 rounded-lg border border-slate-600/40"
            ),
            
            # Sensors
            section_label("SENSORS"),
            rx.flex(
                rx.foreach(
                    MonitorState.equipment_sensors,
                    lambda s: rx.badge(
                        s,
                        variant="soft",
                        color_scheme="blue",
                        size="1",
                        class_name="m-1"
                    )
                ),
                wrap="wrap"
            ),
            
            gradient_separator(),
            
            # Dependency Graph Section
            section_label("DEPENDENCY GRAPH"),
            
            dependency_graph_visualization(),
            
            # Traceability Info
            gradient_separator(),
            section_label("TRACEABILITY"),
            
            rx.hstack(
                rx.vstack(
                    rx.text("Batch", class_name="text-[10px] text-slate-500 uppercase"),
                    rx.text("B-2024-0847", class_name="text-xs font-mono text-slate-200"),
                    spacing="0",
                    align_items="start"
                ),
                rx.vstack(
                    rx.text("Product", class_name="text-[10px] text-slate-500 uppercase"),
                    rx.text("PharmaTech-X", class_name="text-xs font-mono text-slate-200"),
                    spacing="0",
                    align_items="start"
                ),
                rx.vstack(
                    rx.text("QC Gate", class_name="text-[10px] text-slate-500 uppercase"),
                    rx.badge("PASSED", color_scheme="green", size="1"),
                    spacing="0",
                    align_items="start"
                ),
                spacing="4",
                class_name="w-full bg-slate-800/40 p-3 rounded-lg border border-slate-600/30"
            ),
            
            spacing="4",
            class_name=rx.cond(
                MonitorState.is_expanded,
                f"{GLASS_PANEL_PREMIUM} absolute top-4 left-4 bottom-16 w-80 lg:w-96 max-w-[90vw] p-4 rounded-xl {SHADOW_XL} z-40 overflow-y-auto",
                f"{GLASS_PANEL_PREMIUM} absolute top-4 left-4 bottom-16 w-80 lg:w-96 max-w-[90vw] p-4 rounded-xl {SHADOW_XL} z-40 overflow-y-auto hidden"
            )
        )

def dependency_graph_visualization() -> rx.Component:
    """Interactive dependency graph visualization"""
    return rx.vstack(
        # Upstream Section
        rx.vstack(
            rx.hstack(
                rx.icon("arrow-up", size=14, class_name="text-orange-400"),
                rx.text("UPSTREAM DEPENDENCIES", class_name="text-[10px] text-orange-400 font-bold uppercase tracking-wider"),
                spacing="2"
            ),
            rx.hstack(
                rx.foreach(
                    MonitorState.equipment_depends_on,
                    lambda d: rx.box(
                        rx.hstack(
                            rx.box(class_name="w-2 h-2 rounded-full bg-orange-500"),
                            rx.text(d, class_name="text-xs text-slate-200"),
                            spacing="2"
                        ),
                        class_name=f"px-3 py-2 rounded-lg bg-orange-500/10 border border-orange-500/30 {TRANSITION_DEFAULT} hover:bg-orange-500/20 cursor-pointer"
                    )
                ),
                spacing="2",
                wrap="wrap"
            ),
            spacing="2",
            width="100%",
            align_items="start"
        ),
        
        # Connection Lines (SVG)
        rx.box(
            rx.html("""
                <svg width="100%" height="40" class="w-full">
                    <defs>
                        <marker id="arrowDown" viewBox="0 0 10 10" refX="5" refY="5" 
                                markerWidth="4" markerHeight="4" orient="auto-start-reverse">
                            <path d="M 0 0 L 10 5 L 0 10 z" fill="#64748b"/>
                        </marker>
                    </defs>
                    <line x1="50%" y1="0" x2="50%" y2="35" 
                          stroke="#64748b" stroke-width="2" 
                          stroke-dasharray="4,2" marker-end="url(#arrowDown)"/>
                </svg>
            """),
            class_name="w-full"
        ),
        
        # Selected Equipment (Center)
        rx.center(
            rx.box(
                rx.hstack(
                    rx.icon("target", size=18, class_name="text-blue-400"),
                    rx.vstack(
                        rx.text(
                            MonitorState.selected_object_name,
                            class_name="text-sm font-bold text-blue-100"
                        ),
                        rx.text("SELECTED", class_name="text-[9px] text-blue-400 uppercase tracking-wider"),
                        spacing="0",
                        align_items="start"
                    ),
                    spacing="3"
                ),
                class_name="px-4 py-3 rounded-xl bg-blue-500/20 border-2 border-blue-500/50 ring-4 ring-blue-500/10 shadow-lg shadow-blue-500/20"
            ),
            width="100%"
        ),
        
        # Connection Lines (SVG)
        rx.box(
            rx.html("""
                <svg width="100%" height="40" class="w-full">
                    <line x1="50%" y1="5" x2="50%" y2="40" 
                          stroke="#64748b" stroke-width="2" 
                          stroke-dasharray="4,2" marker-end="url(#arrowDown)"/>
                </svg>
            """),
            class_name="w-full"
        ),
        
        # Downstream Section
        rx.vstack(
            rx.hstack(
                rx.icon("arrow-down", size=14, class_name="text-green-400"),
                rx.text("DOWNSTREAM AFFECTED", class_name="text-[10px] text-green-400 font-bold uppercase tracking-wider"),
                spacing="2"
            ),
            rx.hstack(
                rx.foreach(
                    MonitorState.equipment_affects,
                    lambda a: rx.box(
                        rx.hstack(
                            rx.box(class_name="w-2 h-2 rounded-full bg-green-500"),
                            rx.text(a, class_name="text-xs text-slate-200"),
                            spacing="2"
                        ),
                        class_name=f"px-3 py-2 rounded-lg bg-green-500/10 border border-green-500/30 {TRANSITION_DEFAULT} hover:bg-green-500/20 cursor-pointer"
                    )
                ),
                spacing="2",
                wrap="wrap"
            ),
            spacing="2",
            width="100%",
            align_items="start"
        ),
        
        spacing="2",
        width="100%",
        class_name="bg-slate-900/40 p-3 rounded-lg border border-slate-600/30"
    )

def rul_chart(percentage: rx.Var[int]) -> rx.Component:
    """Circular RUL chart with industrial styling"""
    circumference = 2 * 3.1416 * 40
    
    return rx.box(
        rx.html(f"""
            <svg width="100" height="100" viewBox="0 0 100 100" style="transform: rotate(-90deg);">
                <circle cx="50" cy="50" r="40" stroke="#334155" stroke-width="8" fill="transparent" />
                <circle cx="50" cy="50" r="40" stroke="currentColor" stroke-width="8" fill="transparent" 
                        stroke-dasharray="{circumference}" 
                        stroke-dashoffset="{{circumference * (1 - (percentage / 100))}}" 
                        stroke-linecap="round" 
                        class="{{percentage > 50 ? 'text-green-500' : percentage > 20 ? 'text-orange-500' : 'text-red-500'}} transition-all duration-1000" />
            </svg>
        """.replace("{{circumference", "{circumference").replace("percentage", str(percentage))),
        rx.vstack(
            rx.text("RUL", class_name="text-[10px] text-slate-400 font-bold"),
            rx.text(f"{percentage}%", class_name="text-xl font-mono text-slate-100 font-bold"),
            class_name="absolute inset-0 flex items-center justify-center pointer-events-none"
        ),
        class_name="relative w-[100px] h-[100px]"
    )