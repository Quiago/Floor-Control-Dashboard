# app/app.py
"""
Nexus Monitor - Entry Point
Refactorizado con arquitectura modular
"""
import reflex as rx
from dotenv import load_dotenv
from app.pages.monitor import monitor_page
from app.pages.workflow_builder import workflow_builder_page

# Cargar variables de entorno
load_dotenv()

# Crear app
app = rx.App(
    theme=rx.theme(appearance="dark"),
    head_components=[
        # Model Viewer (3D)
        rx.el.script(
            src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.4.0/model-viewer.min.js",
            type="module"
        ),
        # Custom JS para raycaster
        rx.el.script(src="/interaction.js", type="module"),
    ],
)

# Rutas
app.add_page(monitor_page, route="/")
app.add_page(workflow_builder_page, route="/workflow-builder")