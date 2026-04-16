from agente import PseudoAgente, AgenteAdmin

"""Fase 1: Capa de Seguridad (Login)
El sistema pide usuario y contraseña por consola.
Si el login es exitoso, se pasa a la Fase 2 recordando el rol del usuario.
Si falla 3 veces, el sistema se bloquea y termina la ejecucion.
"""

# Credenciales definidas con un diccionario para facilitar la gestion de usuarios
user_credentials = {
    "invitado": {
        "password": "inv123",
        "rol": "invitado"
    },
    "admin": {
        "password": "admin123",
        "rol": "administrador"
    }
}

maximum_retries = 3  # Numero maximo de intentos permitidos para el login


def login() -> tuple[str, str] | tuple[None, None]:
    """Maneja el inicio de sesion del usuario.
    Pide usuario y contraseña, valida contra las credenciales guardadas
    y devuelve una tupla con (usuario, rol) si el login es exitoso,
    o (None, None) si se agotan los intentos.
    """
    retries = 0

    while retries < maximum_retries:
        user = input("\n Ingrese usuario: ").strip().lower()
        password = input(" Ingrese contraseña: ").strip()

        # Verificamos si el usuario existe como llave en el diccionario
        # y si la contraseña coincide. Usar 'in' sobre un dict es mas eficiente
        # que recorrer con un for porque internamente usa hashing.
        if user in user_credentials:
            if user_credentials[user]["password"] == password:
                role = user_credentials[user]["rol"]
                print(f"\n Bienvenido {user}! (Tu rol es: {role})")
                return user, role

        retries += 1
        remaining_attempts = maximum_retries - retries

        if remaining_attempts > 0:
            print(f" Credenciales inválidas. Intentos restantes: {remaining_attempts}")
        else:
            print("\n [Alerta] Usuario bloqueado. Cerrando sistema.")
            return None, None


def commands(user: str, role: str, agent: PseudoAgente) -> None:
    """Bucle principal del agente. Muestra el menu de comandos disponibles,
    captura lo que el usuario escribe y delega la ejecucion al objeto agente.
    El bucle se mantiene mientras system_on sea True y el agente tenga tokens.
    No se usa break para gestionar la salida, solo las condiciones del while.
    """
    system_on: bool = True
    system_message: str = ""

    # El while revisa dos condiciones: que no se haya pedido salir
    # y que el agente aun tenga tokens disponibles para operar
    while system_on and agent.is_alive():
        print("=" * 70)
        print(f" Tokens disponibles: {agent.tokens}")
        print(" Comandos: ping, contar, fecha_hoy, validar_pass, calculadora, dado, historial, salir")
        print()
        cmd = input(" Ingrese un comando: ").strip().lower()
        print("=" * 70)

        if cmd == "salir":
            system_message = "Se ha solicitado terminar la sesión."
            system_on = False
            print("Apagando el sistema... ¡Hasta luego!")

        elif cmd == "ping":
            print(agent.ping())
            system_message = "Respuesta al comando ping."

        elif cmd == "contar":
            result = agent.count()
            print(result)
            system_message = "Comando contar ejecutado."

        elif cmd == "fecha_hoy":
            try:
                result = agent.date(role)
                print(result)
                system_message = f"Comando fecha_hoy ejecutado por un usuario con rol '{role}'."
            except PermissionError as e:
                print(f"[Acceso Denegado] {e}")
                system_message = f"Acceso denegado al comando fecha_hoy para rol '{role}'."

        elif cmd == "validar_pass":
            result = agent.validate_password(user)
            print(result)
            system_message = f"Comando validar_pass ejecutado para el usuario '{user}'."

        elif cmd == "calculadora":
            result = agent.calculator()
            print(result)
            system_message = "Comando calculadora ejecutado."

        elif cmd == "dado":
            result = agent.roll_dice()
            print(result)
            system_message = "Comando dado ejecutado."

        elif cmd == "historial":
            print("Opciones: 'all' (ver todo), 'clear' (limpiar), o escribe una palabra para buscar")
            action = input("Ingrese la accion: ").strip().lower()
            result = agent.chat_log(action)
            print(result)
            system_message = f"Comando historial ejecutado con accion '{action}'."

        else:
            print(f"Comando '{cmd}' no reconocido. Intente nuevamente.")
            system_message = f"Comando no reconocido: '{cmd}'."

        # Registramos cada comando ejecutado en el historial del agente
        agent.log(cmd, role, system_message, user)

        # Si el agente se quedo sin tokens despues del ultimo comando, avisamos
        if not agent.is_alive():
            print("\n[Sistema] El agente se ha quedado sin tokens. Apagando...")

    print(f"\n Estado final - Tokens restantes: {agent.tokens}")


def start_system() -> None:
    """Punto de entrada del programa. Arranca con la pantalla de login
    y si el usuario se autentica, activa el bucle de comandos del agente.
    """
    print("=" * 70)
    print(" Inicio sistema del agente autonomo. Fase 1: Capa de Seguridad (Login)")
    print("=" * 70)

    user, role = login()

    if user is None:
        return

    # Segun el rol del usuario, instanciamos el tipo de agente que corresponde.
    # Si es admin usa AgenteAdmin (historial sin costo), si no, PseudoAgente normal.
    if role == "administrador":
        agent = AgenteAdmin(name="AgentePro")
    else:
        agent = PseudoAgente(name="AgenteBasico")

    print(f"\n{'=' * 60}")
    print(f" Fase 2: {agent.name} activo. Escuchando comandos...")
    commands(user, role, agent)


if __name__ == "__main__":
    start_system()
