# app/components/shared/__init__.py
"""Shared Components - Reusable across the application"""
import reflex as rx
from typing import Optional
from .design_tokens import (
    GRADIENT_PRIMARY, TRANSITION_DEFAULT, SEPARATOR_GRADIENT,
    GLASS_CARD, GLASS_PANEL_PREMIUM, INPUT_FIELD, COLORS, GRAPH_COLORS
)

# === STATUS DOT ===
def status_dot(running: bool = False, color: str = "green") -> rx.Component:
    """Animated status indicator dot"""
    return rx.box(
        class_name=rx.cond(
            running,
            f"w-2 h-2 bg-{color}-500 rounded-full animate-pulse",
            "w-2 h-2 bg-slate-600 rounded-full"
        )
    )

# === STAT PILL ===
def stat_pill(label: str, value: rx.Var[str], color: str = "slate") -> rx.Component:
    """Compact stat pill"""
    return rx.hstack(
        rx.text(label, class_name="text-[9px] text-slate-400 uppercase tracking-wider font-bold"),
        rx.text(value, class_name=f"text-xs font-mono text-{color}-300"),
        spacing="1",
        class_name="px-2 py-1 rounded-full bg-slate-800/60 border border-slate-600/40"
    )

# === SECTION LABEL ===
def section_label(text: str) -> rx.Component:
    """Section label with decorative line"""
    return rx.hstack(
        rx.box(class_name="h-px w-8 bg-gradient-to-r from-transparent to-slate-500/40"),
        rx.text(
            text,
            class_name="text-[10px] text-slate-400 font-bold uppercase tracking-wider"
        ),
        rx.box(class_name="h-px flex-1 bg-gradient-to-r from-slate-500/40 to-transparent"),
        spacing="3",
        width="100%",
        align_items="center"
    )

# === ICON BUTTON ===
def icon_button(
    icon: str,
    on_click,
    variant: str = "ghost",  # ghost, danger, primary
    size: int = 16,
    tooltip: Optional[str] = None
) -> rx.Component:
    """Icon button with variants"""
    
    variants = {
        "ghost": "hover:bg-slate-700/50 text-slate-400 hover:text-white",
        "danger": "hover:bg-red-500/10 text-red-400 hover:text-red-300",
        "primary": f"{GRADIENT_PRIMARY} text-white hover:opacity-90",
        "warning": "hover:bg-orange-500/10 text-orange-400 hover:text-orange-300"
    }
    
    btn = rx.button(
        rx.icon(icon, size=size),
        variant="ghost" if variant == "ghost" else "solid",
        size="1",
        on_click=on_click,
        class_name=f"{variants.get(variant, variants['ghost'])} {TRANSITION_DEFAULT}"
    )
    
    if tooltip:
        return rx.tooltip(btn, content=tooltip)
    return btn

# === PREMIUM INPUT ===
def premium_input(
    placeholder: str,
    value: rx.Var[str],
    on_change,
    input_type: str = "text",
    icon: Optional[str] = None
) -> rx.Component:
    """High-contrast input field with optional icon"""
    input_component = rx.input(
        placeholder=placeholder,
        value=value,
        on_change=on_change,
        type=input_type,
        class_name=INPUT_FIELD
    )
    
    if icon:
        return rx.hstack(
            rx.icon(icon, size=16, class_name="text-slate-400"),
            input_component,
            spacing="2",
            class_name="w-full"
        )
    return input_component

# === FORM FIELD ===
def form_field(
    label: str,
    input_component: rx.Component,
    error: rx.Var[str] = "",
    helper: Optional[str] = None
) -> rx.Component:
    """Consistent form field wrapper"""
    return rx.vstack(
        rx.text(
            label,
            class_name="text-xs text-slate-300 font-bold uppercase tracking-wider"
        ),
        input_component,
        # Error message (always rendered, hidden with CSS)
        rx.text(
            error,
            class_name=rx.cond(
                error != "",
                "text-[10px] text-red-400",
                "text-[10px] text-red-400 hidden"
            )
        ),
        # Helper text (always rendered, hidden with CSS)
        rx.text(
            helper if helper is not None else "",
            class_name=rx.cond(
                (helper is not None) & (error == ""),
                "text-[10px] text-slate-500",
                "text-[10px] text-slate-500 hidden"
            )
        ),
        spacing="1",
        width="100%",
        align_items="start"
    )

# === GLASS CARD ===
def glass_card(
    *children,
    padding: str = "4",
    class_name: str = ""
) -> rx.Component:
    """Consistent glass card component"""
    return rx.box(
        *children,
        class_name=f"{GLASS_CARD} p-{padding} rounded-xl {class_name}"
    )

# === CANVAS EMPTY STATE ===
def canvas_empty_state(
    icon: str = "layout-template",
    title: str = "Empty Canvas",
    description: str = "Drag elements to get started"
) -> rx.Component:
    """Elegant empty state with instructions"""
    return rx.center(
        rx.vstack(
            rx.box(
                rx.icon(icon, size=48, class_name="text-slate-600"),
                class_name="p-6 rounded-full bg-gradient-to-br from-slate-700/30 to-slate-800/20"
            ),
            rx.text(title, class_name="text-lg font-medium text-slate-300"),
            rx.text(description, class_name="text-sm text-slate-500"),
            spacing="4",
            align_items="center"
        ),
        class_name="w-full h-full min-h-[400px]"
    )

# === SEPARATOR WITH GRADIENT ===
def gradient_separator() -> rx.Component:
    """Gradient separator"""
    return rx.box(class_name=SEPARATOR_GRADIENT)

# === DEPENDENCY NODE ===
def dependency_node(
    name: str,
    node_type: str = "upstream",  # upstream, selected, downstream
    status: str = "active"
) -> rx.Component:
    """Node for dependency visualization"""
    colors = {
        "upstream": ("orange", "bg-orange-500/20 border-orange-500/40 text-orange-300"),
        "selected": ("blue", "bg-blue-500/30 border-blue-500/50 text-blue-200 ring-2 ring-blue-500/30"),
        "downstream": ("green", "bg-green-500/20 border-green-500/40 text-green-300")
    }
    
    color_scheme, classes = colors.get(node_type, colors["upstream"])
    
    icons = {
        "upstream": "arrow-up-circle",
        "selected": "target",
        "downstream": "arrow-down-circle"
    }
    
    return rx.hstack(
        rx.icon(icons[node_type], size=14, class_name=f"text-{color_scheme}-400"),
        rx.text(name, class_name="text-xs font-medium truncate"),
        spacing="2",
        class_name=f"px-3 py-2 rounded-lg border {classes} {TRANSITION_DEFAULT} hover:scale-[1.02] cursor-pointer max-w-full"
    )

# === MERMAID DIAGRAM ===
def mermaid_diagram(diagram_code: rx.Var[str]) -> rx.Component:
    """Render a Mermaid.js diagram"""
    return rx.box(
        rx.html(
            rx.Var.create(
                f'<pre class="mermaid">{diagram_code}</pre>'
            )
        ),
        class_name="w-full overflow-hidden rounded-lg bg-slate-900/50 p-2"
    )