# app/states/monitor_state.py
"""Estado para Monitor - Solo lógica de visualización 3D y chat"""
import reflex as rx
from typing import List
import random
import datetime

class MonitorState(rx.State):
    """Estado del Monitor (separado de WorkflowState)"""

    # === 3D SELECTION ===
    selected_object_name: str = ""

    # === UI MODES ===
    menu_mode: str = "main"  # main, actions
    is_expanded: bool = False
    is_alert_active: bool = False

    # === JS COMMANDS (Python → JavaScript) ===
    js_command: str = ""

    # === EQUIPMENT PROPERTIES ===
    equipment_temp: float = 0.0
    equipment_pressure: float = 0.0
    equipment_status: str = "Unknown"
    equipment_rul: int = 0
    equipment_line: str = ""
    equipment_sensors: List[str] = []
    equipment_depends_on: List[str] = []
    equipment_affects: List[str] = []
    equipment_product: str = ""
    
    # === CHAT ===
    chat_input: str = ""
    chat_history: List[dict] = []
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.chat_history = [
            {
                "role": "system",
                "text": "Nexus Ontology Online. Graph tracking enabled.",
                "time": "08:00:00"
            }
        ]
    
    # === EVENTS ===
    
    @rx.event
    def handle_3d_selection(self, object_name: str):
        """Handle selection from 3D model"""
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
        self.equipment_sensors = [
            f"Vib-Sens-{random.randint(100,999)}",
            "Therm-Coupler-A",
            "Flow-Meter-X"
        ]
        self.equipment_depends_on = [
            f"Feeder-{random.randint(1,5)}",
            "Power-Unit-Main"
        ]
        self.equipment_affects = [
            f"Packager-{random.randint(10,20)}",
            "Quality-Gate-B"
        ]
        self.equipment_product = random.choice([
            "Vaccine Batch #99",
            "Serum Vials 50ml",
            "Antibiotic Strips"
        ])
    
    @rx.event
    def clear_selection(self):
        """Clear selection"""
        self.selected_object_name = ""
        self.menu_mode = "main"
        self.is_expanded = False
        self.js_command = "restore"
    
    @rx.event
    def set_menu_mode(self, mode: str):
        """Switch menu mode"""
        self.menu_mode = mode
    
    @rx.event
    def toggle_expand(self):
        """Toggle focus mode"""
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            self.js_command = f"isolate:{self.selected_object_name}"
            self._add_message(
                f"Focused on {self.selected_object_name}. Retrieving full graph context...",
                role="system"
            )
        else:
            self.js_command = "restore"
    
    @rx.event
    def handle_quick_action(self, action: str):
        """Handle quick actions"""
        target = self.selected_object_name
        self._add_message(f"Executing '{action}' on {target}...", role="system")
        
        if action == "STOP":
            self.equipment_status = "Critical"
        elif action == "REPORT":
            self._add_message(f"Generating report for {target}...", role="system")
    
    @rx.event
    def create_workflow_for_selection(self):
        """Navigate to workflow builder for selected equipment"""
        from app.states.workflow_state import WorkflowState
        if not self.selected_object_name:
            return rx.window_alert("Select an object first")
        
        return [
            WorkflowState.prepare_workflow_for_equipment(self.selected_object_name),
            rx.redirect("/workflow-builder")
        ]
    
    # === CHAT ===
    
    @rx.event
    def set_chat_input(self, value: str):
        self.chat_input = value
    
    @rx.event
    def send_message(self):
        if not self.chat_input:
            return
        self._add_message(self.chat_input, role="user")
        self.chat_input = ""
    
    def _add_message(self, text: str, role: str = "system"):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_history = [
            *self.chat_history,
            {"role": role, "text": text, "time": now}
        ]