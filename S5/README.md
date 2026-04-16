# Semana 5: Persistencia con SQLite + API con FastAPI

Esta semana es de **aprendizaje autonomo**. Vas a trabajar directamente con los scripts
de Python, descomentando codigo capitulo por capitulo, ejecutando, observando y escribiendo
tus conclusiones. No necesitas al instructor para avanzar — todo esta explicado dentro de
los archivos.

## Preparacion del entorno

Antes de escribir una sola linea de codigo, vamos a crear un **entorno virtual**.
Esto aisla las dependencias de esta semana (FastAPI, uvicorn, requests) del resto
de tu sistema. Asi evitas conflictos con otros proyectos o con paquetes del sistema.

### 1. Abre una terminal y navega a la carpeta S5

```bash
cd S5
```

### 2. Crea el entorno virtual

```bash
python3 -m venv .venv
```

Esto crea una carpeta `.venv` dentro de `S5/` con una copia aislada de Python.

### 3. Activa el entorno virtual

**macOS / Linux:**
```bash
source .venv/bin/activate
```

**Windows (cmd):**
```cmd
.venv\Scripts\activate
```

**Windows (PowerShell):**
```powershell
.venv\Scripts\Activate.ps1
```

Sabras que esta activo porque veras `(.venv)` al inicio de tu linea de terminal.

### 4. Instala las dependencias

```bash
pip install -r requirements.txt
```

### 5. Verifica la instalacion

```bash
python -c "import fastapi; print('FastAPI', fastapi.__version__, '- OK')"
python -c "import requests; print('Requests - OK')"
```

---

## Sesion 1: Persistencia con SQLite

**Archivo:** `S5_sesion_1.py`
**Terminales necesarias:** 1

SQLite viene incluido con Python — no necesitas instalar nada extra para esta sesion.

### Como trabajar

1. Abre `S5_sesion_1.py` en tu editor
2. Lee el capitulo (la explicacion esta en los comentarios)
3. Descomenta el bloque de codigo indicado
4. Ejecuta el script completo:
   ```bash
   python S5_sesion_1.py
   ```
5. Observa la salida en la terminal
6. Escribe tu conclusion en el comentario `# CONCLUSION:`
7. Avanza al siguiente capitulo

### Capitulos

| # | Tema | Tiempo estimado |
|---|------|-----------------|
| 1 | El problema de la amnesia (RAM vs disco) | 5 min |
| 2 | Crear tablas con SQL | 10 min |
| 3 | Registrar un agente (INSERT) | 10 min |
| 4 | Despertar un agente (SELECT) | 10 min |
| 5 | Tabla de mensajes | 10 min |
| 6 | Bandeja de entrada | 10 min |
| 7 | Experimentacion libre | 5 min |

---

## Sesion 2: Servidor FastAPI

**Archivo:** `S5_sesion_2.py`
**Terminales necesarias:** 2 (servidor + navegador)

**IMPORTANTE:** Todos los comandos se ejecutan desde dentro de la carpeta `S5/`.
El servidor importa funciones de `S5_sesion_1.py`, asi que debe correr desde aqui.

### Paso 1: Levanta el servidor (Terminal 1)

```bash
uvicorn S5_sesion_2:app --reload
```

El flag `--reload` reinicia el servidor automaticamente cada vez que guardas cambios.
Deja esta terminal abierta durante toda la sesion.

### Paso 2: Abre Swagger UI (Navegador)

Visita: [http://localhost:8000/docs](http://localhost:8000/docs)

Esta es la documentacion interactiva que FastAPI genera automaticamente.
Desde aqui puedes probar cada endpoint sin escribir codigo.

### Paso 3: Descomenta capitulo por capitulo

1. Abre `S5_sesion_2.py` en tu editor
2. Descomenta el bloque del capitulo actual
3. Guarda el archivo — el servidor se reinicia solo
4. Recarga la pagina de Swagger UI
5. Prueba el nuevo endpoint desde el navegador
6. Escribe tu conclusion

### Capitulos

| # | Tema | Tiempo estimado |
|---|------|-----------------|
| 1 | Analogia del restaurante (HTTP) | 5 min (solo lectura) |
| 2 | Instalacion y verificacion | 5 min |
| 3 | Mi primer endpoint (GET /) | 10 min |
| 4 | GET con parametros de ruta | 10 min |
| 5 | POST endpoints (crear agentes y mensajes) | 10 min |

---

## Cliente HTTP (Capitulos 6-7)

**Archivo:** `S5_cliente.py`
**Terminales necesarias:** 2 (servidor corriendo + terminal para el cliente)

El servidor de la sesion 2 **debe seguir corriendo** en Terminal 1.

### En Terminal 2:

```bash
python S5_cliente.py
```

Misma dinamica: descomenta las funciones y el bloque `__main__`, ejecuta, observa.

| # | Tema | Tiempo estimado |
|---|------|-----------------|
| 6 | El agente como cliente HTTP (requests) | 10 min |
| 7 | El circuito completo (POST + GET desde Python) | 10 min |

---

## Limpieza

Cuando termines o quieras empezar de cero:

```bash
# Borrar la base de datos (se regenera al ejecutar de nuevo)
rm agentes.db

# Desactivar el entorno virtual
deactivate
```

---

## Resumen del flujo

```
Terminal 1                          Terminal 2                Navegador
──────────                          ──────────                ─────────
                                                              
[Sesion 1]                                                    
python S5_sesion_1.py                                         
  (caps 1-7, una terminal)                                    
                                                              
[Sesion 2]                                                    
uvicorn S5_sesion_2:app --reload                              localhost:8000/docs
  (dejar corriendo)                                           (probar endpoints)
                                                              
                                    [Caps 6-7]                
                                    python S5_cliente.py      
                                      (requiere servidor)     
```
