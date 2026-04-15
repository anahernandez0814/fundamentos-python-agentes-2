import datetime

# Alias Type
# Usar un alias como AgentMemory nos permite darle un nombre claro a una estructura de datos
# que de otro modo seria solo "list[dict[str, str]]", algo dificil de leer y de entender a simple vista.
# Cuando trabajamos con modelos de IA, las funciones reciben y devuelven estructuras complejas
# (listas de diccionarios, historiales de conversacion, etc). Si tipamos todo con tipos genericos
# como list o dict, cualquier persona (o modelo) que lea el codigo no sabe que representa esa lista.
# En cambio, si ve "AgentMemory" entiende de inmediato que es la memoria del agente.
# Esto hace el codigo mas legible para humanos y mas facil de interpretar para un LLM
# que necesita entender el contexto de los datos que esta procesando.
type Historial = dict[str, str]
type AgentMemory = list[Historial]
"""Fase 1: Capa de Seguridad (Login)
Antes de que el Agente despierte y comience a escuchar comandos, debe verificar quién intenta 
acceder:

El sistema debe pedir un usuario y una contraseña por consola.
Roles: Define en tu código un perfil de invitado (ej. user = "invitado") y 
un administrador (admin = "admin"), con sus respectivas contraseñas.
Sistema de Bloqueo: El usuario tiene un máximo de 3 intentos. Si falla 3 veces, 
el bucle de login se rompe, el programa imprime [Alerta] Usuario bloqueado. Cerrando sistema. 
y la ejecución termina.
Si el inicio de sesión es exitoso, el sistema pasa a la Fase 2 y debe recordar con qué rol ingresó el usuario.
"""

# Fase 1: Capa de Seguridad (Login)
# Credenciales definidas utilizando un diccionario para facilitar la gestión
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

maximum_retries = 3 # Número máximo de intentos permitidos para el login

# Función que realiza el proceso de autenticación del usuario
def login() -> tuple[str, str] | tuple[None, None]:
    """Maneja el inicio de sesion del usuario.
    Pide usuario y contraseña, valida contra las credenciales guardadas
    y devuelve una tupla con (usuario, rol) si el login es exitoso,
    o (None, None) si se agotan los intentos.
    """
    retries = 0 # Variables para contar intentos y gestionar el bloqueo
    
    while retries < maximum_retries:
        user = input("\n Ingrese usuario: ").strip().lower()
        password = input(" Ingrese contraseña: ").strip()
        
        """Este bloque verifica si el usuario existe en el diccionario de credenciales 
        y si la contraseña es correcta. Con el 'in' en el diccionario verificamos que el 
        valor buscado existe como llave, lo que es más eficiente que 
        usar un ciclo for para buscarlo."""
        if user in user_credentials:
            if user_credentials[user]["password"] == password:
                role = user_credentials[user]["rol"]
                print(f"\n Bienvenido {user}! (Tú rol es: {role})")
                return user, role
        
        retries += 1 #Incremento el contador en 1 cada vez que el login falla
        remaining_attempts = maximum_retries - retries
        
        if remaining_attempts > 0:
            print(f" Credenciales inválidas. Intentos restantes: {remaining_attempts}")
        else:
            print("\n [Alerta] Usuario bloqueado. Cerrando sistema.")
            return None, None

"""
Fase 2: 
Comandos Base (Repaso de Clase) Se mantienen los comandos base para el pseudoagente.

Fase 3: Comandos avanzados
Se agregan nuevas herramientas al pseudoagente, 
como una calculadora básica, validación de contraseñas, 
y un comando para mostrar la fecha actual (solo para administradores).
"""

def commands(user: str, role: str) -> None:
    """Bucle principal del agente. Muestra el menu de comandos disponibles,
    captura lo que el usuario escribe y llama a la funcion correspondiente.
    Recibe el nombre de usuario y su rol para controlar permisos.
    """
    cmd: str = ""
    system_on: bool = True
    chat_history: AgentMemory = [] # Marca de tiempo (timestamp), comando usado, rol, descripcion
    system_message: str = "" # Mensajes generados por el sistema para cada comando

    # Variable para pruebas, simulación de persistencia de historial
    test_chat_history: AgentMemory = [{'timestamp': '2026-03-29 18:36:30', 'comando': 'ping', 'rol': 'administrador', 'autor': 'admin', 'descripcion': 'Respuesta al comando ping.'}, 
                         {'timestamp': '2026-03-29 18:36:43', 'comando': 'contar', 'rol': 'administrador', 'autor': 'admin', 'descripcion': "Comando contar ejecutado. Palabra ingresada: 'oscuridad'"}, 
                         {'timestamp': '2026-03-29 18:37:01', 'comando': 'fecha_hoy', 'rol': 'administrador', 'autor': 'admin', 'descripcion': "Comando fecha_hoy ejecutado por un usuario con rol 'administrador'."}, 
                         {'timestamp': '2026-03-29 18:37:22', 'comando': 'validar_pass', 'rol': 'administrador', 'autor': 'admin', 'descripcion': "Comando validar_pass ejecutado para el usuario 'admin'."}, 
                         {'timestamp': '2026-03-29 18:37:47', 'comando': 'calculadora', 'rol': 'administrador', 'autor': 'admin', 'descripcion': 'Comando calculadora ejecutado.'}, 
                         {'timestamp': '2026-03-29 18:37:55', 'comando': 'salir', 'rol': 'administrador', 'autor': 'admin', 'descripcion': 'Se ha solicitado terminar la sesión.'}] 
    
    while system_on:
        print("=" * 70)
        print("Comandos disponibles: ping, contar, fecha_hoy, validar_pass, calculadora, historial, salir")
        print("\n")
        cmd = input("Ingrese un comando: ").lower()
        print("=" * 70)
        
        if cmd == "salir":
            system_message = "Se ha solicitado terminar la sesión."
            system_on = False
            print("Apagando el sistema... ¡Hasta luego!")
        elif cmd == "ping":
            system_message = "Respuesta al comando ping."
            print("pong")
        elif cmd == "contar":
            result = count()
            print(result)
            system_message = f"Comando contar ejecutado."
        # Comandos nuevos agregados para la fase 3
        elif cmd == "fecha_hoy":
            try:
                result = date(role)
                print(result)
                system_message = f"Comando fecha_hoy ejecutado por un usuario con rol '{role}'."
            except PermissionError as e:
                print(f"[Acceso Denegado] {e}")
                system_message = f"Acceso denegado al comando fecha_hoy para rol '{role}'."
        elif cmd == "validar_pass":
            result = validate_password(user)
            print(result)
            system_message = f"Comando validar_pass ejecutado para el usuario '{user}'."
        elif cmd == "calculadora":
            result = calculator()
            print(result)
            system_message = "Comando calculadora ejecutado."
        elif cmd == "historial":
            print("Opciones: 'all' (ver todo), 'clear' (limpiar), o escribe una palabra para buscar")
            action = input("Ingrese la accion: ").strip().lower()
            result = chat_log(action, chat_history, test_chat_history)
            print(result)
            system_message = f"Comando historial ejecutado con accion '{action}'."

        else: 
            print(f"Comando '{cmd}' no reconocido. Intente nuevamente.")
            system_message = f"Comando no reconocido: '{cmd}'."
        
        log(cmd, role, system_message, chat_history, user) # Llamada a la función log para registrar cada comando ejecutado y su resultado
        print("\n",chat_history, "\n") 

#Se utiliza una función separada para manejar el comando contar,
#lo que mejora la organización del código y facilita su mantenimiento.
def count() -> str:
    """Pide una palabra al usuario y cuenta cuantas letras, vocales
    y consonantes tiene. Devuelve un mensaje de texto con el resumen
    del conteo para que quede registrado en el historial.
    """
    word = input("Ingrese una palabra: ").strip().lower()
    letters_total = len(word)
    total_vowels = 0
    total_consonants = 0

    for i in word:
        if i in "aeiou":
            total_vowels += 1
        else:
            total_consonants += 1
    result = f"Total de letras: {letters_total}\nTotal de vocales: {total_vowels}\nTotal de consonantes: {total_consonants}"
    return result

# Muestra la fecha actual solo si el rol es administrador.
def date(role: str) -> str:
    """Muestra la fecha de hoy.
    Solo funciona si el usuario tiene rol de administrador.
    Si el rol no tiene permisos, lanza un PermissionError que debe
    ser atrapado por quien llame a esta funcion.
    Retorna un string con la fecha actual.
    """
    # Cuando el rol no es administrador, raise lanza la excepcion PermissionError.
    # Esto hace que la funcion se detenga inmediatamente y el error "viaje" hacia arriba,
    # es decir, vuelve al lugar donde se llamo esta funcion (el bucle principal en commands()).
    # Alla, el bloque try/except lo atrapa con "except PermissionError" y muestra
    # el mensaje de forma controlada, sin que el programa se cierre o crashee.
    if role != "administrador":
        raise PermissionError("Privilegios insuficientes")
    day = datetime.date.today()
    return f"Fecha actual: {day}"

# Funcion en donde se valida la contraseña ingresada por el usuario, se pasa el valor de usuario 
# para evitar que el usuario pueda usar su nombre como contraseña, lo que es una mala práctica de seguridad.
def validate_password(user: str) -> str:
    """Pide una nueva contraseña y revisa si cumple las reglas basicas:
    que no sea igual al nombre de usuario y que tenga al menos 8 caracteres.
    Devuelve un string con el resultado de la validacion.
    """
    new_password = input("Ingrese una nueva contraseña para validar: ").strip()
    if new_password.lower() == user.lower():
        return "Rechazada: La contraseña no puede ser igual al nombre de usuario."
    elif len(new_password) < 8:
        return "La contraseña es demasiado corta. Debe tener al menos 8 caracteres."
    return "Contraseña válida."

def calculator() -> str:
    """Calculadora basica que pide dos numeros y un operador (+, -, *, /).
    Usa float para aceptar tanto enteros como decimales sin que el programa falle.
    Tiene proteccion contra texto no numerico (try/except ValueError)
    y contra division por cero.
    Devuelve un string con el resultado o con el mensaje de error correspondiente.
    """
    try:
        number_one = float(input("Ingresa el primer número: ").strip())
        operador = input("Ingresa el operador (+, -, *, /): ").strip()
        number_two = float(input("Ingresa el segundo número: ").strip())
    except ValueError:
        return "Error: debes ingresar valores numéricos válidos."

    if operador == "+":
        resultado = number_one + number_two
    elif operador == "-":
        resultado = number_one - number_two
    elif operador == "*":
        resultado = number_one * number_two
    elif operador == "/":
        if number_two == 0:
            return "Error: no se puede dividir por cero."
        resultado = number_one / number_two
    else:
        return f"Operador no válido. Usa +, -, * o /."

    return f"Resultado: {resultado}"

def chat_log(action: str, chat_history: AgentMemory, test_chat_history: AgentMemory) -> str:
    """Gestiona todo lo relacionado con el historial de comandos.
    Recibe la accion a realizar: "all" para ver todo, "clear" para limpiar,
    o cualquier otra palabra para buscarla en los registros.
    No imprime nada, solo arma el texto y lo devuelve como string
    para que el bucle principal se encargue de mostrarlo.
    """
    if action == "all":
        if not chat_history:
            return "[PseudoAgente] No hay historial almacenado."
        lines: list[str] = []
        for memory in chat_history:
            lines.append(f"{memory['timestamp']} - Comando: {memory['comando']}, Rol: {memory['rol']}, Descripción: {memory['descripcion']}")
        return "\n".join(lines)

    elif action == "clear":
        chat_history.clear()
        return "[PseudoAgente] Historial limpiado."

    else:
        # La accion es una palabra clave para buscar en el historial
        # Con el operador in comparamos si la palabra clave aparece dentro del mensaje, aunque sea una parte del texto.
        coincidencias: int = 0
        lines: list[str] = []
        for memoria in test_chat_history:
            mensaje = memoria["descripcion"].lower()
            if action in mensaje:
                coincidencias += 1
                lines.append(f"Autor: {memoria['autor']} | Mensaje: {memoria['descripcion']}")
        lines.append(f"Coincidencias encontradas: {coincidencias}")
        if coincidencias == 0:
            lines.append("[PseudoAgente] No encontré registros que coincidan con esa palabra.")
        return "\n".join(lines)

def log(cmd: str, role: str, system_message: str, chat_history: AgentMemory, user: str) -> None:
    """Crea un registro (diccionario) con la info del comando ejecutado:
    fecha/hora, comando, rol, autor y descripcion. Luego lo agrega
    al historial para que quede guardado en memoria.
    """
    log_entry: Historial = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "comando": cmd,
        "rol": role,
        "autor": user,
        "descripcion": system_message
    }
    chat_history.append(log_entry)

# Punto de entrada principal del sistema.
def start_system() -> None:
    """Punto de entrada del programa. Arranca el sistema mostrando
    la pantalla de login y, si el usuario se autentica correctamente,
    activa el bucle de comandos del agente.
    """
    print("=" * 70)
    print("Inicio sistema del agente autonomo. Fase 1: Capa de Seguridad (Login)")
    print("=" * 70)
    
    #Llamamos a la función de login y obtenemos el usuario y rol. 
    # Si el login falla, el sistema se cierra.
    user, role = login()
    
    if user is None: 
        return
    
    """Fase 2: Comandos Base (Repaso de Clase)
    El menú infinito (while) debe mantener los comandos que exploramos en 
    nuestra sesión interactiva:

    ping: Responde con "pong!".
    contar: Pide una frase y cuenta las vocales y consonantes usando un ciclo for.
    salir: Rompe el bucle principal y apaga el Agente de forma elegante."""

    # El sistema pasa a la fase 2 y 3 solo si el login es exitoso, y se le pasan el usuario y rol para gestionar los comandos disponibles.
    print("\n" + "=" * 60)
    print("Fase 2: Agente activo. Escuchando comandos...")
    commands(user, role)


if __name__ == "__main__":
    start_system()