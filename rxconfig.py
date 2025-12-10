import reflex as rx
from dotenv import load_dotenv

# Cargar variables ANTES de definir la config
load_dotenv()

config = rx.Config(
    app_name="app",
    plugins=[rx.plugins.TailwindV3Plugin()],
    # Disable strict mode to prevent double renders during simulation
    react_strict_mode=False,
    # TEMPORARY: Set loglevel to reduce noise
    loglevel="warning",
)
