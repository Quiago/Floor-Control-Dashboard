# app/components/shared/design_tokens.py
"""Design System - Paleta y utilidades visuales estilo n8n/21dev"""

# === PALETA DE COLORES ===
COLORS = {
    # Backgrounds
    "bg_primary": "#0a0a0f",
    "bg_surface": "#12121a",
    "bg_elevated": "#1a1a24",
    "bg_overlay": "rgba(10, 10, 15, 0.95)",
    
    # Borders
    "border_subtle": "rgba(255, 255, 255, 0.06)",
    "border_default": "rgba(255, 255, 255, 0.1)",
    "border_strong": "rgba(255, 255, 255, 0.15)",
    
    # Text
    "text_primary": "#e5e7eb",
    "text_secondary": "#9ca3af",
    "text_tertiary": "#6b7280",
    "text_muted": "#4b5563",
    
    # Accents
    "accent_emerald": "#10b981",
    "accent_cyan": "#06b6d4",
    "accent_amber": "#f59e0b",
    "accent_rose": "#f43f5e",
    "accent_violet": "#8b5cf6",
}

# === GLASSMORPHISM ===
GLASS_PANEL = (
    "backdrop-blur-xl bg-gradient-to-br from-white/5 to-white/[0.02] "
    "border border-white/10"
)

GLASS_STRONG = (
    "backdrop-blur-2xl bg-gradient-to-br from-white/8 to-white/[0.03] "
    "border border-white/12"
)

# === GRADIENTES ===
GRADIENT_PRIMARY = "bg-gradient-to-r from-emerald-600 to-cyan-600"
GRADIENT_WARNING = "bg-gradient-to-r from-amber-600 to-orange-600"
GRADIENT_DANGER = "bg-gradient-to-r from-rose-600 to-red-600"
GRADIENT_SURFACE = "bg-gradient-to-br from-white/5 to-transparent"

# === SHADOWS ===
SHADOW_SM = "shadow-sm shadow-black/20"
SHADOW_MD = "shadow-md shadow-black/30"
SHADOW_LG = "shadow-lg shadow-black/40"
SHADOW_XL = "shadow-xl shadow-black/50"

# === TRANSITIONS ===
TRANSITION_DEFAULT = "transition-all duration-200 ease-out"
TRANSITION_FAST = "transition-all duration-150 ease-out"
TRANSITION_SLOW = "transition-all duration-300 ease-out"

# === HOVER STATES ===
HOVER_LIFT = "hover:scale-[1.02] active:scale-[0.98]"
HOVER_GLOW = "hover:shadow-lg hover:shadow-emerald-500/20"
HOVER_BORDER = "hover:border-white/20"

# === SEPARADORES ===
SEPARATOR_GRADIENT = (
    "h-px w-full bg-gradient-to-r from-transparent "
    "via-white/10 to-transparent"
)

# === UTILIDADES ===
def get_status_color(status: str) -> str:
    """Retorna color según estado"""
    colors = {
        "active": COLORS["accent_emerald"],
        "warning": COLORS["accent_amber"],
        "critical": COLORS["accent_rose"],
        "info": COLORS["accent_cyan"],
        "paused": COLORS["text_tertiary"],
        "draft": COLORS["text_muted"],
    }
    return colors.get(status.lower(), COLORS["text_secondary"])

def get_severity_color(severity: str) -> str:
    """Retorna color según severidad"""
    colors = {
        "info": "blue",
        "warning": "yellow",
        "critical": "red",
    }
    return colors.get(severity.lower(), "gray")