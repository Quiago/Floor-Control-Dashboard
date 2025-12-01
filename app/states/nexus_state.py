import reflex as rx
import asyncio
from typing import TypedDict, List, Optional
import datetime
import random

# --- Definición de Tipos de Datos ---

class ChatMessage(TypedDict):
    role: str
    text: str
    time: str

class WorkflowStep(TypedDict):
    id: str
    title: str
    status: str
    time: str
    
class EquipmentProp(TypedDict):
    temperature: float
    pressure: float
    status: str
    last_maintenance: str

# --- Estado Principal ---

class NexusState(rx.State):
    # Variables de UI generales
    active_tab: str = "monitor"
    is_alert_active: bool = False
    simulation_running: bool = False
    
    # --- ESTADO DE INTERACCIÓN 3D ---
    selected_object_name: Optional[str] = None
    selected_object_props: Optional[EquipmentProp] = None
    
    # Variables de Datos (Chat y Workflows)
    chat_input: str = ""
    chat_history: List[ChatMessage] = [
        {"role": "system", "text": "Nexus AI Online. Waiting for input...", "time": "08:00:00"}
    ]
    workflow_steps: List[WorkflowStep] = [
        {"id": "1", "title": "Morning Calibration", "status": "completed", "time": "08:05:00"},
        {"id": "2", "title": "Conveyor Sync", "status": "active", "time": "08:15:00"},
    ]

    # --- EVENTOS (ACTIONS) ---

    @rx.event
    def handle_3d_selection(self, object_name: str):
        """
        Recibe el nombre del objeto desde el JS.
        """
        # DEBUG: Esto imprimirá en tu terminal de Python
        print(f"🐍 [PYTHON] Evento recibido desde JS. Objeto: '{object_name}'")

        if not object_name:
            self.selected_object_name = None
            self.selected_object_props = None
            return
            
        self.selected_object_name = object_name
        
        # Generamos datos aleatorios simulados
        self.selected_object_props = {
            "temperature": round(random.uniform(45.0, 85.0), 1),
            "pressure": round(random.uniform(100.0, 250.0), 1),
            "status": random.choice(["Optimal", "Warning", "Critical"]),
            "last_maintenance": datetime.datetime.now().strftime("%Y-%m-%d")
        }

    @rx.event
    def clear_selection(self):
        """Cierra el menú flotante"""
        self.selected_object_name = None
        self.selected_object_props = None

    @rx.event
    async def execute_maintenance(self):
        """Simula mantenimiento"""
        if not self.selected_object_name:
            return
        
        self._add_message(f"Initiating maintenance sequence on {self.selected_object_name}...", role="system")
        
        yield
        await asyncio.sleep(1.5)
        
        if self.selected_object_props:
            self.selected_object_props["status"] = "Optimal"
            self.selected_object_props["temperature"] = 45.0
            
        self._add_message(f"Maintenance complete. {self.selected_object_name} is stable.", role="system")

    # --- Helpers Standard ---
    
    def set_tab(self, tab: str):
        self.active_tab = tab

    def set_chat_input(self, value: str):
        self.chat_input = value

    def _add_message(self, text: str, role: str = "system"):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_history.append({"role": role, "text": text, "time": now})

    @rx.event
    def send_message(self):
        if not self.chat_input: return
        self._add_message(self.chat_input, role="user")
        self.chat_input = ""