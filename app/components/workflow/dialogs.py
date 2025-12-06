# app/components/workflow/dialogs.py
"""Diálogos del workflow builder"""
import reflex as rx
from app.states.workflow_state import WorkflowState
from app.components.shared.design_tokens import GLASS_STRONG, SHADOW_XL 
from app.components.shared import gradient_separator, icon_button

def workflow_list_dialog() -> rx.Component:
    """Diálogo de workflows guardados"""
    return rx.cond(
        WorkflowState.show_workflow_list,
        rx.box(
            # Overlay
            rx.box(
                class_name="fixed inset-0 bg-black/50 z-40",
                on_click=WorkflowState.toggle_workflow_list
            ),
            
            # Dialog
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.text(
                            "Saved Workflows",
                            class_name="text-lg font-bold text-white"
                        ),
                        rx.spacer(),
                        icon_button(
                            "x",
                            WorkflowState.toggle_workflow_list,
                            size=16
                        ),
                        width="100%"
                    ),
                    
                    gradient_separator(),
                    
                    rx.cond(
                        WorkflowState.saved_workflows.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                WorkflowState.saved_workflows,
                                workflow_list_item
                            ),
                            spacing="2",
                            width="100%",
                            class_name="max-h-[500px] overflow-y-auto"
                        ),
                        rx.text(
                            "No saved workflows yet",
                            class_name="text-gray-500 text-sm py-8 text-center"
                        )
                    ),
                    
                    spacing="2",
                    width="100%"
                ),
                class_name=f"fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 {GLASS_STRONG} p-6 border border-white/10 rounded-xl z-50 w-[500px] {SHADOW_XL}"
            )
        ),
        rx.fragment()
    )

def workflow_list_item(workflow: rx.Var[dict]) -> rx.Component:
    """Item de workflow en la lista"""
    return rx.hstack(
        rx.vstack(
            rx.text(workflow['name'], class_name="text-sm font-medium text-white"),
            rx.hstack(
                rx.badge(workflow['status'], size="1"),
                rx.text(
                    workflow['updated_at'],
                    class_name="text-[10px] text-gray-500 font-mono"
                ),
                spacing="2"
            ),
            spacing="0",
            align_items="start"
        ),
        rx.spacer(),
        rx.hstack(
            icon_button(
                "folder-open",
                lambda: WorkflowState.load_workflow(workflow['id']),
                size=14,
                tooltip="Open"
            ),
            icon_button(
                "trash-2",
                lambda: WorkflowState.delete_workflow(workflow['id']),
                variant="danger",
                size=14,
                tooltip="Delete"
            ),
            spacing="1"
        ),
        class_name="w-full p-3 bg-gray-800/50 rounded-lg hover:bg-gray-800 transition-colors border border-white/5",
        width="100%"
    )

def test_results_dialog() -> rx.Component:
    """Diálogo de resultados de test"""
    return rx.cond(
        WorkflowState.test_mode,
        rx.box(
            # Overlay
            rx.box(
                class_name="fixed inset-0 bg-black/50 z-40",
                on_click=WorkflowState.close_test_mode
            ),
            
            # Dialog
            rx.box(
                rx.vstack(
                    rx.hstack(
                        rx.icon("flask-conical", size=20, class_name="text-amber-400"),
                        rx.text(
                            "Test Results",
                            class_name="text-lg font-bold text-white"
                        ),
                        rx.spacer(),
                        icon_button("x", WorkflowState.close_test_mode, size=16),
                        width="100%",
                        align_items="center"
                    ),
                    
                    gradient_separator(),
                    
                    rx.cond(
                        WorkflowState.test_results.length() > 0,
                        rx.vstack(
                            rx.foreach(
                                WorkflowState.test_results,
                                test_result_item
                            ),
                            spacing="2",
                            width="100%",
                            class_name="max-h-[400px] overflow-y-auto"
                        ),
                        rx.text(
                            "No triggers configured",
                            class_name="text-gray-500 text-sm py-4"
                        )
                    ),
                    
                    spacing="2",
                    width="100%"
                ),
                class_name=f"fixed top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 {GLASS_STRONG} p-6 border border-white/10 rounded-xl z-50 w-[500px] {SHADOW_XL}"
            )
        ),
        rx.fragment()
    )

def test_result_item(result: rx.Var[dict]) -> rx.Component:
    """Item de resultado de test"""
    return rx.hstack(
        rx.icon(
            rx.cond(result['would_trigger'], "alert-circle", "check-circle"),
            size=16,
            class_name=rx.cond(
                result['would_trigger'],
                "text-rose-400",
                "text-emerald-400"
            )
        ),
        rx.vstack(
            rx.text(result['trigger_node'], class_name="text-sm text-white"),
            rx.text(
                f"{result['sensor']}: {result['current_value']} {result['operator']} {result['threshold']}",
                class_name="text-xs text-gray-400 font-mono"
            ),
            spacing="0",
            align_items="start"
        ),
        rx.spacer(),
        rx.badge(
            rx.cond(result['would_trigger'], "Would trigger", "OK"),
            color_scheme=rx.cond(result['would_trigger'], "red", "green"),
            size="1"
        ),
        class_name="w-full p-2 bg-gray-800/50 rounded border border-white/5",
        width="100%"
    )