# app/states/workflow_state.py
"""
Workflow Builder State - ENHANCED VERSION with Configuration

Adds node configuration, save/load, and test execution while
preserving the working ReactFlow drag/drop logic.
"""
import reflex as rx
from typing import List, Dict, Any
import random
import uuid
from app.extractors.glb_parser import load_equipment_from_glb
from app.components.shared.design_tokens import COLORS


# Import services (lazy import to avoid circular deps)
def get_db():
    from app.services.database import db
    return db

def get_workflow_engine():
    from app.services.workflow_engine import workflow_engine
    return workflow_engine

def get_sensors_for_type(eq_type: str) -> List[Dict]:
    from app.extractors.glb_parser import get_sensors_for_type as get_sensors
    return get_sensors(eq_type)


class WorkflowState(rx.State):
    """Workflow builder state with full configuration support."""
    
    # ===========================================
    # REACTFLOW STATE (PRESERVED - DO NOT MODIFY)
    # ===========================================
    
    nodes: List[Dict[str, Any]] = []
    edges: List[Dict[str, Any]] = []
    
    # Drag and Drop State
    dragged_type: str = ""
    dragged_is_action: bool = False
    
    # UI State
    show_equipment_panel: bool = True
    selected_node_id: str = ""
    
    # Counter for unique IDs
    _node_counter: int = 0
    
    # ===========================================
    # NEW: WORKFLOW METADATA
    # ===========================================
    
    current_workflow_id: str = ""
    current_workflow_name: str = "New Workflow"
    current_workflow_status: str = "draft"  # draft, active, paused
    
    # Workflow list for Open dialog
    saved_workflows: List[Dict] = []
    show_workflow_list: bool = False

    # --- NUEVO: LISTA DE WORKFLOWS ACTIVOS (Para el Monitor) ---
    active_workflows_list: List[Dict] = []

    # ===========================================
    # NEW: NODE CONFIGURATION STATE
    # ===========================================
    
    # Currently selected node for configuration
    show_config_panel: bool = False
    selected_node_category: str = ""
    selected_node_is_action: bool = False
    
    # Config form values
    config_sensor_type: str = ""
    config_operator: str = ">"
    config_threshold: str = "50"
    config_threshold_max: str = "100"
    config_severity: str = "warning"
    
    # Action-specific config
    config_phone_number: str = ""
    config_email: str = ""
    config_webhook_url: str = ""
    config_message_template: str = ""
    
    # Alerts
    recent_alerts: List[Dict] = []
    
    # ===========================================
    # NEW: TEST MODE
    # ===========================================
    
    test_mode: bool = False
    test_results: List[Dict] = []
    show_save_dialog: bool = False
    
    # ===========================================
    # NEW: SIMULATION MODE
    # ===========================================
    
    simulation_running: bool = False
    simulation_speed: int = 2  # seconds between ticks
    simulation_tick_count: int = 0
    current_sensor_values: List[Dict] = []  # List of {key, value, threshold, equipment} dicts
    
    # Alert feed (live alerts during simulation)
    alert_feed: List[Dict] = []
    show_alert_feed: bool = True
    
    # Toast notification
    toast_message: str = ""
    toast_type: str = "info"  # info, success, warning, error
    show_toast: bool = False

    # ===========================================
    # NEW EQUIPMENT VARIABLES
    # ===========================================

    # Nueva variable para la lista de equipos reales del 3D
    available_equipment: List[Dict] = []
    
    # Variable para guardar el ID específico seleccionado en el nodo
    config_specific_equipment_id: str = ""

    latest_alert_equipment: str = ""
    
    # ===========================================
    # DEFINITIONS (Enhanced)
    # ===========================================
    
    
    @rx.var
    def category_definitions(self) -> List[Dict]:
        return [
            {'key': 'analyzer', 'name': 'Analyzers', 'icon': 'scan', 'type': 'equipment', 'color': 'purple'},
            {'key': 'robot', 'name': 'Robots', 'icon': 'box', 'type': 'equipment', 'color': 'blue'},
            {'key': 'centrifuge', 'name': 'Centrifuges', 'icon': 'circle-dot', 'type': 'equipment', 'color': 'cyan'},
            {'key': 'storage', 'name': 'Storage', 'icon': 'package', 'type': 'equipment', 'color': 'green'},
            {'key': 'conveyor', 'name': 'Conveyors', 'icon': 'arrow-right', 'type': 'equipment', 'color': 'yellow'},
            {'key': 'whatsapp', 'name': 'WhatsApp', 'icon': 'message-circle', 'type': 'action', 'color': 'green'},
            {'key': 'email', 'name': 'Email', 'icon': 'mail', 'type': 'action', 'color': 'blue'},
            {'key': 'alert', 'name': 'System Alert', 'icon': 'bell', 'type': 'action', 'color': 'red'},
            {'key': 'webhook', 'name': 'Webhook', 'icon': 'globe', 'type': 'action', 'color': 'gray'}
        ]
    
    @rx.var
    def equipment_categories(self) -> List[Dict]:
        return [c for c in self.category_definitions if c['type'] == 'equipment']
    
    @rx.var
    def action_categories(self) -> List[Dict]:
        return [c for c in self.category_definitions if c['type'] == 'action']
    
    @rx.var
    def operator_options(self) -> List[Dict]:
        return [
            {'value': '>', 'label': '> Greater than'},
            {'value': '<', 'label': '< Less than'},
            {'value': '>=', 'label': '>= Greater or equal'},
            {'value': '<=', 'label': '<= Less or equal'},
            {'value': '==', 'label': '== Equal to'},
            {'value': '!=', 'label': '!= Not equal'},
            {'value': 'between', 'label': 'Between (range)'},
        ]
    
    @rx.var
    def severity_options(self) -> List[Dict]:
        return [
            {'value': 'info', 'label': 'Info', 'color': 'blue'},
            {'value': 'warning', 'label': 'Warning', 'color': 'yellow'},
            {'value': 'critical', 'label': 'Critical', 'color': 'red'},
        ]
    
    @rx.var
    def selected_node_sensors(self) -> List[Dict]:
        """Get available sensors for the selected node's equipment type."""
        if not self.selected_node_id:
            return []
        
        node = next((n for n in self.nodes if n['id'] == self.selected_node_id), None)
        if not node:
            return []
        
        category = node.get('data', {}).get('category', '')
        return get_sensors_for_type(category)
    
    @rx.var
    def selected_node_is_configured(self) -> bool:
        """Check if selected node has configuration."""
        if not self.selected_node_id:
            return False
        node = next((n for n in self.nodes if n['id'] == self.selected_node_id), None)
        if not node:
            return False
        return node.get('data', {}).get('configured', False)
    
    # ===========================================
    # COMPUTED VARS
    # ===========================================
    
    @rx.var
    def is_dragging(self) -> bool:
        return self.dragged_type != ""
    
    @rx.var
    def node_count(self) -> int:
        return len(self.nodes)
    
    @rx.var
    def edge_count(self) -> int:
        return len(self.edges)
    
    # ===========================================
    # EVENTS
    # ===========================================
    
    @rx.event
    def load_equipment(self):
        """Se ejecuta al inicio. Carga TODO: Alertas, Equipos del 3D y Workflows activos."""
        self._load_recent_alerts()
        self.load_equipment_list()
        self._load_active_workflows()

    @rx.event
    def load_equipment_list(self):
        """Carga la lista real de equipos desde el GLB"""
        data = load_equipment_from_glb()
        self.available_equipment = data

    def _load_active_workflows(self):
        """Carga workflows activos para el monitor"""
        try:
            db = get_db()
            workflows = db.get_all_workflows(status="active")
            self.active_workflows_list = [
                {
                    'id': w['id'],
                    'title': w['name'],
                    'status': 'active',
                    'updated_at': w.get('updated_at', '')[:10]
                }
                for w in workflows
            ]
        except Exception as e:
            print(f"Error loading workflows: {e}")
            self.active_workflows_list = []

    @rx.event
    def prepare_workflow_for_equipment(self, equipment_name: str):
        """Crea un workflow nuevo para el equipo seleccionado desde el 3D."""
        self.new_workflow()
        self.current_workflow_name = f"Auto: {equipment_name}"

        # Generar nodo
        self._node_counter += 1
        node_id = f"node_{self._node_counter}"

        # Intentar adivinar la categoría por el nombre
        category = 'equipment'
        for cat in self.category_definitions:
            if cat['key'] in equipment_name.lower():
                category = cat['key']
                break

        new_node = {
            'id': node_id,
            'type': 'default',
            'position': {'x': 250, 'y': 200},
            'data': {
                'label': equipment_name,
                'category': category,
                'configured': True,
                'config': {'specific_equipment_id': equipment_name}
            },
            'style': {
                'background': '#1f2937',
                'color': 'white',
                'border': '2px solid #6b7280',
                'borderRadius': '8px',
                'padding': '10px',
                'minWidth': '150px',
                'textAlign': 'center'
            }
        }
        self.nodes.append(new_node)

        # Configurar UI para edición inmediata
        self.selected_node_id = node_id
        self.selected_node_category = category
        self.config_specific_equipment_id = equipment_name
        self.show_config_panel = True

    @rx.event
    def set_config_specific_equipment_id(self, value: str):
        self.config_specific_equipment_id = value
    
    # ===========================================
    # DRAG AND DROP (PRESERVED FROM WORKING VERSION)
    # ===========================================
    
    @rx.event
    def start_drag(self, item_key: str, is_action: bool):
        """Start dragging an item."""
        self.dragged_type = item_key
        self.dragged_is_action = is_action
    
    @rx.event
    def cancel_drag(self):
        """Cancel drag operation."""
        self.dragged_type = ""
        self.dragged_is_action = False
    
    @rx.event
    def handle_drop(self, x: int, y: int):
        """Handle drop on canvas - receives [clientX, clientY] from mouse up."""
        if not self.dragged_type:
            return
        
        # Reconstruct list for internal logic
        coords = [x, y]
        print(f"Drop coords: {coords}")
        client_x, client_y = coords
        
        canvas_el = rx.call_script(f"""
            (function() {{
                const canvas = document.getElementById('workflow-canvas');
                if (canvas) {{
                    const rect = canvas.getBoundingClientRect();
                    return [rect.left, rect.top];
                }}
                return [200, 80];
            }})()
        """)
        
        canvas_left = 200
        canvas_top = 80
        
        # Adjust calculations as needed based on your layout
        x_pos = client_x - canvas_left - 64
        y_pos = client_y - canvas_top - 64
        
        self._node_counter += 1
        node_id = f"node_{self._node_counter}"
        
        cat_info = next((c for c in self.category_definitions if c['key'] == self.dragged_type), None)
        label = f"{cat_info['name']}-{self._node_counter}" if cat_info else self.dragged_type
        color = cat_info['color'] if cat_info else 'gray'
        
        if self.dragged_is_action:
            bg_color = {
                'green': '#166534', 'blue': '#1e40af', 
                'red': '#991b1b', 'gray': '#374151'
            }.get(color, '#374151')
            border_color = {
                'green': '#22c55e', 'blue': '#3b82f6',
                'red': '#ef4444', 'gray': '#6b7280'
            }.get(color, '#6b7280')
        else:
            bg_color = {
                'purple': '#581c87', 'blue': '#1e3a8a',
                'cyan': '#164e63', 'green': '#14532d', 'yellow': '#713f12'
            }.get(color, '#1f2937')
            border_color = {
                'purple': '#a855f7', 'blue': '#3b82f6',
                'cyan': '#22d3ee', 'green': '#22c55e', 'yellow': '#eab308'
            }.get(color, '#6b7280')
        
        new_node = {
            'id': node_id,
            'type': 'default',
            'position': {'x': max(0, x_pos), 'y': max(0, y_pos)},
            'data': {
                'label': label,
                'category': self.dragged_type,
                'is_action': self.dragged_is_action,
                'configured': False,
                'config': {}
            },
            'style': {
                'background': bg_color,
                'color': 'white',
                'border': f'2px solid {border_color}',
                'borderRadius': '8px',
                'padding': '10px 15px',
                'fontSize': '12px',
                'fontWeight': '500',
                'minWidth': '120px',
                'textAlign': 'center',
                'cursor': 'pointer'
            },
            'sourcePosition': 'right',
            'targetPosition': 'left',
        }
        
        self.nodes = [*self.nodes, new_node]
        self.dragged_type = ""
        self.dragged_is_action = False
        
        self.selected_node_id = node_id
        self.selected_node_category = new_node['data']['category']
        self.selected_node_is_action = new_node['data']['is_action']
        self.show_config_panel = True
        self._reset_config_form()
    
    # ===========================================
    # REACTFLOW EVENT HANDLERS (PRESERVED)
    # ===========================================
    
    @rx.event
    def on_connect(self, connection: Dict):
        """Handle new edge connection."""
        if not connection:
            return
        
        source = connection.get('source', '')
        target = connection.get('target', '')
        
        if not source or not target:
            return
        
        existing = [e for e in self.edges if e.get('source') == source and e.get('target') == target]
        if existing:
            return
        
        new_edge = {
            'id': f"edge_{source}_{target}",
            'source': source,
            'target': target,
            'type': 'smoothstep',
            'animated': True,
            'style': {'stroke': '#3b82f6', 'strokeWidth': 2}
        }
        
        self.edges = [*self.edges, new_edge]
    
    @rx.event
    def on_nodes_change(self, changes: List[Dict]):
        """Handle node changes (position, selection, removal)."""
        if not changes:
            return
        
        nodes_dict = {n['id']: n for n in self.nodes}
        
        for change in changes:
            change_type = change.get('type', '')
            node_id = change.get('id', '')
            
            if change_type == 'position' and node_id in nodes_dict:
                pos = change.get('position')
                if pos and 'x' in pos and 'y' in pos:
                    nodes_dict[node_id] = {
                        **nodes_dict[node_id],
                        'position': {'x': pos['x'], 'y': pos['y']}
                    }
            
            elif change_type == 'select' and node_id in nodes_dict:
                if change.get('selected', False):
                    node = nodes_dict[node_id]
                    self.selected_node_id = node_id
                    self.selected_node_category = node.get('data', {}).get('category', '')
                    self.selected_node_is_action = node.get('data', {}).get('is_action', False)
                    self.show_config_panel = True
                    self._load_node_config(node)
            
            elif change_type == 'remove' and node_id in nodes_dict:
                del nodes_dict[node_id]
                self.edges = [e for e in self.edges if e.get('source') != node_id and e.get('target') != node_id]
                if self.selected_node_id == node_id:
                    self.selected_node_id = ""
                    self.show_config_panel = False
        
        self.nodes = list(nodes_dict.values())
    
    @rx.event
    def on_edges_change(self, changes: List[Dict]):
        """Handle edge changes."""
        if not changes:
            return
        
        edges_dict = {e['id']: e for e in self.edges}
        
        for change in changes:
            change_type = change.get('type', '')
            edge_id = change.get('id', '')
            
            if change_type == 'remove' and edge_id in edges_dict:
                del edges_dict[edge_id]
        
        self.edges = list(edges_dict.values())
    
    # ===========================================
    # NODE CONFIGURATION
    # ===========================================
    
    def _reset_config_form(self):
        """Reset configuration form to defaults."""
        self.config_sensor_type = ""
        self.config_operator = ">"
        self.config_threshold = "50"
        self.config_threshold_max = "100"
        self.config_severity = "warning"
        self.config_phone_number = ""
        self.config_email = ""
        self.config_webhook_url = ""
        self.config_message_template = ""
    
    def _load_node_config(self, node: Dict):
        """Load existing configuration into form."""
        config = node.get('data', {}).get('config', {})
        self.config_specific_equipment_id = config.get('specific_equipment_id', '')

        if not config:
            self._reset_config_form()
            return
        
        self.config_sensor_type = config.get('sensor_type', '')
        self.config_operator = config.get('operator', '>')
        self.config_threshold = str(config.get('threshold', 50))
        self.config_threshold_max = str(config.get('threshold_max', 100))
        self.config_severity = config.get('severity', 'warning')
        self.config_phone_number = config.get('phone_number', '')
        self.config_email = config.get('email', '')
        self.config_webhook_url = config.get('webhook_url', '')
        self.config_message_template = config.get('message_template', '')
    
    @rx.event
    def close_config_panel(self):
        """Close the configuration panel."""
        self.show_config_panel = False
        self.selected_node_id = ""
    
    @rx.event
    def set_config_sensor_type(self, value: str):
        self.config_sensor_type = value
    
    @rx.event
    def set_config_operator(self, value: str):
        self.config_operator = value
    
    @rx.event
    def set_config_threshold(self, value: str):
        self.config_threshold = value
    
    @rx.event
    def set_config_threshold_max(self, value: str):
        self.config_threshold_max = value
    
    @rx.event
    def set_config_severity(self, value: str):
        self.config_severity = value
    
    @rx.event
    def set_config_phone_number(self, value: str):
        self.config_phone_number = value
    
    @rx.event
    def set_config_email(self, value: str):
        self.config_email = value
    
    @rx.event
    def set_config_webhook_url(self, value: str):
        self.config_webhook_url = value
    
    @rx.event
    def set_config_message_template(self, value: str):
        self.config_message_template = value
    
    @rx.event
    def save_node_config(self):
        """Save configuration to the selected node."""
        if not self.selected_node_id:
            return
        
        if self.selected_node_is_action:
            config = {
                'severity': self.config_severity,
                'phone_number': self.config_phone_number,
                'email': self.config_email,
                'webhook_url': self.config_webhook_url,
                'message_template': self.config_message_template,
            }
        else:
            try:
                threshold = float(self.config_threshold)
            except ValueError:
                threshold = 50
            
            try:
                threshold_max = float(self.config_threshold_max)
            except ValueError:
                threshold_max = 100
            
            config = {
                'sensor_type': self.config_sensor_type,
                'operator': self.config_operator,
                'threshold': threshold,
                'threshold_max': threshold_max,
                'severity': self.config_severity,
                'specific_equipment_id': self.config_specific_equipment_id,
                'equipment_id': self.selected_node_id,
            }
        
        updated_nodes = []
        for node in self.nodes:
            if node['id'] == self.selected_node_id:
                updated_node = {
                    **node,
                    'data': {
                        **node.get('data', {}),
                        'configured': True,
                        'config': config
                    },
                    'style': {
                        **node.get('style', {}),
                        'boxShadow': '0 0 10px rgba(34, 197, 94, 0.5)'
                    }
                }
                updated_nodes.append(updated_node)
            else:
                updated_nodes.append(node)
        
        self.nodes = updated_nodes
        self._show_toast(f"Configuration saved for {self.selected_node_category}", "success")
    
    # ===========================================
    # WORKFLOW MANAGEMENT
    # ===========================================
    
    @rx.event
    def set_workflow_name(self, name: str):
        self.current_workflow_name = name
    
    @rx.event
    def new_workflow(self):
        """Create a new empty workflow."""
        self.nodes = []
        self.edges = []
        self.current_workflow_id = ""
        self.current_workflow_name = "New Workflow"
        self.current_workflow_status = "draft"
        self.selected_node_id = ""
        self.show_config_panel = False
        self._node_counter = 0
        self.simulation_running = False
        self.alert_feed = []
        self.current_sensor_values = []
    
    @rx.event
    def save_workflow(self):
        """Save the current workflow."""
        if not self.nodes:
            self._show_toast("Nothing to save - add nodes first", "warning")
            return
        
        # GENERAR ID SI ES NUEVO (CORREGIDO)
        if not self.current_workflow_id:
            self.current_workflow_id = str(uuid.uuid4())
            
        db = get_db()
        
        # USAR METODO CORRECTO save_workflow (CORREGIDO)
        try:
            db.save_workflow(
                workflow_id=self.current_workflow_id,
                name=self.current_workflow_name,
                description="", # No hay descripción en este estado
                nodes=self.nodes,
                edges=self.edges,
                status=self.current_workflow_status
            )
            self._show_toast(f"Workflow '{self.current_workflow_name}' saved!", "success")
            self._load_active_workflows()
        except Exception as e:
            print(f"Database error: {e}")
            self._show_toast("Failed to save workflow", "error")
    
    @rx.event
    def toggle_workflow_list(self):
        """Toggle workflow list dialog."""
        if not self.show_workflow_list:
            self._load_workflows()
        self.show_workflow_list = not self.show_workflow_list
    
    def _load_workflows(self):
        """Load saved workflows from database."""
        try:
            db = get_db()
            # USAR METODO CORRECTO get_all_workflows (CORREGIDO)
            workflows = db.get_all_workflows()
            
            self.saved_workflows = [
                {
                    'id': w['id'],
                    'name': w['name'],
                    'status': w['status'],
                    'updated_at': w.get('updated_at', '')[:16].replace('T', ' ')
                }
                for w in workflows
            ]
        except Exception as e:
            print(f"Error loading workflows: {e}")
            self.saved_workflows = []
    
    @rx.event
    def load_workflow(self, workflow_id: str):
        """Load a workflow by ID."""
        db = get_db()
        workflow = db.get_workflow(workflow_id)
        
        if workflow:
            self.nodes = workflow.get('nodes', [])
            self.edges = workflow.get('edges', [])
            self.current_workflow_id = workflow_id
            self.current_workflow_name = workflow.get('name', 'Loaded Workflow')
            self.current_workflow_status = workflow.get('status', 'draft')
            
            max_counter = 0
            for node in self.nodes:
                try:
                    num = int(node['id'].split('_')[1])
                    max_counter = max(max_counter, num)
                except (IndexError, ValueError):
                    pass
            self._node_counter = max_counter
            
            self.show_workflow_list = False
            self.simulation_running = False
            self.alert_feed = []
            self._show_toast(f"Loaded '{self.current_workflow_name}'", "success")
    
    @rx.event
    def delete_workflow(self, workflow_id: str):
        """Delete a workflow."""
        db = get_db()
        db.delete_workflow(workflow_id)
        
        if workflow_id == self.current_workflow_id:
            self.new_workflow()
        
        self._load_workflows()
        self._show_toast("Workflow deleted", "info")
    
    @rx.event
    def activate_workflow(self):
        """Activate the current workflow."""
        if not self.nodes:
            self._show_toast("Add nodes before activating", "warning")
            return
        
        self.current_workflow_status = "active"
        self.save_workflow()
        self._show_toast("Workflow activated! Click 'Start Simulation' to begin.", "success")
    
    @rx.event
    def pause_workflow(self):
        """Pause the current workflow."""
        self.current_workflow_status = "paused"
        self.simulation_running = False
        self.save_workflow()
        self._show_toast("Workflow paused", "info")
    
    @rx.event
    def clear_workflow(self):
        """Clear all nodes and edges."""
        self.nodes = []
        self.edges = []
        self.selected_node_id = ""
        self.show_config_panel = False
        self._node_counter = 0
        self.simulation_running = False
        self.alert_feed = []
        self.current_sensor_values = []
    
    # ===========================================
    # TEST MODE
    # ===========================================
    
    @rx.event
    def test_workflow_execution(self):
        """Test the workflow with simulated data."""
        if not self.nodes:
            self._show_toast("Add nodes to test", "warning")
            return
        
        results = []
        
        for node in self.nodes:
            if node.get('data', {}).get('is_action', False):
                continue
            
            config = node.get('data', {}).get('config', {})
            if not config:
                continue
            
            sensor_type = config.get('sensor_type', 'unknown')
            threshold = config.get('threshold', 50)
            operator = config.get('operator', '>')
            
            current_value = threshold * 0.9
            
            engine = get_workflow_engine()
            would_trigger = engine.evaluate_condition(current_value, operator, threshold)
            
            results.append({
                'trigger_node': node.get('data', {}).get('label', node['id']),
                'sensor': sensor_type,
                'current_value': round(current_value, 2),
                'operator': operator,
                'threshold': threshold,
                'would_trigger': would_trigger
            })
        
        self.test_results = results
        self.test_mode = True
    
    @rx.event
    def close_test_mode(self):
        """Close test mode dialog."""
        self.test_mode = False
    
    # ===========================================
    # EQUIPMENT LOADING (LEGACY - NOW HANDLED IN load_equipment)
    # ===========================================

    def _load_recent_alerts(self):
        """Load recent alerts from database."""
        try:
            db = get_db()
            alerts = db.get_recent_alerts(limit=10)
            self.recent_alerts = alerts
        except Exception as e:
            print(f"Error loading alerts: {e}")
    
    @rx.event
    def add_test_node(self):
        """Debug: Add a test node directly."""
        self._node_counter += 1
        test_node = {
            'id': f"test_{self._node_counter}",
            'type': 'default',
            'position': {'x': 100, 'y': 100},
            'data': {'label': f'Test Node {self._node_counter}'},
            'style': {
                'background': '#1e40af',
                'color': 'white',
                'border': '2px solid #3b82f6',
                'borderRadius': '8px',
                'padding': '10px',
            }
        }
        self.nodes = [*self.nodes, test_node]
        print(f"DEBUG: Added test node, total: {len(self.nodes)}")
    
    @rx.event
    def refresh_alerts(self):
        """Refresh the alerts list."""
        self._load_recent_alerts()
    
    # ===========================================
    # SIMULATION MODE HANDLERS
    # ===========================================
    
    @rx.event
    def toggle_alert_feed(self):
        """Toggle alert feed visibility."""
        self.show_alert_feed = not self.show_alert_feed
    
    @rx.event
    def clear_alert_feed(self):
        """Clear the alert feed."""
        self.alert_feed = []
    
    @rx.event
    def start_simulation(self):
        """Start the simulation."""
        if self.simulation_running:
            return
        
        # Check if workflow is ready
        has_configured_equipment = False
        has_connected_action = False
        
        for node in self.nodes:
            if not node.get('data', {}).get('is_action', False):
                if node.get('data', {}).get('configured', False):
                    has_configured_equipment = True
                    for edge in self.edges:
                        if edge.get('source') == node['id']:
                            has_connected_action = True
                            break
        
        if not has_configured_equipment:
            self._show_toast("Configure at least one equipment node first", "warning")
            return
        
        if not has_connected_action:
            self._show_toast("Connect equipment to an action node first", "warning")
            return
        
        if not self.current_workflow_id:
            self.save_workflow()
        
        self.simulation_tick_count = 0
        self.simulation_running = True
        self._show_toast(f"🚀 Simulation started! Updates every {self.simulation_speed}s", "success")
    
    @rx.event
    def stop_simulation(self):
        """Stop the simulation."""
        self.simulation_running = False
        self.current_sensor_values = []
        self._show_toast("Simulation stopped", "info")
    
    @rx.event
    async def simulation_tick(self):
        """Process one simulation tick - called by JavaScript interval."""
        if not self.simulation_running:
            return
        
        self.simulation_tick_count += 1
        tick = self.simulation_tick_count
        
        # Generate sensor data
        sensor_data_dict, sensor_data_list = self._generate_sensor_data(tick)
        self.current_sensor_values = sensor_data_list
        
        print(f"[Simulation] Tick {tick}: {len(sensor_data_list)} sensors")
        
        # Evaluate workflow and trigger actions
        await self._evaluate_and_trigger(sensor_data_dict, tick)
    
    def _generate_sensor_data(self, tick: int):
        """Generate simulated sensor data based on configured nodes."""
        import math
        
        data_dict = {}
        data_list = []
        
        for node in self.nodes:
            if node.get('data', {}).get('is_action', False):
                continue
            
            config = node.get('data', {}).get('config', {})
            if not config:
                continue
            
            equipment_id = config.get('equipment_id', node['id'])
            sensor_type = config.get('sensor_type', '')
            threshold = float(config.get('threshold', 50))
            
            if not sensor_type:
                continue
            
            sensor_key = f"{equipment_id}.{sensor_type}"
            
            # Generate value that oscillates around 80% of threshold
            base_value = threshold * 0.8
            noise = random.uniform(-threshold * 0.1, threshold * 0.1)
            oscillation = math.sin(tick * 0.3) * threshold * 0.15
            
            value = base_value + noise + oscillation
            
            # Every 8 ticks, create a spike that exceeds threshold
            if tick % 8 == 0:
                value = threshold * random.uniform(1.1, 1.3)
            
            value = round(value, 2)
            data_dict[sensor_key] = value
            
            data_list.append({
                'key': sensor_type,
                'value': value,
                'threshold': threshold,
                'equipment': node.get('data', {}).get('label', equipment_id)
            })
        
        return data_dict, data_list
    
    async def _evaluate_and_trigger(self, sensor_data: Dict[str, float], tick: int):
        """Evaluate workflow conditions and trigger actions if needed."""
        from app.services.workflow_engine import workflow_engine
        
        # Build adjacency map
        adjacency = {}
        for edge in self.edges:
            source = edge.get('source', '')
            target = edge.get('target', '')
            if source not in adjacency:
                adjacency[source] = []
            adjacency[source].append(target)
        
        nodes_map = {n['id']: n for n in self.nodes}
        
        for node in self.nodes:
            if node.get('data', {}).get('is_action', False):
                continue
            
            config = node.get('data', {}).get('config', {})
            if not config or not config.get('sensor_type'):
                continue
            
            equipment_id = config.get('equipment_id', node['id'])
            sensor_type = config.get('sensor_type')
            operator = config.get('operator', '>')
            threshold = float(config.get('threshold', 0))
            
            sensor_key = f"{equipment_id}.{sensor_type}"
            current_value = sensor_data.get(sensor_key)
            
            if current_value is None:
                continue
            
            triggered = workflow_engine.evaluate_condition(
                current_value, operator, threshold
            )
            
            if triggered:
                specific_id = node['data'].get('config', {}).get('specific_equipment_id')
                if specific_id:
                    self.latest_alert_equipment = specific_id
                    
                connected_ids = adjacency.get(node['id'], [])
                
                for action_id in connected_ids:
                    action_node = nodes_map.get(action_id)
                    if action_node:
                        await self._execute_action(
                            node, action_node, current_value, threshold, sensor_type
                        )
    
    async def _execute_action(self, trigger_node: Dict, action_node: Dict, 
                             value: float, threshold: float, sensor_type: str):
        """Execute an action node (send notification)."""
        from app.services.notification_service import notification_service, AlertTemplates
        from datetime import datetime
        
        action_config = action_node.get('data', {}).get('config', {})
        action_type = action_node.get('data', {}).get('category', '')
        equipment_name = trigger_node.get('data', {}).get('label', 'Equipment')
        severity = action_config.get('severity', 'warning')
        
        alert_content = AlertTemplates.threshold_alert(
            equipment_name=equipment_name,
            sensor=sensor_type,
            value=value,
            threshold=threshold,
            unit=action_config.get('unit', ''),
            severity=severity
        )
        
        result = None
        recipient = ""
        
        if action_type == 'whatsapp':
            recipient = action_config.get('phone_number', '')
            if recipient:
                result = await notification_service.send_whatsapp(
                    recipient, alert_content['text']
                )
                print(f"[WHATSAPP] Sent to {recipient}: {alert_content['subject']}")
        
        elif action_type == 'email':
            recipient = action_config.get('email', '')
            if recipient:
                result = await notification_service.send_email(
                    recipient,
                    alert_content['subject'],
                    alert_content['text'],
                    html_body=alert_content.get('html')
                )
                print(f"[EMAIL] Sent to {recipient}: {alert_content['subject']}")
        
        elif action_type == 'alert':
            recipient = 'system'
            result = type('Result', (), {'success': True, 'message_id': 'system'})()
            print(f"[SYSTEM ALERT] {alert_content['subject']}")
        
        elif action_type == 'webhook':
            recipient = action_config.get('webhook_url', '')
            if recipient:
                result = await notification_service.send_webhook(
                    recipient,
                    {
                        'equipment': equipment_name,
                        'sensor': sensor_type,
                        'value': value,
                        'threshold': threshold,
                        'severity': severity,
                        'timestamp': datetime.now().isoformat()
                    }
                )
                print(f"[WEBHOOK] Sent to {recipient}")
        
        alert_entry = {
            'id': f"alert_{datetime.now().timestamp()}",
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'equipment': equipment_name,
            'sensor': sensor_type,
            'value': value,
            'threshold': threshold,
            'action_type': action_type,
            'recipient': recipient,
            'severity': severity,
            'success': result.success if result else False
        }
        
        self.alert_feed = [alert_entry, *self.alert_feed[:19]]
        
        emoji = "🔴" if severity == "critical" else "🟡"
        self._show_toast(
            f"{emoji} ALERT: {equipment_name} {sensor_type}={value} (>{threshold})",
            "error" if severity == "critical" else "warning"
        )
        
        if self.current_workflow_id:
            try:
                get_db().log_alert(
                    workflow_id=self.current_workflow_id,
                    action_type=action_type,
                    recipient=recipient,
                    message=alert_content['text'],
                    status='sent' if (result and result.success) else 'failed'
                )
            except Exception as e:
                print(f"Error logging alert: {e}")
    
    @rx.event
    async def trigger_manual_alert(self):
        """Manually trigger an alert for testing."""
        if not self.nodes:
            self._show_toast("Add nodes to the workflow first", "warning")
            return
        
        trigger_node = None
        for node in self.nodes:
            if not node.get('data', {}).get('is_action', False):
                if node.get('data', {}).get('configured', False):
                    trigger_node = node
                    break
        
        if not trigger_node:
            self._show_toast("Configure at least one equipment node", "warning")
            return
        
        action_node = None
        for edge in self.edges:
            if edge.get('source') == trigger_node['id']:
                target_id = edge.get('target')
                action_node = next((n for n in self.nodes if n['id'] == target_id), None)
                break
        
        if not action_node:
            self._show_toast("Connect equipment to an action node", "warning")
            return
        
        config = trigger_node.get('data', {}).get('config', {})
        threshold = float(config.get('threshold', 50))
        sensor_type = config.get('sensor_type', 'sensor')
        
        test_value = round(threshold * 1.25, 2)
        
        self._show_toast("🧪 Triggering test alert...", "info")
        
        await self._execute_action(
            trigger_node, action_node, test_value, threshold, sensor_type
        )
    
    def _show_toast(self, message: str, toast_type: str = "info"):
        """Show a toast notification."""
        self.toast_message = message
        self.toast_type = toast_type
        self.show_toast = True
    
    @rx.event
    def hide_toast(self):
        """Hide the toast notification."""
        self.show_toast = False
    
    @rx.event
    def set_simulation_speed(self, speed: str):
        """Set simulation speed (seconds between ticks)."""
        try:
            self.simulation_speed = int(speed)
        except ValueError:
            pass

    # ===========================================
    # UI HELPERS
    # ===========================================
    
    @rx.event
    def toggle_equipment_panel(self):
        self.show_equipment_panel = not self.show_equipment_panel
    
    @rx.event
    def check_url_params(self):
        """Se ejecuta al montar la página del builder"""
        args = self.router.page.params
        target = args.get("target")
        if target:
            # Lógica para añadir automáticamente el nodo al canvas
            self.add_node_for_target(target)

    def add_node_for_target(self, target_name: str):
        # Crear nodo automáticamente en el centro
        new_node = {
            'id': f"node_auto_{self._node_counter}",
            'type': 'default',
            'data': {
                'label': target_name, 
                'category': 'equipment', # Tendrías que inferir el tipo basándote en el nombre
                'config': {'specific_equipment_id': target_name}
            },
            # ... estilos ...
        }
        self.nodes.append(new_node)