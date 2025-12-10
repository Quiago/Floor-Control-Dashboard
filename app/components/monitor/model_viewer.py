# app/components/monitor/model_viewer.py
"""3D Model Viewer con Raycaster y Overlays"""
import reflex as rx
from app.states.monitor_state import MonitorState
from app.components.shared.design_tokens import GLASS_STRONG, TRANSITION_DEFAULT, SHADOW_LG, COLORS

def model_viewer_3d() -> rx.Component:
    """
    Componente 3D con:
    - Model viewer
    - Bridge input (JS ↔ Python)
    - Command input (Python → JS)
    - Overlays (context menu, properties)
    """
    return rx.box(
        # 1. BRIDGE: JS → Python (selección 3D)
        rx.el.input(
            id="bridge-input",
            class_name="hidden",
            on_change=MonitorState.handle_3d_selection
        ),
        
        # 2. COMMAND: Python → JS (alertas, isolate, restore)
        rx.el.input(
            id="command-input",
            class_name="hidden",
            read_only=True,
            value=MonitorState.js_command
        ),

        # 2.5 ALERT EQUIPMENT: Python → JS (equipment ID for visual alerts)
        rx.el.input(
            id="alert-equipment-input",
            class_name="hidden",
            read_only=True,
            value=MonitorState.alert_equipment_mirror,
            data_alert_equipment=MonitorState.alert_equipment_mirror
        ),

        # 3. MODELO 3D
        rx.html(f"""
            <model-viewer
                src="/pharmaceutical_manufacturing_machinery.glb"
                camera-orbit="45deg 55deg 2.5m" 
                camera-controls 
                autoplay 
                shadow-intensity="1"
                style="width: 100%; height: 100%; min-height: 500px; display: block; background: {COLORS["bg_primary"]};">
                <div slot="poster" style="color: white; text-align: center; padding-top: 50%;">
                    Loading 3D Model...
                </div>
            </model-viewer>
        """),
        
        # 4. CONTROLES HINT
        controls_hint(),
        
        # 5. ALERT INDICATOR (top-right)
        rx.cond(
            MonitorState.is_alert_active,
            rx.box(
                rx.icon("triangle-alert", size=20, class_name="text-white animate-pulse"),
                class_name=f"absolute top-4 right-4 p-3 rounded-full bg-rose-600 {SHADOW_LG} z-20"
            ),
            rx.fragment()
        ),
        
        class_name=f"relative w-full h-full rounded-xl overflow-hidden border {COLORS['border_default']} bg-[{COLORS['bg_primary']}]"
    )

def controls_hint() -> rx.Component:
    """Hint de controles (esquina superior izquierda)"""
    return rx.cond(
        ~MonitorState.is_expanded,
        rx.hstack(
            rx.hstack(
                rx.icon("mouse-pointer-2", size=14),
                rx.text("Rotate", class_name="text-[10px] font-medium"),
                spacing="1"
            ),
            rx.box(class_name="w-px h-3 bg-white/20"),
            rx.hstack(
                rx.icon("move", size=14),
                rx.text("Pan", class_name="text-[10px] font-medium"),
                spacing="1"
            ),
            spacing="3",
            class_name=f"{GLASS_STRONG} px-3 py-1.5 rounded-full absolute top-4 left-4 z-20 text-gray-300"
        ),
        rx.fragment()
    )