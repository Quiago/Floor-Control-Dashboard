# app/workflow_builder.py
import reflex as rx
from app.reactflow import react_flow, background, controls, minimap
from app.states.workflow_state import WorkflowState


def workflow_header() -> rx.Component:
    return rx.hstack(
        rx.hstack(
            rx.icon("workflow", size=24, class_name="text-blue-400"),
            rx.heading("Workflow Builder", size="6", class_name="text-white"),
            spacing="3"
        ),
        rx.spacer(),
        rx.hstack(
            rx.button(
                rx.hstack(rx.icon("home", size=16), rx.text("Monitor"), spacing="2"),
                variant="ghost",
                on_click=rx.redirect("/")
            ),
            rx.button(
                rx.hstack(rx.icon("save", size=16), rx.text("Save"), spacing="2"),
                variant="solid",
                color_scheme="blue"
            ),
            spacing="2"
        ),
        class_name="w-full p-4 border-b border-gray-800 bg-gray-900"
    )

# Paste this BEFORE category_button
def get_icon(icon_name: rx.Var[str]) -> rx.Component:
    return rx.match(
        icon_name,
        ("scan", rx.icon("scan", size=18)),
        ("box", rx.icon("box", size=18)),
        ("circle-dot", rx.icon("circle-dot", size=18)),
        ("package", rx.icon("package", size=18)),
        ("arrow-right", rx.icon("arrow-right", size=18)),
        ("circle", rx.icon("circle", size=18)),
        ("zap", rx.icon("zap", size=18)),
        ("message-circle", rx.icon("message-circle", size=18)),
        ("mail", rx.icon("mail", size=18)),
        ("bell", rx.icon("bell", size=18)),
        # Fallback
        rx.icon("circle-help", size=18)
    )

def category_button(category: rx.Var) -> rx.Component:
    # 1. Cast to dict so we can access keys
    category = category.to(dict)
    
    return rx.button(
        rx.hstack(
            # 2. Use the helper function instead of rx.icon
            get_icon(category['icon']),
            rx.text(category['name'], size="2"),
            spacing="2"
        ),
        variant="outline",
        class_name="w-full border-gray-700 hover:bg-blue-900/20 hover:border-blue-500 justify-start",
        # 3. Access keys safely
        on_click=lambda: WorkflowState.add_category_node(
            category['key'], 
            category['type'] == 'action'
        )
    )


def equipment_panel() -> rx.Component:
    return rx.cond(
        WorkflowState.show_equipment_panel,
        rx.vstack(
            rx.hstack(
                rx.text("TOOLBOX", class_name="text-xs font-bold text-gray-400 uppercase"),
                rx.spacer(),
                rx.button(
                    rx.icon("x", size=14),
                    variant="ghost",
                    size="1",
                    on_click=WorkflowState.toggle_equipment_panel
                ),
                width="100%"
            ),
            
            rx.box(
                rx.vstack(
                    rx.text("EQUIPMENT", class_name="text-[10px] text-gray-500 font-bold uppercase mb-2"),
                    rx.foreach(
                        WorkflowState.equipment_categories,
                        category_button
                    ),
                    
                    rx.separator(class_name="my-4 bg-gray-700"),
                    
                    rx.text("ACTIONS", class_name="text-[10px] text-gray-500 font-bold uppercase mb-2"),
                    rx.foreach(
                        WorkflowState.action_categories,
                        category_button
                    ),
                    
                    spacing="2",
                    width="100%"
                ),
                class_name="flex-1 overflow-y-auto",
                height="calc(100vh - 180px)"
            ),
            
            rx.vstack(
                rx.separator(class_name="bg-gray-700"),
                rx.button(
                    rx.hstack(rx.icon("trash-2", size=14), rx.text("Clear"), spacing="2"),
                    variant="ghost",
                    class_name="w-full text-red-400 hover:bg-red-900/20",
                    on_click=WorkflowState.clear_workflow
                ),
                spacing="2",
                width="100%"
            ),
            
            class_name="w-64 h-full bg-gray-900 border-r border-gray-800 flex flex-col p-4",
            spacing="0"
        ),
        rx.button(
            rx.icon("panel-left", size=16),
            variant="ghost",
            class_name="absolute top-20 left-4 z-50 bg-gray-900 border border-gray-700 hover:bg-gray-800",
            on_click=WorkflowState.toggle_equipment_panel
        )
    )


def config_menu() -> rx.Component:
    return rx.cond(
        WorkflowState.selected_node_id != "",
        rx.cond(
            WorkflowState.selected_node,
            rx.vstack(
                rx.hstack(
                    rx.text("Configure Node", class_name="font-bold text-white"),
                    rx.spacer(),
                    rx.button(
                        rx.icon("x", size=14),
                        variant="ghost",
                        size="1",
                        on_click=WorkflowState.close_config_menu
                    ),
                    width="100%"
                ),
                rx.separator(class_name="bg-gray-700"),
                
                rx.cond(
                    # FIX 1: Add .to(dict) before accessing ['is_action']
                    ~WorkflowState.selected_node['data'].to(dict)['is_action'],
                    rx.vstack(
                        rx.text("SELECT EQUIPMENT", class_name="text-[10px] text-gray-500 font-bold uppercase"),
                        rx.foreach(
                            WorkflowState.equipment_for_selected_category.to(list),
                            lambda eq: rx.button(
                                rx.text(eq.to(dict)['label'], size="2"),
                                variant="soft",
                                class_name="w-full justify-start",
                                on_click=lambda: WorkflowState.configure_equipment_node(
                                    WorkflowState.selected_node_id,
                                    eq.to(dict)['id']
                                )
                            )
                        ),
                        
                        rx.cond(
                            # FIX 2: Add .to(dict) before accessing ['configured']
                            WorkflowState.selected_node['data'].to(dict)['configured'],
                            rx.vstack(
                                rx.separator(class_name="bg-gray-700 my-2"),
                                rx.text("SENSORS", class_name="text-[10px] text-gray-500 font-bold uppercase"),
                                rx.foreach(
                                    # FIX 3: Add .to(dict) before accessing ['sensors']
                                    WorkflowState.selected_node['data'].to(dict)['sensors'].to(list),
                                    lambda sensor: rx.vstack(
                                        rx.text(sensor.to(dict)['name'], size="1", class_name="font-semibold"),
                                        rx.hstack(
                                            rx.input(
                                                placeholder=f"Min {sensor.to(dict)['unit']}",
                                                type="number",
                                                size="1",
                                                class_name="w-20"
                                            ),
                                            rx.input(
                                                placeholder=f"Max {sensor.to(dict)['unit']}",
                                                type="number",
                                                size="1",
                                                class_name="w-20"
                                            ),
                                            spacing="1"
                                        ),
                                        class_name="bg-gray-800/50 p-2 rounded w-full",
                                        spacing="1"
                                    )
                                ),
                                spacing="2",
                                width="100%"
                            ),
                            rx.fragment()
                        ),
                        
                        spacing="2",
                        width="100%"
                    ),
                    
                    rx.vstack(
                        rx.text("ACTION CONFIG", class_name="text-[10px] text-gray-500 font-bold uppercase"),
                        
                        rx.cond(
                            # FIX 4: Add .to(dict) before accessing ['category']
                            WorkflowState.selected_node['data'].to(dict)['category'] == 'whatsapp',
                            rx.vstack(
                                rx.text("Phone Number", size="1"),
                                rx.input(placeholder="+1234567890", class_name="w-full"),
                                rx.text("Message", size="1", class_name="mt-2"),
                                rx.text_area(placeholder="Alert message...", class_name="w-full"),
                                spacing="1",
                                width="100%"
                            ),
                            rx.fragment()
                        ),
                        
                        rx.cond(
                            # FIX 5: Add .to(dict) before accessing ['category']
                            WorkflowState.selected_node['data'].to(dict)['category'] == 'email',
                            rx.vstack(
                                rx.text("To Email", size="1"),
                                rx.input(placeholder="user@example.com", class_name="w-full"),
                                rx.text("Subject", size="1", class_name="mt-2"),
                                rx.input(placeholder="Alert Subject", class_name="w-full"),
                                rx.text("Body", size="1", class_name="mt-2"),
                                rx.text_area(placeholder="Email content...", class_name="w-full"),
                                spacing="1",
                                width="100%"
                            ),
                            rx.fragment()
                        ),
                        
                        rx.cond(
                            # FIX 6: Add .to(dict) before accessing ['category']
                            WorkflowState.selected_node['data'].to(dict)['category'] == 'alert',
                            rx.vstack(
                                rx.text("Alert Message", size="1"),
                                rx.text_area(placeholder="System alert...", class_name="w-full"),
                                rx.text("Priority", size="1", class_name="mt-2"),
                                rx.select(
                                    ["Low", "Medium", "High", "Critical"],
                                    default_value="Medium"
                                ),
                                spacing="1",
                                width="100%"
                            ),
                            rx.fragment()
                        ),
                        
                        rx.button(
                            "Save Configuration",
                            class_name="w-full mt-4",
                            color_scheme="blue"
                        ),
                        
                        spacing="2",
                        width="100%"
                    )
                ),
                
                class_name="absolute top-20 right-4 w-80 bg-gray-900/95 backdrop-blur-md p-4 rounded-xl border border-gray-600 shadow-2xl z-50 max-h-[80vh] overflow-y-auto",
                spacing="2"
            ),
            rx.fragment()
        ),
        rx.fragment()
    )


def workflow_canvas() -> rx.Component:
    return rx.box(
        react_flow(
            background(color="#374151", gap=16, size=1, variant="dots"),
            controls(),
            minimap(
                node_color="#4b5563",
                mask_color="#1f2937",
                class_name="!bg-gray-900 !border !border-gray-700"
            ),
            nodes_draggable=True,
            nodes_connectable=True,
            on_connect=WorkflowState.on_connect,
            on_nodes_change=WorkflowState.on_nodes_change,
            on_edges_change=WorkflowState.on_edges_change,
            nodes=WorkflowState.nodes,
            edges=WorkflowState.edges,
            fit_view=True,
            class_name="bg-gray-950"
        ),
        config_menu(),
        class_name="flex-1 h-full relative"
    )


def workflow_builder() -> rx.Component:
    return rx.vstack(
        workflow_header(),
        rx.hstack(
            equipment_panel(),
            workflow_canvas(),
            spacing="0",
            class_name="flex-1 w-full h-full relative"
        ),
        spacing="0",
        class_name="h-screen w-full bg-black",
        on_mount=WorkflowState.load_equipment
    )