# app/components/shared/design_tokens.py
"""Design System - Industrial/Enterprise Color Palette"""

# === INDUSTRIAL COLOR PALETTE ===
COLORS = {
    # Backgrounds - Deep industrial slate
    "bg_primary": "#0f1419",
    "bg_surface": "#1a2332",
    "bg_elevated": "#243044",
    "bg_overlay": "rgba(15, 20, 25, 0.95)",
    "bg_input": "rgba(30, 41, 59, 0.9)",
    
    # Borders - Steel tones
    "border_subtle": "rgba(148, 163, 184, 0.1)",
    "border_default": "rgba(148, 163, 184, 0.2)",
    "border_strong": "rgba(148, 163, 184, 0.3)",
    "border_focus": "rgba(59, 130, 246, 0.5)",
    
    # Text - High contrast for readability
    "text_primary": "#f1f5f9",
    "text_secondary": "#cbd5e1",
    "text_tertiary": "#94a3b8",
    "text_muted": "#64748b",
    "text_input": "#ffffff",
    
    # Industrial Accents
    "accent_blue": "#3b82f6",        # Primary action
    "accent_steel": "#64748b",        # Neutral
    "accent_safety_orange": "#f97316", # Warning/Alert
    "accent_success": "#22c55e",       # Success/Active
    "accent_danger": "#ef4444",        # Critical/Stop
    "accent_info": "#0ea5e9",          # Information
    
    # Legacy compatibility
    "accent_emerald": "#22c55e",
    "accent_cyan": "#0ea5e9",
    "accent_amber": "#f97316",
    "accent_rose": "#ef4444",
    "accent_violet": "#8b5cf6",
}

# === PREMIUM GLASSMORPHISM ===
GLASS_PANEL = (
    "backdrop-blur-xl bg-gradient-to-br from-slate-800/70 to-slate-900/80 "
    "border border-slate-600/30"
)

GLASS_STRONG = (
    "backdrop-blur-2xl bg-gradient-to-br from-slate-800/80 to-slate-900/90 "
    "border border-slate-500/30 shadow-2xl shadow-black/40"
)

GLASS_PANEL_PREMIUM = (
    "backdrop-blur-2xl bg-gradient-to-br from-slate-800/85 to-slate-950/95 "
    "border border-slate-500/40 shadow-2xl shadow-black/50"
)

GLASS_CARD = (
    "backdrop-blur-xl bg-slate-800/60 border border-slate-600/40 "
    "shadow-lg shadow-black/20"
)

# === INPUT STYLES - HIGH CONTRAST ===
INPUT_BASE = (
    "bg-slate-800/90 border-slate-500/50 text-white placeholder-slate-400 "
    "focus:border-blue-500 focus:ring-1 focus:ring-blue-500/50 "
    "hover:border-slate-400/50 transition-colors"
)

INPUT_FIELD = f"w-full {INPUT_BASE}"

# === GRADIENTES ===
GRADIENT_PRIMARY = "bg-gradient-to-r from-blue-600 to-cyan-600"
GRADIENT_SUCCESS = "bg-gradient-to-r from-green-600 to-emerald-600"
GRADIENT_WARNING = "bg-gradient-to-r from-orange-500 to-amber-500"
GRADIENT_DANGER = "bg-gradient-to-r from-red-600 to-rose-600"
GRADIENT_SURFACE = "bg-gradient-to-br from-slate-700/30 to-transparent"

# === SHADOWS ===
SHADOW_SM = "shadow-sm shadow-black/30"
SHADOW_MD = "shadow-md shadow-black/40"
SHADOW_LG = "shadow-lg shadow-black/50"
SHADOW_XL = "shadow-xl shadow-black/60"
SHADOW_GLOW_BLUE = "shadow-lg shadow-blue-500/20"
SHADOW_GLOW_ORANGE = "shadow-lg shadow-orange-500/20"

# === TRANSITIONS ===
TRANSITION_DEFAULT = "transition-all duration-200 ease-out"
TRANSITION_FAST = "transition-all duration-150 ease-out"
TRANSITION_SLOW = "transition-all duration-300 ease-out"

# === HOVER STATES ===
HOVER_LIFT = "hover:scale-[1.02] active:scale-[0.98]"
HOVER_GLOW = "hover:shadow-lg hover:shadow-blue-500/20"
HOVER_BORDER = "hover:border-slate-400/50"

# === SEPARATORS ===
SEPARATOR_GRADIENT = (
    "h-px w-full bg-gradient-to-r from-transparent "
    "via-slate-500/30 to-transparent"
)

# === DEPENDENCY GRAPH COLORS ===
GRAPH_COLORS = {
    "upstream": "#f97316",      # Orange for dependencies
    "selected": "#3b82f6",      # Blue for current
    "downstream": "#22c55e",    # Green for affected
    "edge": "#64748b",          # Steel for connections
}

# === UTILITY FUNCTIONS ===
def get_status_color(status: str) -> str:
    """Returns color based on status"""
    colors = {
        "active": COLORS["accent_success"],
        "running": COLORS["accent_success"],
        "warning": COLORS["accent_safety_orange"],
        "critical": COLORS["accent_danger"],
        "error": COLORS["accent_danger"],
        "info": COLORS["accent_info"],
        "paused": COLORS["text_tertiary"],
        "draft": COLORS["text_muted"],
        "optimal": COLORS["accent_success"],
    }
    return colors.get(status.lower(), COLORS["text_secondary"])

def get_severity_color(severity: str) -> str:
    """Returns Radix color scheme based on severity"""
    colors = {
        "info": "blue",
        "warning": "orange",
        "critical": "red",
    }
    return colors.get(severity.lower(), "gray")

def get_status_badge_color(status: str) -> str:
    """Returns Radix color scheme for badges"""
    colors = {
        "active": "green",
        "running": "green",
        "optimal": "green",
        "warning": "orange",
        "critical": "red",
        "error": "red",
        "paused": "gray",
        "draft": "gray",
    }
    return colors.get(status.lower(), "gray")