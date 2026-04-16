import os
from dotenv import load_dotenv

# Cargo el .env desde la misma carpeta del archivo para que funcione
# sin importar desde dónde se arranque el servidor.
# Si alguien corre esto sin .env (por ejemplo en CI), os.getenv
# devuelve el valor por defecto y no explota.
load_dotenv()

AGENCIA_API_KEY: str = os.getenv("AGENCIA_API_KEY", "agencia-key-dev")
EXTERNAL_API_URL: str = os.getenv(
    "EXTERNAL_API_URL", "https://api.adviceslip.com/advice"
)
