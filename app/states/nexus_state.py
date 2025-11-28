import reflex as rx
import asyncio
from typing import TypedDict
import datetime


class ChatMessage(TypedDict):
    role: str
    text: str
    time: str


class WorkflowStep(TypedDict):
    id: str
    title: str
    status: str
    time: str


class NexusState(rx.State):
    active_tab: str = "monitor"
    is_alert_active: bool = False
    simulation_running: bool = False
    chat_history: list[ChatMessage] = [
        {
            "role": "system",
            "text": "Nexus AI initialized. Monitoring floor status...",
            "time": "08:00:00",
        }
    ]
    workflow_steps: list[WorkflowStep] = [
        {
            "id": "1",
            "title": "Morning Calibration",
            "status": "completed",
            "time": "08:05:00",
        },
        {"id": "2", "title": "Conveyor Sync", "status": "active", "time": "08:15:00"},
    ]
    chat_input: str = ""

    @rx.event
    def set_tab(self, tab: str):
        self.active_tab = tab

    @rx.event
    def set_chat_input(self, value: str):
        self.chat_input = value

    def _add_message(self, text: str, role: str = "system"):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        self.chat_history.append({"role": role, "text": text, "time": now})

    def _add_workflow(self, title: str, status: str):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        new_id = str(len(self.workflow_steps) + 1)
        self.workflow_steps.append(
            {"id": new_id, "title": title, "status": status, "time": now}
        )

    @rx.event(background=True)
    async def start_simulation(self):
        async with self:
            if self.simulation_running:
                return
            self.simulation_running = True
            self._add_message("Scanning production floor...", role="system")
        await asyncio.sleep(2)
        async with self:
            self.is_alert_active = True
            self._add_message("⚠️ Metal Shaving Detected on Conveyor B-3", role="system")
            self._add_workflow("Protocol 404: Auto-Stop", "active")
            self._add_message(
                "✅ Action executed: Line halted, cleaning sequence initiated",
                role="system",
            )
            self.simulation_running = False

    @rx.event
    def send_message(self):
        if not self.chat_input:
            return
        self._add_message(self.chat_input, role="user")
        self.chat_input = ""