import datetime
import random

# Alias Type
# Usar alias nos permite darle un nombre claro a una estructura de datos
# que de otro modo seria solo "list[dict[str, str]]", algo dificil de leer a simple vista.
# Si alguien ve "AgentMemory" entiende de inmediato que es la memoria del agente,
# sin tener que interpretar el tipo generico completo.
type LogEntry = dict[str, str]
type AgentMemory = list[LogEntry]

# La diferencia entre una variable temporal dentro de un metodo y una que empieza con self.
# es que la temporal solo vive mientras ese metodo se ejecuta y despues desaparece de memoria.
# En cambio, self. guarda el valor dentro del objeto, y cualquier otro metodo de la misma
# instancia puede acceder a el durante toda la vida del objeto.
class PseudoAgente:
    """Clase que encapsula toda la logica del agente autonomo.
    Cada instancia tiene su propia memoria (historial) y un limite
    de tokens que se va consumiendo con cada comando ejecutado.
    """

    def __init__(self, name: str) -> None:
        self.name = name
        self.tokens = 100
        self.chat_history: AgentMemory = []

    def ping(self) -> str:
        """Responde con pong. Comando basico para verificar que el agente esta activo."""
        self.tokens -= 2
        return "pong"

    def count(self) -> str:
        """Pide una palabra al usuario y cuenta cuantas letras, vocales
        y consonantes tiene. Devuelve un resumen con el conteo.
        """
        self.tokens -= 5
        word = input("Ingrese una palabra: ").strip().lower()
        letters_total = len(word)
        total_vowels = 0
        total_consonants = 0

        for i in word:
            if i in "aeiou":
                total_vowels += 1
            else:
                total_consonants += 1

        result = (f"Total de letras: {letters_total}\n"
                  f"Total de vocales: {total_vowels}\n"
                  f"Total de consonantes: {total_consonants}")
        return result

    def date(self, role: str) -> str:
        """Muestra la fecha actual. Solo funciona si el rol es administrador.
        Si no tiene permisos, lanza PermissionError para que el bucle
        principal lo atrape con try/except sin que el programa crashee.
        """
        if role != "administrador":
            raise PermissionError("Privilegios insuficientes")
        self.tokens -= 3
        day = datetime.date.today()
        return f"Fecha actual: {day}"

    def validate_password(self, user: str) -> str:
        """Pide una nueva contraseña y revisa si cumple reglas basicas:
        que no sea igual al nombre de usuario y que tenga al menos 8 caracteres.
        """
        self.tokens -= 4
        new_password = input("Ingrese una nueva contraseña para validar: ").strip()
        if new_password.lower() == user.lower():
            return "Rechazada: La contraseña no puede ser igual al nombre de usuario."
        elif len(new_password) < 8:
            return "La contraseña es demasiado corta. Debe tener al menos 8 caracteres."
        return "Contraseña válida."

    def calculator(self) -> str:
        """Calculadora basica que pide dos numeros y un operador (+, -, *, /).
        Usa float para aceptar enteros y decimales. Tiene proteccion contra
        texto no numerico (ValueError) y contra division por cero.
        """
        self.tokens -= 8
        try:
            number_one = float(input("Ingresa el primer número: ").strip())
            operator = input("Ingresa el operador (+, -, *, /): ").strip()
            number_two = float(input("Ingresa el segundo número: ").strip())
        except ValueError:
            return "Error: debes ingresar valores numéricos válidos."

        if operator == "+":
            result = number_one + number_two
        elif operator == "-":
            result = number_one - number_two
        elif operator == "*":
            result = number_one * number_two
        elif operator == "/":
            if number_two == 0:
                return "Error: no se puede dividir por cero."
            result = number_one / number_two
        else:
            return "Operador no válido. Usa +, -, * o /."

        return f"Resultado: {result}"

    def roll_dice(self) -> str:
        """Lanza un dado virtual y devuelve un numero aleatorio entre 1 y 6.
        Consume poca bateria porque es una operacion simple.
        """
        self.tokens -= 1
        result = random.randint(1, 6)
        return f"Resultado del dado: {result}"

    def chat_log(self, action: str) -> str:
        """Gestiona el historial de comandos del agente.
        Recibe la accion: 'all' para ver todo, 'clear' para limpiar,
        o cualquier otra palabra para buscar coincidencias en los registros.
        """
        self.tokens -= 5

        if action == "all":
            if not self.chat_history:
                return "[PseudoAgente] No hay historial almacenado."
            lines: list[str] = []
            for memory in self.chat_history:
                lines.append(
                    f"{memory['timestamp']} - Comando: {memory['comando']}, "
                    f"Rol: {memory['rol']}, Descripción: {memory['descripcion']}"
                )
            return "\n".join(lines)

        elif action == "clear":
            self.chat_history.clear()
            return "[PseudoAgente] Historial limpiado."

        else:
            # Busca la palabra clave dentro de la descripcion de cada registro
            matches: int = 0
            lines: list[str] = []
            for entry in self.chat_history:
                message = entry["descripcion"].lower()
                if action in message:
                    matches += 1
                    lines.append(f"Autor: {entry['autor']} | Mensaje: {entry['descripcion']}")
            lines.append(f"Coincidencias encontradas: {matches}")
            if matches == 0:
                lines.append("[PseudoAgente] No encontré registros que coincidan con esa palabra.")
            return "\n".join(lines)

    def log(self, cmd: str, role: str, system_message: str, user: str) -> None:
        """Crea un registro con la info del comando ejecutado y lo agrega
        al historial interno del agente (self.chat_history).
        """
        log_entry: LogEntry = {
            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "comando": cmd,
            "rol": role,
            "autor": user,
            "descripcion": system_message
        }
        self.chat_history.append(log_entry)

    def is_alive(self) -> bool:
        """Verifica si el agente todavia tiene tokens para seguir operando."""
        return self.tokens > 0


# Usar herencia para crear AgenteAdmin es mejor que copiar y pegar todo el PseudoAgente,
# porque reutilizamos toda la logica que ya existe y solo modificamos lo que necesitamos.
# Si mañana cambiamos algo en PseudoAgente, AgenteAdmin lo hereda automaticamente.
class AgenteAdmin(PseudoAgente):
    """Version especializada del agente para usuarios con rol administrador.
    Hereda todo de PseudoAgente pero consultar el historial no le cuesta tokens.
    """

    def __init__(self, name: str) -> None:
        # super().__init__() llama al constructor del padre (PseudoAgente),
        # asi reutilizamos la inicializacion de tokens, historial y nombre
        # sin tener que repetir ese codigo aca.
        super().__init__(name)

    def chat_log(self, action: str) -> str:
        """Sobreescritura del metodo chat_log.
        Para el admin, revisar el historial no consume tokens.
        Guardamos los tokens antes de llamar al metodo del padre
        y los restauramos despues, asi evitamos duplicar toda la logica.
        """
        tokens_before = self.tokens
        result = super().chat_log(action)
        self.tokens = tokens_before
        return result
