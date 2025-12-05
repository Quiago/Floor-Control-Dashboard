import reflex as rx
import asyncio
from typing import List
import datetime
import random
from app.states.workflow_state import WorkflowState

class NexusState(rx.State):
    """Main application state"""
    
    is_alert_active: bool = False
    simulation_running: bool = False
    
    # 3D Interaction
    selected_object_name: str = ""
    
    # Modes
    menu_mode: str = "main"
    is_expanded: bool = False
    show_workflow_builder: bool = False
    js_command: str = ""
    
    # Equipment props
    equipment_temp: float = 0.0
    equipment_pressure: float = 0.0
    equipment_status: str = "Unknown"
    equipment_rul: int = 0
    equipment_line: str = ""
    equipment_sensors: List[str] = []
    equipment_depends_on: List[str] = []
    equipment_affects: List[str] = []
    equipment_product: str = ""
    
    # Data
    chat_input: str = ""
    chat_history: List[dict] = []
    workflow_steps: List[dict] = []
    
    # Workflow Builder
    workflow_nodes: List[dict] = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_history = [
            {"role": "system", "text": "Nexus Ontology Online. Graph tracking enabled.", "time": "08:00:00"}
        ]
        self.workflow_steps = [
            {"id": "1", "title": "Morning Calibration", "status": "completed", "time": "08:05:00"},
            {"id": "2", "title": "Conveyor Sync", "status": "active", "time": "08:15:00"},
        ]

    @rx.event
    def handle_3d_selection(self, object_name: str):
        """Handle selection from 3D"""
        if not object_name:
            self.clear_selection()
            return
            
        self.selected_object_name = object_name
        self.menu_mode = "main"
        
        # Simulate knowledge graph query
        rul = random.randint(40, 98)
        self.equipment_temp = round(random.uniform(45.0, 85.0), 1)
        self.equipment_pressure = round(random.uniform(100.0, 250.0), 1)
        self.equipment_status = random.choice(["Optimal", "Warning", "Critical"])
        self.equipment_rul = rul
        self.equipment_line = f"Line-{random.choice(['Alpha', 'Beta', 'Gamma'])}"
        self.equipment_sensors = [f"Vib-Sens-{random.randint(100,999)}", "Therm-Coupler-A", "Flow-Meter-X"]
        self.equipment_depends_on = [f"Feeder-{random.randint(1,5)}", "Power-Unit-Main"]
        self.equipment_affects = [f"Packager-{random.randint(10,20)}", "Quality-Gate-B"]
        self.equipment_product = random.choice(["Vaccine Batch #99", "Serum Vials 50ml", "Antibiotic Strips"])

    @rx.event
    def clear_selection(self):
        self.selected_object_name = ""
        self.menu_mode = "main"
        self.is_expanded = False
        self.js_command = "restore"

    @rx.event
    def set_menu_mode(self, mode: str):
        self.menu_mode = mode

    @rx.event
    def toggle_expand(self):
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.js_command = f"isolate:{self.selected_object_name}"
            self._add_message(f"Focused on {self.selected_object_name}. Retrieving full graph context...", role="system")
        else:
            self.js_command = "restore"

    @rx.event
    def handle_quick_action(self, action: str):
        target = self.selected_object_name
        self._add_message(f"Executing '{action}' on {target}...", role="system")
        if action == "STOP":
            self.equipment_status = "Critical"
        elif action == "REPORT":
            self._add_workflow(f"Gen Report: {target}", "active")
        
    @rx.event
    async def execute_maintenance(self):
        if not self.selected_object_name: return
        self._add_message(f"Maintenance initiated on {self.selected_object_name}...", role="system")
        yield
        await asyncio.sleep(1.5)
        self.equipment_status = "Optimal"
        self.equipment_temp = 45.0
        self.equipment_rul = 100
        self._add_message(f"Maintenance complete.", role="system")

    # Helpers
    @rx.event
    def toggle_workflow_builder(self):
        self.show_workflow_builder = not self.show_workflow_builder
        
    @rx.event
    def set_chat_input(self, value: str):
        self.chat_input = value
        
    def _add_message(self, text: str, role: str = "system"):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_history = [*self.chat_history, {"role": role, "text": text, "time": now}]
        
    def _add_workflow(self, title: str, status: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.workflow_steps = [*self.workflow_steps, {"id": str(len(self.workflow_steps)+1), "title": title, "status": status, "time": now}]
        
    @rx.event
    def send_message(self):
        if not self.chat_input: return
        self._add_message(self.chat_input, role="user")
        self.chat_input = ""
        
    # Workflow Builder
    @rx.event
    def add_workflow_node(self, node_type: str):
        node_id = f"node_{len(self.workflow_nodes) + 1}"
        self.workflow_nodes = [*self.workflow_nodes, {
            "id": node_id,
            "type": node_type,
            "label": f"{node_type.title()} {len(self.workflow_nodes) + 1}"
        }]
        
    @rx.event
    def clear_workflow_canvas(self):
        self.workflow_nodes = []

    # --- ERROR FIX: Call the correct method in WorkflowState ---
    @rx.event
    def create_workflow_for_selection(self):
        """Acción rápida: Crear workflow para el objeto seleccionado"""
        if not self.selected_object_name:
            return rx.toast.warning("Select an object first")

        # Esta función ahora existe en WorkflowState
        return [
            WorkflowState.prepare_workflow_for_equipment(self.selected_object_name),
            rx.redirect("/workflow-builder")
        ]