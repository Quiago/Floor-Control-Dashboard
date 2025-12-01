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
    
    # Nuevas variables para el Menú Avanzado
    menu_mode: str = "main"  # Puede ser 'main' (propiedades) o 'actions' (quick actions)
    is_expanded: bool = False # Controla si estamos en modo "Solo ver equipo"
    js_command: str = ""      # Canal de comandos hacia Javascript (isolate/restore)
    
    # Variables de Datos
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
        """Recibe la selección desde JS"""
        print(f"🐍 Selección recibida: '{object_name}'")

        if not object_name:
            # Si deseleccionan, reseteamos todo
            self.clear_selection()
            return
            
        self.selected_object_name = object_name
        self.menu_mode = "main" # Siempre abrir en menú principal
        
        # Datos simulados
        self.selected_object_props = {
            "temperature": round(random.uniform(45.0, 85.0), 1),
            "pressure": round(random.uniform(100.0, 250.0), 1),
            "status": random.choice(["Optimal", "Warning", "Critical"]),
            "last_maintenance": datetime.datetime.now().strftime("%Y-%m-%d")
        }

    @rx.event
    def clear_selection(self):
        """Limpia selección y restaura la vista 3D completa"""
        self.selected_object_name = None
        self.selected_object_props = None
        self.menu_mode = "main"
        self.is_expanded = False
        self.js_command = "restore" # Comanda a JS para mostrar todo de nuevo

    @rx.event
    def set_menu_mode(self, mode: str):
        """Cambia entre 'main' y 'actions'"""
        self.menu_mode = mode

    @rx.event
    def toggle_expand(self):
        """Activa/Desactiva el aislamiento del equipo en 3D"""
        self.is_expanded = not self.is_expanded
        if self.is_expanded:
            # Enviamos comando especial a JS: isolate:NombreObjeto
            self.js_command = f"isolate:{self.selected_object_name}"
            self._add_message(f"Isolating view for {self.selected_object_name}", role="system")
        else:
            self.js_command = "restore"
            self._add_message("Restoring full facility view", role="system")

    @rx.event
    def handle_quick_action(self, action: str):
        """Ejecuta acciones rápidas"""
        target = self.selected_object_name
        self._add_message(f"Executing '{action}' protocol on {target}...", role="system")
        
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
        self._add_message(f"Maintenance complete.", role="system")

    # --- Helpers ---
    
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