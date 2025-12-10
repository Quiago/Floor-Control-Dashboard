# app/components/monitor/model_viewer.py
"""3D Model Viewer con Raycaster y Overlays"""
import reflex as rx
from app.states.monitor_state import MonitorState
from app.components.shared.design_tokens import GLASS_STRONG, SHADOW_LG, COLORS

def model_viewer_3d() -> rx.Component:
    """
    Componente 3D con:
    - Model viewer
    - Bridge input (JS ↔ Python)
    - Command input (Python → JS)
    - Overlays (context menu, properties)

    NOTE: @rx.memo removed because it was causing React Hooks order violations
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

        # 2.5 ALERT EQUIPMENT: Non-reactive bridge via custom event
        # This element receives custom events from Python without triggering React re-renders
        rx.el.div(
            id="alert-equipment-bridge",
            style={"display": "none"}
        ),

        rx.script("""
            (function() {
                var bridge = document.getElementById('alert-equipment-bridge');
                if (!bridge) {
                    console.error('[Alert Bridge] Bridge element not found');
                    return;
                }

                var currentAlertEquipment = null;
                var blinkingInterval = null;

                // Listen for custom alert events
                bridge.addEventListener('nexusAlert', function(e) {
                    var equipmentId = e.detail;
                    console.log('[Nexus Alert Bridge] Alert received:', equipmentId);

                    // Update current alert equipment
                    currentAlertEquipment = equipmentId;

                    // Start blinking if not already blinking
                    if (!blinkingInterval) {
                        startBlinking();
                    }
                });

                // Listen for stop blinking event
                bridge.addEventListener('stopBlinking', function() {
                    console.log('[Nexus Alert Bridge] Stopping blinking');
                    if (blinkingInterval) {
                        clearInterval(blinkingInterval);
                        blinkingInterval = null;
                    }
                    currentAlertEquipment = null;
                });

                function startBlinking() {
                    // Trigger immediate flash
                    triggerFlash();

                    // Then blink every 3 seconds
                    blinkingInterval = setInterval(function() {
                        if (currentAlertEquipment) {
                            triggerFlash();
                        } else {
                            // Stop blinking if no equipment
                            clearInterval(blinkingInterval);
                            blinkingInterval = null;
                        }
                    }, 3000);
                }

                function triggerFlash() {
                    if (!currentAlertEquipment) return;

                    var commandInput = document.getElementById('command-input');
                    if (commandInput) {
                        var setter = Object.getOwnPropertyDescriptor(window.HTMLInputElement.prototype, "value").set;
                        setter.call(commandInput, 'alert:' + currentAlertEquipment);
                        commandInput.dispatchEvent(new Event('input', { bubbles: true }));
                    }
                }

                console.log('[Nexus Alert Bridge] Ready with continuous blinking support');
            })();
        """),

        # 3. MODELO 3D
        rx.html(f"""
            <model-viewer
                src="/pharmaceutical_manufacturing_machinery.glb"
                camera-orbit="45deg 55deg 2.5m" 
                camera-controls 
                autoplay 
                shadow-intensity="1"
                style="width: 100%; height: 100%; min-height: 200px; display: block; background: {COLORS["bg_primary"]};">
                <div slot="poster" style="color: white; text-align: center; padding-top: 50%;">
                    Loading 3D Model...
                </div>
            </model-viewer>
        """),
        
        # 4. CONTROLES HINT
        controls_hint(),
        
        # 5. ALERT INDICATOR (top-right, always rendered, hidden with CSS)
        rx.box(
            rx.icon("triangle-alert", size=20, class_name="text-white animate-pulse"),
            class_name=rx.cond(
                MonitorState.is_alert_active,
                f"absolute top-4 right-4 p-3 rounded-full bg-rose-600 {SHADOW_LG} z-20",
                f"absolute top-4 right-4 p-3 rounded-full bg-rose-600 {SHADOW_LG} z-20 hidden"
            )
        ),
        
        class_name=f"relative w-full h-full rounded-xl overflow-hidden border {COLORS['border_default']} bg-[{COLORS['bg_primary']}]"
    )

def controls_hint() -> rx.Component:
    """Hint de controles (esquina superior izquierda) - always rendered, hidden with CSS"""
    return rx.hstack(
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
        class_name=rx.cond(
            ~MonitorState.is_expanded,
            f"{GLASS_STRONG} px-3 py-1.5 rounded-full absolute top-4 left-4 z-20 text-gray-300",
            f"{GLASS_STRONG} px-3 py-1.5 rounded-full absolute top-4 left-4 z-20 text-gray-300 hidden"
        )
    )