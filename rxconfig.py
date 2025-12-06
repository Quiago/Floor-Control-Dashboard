import reflex as rx
from dotenv import load_dotenv # <--- Añadir

# Cargar variables ANTES de definir la config
load_dotenv()

config = rx.Config(app_name="app", plugins=[rx.plugins.TailwindV3Plugin()])
