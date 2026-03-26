import datetime # Se importa libreria para agregar el nuevo comando de fecha_hoy

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
    print("=" * 70)
    print("Comandos disponibles: ping, contar, fecha_hoy, validar_pass, calculadora, salir")
    print("=" * 70)

    cmd = ""
    system_on = True
    
    while system_on:
        cmd = input("Ingrese un comando: ").lower()
        print("Comandos disponibles: ping, contar, fecha_hoy, validar_pass, calculadora, salir")
        print("=" * 70)
        
        if cmd == "salir":
            system_on = False
            print("Apagando el sistema... ¡Hasta luego!")
        elif cmd == "ping":
            print("pong")
        elif cmd == "contar":
            count()
        # Comandos nuevos agregados para la fase 3
        elif cmd == "fecha_hoy":
            date(role)
        elif cmd == "validar_pass":
            validate_password(user)
        elif cmd == "calculadora":
            calculator()
        else: 
            print(f"Comando '{cmd}' no reconocido. Intente nuevamente.")

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
    print("=" * 60)
    commands(user, role)


if __name__ == "__main__":
    start_system()