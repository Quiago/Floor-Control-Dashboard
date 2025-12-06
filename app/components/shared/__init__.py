# app/components/shared/__init__.py
"""Componentes compartidos - Reutilizables en toda la app"""
import reflex as rx
from typing import Optional
from .design_tokens import GRADIENT_PRIMARY, TRANSITION_DEFAULT, SEPARATOR_GRADIENT

# === STATUS DOT ===
def status_dot(running: bool = False, color: str = "emerald") -> rx.Component:
    """Dot animado indicador de estado"""
    return rx.box(
        class_name=rx.cond(
            running,
            f"w-2 h-2 bg-{color}-500 rounded-full animate-pulse",
            "w-2 h-2 bg-gray-600 rounded-full"
        )
    )

# === STAT PILL ===
def stat_pill(label: str, value: rx.Var[str], color: str = "gray") -> rx.Component:
    """Pill compacto para estadísticas"""
    return rx.hstack(
        rx.text(label, class_name="text-[9px] text-gray-500 uppercase tracking-wider font-bold"),
        rx.text(value, class_name=f"text-xs font-mono text-{color}-400"),
        spacing="1",
        class_name="px-2 py-1 rounded-full bg-white/5 border border-white/10"
    )

# === SECTION LABEL ===
def section_label(text: str) -> rx.Component:
    """Label de sección con línea decorativa"""
    return rx.hstack(
        rx.box(class_name="h-px w-8 bg-gradient-to-r from-transparent to-white/20"),
        rx.text(
            text,
            class_name="text-[10px] text-gray-500 font-bold uppercase tracking-wider"
        ),
        rx.box(class_name="h-px flex-1 bg-gradient-to-r from-white/20 to-transparent"),
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
    """Botón de icono con variantes"""
    
    variants = {
        "ghost": "hover:bg-white/10 text-gray-400 hover:text-white",
        "danger": "hover:bg-rose-500/10 text-rose-400 hover:text-rose-300",
        "primary": f"{GRADIENT_PRIMARY} text-white hover:opacity-90"
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

# === FORM FIELD ===
def form_field(
    label: str,
    input_component: rx.Component,
    error: rx.Var[str] = "",
    helper: Optional[str] = None
) -> rx.Component:
    """Wrapper consistente para campos de formulario"""
    return rx.vstack(
        rx.text(
            label,
            class_name="text-xs text-gray-400 font-bold uppercase tracking-wider"
        ),
        input_component,
        rx.cond(
            error != "",
            rx.text(error, class_name="text-[10px] text-rose-400"),
            rx.cond(
                helper is not None,
                rx.text(helper, class_name="text-[10px] text-gray-600"),
                rx.fragment()
            )
        ),
        spacing="1",
        width="100%",
        align_items="start"
    )

# === CANVAS EMPTY STATE ===
def canvas_empty_state(
    icon: str = "layout-template",
    title: str = "Canvas vacío",
    description: str = "Arrastra elementos para empezar"
) -> rx.Component:
    """Estado vacío elegante con instrucciones"""
    return rx.center(
        rx.vstack(
            rx.box(
                rx.icon(icon, size=48, class_name="text-gray-700"),
                class_name="p-6 rounded-full bg-gradient-to-br from-white/5 to-white/[0.02]"
            ),
            rx.text(title, class_name="text-lg font-medium text-gray-300"),
            rx.text(description, class_name="text-sm text-gray-600"),
            spacing="4",
            align_items="center"
        ),
        class_name="w-full h-full min-h-[400px]"
    )

# === SEPARATOR WITH GRADIENT ===
def gradient_separator() -> rx.Component:
    """Separador con gradiente"""
    return rx.box(class_name=SEPARATOR_GRADIENT)