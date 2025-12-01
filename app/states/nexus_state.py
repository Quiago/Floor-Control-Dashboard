import reflex as rx
import asyncio
from typing import TypedDict, List, Optional
import datetime
import random

# --- Tipos de Datos Enriquecidos ---

class ChatMessage(TypedDict):
    role: str
    text: str
    time: str

class WorkflowStep(TypedDict):
    id: str
    title: str
    status: str
    time: str

# Nuevo: Estructura de Grafo de Conocimiento
class EquipmentProp(TypedDict):
    temperature: float
    pressure: float
    status: str
    last_maintenance: str
    # Datos de Ontología / Grafo
    rul_percentage: int      # Vida Útil Restante
    production_line: str     # A qué línea pertenece
    connected_sensors: List[str] # Lista de sensores IoT
    depends_on: List[str]    # Dependencias (Upstream)
    affects_to: List[str]    # Impacto (Downstream)
    product_context: str     # Qué producto está procesando

# --- Estado Principal ---

class NexusState(rx.State):
    active_tab: str = "monitor"
    is_alert_active: bool = False
    simulation_running: bool = False
    
    # 3D Interaction
    selected_object_name: Optional[str] = None
    selected_object_props: Optional[EquipmentProp] = None
    
    # Modes
    menu_mode: str = "main"
    is_expanded: bool = False
    js_command: str = ""
    
    # Data
    chat_input: str = ""
    chat_history: List[ChatMessage] = [
        {"role": "system", "text": "Nexus Ontology Online. Graph tracking enabled.", "time": "08:00:00"}
    ]
    workflow_steps: List[WorkflowStep] = [
        {"id": "1", "title": "Morning Calibration", "status": "completed", "time": "08:05:00"},
        {"id": "2", "title": "Conveyor Sync", "status": "active", "time": "08:15:00"},
    ]

    @rx.event
    def handle_3d_selection(self, object_name: str):
        """Genera datos ricos simulando una consulta al Grafo de Conocimiento"""
        if not object_name:
            self.clear_selection()
            return
            
        self.selected_object_name = object_name
        self.menu_mode = "main"
        
        # Simulamos datos complejos del grafo
        rul = random.randint(40, 98)
        
        self.selected_object_props = {
            "temperature": round(random.uniform(45.0, 85.0), 1),
            "pressure": round(random.uniform(100.0, 250.0), 1),
            "status": random.choice(["Optimal", "Warning", "Critical"]),
            "last_maintenance": datetime.datetime.now().strftime("%Y-%m-%d"),
            
            # Datos de Ontología
            "rul_percentage": rul,
            "production_line": f"Line-{random.choice(['Alpha', 'Beta', 'Gamma'])}",
            "connected_sensors": [f"Vib-Sens-{random.randint(100,999)}", "Therm-Coupler-A", "Flow-Meter-X"],
            "depends_on": [f"Feeder-{random.randint(1,5)}", "Power-Unit-Main"],
            "affects_to": [f"Packager-{random.randint(10,20)}", "Quality-Gate-B"],
            "product_context": random.choice(["Vaccine Batch #99", "Serum Vials 50ml", "Antibiotic Strips"])
        }

    @rx.event
    def clear_selection(self):
        self.selected_object_name = None
        self.selected_object_props = None
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
            self.selected_object_props["status"] = "Critical"
        elif action == "REPORT":
            self._add_workflow(f"Gen Report: {target}", "active")
        
    @rx.event
    async def execute_maintenance(self):
        if not self.selected_object_name: return
        self._add_message(f"Maintenance initiated on {self.selected_object_name}...", role="system")
        yield
        await asyncio.sleep(1.5)
        if self.selected_object_props:
            self.selected_object_props["status"] = "Optimal"
            self.selected_object_props["temperature"] = 45.0
            self.selected_object_props["rul_percentage"] = 100 # Reset RUL
        self._add_message(f"Maintenance complete.", role="system")

    # Helpers
    def set_tab(self, tab: str): self.active_tab = tab
    def set_chat_input(self, value: str): self.chat_input = value
    def _add_message(self, text: str, role: str = "system"):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_history.append({"role": role, "text": text, "time": now})
    def _add_workflow(self, title: str, status: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.workflow_steps.append({"id": str(len(self.workflow_steps)+1), "title": title, "status": status, "time": now})
    @rx.event
    def send_message(self):
        if not self.chat_input: return
        self._add_message(self.chat_input, role="user")
        self.chat_input = ""