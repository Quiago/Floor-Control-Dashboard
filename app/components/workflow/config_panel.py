# app/components/workflow/config_panel.py
"""Node configuration panel"""
import reflex as rx
from app.states.workflow_state import WorkflowState
from app.components.shared.design_tokens import (
    GLASS_STRONG, GLASS_PANEL_PREMIUM, SHADOW_XL, GRADIENT_PRIMARY, 
    TRANSITION_DEFAULT, INPUT_FIELD
)
from app.components.shared import form_field, gradient_separator

def config_panel() -> rx.Component:
    """Panel flotante de configuración"""
    return rx.cond(
        WorkflowState.show_config_panel,
        rx.box(
            rx.vstack(
                # Header
                rx.hstack(
                    rx.vstack(
                        rx.text(
                            "Configure Node",
                            class_name="text-sm font-bold text-white"
                        ),
                        rx.text(
                            WorkflowState.selected_node_category,
                            class_name="text-xs text-gray-400 capitalize"
                        ),
                        spacing="0",
                        align_items="start"
                    ),
                    rx.spacer(),
                    rx.badge(
                        rx.cond(
                            WorkflowState.selected_node_is_configured,
                            "Configured",
                            "Not configured"
                        ),
                        color_scheme=rx.cond(
                            WorkflowState.selected_node_is_configured,
                            "green",
                            "gray"
                        ),
                        size="1"
                    ),
                    rx.button(
                        rx.icon("x", size=14),
                        variant="ghost",
                        size="1",
                        on_click=WorkflowState.close_config_panel
                    ),
                    width="100%",
                    align_items="start"
                ),
                
                gradient_separator(),
                
                # Form
                rx.cond(
                    WorkflowState.selected_node_is_action,
                    action_config_form(),
                    equipment_config_form()
                ),
                
                gradient_separator(),
                
                # Save Button
                rx.button(
                    rx.hstack(
                        rx.icon("check", size=16),
                        rx.text("Save Configuration"),
                        spacing="2"
                    ),
                    variant="solid",
                    class_name=f"{GRADIENT_PRIMARY} text-white w-full",
                    on_click=WorkflowState.save_node_config
                ),
                
                spacing="3",
                width="100%"
            ),
            class_name=f"absolute top-20 right-4 {GLASS_PANEL_PREMIUM} p-4 rounded-xl z-50 w-80 max-w-[90vw] {SHADOW_XL}"
        ),
        rx.fragment()
    )

def equipment_config_form() -> rx.Component:
    """Form para nodos de equipos"""
    return rx.vstack(
        # Equipment Selector
        form_field(
            "Target Equipment (3D Asset)",
            rx.select.root(
                rx.select.trigger(placeholder="Select machine...", class_name="w-full"),
                rx.select.content(
                    rx.foreach(
                        WorkflowState.available_equipment,
                        lambda eq: rx.select.item(eq["label"], value=eq["name"])
                    )
                ),
                value=WorkflowState.config_specific_equipment_id,
                on_change=WorkflowState.set_config_specific_equipment_id,
            )
        ),
        
        # Sensor
        form_field(
            "Sensor",
            rx.select.root(
                rx.select.trigger(placeholder="Select sensor...", class_name="w-full"),
                rx.select.content(
                    rx.foreach(
                        WorkflowState.selected_node_sensors,
                        lambda s: rx.select.item(
                            rx.hstack(
                                rx.text(s['name']),
                                rx.text(f"({s['unit']})", class_name="text-slate-400 text-xs"),
                                spacing="2"
                            ),
                            value=s['id']
                        )
                    )
                ),
                value=WorkflowState.config_sensor_type,
                on_change=WorkflowState.set_config_sensor_type,
            )
        ),
        
        # Operator + Threshold
        rx.hstack(
            form_field(
                "Condition",
                rx.select.root(
                    rx.select.trigger(class_name="w-full"),
                    rx.select.content(
                        rx.foreach(
                            WorkflowState.operator_options,
                            lambda op: rx.select.item(op['label'], value=op['value'])
                        )
                    ),
                    value=WorkflowState.config_operator,
                    on_change=WorkflowState.set_config_operator,
                ),
            ),
            form_field(
                "Threshold",
                rx.input(
                    type="number",
                    value=WorkflowState.config_threshold,
                    on_change=WorkflowState.set_config_threshold,
                    class_name=INPUT_FIELD
                )
            ),
            spacing="2",
            width="100%"
        ),
        
        # Severity
        form_field(
            "Alert Severity",
            rx.hstack(
                rx.foreach(
                    WorkflowState.severity_options,
                    lambda sev: rx.button(
                        sev['label'],
                        variant=rx.cond(
                            WorkflowState.config_severity == sev['value'],
                            "solid",
                            "outline"
                        ),
                        color_scheme=sev['color'],
                        size="1",
                        on_click=WorkflowState.set_config_severity(sev['value']),
                        class_name=TRANSITION_DEFAULT
                    )
                ),
                spacing="2"
            )
        ),
        
        spacing="4",
        width="100%"
    )

def action_config_form() -> rx.Component:
    """Form para nodos de acción"""
    return rx.vstack(
        rx.cond(
            WorkflowState.selected_node_category == "whatsapp",
            form_field(
                "Phone Number",
                rx.input(
                    placeholder="+1234567890",
                    value=WorkflowState.config_phone_number,
                    on_change=WorkflowState.set_config_phone_number,
                    class_name=INPUT_FIELD
                )
            ),
            rx.fragment()
        ),
        
        rx.cond(
            WorkflowState.selected_node_category == "email",
            form_field(
                "Email Address",
                rx.input(
                    placeholder="alert@company.com",
                    value=WorkflowState.config_email,
                    on_change=WorkflowState.set_config_email,
                    class_name=INPUT_FIELD
                )
            ),
            rx.fragment()
        ),
        
        rx.cond(
            WorkflowState.selected_node_category == "webhook",
            form_field(
                "Webhook URL",
                rx.input(
                    placeholder="https://api.example.com/webhook",
                    value=WorkflowState.config_webhook_url,
                    on_change=WorkflowState.set_config_webhook_url,
                    class_name=INPUT_FIELD
                )
            ),
            rx.fragment()
        ),
        
        form_field(
            "Alert Severity",
            rx.hstack(
                rx.foreach(
                    WorkflowState.severity_options,
                    lambda sev: rx.button(
                        sev['label'],
                        variant=rx.cond(
                            WorkflowState.config_severity == sev['value'],
                            "solid",
                            "outline"
                        ),
                        color_scheme=sev['color'],
                        size="1",
                        on_click=WorkflowState.set_config_severity(sev['value'])
                    )
                ),
                spacing="2"
            )
        ),
        
        spacing="4",
        width="100%"
    )