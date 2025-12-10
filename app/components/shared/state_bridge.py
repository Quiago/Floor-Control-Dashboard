"""State Bridge - JavaScript visibility controller bridge

This module provides helpers to communicate with the JavaScript visibility controller
without triggering React re-renders that cause Hooks order violations.
"""
import reflex as rx
from typing import Dict, Any


def state_bridge() -> rx.Component:
    """
    Invisible bridge element for JavaScript visibility controller.

    This component creates a hidden div that JavaScript can observe for state changes.
    Data attributes are updated via custom events from Python, and JavaScript
    handles DOM manipulation directly without React reconciliation.
    """
    return rx.fragment(
        # State bridge element (observed by JavaScript)
        rx.el.div(
            id="state-bridge",
            data_simulation_running="false",
            data_sensor_count="0",
            data_alert_count="0",
            data_alert_active="false",
            data_is_expanded="false",
            data_selected_equipment="",
            data_menu_mode="main",
            data_is_thinking="false",
            data_awaiting_approval="false",
            style={"display": "none"}
        ),

        # Load visibility controller script
        rx.script(src="/visibility_controller.js")
    )


def emit_state_change(change_type: str, value: Any) -> str:
    """
    Generate JavaScript to emit a state change event.

    Args:
        change_type: Type of state change (simulation, alert, knowledge-graph, context-menu, chat)
        value: The new value (can be dict, bool, str, etc.)

    Returns:
        JavaScript code string to emit the custom event

    Usage:
        yield rx.call_script(emit_state_change('simulation', {
            'running': True,
            'sensorCount': 5,
            'alertCount': 2
        }))
    """
    import json

    # Convert value to JSON-safe format
    if isinstance(value, dict):
        value_json = json.dumps(value)
    elif isinstance(value, bool):
        value_json = 'true' if value else 'false'
    elif isinstance(value, (int, float)):
        value_json = str(value)
    else:
        value_json = f'"{value}"'

    return f"""
        (function() {{
            var event = new CustomEvent('nexusStateChange', {{
                detail: {{
                    type: '{change_type}',
                    value: {value_json}
                }}
            }});
            window.dispatchEvent(event);
            console.log('[StateBridge] Emitted:', '{change_type}', {value_json});
        }})();
    """


def update_simulation_visibility(running: bool, sensor_count: int = 0, alert_count: int = 0) -> str:
    """Generate JS to update simulation visibility state."""
    return emit_state_change('simulation', {
        'running': running,
        'sensorCount': sensor_count,
        'alertCount': alert_count
    })


def update_alert_visibility(is_active: bool) -> str:
    """Generate JS to update alert indicator visibility."""
    return emit_state_change('alert', is_active)


def update_knowledge_graph_visibility(is_expanded: bool) -> str:
    """Generate JS to update knowledge graph panel visibility."""
    return emit_state_change('knowledge-graph', is_expanded)


def update_context_menu_visibility(equipment: str, mode: str = 'main') -> str:
    """Generate JS to update context menu visibility."""
    return emit_state_change('context-menu', {
        'equipment': equipment,
        'mode': mode
    })


def update_chat_panel_visibility(is_thinking: bool = False, awaiting_approval: bool = False) -> str:
    """Generate JS to update chat panel states visibility."""
    return emit_state_change('chat', {
        'thinking': is_thinking,
        'approval': awaiting_approval
    })
