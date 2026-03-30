import datetime
from os import system # Se importa libreria para agregar el nuevo comando de fecha_hoy

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
def login():
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

def commands(user, role): 
    cmd = ""
    system_on = True
    chat_history = [] # Marca de tiempo (timestamp), comando usado, rol, descripcion 
    system_message = [] # Mensajes generados por el sistema para cada comando

    # Variable para pruebas, simulación de persistencia de historial
    test_chat_history = [{'timestamp': '2026-03-29 18:36:30', 'comando': 'ping', 'rol': 'administrador', 'autor': 'admin', 'descripcion': 'Respuesta al comando ping.'}, 
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
            system_message = count()
        # Comandos nuevos agregados para la fase 3
        elif cmd == "fecha_hoy":
            date(role)
            system_message = f"Comando fecha_hoy ejecutado por un usuario con rol '{role}'."
        elif cmd == "validar_pass":
            validate_password(user)
            system_message = f"Comando validar_pass ejecutado para el usuario '{user}'."
        elif cmd == "calculadora":
            calculator()
            system_message = "Comando calculadora ejecutado."
        elif cmd == "historial":
            system_message = chat_log(cmd, chat_history, test_chat_history)

        else: 
            print(f"Comando '{cmd}' no reconocido. Intente nuevamente.")
            system_message = f"Comando no reconocido: '{cmd}'."
        
        log(cmd, role, system_message, chat_history, user) # Llamada a la función log para registrar cada comando ejecutado y su resultado
        print("\n",chat_history, "\n") 

#Se utiliza una función separada para manejar el comando contar,
#lo que mejora la organización del código y facilita su mantenimiento.
def count():
    word = input("Ingrese una palabra: ").strip().lower()
    letters_total = len(word)
    total_vowels = 0
    total_consonants = 0

    for i in word:
        if i in "aeiou":
            total_vowels += 1
        else:
            total_consonants += 1
    print(f"Total de letras: {letters_total}")
    print(f"Total de vocales: {total_vowels}")
    print(f"Total de consonantes: {total_consonants}")
    mensaje = f"Comando contar ejecutado. Palabra ingresada: '{word}'"  
    return mensaje

# Muestra la fecha actual solo si el rol es administrador.
def date(role):
    if role == "administrador":
        day = datetime.date.today()
        print(f"Fecha actual: {day}")
    else:
        print("[Acceso Denegado] Este comando requiere privilegios de administrador.")

# Funcion en donde se valida la contraseña ingresada por el usuario, se pasa el valor de usuario 
# para evitar que el usuario pueda usar su nombre como contraseña, lo que es una mala práctica de seguridad.
def validate_password(user):
    new_password = input("Ingrese una nueva contraseña para validar: ").strip()
    if new_password.lower() == user.lower():
                print("Rechazada: La contraseña no puede ser igual al nombre de usuario.")
    elif len(new_password) < 8:
        print("La contraseña es demasiado corta. Debe tener al menos 8 caracteres.")
        return False
    print("Contraseña válida.")
    return True

""" 
Se define la función calculadora, que permite realizar operaciones básicas, 
se utiliza un bloque try-except para manejar errores de entrada, como ingresar texto en lugar de números, 
y se incluyen validaciones para operadores no válidos y división por cero.
Adicional se utiliza la función float() para permitir el ingreso de números decimales, 
lo que hace la calculadora más versátil, ya si se ingresa un número entero, 
se convertirá automáticamente a decimal sin afectar el resultado.
No se utiliza int directamente para evitar que el programa se rompa si el usuario ingresa un número decimal y no se
utiliza double porque en Python no existe ese tipo de dato, el equivalente sería float, 
que es el tipo de dato para números decimales.
"""
def calculator():
    try:
        number_one = float(input("Ingresa el primer número: ").strip())
        operador = input("Ingresa el operador (+, -, *, /): ").strip()
        number_two = float(input("Ingresa el segundo número: ").strip())
    except ValueError:
        print("Error: debes ingresar valores numéricos válidos.")
        return

    if operador == "+":
        resultado = number_one + number_two
    elif operador == "-":
        resultado = number_one - number_two
    elif operador == "*":
        resultado = number_one * number_two
    elif operador == "/":
        if number_two == 0:
            print("Error: no se puede dividir por cero.")
            return
        resultado = number_one / number_two
    else:
        print("Operador no válido. Usa +, -, * o /.")
        return

    print(f"Resultado: {resultado}")

# La función chat_log maneja el submenú de historial del pseudoagente. 
# Le pido al usuario un subcomando y, dependiendo de lo que ingrese, muestro todo el historial con historial all, lo limpio con historial clear, 
# o busco entradas por palabra clave con historial. En todos los casos retorno un mensaje describiendo lo que se ejecutó.
def chat_log(cmd, chat_history, test_chat_history):
    print("Comandos disponibles: historial, historial all, historial clear")
    cmd = input("Ingrese un comando: ").strip().lower()
    # Para manejar las singularidades del comando separé la entrada con split() y así distinguí historial, historial all e historial clear.
    parts = cmd.split()

    if len(parts) == 2 and parts[0] == "historial" and parts[1] == "all":
        if not chat_history:
            print("[PseudoAgente] No hay historial almacenado.")
            return "Comando historial all ejecutado. Historial vacío."
        else:
            for memory in chat_history:
                print(f"{memory['timestamp']} - Comando: {memory['comando']}, Rol: {memory['rol']}, Descripción: {memory['descripcion']}")
            system_message = "Comando historial all ejecutado. Se muestra todo el historial de comandos."
           
    elif len(parts) == 2 and parts[0] == "historial" and parts[1] == "clear":
        chat_history.clear()
        print("[PseudoAgente] Historial limpiado.")
        system_message = "Comando historial clear ejecutado. Se ha limpiado el historial de comandos."
    
    elif len(parts) == 1 and parts[0] == "historial":
        palabra_clave = input("Ingresa la palabra clave a buscar: ").strip().lower()
        coincidencias = 0
        for memoria in test_chat_history:
            mensaje = memoria["descripcion"].lower()
            # Con el operador in comparé si la palabra clave aparece dentro del mensaje, aunque sea una parte del texto.
            if palabra_clave in mensaje:
                coincidencias += 1
                print(f"Autor: {memoria['autor']} | Mensaje: {memoria['descripcion']}")
        print(f"Coincidencias encontradas: {coincidencias}")

        if coincidencias == 0:
            print("[PseudoAgente] No encontré registros que coincidan con esa palabra.")
        system_message = f"Busqueda en historial con palabra clave '{palabra_clave}' ({coincidencias} coincidencias)."
    else:
        print("[PseudoAgente] Comando no reconocido dentro de historial.")
        system_message = f"Subcomando de historial no valido: '{cmd}'."

    return system_message

def log(cmd, role, system_message, chat_history, user):
    log_entry = {
        "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "comando": cmd,
        "rol": role,
        "autor": user,
        "descripcion": system_message
    }
    chat_history.append(log_entry)

# Punto de entrada principal del sistema. 
def start_system():
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