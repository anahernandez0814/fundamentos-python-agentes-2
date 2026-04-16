import datetime
import random

# Estos alias los heredé de la Semana 4. En vez de escribir
# list[dict[str, str]] cada vez que quiero hablar de la memoria
# del agente, le puse un nombre que dice lo que es.
type LogEntry = dict[str, str]
type AgentMemory = list[LogEntry]


class PseudoAgente:
    """El agente base. Viene de la Semana 4 con dos cambios importantes:
    'tokens' se renombró a 'energia' para que coincida con lo que guarda
    la base de datos, y el constructor ahora recibe 'rol' y 'energia'
    como parámetros para poder reconstruir el agente desde la DB
    con sus valores reales en vez de empezar siempre desde cero.
    """

    def __init__(self, name: str, rol: str = "agente", energia: int = 100) -> None:
        self.name = name
        self.rol = rol
        self.energia = energia
        self.chat_history: AgentMemory = []

    def completar_mision(self, energia_requerida: int) -> bool:
        """Acá está la decisión de dominio más importante del reto: la clase
        decide si hay energía suficiente para la misión, no el endpoint.
        Si alcanza, descuenta y devuelve True. Si no, no toca nada y devuelve False.
        Así el endpoint solo coordina — no mete lógica de negocio.
        """
        if self.energia < energia_requerida:
            return False
        self.energia -= energia_requerida
        return True

    def ping(self) -> str:
        """Lo más básico: confirma que el agente está vivo. Cuesta 2 de energía."""
        self.energia -= 2
        return "pong"

    def count(self) -> str:
        """Cuenta letras, vocales y consonantes de una palabra.
        Este método usa input() porque lo diseñé para la consola en la Semana 4.
        En el servidor nunca se llama, pero lo dejé para no perder la historia.
        """
        self.energia -= 5
        word = input("Ingrese una palabra: ").strip().lower()
        letters_total = len(word)
        total_vowels = sum(1 for c in word if c in "aeiou")
        total_consonants = letters_total - total_vowels
        return (
            f"Total de letras: {letters_total}\n"
            f"Total de vocales: {total_vowels}\n"
            f"Total de consonantes: {total_consonants}"
        )

    def date(self, role: str) -> str:
        """Solo los admins pueden ver la fecha. Si alguien más lo intenta,
        levanto un PermissionError para que el llamador lo maneje con try/except.
        """
        if role != "administrador":
            raise PermissionError("Privilegios insuficientes")
        self.energia -= 3
        return f"Fecha actual: {datetime.date.today()}"

    def validate_password(self, user: str) -> str:
        """Valida que una contraseña nueva cumpla reglas mínimas.
        También usa input() — es un método interactivo de consola de la Semana 4.
        """
        self.energia -= 4
        new_password = input("Ingrese una nueva contraseña para validar: ").strip()
        if new_password.lower() == user.lower():
            return "Rechazada: La contraseña no puede ser igual al nombre de usuario."
        if len(new_password) < 8:
            return "La contraseña es demasiado corta. Debe tener al menos 8 caracteres."
        return "Contraseña válida."

    def calculator(self) -> str:
        """Calculadora básica de consola (+, -, *, /).
        Igual que count() y validate_password(), este método vive aquí
        por herencia de la Semana 4 pero no se usa desde el servidor.
        """
        self.energia -= 8
        try:
            number_one = float(input("Ingresa el primer número: ").strip())
            operator = input("Ingresa el operador (+, -, *, /): ").strip()
            number_two = float(input("Ingresa el segundo número: ").strip())
        except ValueError:
            return "Error: debes ingresar valores numéricos válidos."

        if operator == "+":
            return f"Resultado: {number_one + number_two}"
        if operator == "-":
            return f"Resultado: {number_one - number_two}"
        if operator == "*":
            return f"Resultado: {number_one * number_two}"
        if operator == "/":
            if number_two == 0:
                return "Error: no se puede dividir por cero."
            return f"Resultado: {number_one / number_two}"
        return "Operador no válido. Usa +, -, * o /."

    def roll_dice(self) -> str:
        """Tira un dado virtual. Solo cuesta 1 de energía porque es simple."""
        self.energia -= 1
        return f"Resultado del dado: {random.randint(1, 6)}"

    def chat_log(self, action: str) -> str:
        """Gestiona el historial de comandos del agente.
        'all' muestra todo, 'clear' lo borra, cualquier otra palabra
        busca coincidencias en las descripciones de los registros.
        """
        self.energia -= 5

        if action == "all":
            if not self.chat_history:
                return "[PseudoAgente] No hay historial almacenado."
            lines = [
                f"{m['timestamp']} - Comando: {m['comando']}, "
                f"Rol: {m['rol']}, Descripción: {m['descripcion']}"
                for m in self.chat_history
            ]
            return "\n".join(lines)

        if action == "clear":
            self.chat_history.clear()
            return "[PseudoAgente] Historial limpiado."

        matches = [e for e in self.chat_history if action in e["descripcion"].lower()]
        lines = [f"Autor: {e['autor']} | Mensaje: {e['descripcion']}" for e in matches]
        lines.append(f"Coincidencias encontradas: {len(matches)}")
        if not matches:
            lines.append("[PseudoAgente] No encontré registros que coincidan.")
        return "\n".join(lines)

    def log(self, cmd: str, role: str, system_message: str, user: str) -> None:
        """Guarda un registro de lo que hizo el agente en su historial interno."""
        self.chat_history.append(
            {
                "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "comando": cmd,
                "rol": role,
                "autor": user,
                "descripcion": system_message,
            }
        )

    def is_alive(self) -> bool:
        """Devuelve True mientras el agente tenga energía para seguir operando."""
        return self.energia > 0


# Usar herencia acá tiene mucho sentido: AgenteAdmin no necesita
# reescribir todo, solo cambiar lo que es diferente para un admin.
class AgenteAdmin(PseudoAgente):
    """El agente con privilegios de administrador.

    Todo lo hereda de PseudoAgente con una sola diferencia: revisar
    el historial no le cuesta energía, porque los admins tienen acceso
    libre a la información. Al completar misiones funciona igual que
    un PseudoAgente, pero como es una instancia de AgenteAdmin,
    isinstance(agente, AgenteAdmin) devuelve True — útil para auditoría
    en los logs y en las respuestas del servidor.
    """

    def __init__(self, name: str, rol: str = "admin", energia: int = 100) -> None:
        # super().__init__ me evita repetir la lógica de inicialización del padre.
        super().__init__(name, rol, energia)

    def chat_log(self, action: str) -> str:
        """Para el admin, revisar el historial es gratis. El truco es guardar
        la energía antes de llamar al método del padre y restaurarla después,
        sin tener que duplicar toda la lógica de búsqueda.
        """
        energia_before = self.energia
        result = super().chat_log(action)
        self.energia = energia_before
        return result
