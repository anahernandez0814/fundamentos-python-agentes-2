import os
import sys

# Agrega Reto/ al path para que pytest pueda importar main, db y config
# sin importar desde qué directorio se corra el comando pytest.
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
