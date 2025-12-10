// src/utils/designTokens.js
// Industrial Color Palette and Design System

export const COLORS = {
    // Backgrounds - Deep industrial slate
    bg_primary: '#0f1419',
    bg_surface: '#1a2332',
    bg_elevated: '#243044',
    bg_overlay: 'rgba(15, 20, 25, 0.95)',
    bg_input: 'rgba(30, 41, 59, 0.9)',

    // Borders - Steel tones
    border_subtle: 'rgba(148, 163, 184, 0.1)',
    border_default: 'rgba(148, 163, 184, 0.2)',
    border_strong: 'rgba(148, 163, 184, 0.3)',
    border_focus: 'rgba(59, 130, 246, 0.5)',

    // Text - High contrast for readability
    text_primary: '#f1f5f9',
    text_secondary: '#cbd5e1',
    text_tertiary: '#94a3b8',
    text_muted: '#64748b',
    text_input: '#ffffff',

    // Industrial Accents
    accent_blue: '#3b82f6',
    accent_steel: '#64748b',
    accent_safety_orange: '#f97316',
    accent_success: '#22c55e',
    accent_danger: '#ef4444',
    accent_info: '#0ea5e9',

    // Legacy compatibility
    accent_emerald: '#22c55e',
    accent_cyan: '#0ea5e9',
    accent_amber: '#f97316',
    accent_rose: '#ef4444',
    accent_violet: '#8b5cf6',
};

export const GRAPH_COLORS = {
    upstream: '#f97316',
    selected: '#3b82f6',
    downstream: '#22c55e',
    edge: '#64748b',
};

export function getStatusColor(status) {
    const colors = {
        active: COLORS.accent_success,
        running: COLORS.accent_success,
        warning: COLORS.accent_safety_orange,
        critical: COLORS.accent_danger,
        error: COLORS.accent_danger,
        info: COLORS.accent_info,
        paused: COLORS.text_tertiary,
        draft: COLORS.text_muted,
        optimal: COLORS.accent_success,
    };
    return colors[status?.toLowerCase()] || COLORS.text_secondary;
}

export function getSeverityColor(severity) {
    const colors = {
        info: 'blue',
        warning: 'orange',
        critical: 'red',
    };
    return colors[severity?.toLowerCase()] || 'gray';
}

export function getStatusBadgeClass(status) {
    const classes = {
        active: 'bg-green-500/20 text-green-400 border-green-500/30',
        running: 'bg-green-500/20 text-green-400 border-green-500/30',
        optimal: 'bg-green-500/20 text-green-400 border-green-500/30',
        warning: 'bg-orange-500/20 text-orange-400 border-orange-500/30',
        critical: 'bg-red-500/20 text-red-400 border-red-500/30',
        error: 'bg-red-500/20 text-red-400 border-red-500/30',
        paused: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
        draft: 'bg-gray-500/20 text-gray-400 border-gray-500/30',
    };
    return classes[status?.toLowerCase()] || 'bg-gray-500/20 text-gray-400 border-gray-500/30';
}
