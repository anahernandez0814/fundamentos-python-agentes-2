# 🏛️ Reto de Consolidación: La Agencia de Agentes

**Fecha límite de entrega:** Jueves al terminar la sesión.

**Forma de entrega:** Pull-Request a la rama `reto_consolidacion` desde tu repositorio forkeado.

## 🎯 Contexto

Hasta ahora has recorrido un camino claro: en la **Semana 4** nació la Entidad — tu `PseudoAgente` dejó de ser un script suelto y se convirtió en una clase con memoria, energía y hasta una versión "Pro" (`AgenteAdmin`). En la **Semana 5** le diste dos sentidos nuevos: **persistencia** con SQLite (tu agente ya no se muere cuando cierras la terminal) y **voz al mundo** con FastAPI (otros programas pueden hablarle por HTTP).

Pero un agente solo es útil cuando se organiza con otros. Este reto marca el siguiente paso natural: los individuos se convierten en una **Agencia**. Y una Agencia real no es simplemente "un script más grande": es un sistema que **se protege** (autenticación), **se configura** sin hardcodear secretos (variables de entorno), **se audita** (logs estructurados) y **se alimenta del mundo exterior** (consumo de APIs públicas). Tu trabajo no es aprender todo desde cero — es **integrar lo que ya sabes** y dar **cuatro saltos concretos de investigación**.

## 🧩 Lo que ya sabes y vas a reutilizar

No vas a reinventar nada de esto; lo vas a **aprovechar**:

- **POO con herencia (S4):** `PseudoAgente`, `AgenteAdmin`, `super().__init__()`, override de métodos, `isinstance`.
- **Modularización (S4):** separación en varios `.py` con imports, regla de no dejar estado flotando fuera de las clases.
- **Librería estándar (S4):** `datetime` para timestamps, `random`, `os`, `json`.
- **SQLite (S5 Sesión 1):** `CREATE TABLE IF NOT EXISTS`, `INSERT`, `SELECT`, `WHERE`, `ORDER BY`, parámetros `?`, `PRIMARY KEY`, `AUTOINCREMENT`.
- **FastAPI (S5 Sesión 2):** decoradores `@app.get` / `@app.post`, path params `{nombre}`, `HTTPException`, modelos `BaseModel` de Pydantic, Swagger UI automático en `/docs`.
- **Cliente HTTP (S5 Sesión 2):** `requests.get`, `requests.post`, `response.status_code`, `response.json()`.

## 📋 Requerimientos Funcionales

### R1. Arquitectura modular
Tu proyecto debe tener como mínimo estos archivos, cada uno con una única responsabilidad clara:

* `agente.py` — clases `PseudoAgente` y `AgenteAdmin` (puedes importarlas o adaptar las tuyas de la Semana 4). Aquí **no hay SQL ni FastAPI**.
* `db.py` — funciones que hablan con SQLite: crear tablas, registrar agente, despertar agente, enviar mensaje, leer mensajes, y las nuevas funciones para `misiones`. Aquí **no hay FastAPI**.
* `main.py` — la aplicación FastAPI y los endpoints. Importa desde `agente.py` y `db.py`. Aquí **no defines clases de dominio ni queries SQL en crudo**.
* `cliente.py` — script que consume tu API por HTTP con `requests`. Ejecuta un guion de demostración end-to-end.
* `config.py` *(opcional pero recomendado)* — carga de variables de entorno.

### R2. Clases de dominio reutilizadas
Importa `PseudoAgente` y `AgenteAdmin` en `main.py`. La regla dura: **al "despertar" a un agente desde la base de datos, debes reconstruir su clase según el rol**. Si en la tabla `agentes` su rol es `"admin"` debes instanciar `AgenteAdmin(...)`; si es otro, `PseudoAgente(...)`. Esto se verifica con `isinstance`. No basta con devolver un diccionario: el objeto de dominio debe volver a existir cuando tu código lo necesite (por ejemplo, al completar una misión y descontar energía, quien decide cómo se descuenta es la clase, no el endpoint).

### R3. Persistencia con SQLite
Conserva las tablas `agentes` y `mensajes` tal como las construiste en la Semana 5. **Crea una tabla nueva** llamada `misiones` que como mínimo contenga:

```sql
CREATE TABLE IF NOT EXISTS misiones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    descripcion TEXT,
    agente_asignado TEXT,
    estado TEXT,                -- 'pendiente' | 'en_curso' | 'completada' | 'fallida'
    energia_requerida INTEGER,
    created_at TEXT             -- timestamp ISO
);
```

Puedes (y te invitamos a) **agregar más columnas** si lo consideras útil. Eso es una de tus **decisiones de ingeniería** (ver sección 🧭). Usa siempre parámetros `?` en tus queries — nunca construyas SQL con f-strings.

### R4. API con FastAPI
Conserva los endpoints que ya tenías de la Semana 5 (`GET /`, `GET /agente/{nombre}`, `GET /agentes/`, `POST /agentes/`, `POST /mensajes/`, `GET /mensajes/{nombre}`). **Agrega** los siguientes:

| Método | Ruta | Protegido | Qué hace |
|---|---|---|---|
| `POST` | `/misiones/` | Sí (API key) | Crea una misión. Si el `agente_asignado` no existe en la tabla `agentes`, responde `404`. |
| `GET` | `/misiones/{id}` | No | Devuelve la misión o `404`. |
| `GET` | `/agente/{nombre}/misiones` | No | Lista las misiones asignadas a un agente. |
| `POST` | `/misiones/{id}/completar` | Sí (API key) | Marca la misión como `"completada"`. **Aquí se usa la clase de S4:** despierta el agente desde la DB, reconstruye la instancia correcta, descuenta `energia_requerida` a través de un método de la clase, y persiste el nuevo estado del agente. |
| `GET` | `/briefing/{nombre}` | No | Combina datos locales del agente con información traída de una **API pública externa** (ver salto de complejidad §5.2). |

Todos los endpoints deben verse en Swagger UI (`http://localhost:8000/docs`).

### R5. Cliente HTTP de demostración
`cliente.py` debe ejecutar, sin intervención manual, un guion que:

1. Verifica que el servidor está vivo (`GET /`).
2. Crea un agente (`POST /agentes/`) con autenticación.
3. Crea una misión asignada a ese agente (`POST /misiones/`) con autenticación.
4. Completa la misión (`POST /misiones/{id}/completar`) con autenticación.
5. Consulta el briefing del agente (`GET /briefing/{nombre}`) y lo imprime.
6. Envía un mensaje entre agentes y lee la bandeja.

Este guion es la prueba viva de que tu circuito funciona de punta a punta.

## 🧠 Salto de Complejidad (investigación obligatoria)

Estas cuatro áreas **no las vimos en clase**. Tendrás que investigar, leer documentación, buscar ejemplos y decidir cómo integrarlas. Cada una resuelve un problema real de la Agencia.

### 5.1 🔐 Autenticación con API key
**Problema:** ahora que tu API está expuesta, cualquier persona podría crear agentes fantasma o completar misiones ajenas. La Agencia necesita una llave maestra que sólo conocen sus operadores.

**Qué entregar:**
* Una función (dependencia de FastAPI) que lea un header `X-API-KEY` de cada request y lo compare contra el valor configurado en tu `.env`. Si no coincide o no viene: `HTTPException(status_code=401, detail="API key inválida")`.
* Aplicar esa dependencia a **todos los endpoints de escritura** marcados con "Sí (API key)" en la tabla de §R4.
* Decisión tuya: si los `GET` también deben protegerse o no (justifícalo en el README).

**Pistas para investigar:** `"FastAPI api key header dependency"`, `fastapi.Header`, `fastapi.Depends`.

### 5.2 🌐 Inteligencia externa (API pública)
**Problema:** un agente aislado de la realidad no es inteligente. Dale un canal al mundo.

**Qué entregar:**
* El endpoint `GET /briefing/{nombre}` debe, internamente, hacer `requests.get(...)` a una **API pública sin autenticación** que tú elijas. La respuesta del endpoint debe combinar:
  * Datos locales del agente (de la tabla `agentes`).
  * Un campo traído de la API externa (un hecho, un consejo, el clima, una frase, una cotización… lo que tenga sentido con tu narrativa).
  * Una marca del origen (`"fuente_externa": "..."`).
* Manejo de fallos: la API externa puede tardar o estar caída. Define un timeout razonable y un plan de contingencia con `try/except`. Nunca dejes que tu servidor se cuelgue por culpa de un tercero.

**Pistas para investigar:** `"public API no auth json"`, `"requests timeout exception handling"`, `"public APIs list GitHub"`.

### 5.3 🗝️ Configuración con variables de entorno
**Problema:** la API key de tu Agencia y la URL de la API externa **no deben estar en el código fuente**. Si las subes a GitHub, cualquiera las copia.

**Qué entregar:**
* Un archivo `.env` (local, **no se versiona**) con al menos:
  * `AGENCIA_API_KEY=...`
  * `EXTERNAL_API_URL=...`
* Un archivo `.env.example` (sí se versiona) con las mismas claves pero sin valores reales, para que otra persona sepa qué configurar.
* Tu código carga esas variables al arrancar y las usa. No hay strings literales con secretos en el código.
* Tu `.gitignore` incluye `.env`.

**Pistas para investigar:** `"python-dotenv load_dotenv"`, `"os.environ getenv default"`.

### 5.4 📝 Observabilidad con `logging`
**Problema:** `print()` está bien para practicar, pero una Agencia no audita con `print`. Necesitas registros con niveles, formato y contexto.

**Qué entregar:**
* Configuración del módulo estándar `logging` en tu `main.py` con: formato (mínimo fecha, nivel y mensaje) y nivel por defecto `INFO`.
* Reemplaza **todos los `print` del servidor** por llamadas al logger, usando el nivel apropiado:
  * `logger.info(...)` — eventos normales (agente creado, misión completada).
  * `logger.warning(...)` — situaciones raras pero no rotas (API externa respondió lento, fallback activado).
  * `logger.error(...)` — fallos reales (integridad SQL, excepciones no esperadas).
* Justifica tus elecciones de nivel en un comentario corto cerca de la configuración.

**Pistas para investigar:** `"python logging basicConfig levels"`, `"logging formatter handlers"`.

## 🧭 Decisiones de Ingeniería (tu huella en el proyecto)

Hay tres decisiones que **no te vamos a dar resueltas**. Tómalas, impleméntalas y **justifícalas en un `README.md` del proyecto** (mínimo 3 líneas cada una):

1. **Esquema de la tabla `misiones`.** ¿Qué columnas extra agregaste más allá del mínimo? ¿Por qué? (Ej: `prioridad`, `deadline`, `creado_por`, `recompensa`…).
2. **API pública elegida.** ¿Cuál escogiste? ¿Por qué encaja con la narrativa de agentes? ¿Qué añade al briefing?
3. **Estrategia de resiliencia.** ¿Qué pasa cuando la API externa falla o tarda? ¿Tu agente responde con un mensaje de fallback, omite el campo, o devuelve un error? ¿Por qué?

## 🌟 Reto Eutagógico (opcional, +extra)

Si ya cumpliste todo lo anterior y quieres ir más lejos, **elige UNO** de estos retos:

* **CRUD completo:** implementa `PUT /agentes/{nombre}` (actualiza energía o rol) y `DELETE /agentes/{nombre}`. Decide qué pasa con las misiones asignadas a un agente que se elimina.
* **Validadores Pydantic custom:** en el `MisionRequest`, usa `@field_validator` (Pydantic v2) para que `energia_requerida > 0` y `estado` solo acepte los valores del enum permitido.
* **Tests con `pytest`:** escribe al menos 2 tests que usen `fastapi.testclient.TestClient` para cubrir: (a) `POST /misiones/` sin API key devuelve 401, (b) `GET /briefing/{nombre}` retorna la estructura esperada con datos locales + externos mockeados.

## 📦 Entregables

1. **Código** en la rama `reto_consolidacion`:
   * `agente.py`, `db.py`, `main.py`, `cliente.py` (y `config.py` si decides usarlo).
   * `tests/test_*.py` si eliges el reto eutagógico de pytest.
2. **Archivos de configuración:**
   * `.env.example` versionado, con las claves necesarias (sin valores).
   * `.gitignore` actualizado para excluir `.env`.
3. **Base de datos con datos semilla:** `agentes.db` con al menos **3 agentes**, **5 mensajes** y **3 misiones en estados distintos**.
4. **`README.md` del proyecto** con:
   * Cómo instalar dependencias y ejecutar (`uvicorn`, `cliente.py`).
   * Tabla de endpoints documentados.
   * Las tres **Decisiones de Ingeniería** justificadas.
   * Un apartado "Referencias consultadas" con enlaces a la documentación / artículos que usaste para investigar.
5. **Evidencia visual:** capturas del Swagger UI mostrando (a) un endpoint protegido respondiendo **401 sin key**, (b) el mismo respondiendo **200/201 con key válida**, y (c) `GET /briefing/{nombre}` devolviendo datos combinados.

## ✅ Criterios de Evaluación

Usa esta lista para auto-auditarte antes de abrir el PR:

- [ ] El servidor levanta sin errores con `uvicorn main:app --reload`.
- [ ] Todos los endpoints (los de Semana 5 + los nuevos) aparecen en `http://localhost:8000/docs`.
- [ ] Los endpoints de escritura (`POST /misiones/`, `POST /misiones/{id}/completar`, etc.) rechazan peticiones sin `X-API-KEY` válido con código **401**.
- [ ] `GET /briefing/{nombre}` retorna un JSON que mezcla datos locales del agente con información de una API externa.
- [ ] `cliente.py` ejecuta el flujo completo sin intervención manual y sin errores.
- [ ] Los datos persisten entre reinicios del servidor.
- [ ] En `main.py` **no hay llamadas a `print`**; todo registro pasa por `logger.*`.
- [ ] El archivo `.env` **no está versionado**; sí existe `.env.example`.
- [ ] Al despertar un agente con rol `"admin"`, `isinstance(agente, AgenteAdmin)` devuelve `True`; con cualquier otro rol, queda como `PseudoAgente`.
- [ ] El `README.md` del proyecto justifica las tres Decisiones de Ingeniería y lista las referencias consultadas.

## 🤖 Política de Vibecoding y Auditoría

La IA es una buena compañera para entender errores y leer documentación. No es una buena compañera para entregar trabajo que no entiendes. Úsala para desbloquearte, no para reemplazarte.

**Regla de auditoría:** deja un comentario con **tus propias palabras** exactamente encima de:

1. **La dependencia `verificar_api_key`** (o como la hayas llamado): explica en 2 líneas qué decidiste proteger, qué dejaste libre, y por qué.
2. **El endpoint `GET /briefing/{nombre}`:** explica en 2 líneas qué API externa elegiste y cuál fue tu plan de contingencia si falla.
3. **La configuración del `logging`:** explica en 2 líneas por qué elegiste los niveles que elegiste y qué formato de registro te pareció útil.

*Nota: entregas que mantengan `print(...)` en `main.py`, que tengan el archivo `.env` versionado, o cuyos endpoints protegidos acepten cualquier request (auth que no rechaza de verdad), no serán aprobadas.*

## 📚 Pistas de investigación

Estos son los términos con los que te recomendamos **empezar a buscar**. No son URLs: la búsqueda es parte del reto.

* `"FastAPI api key header dependency"`
* `"fastapi Depends header authentication"`
* `"python-dotenv load_dotenv"`
* `"os.environ getenv default value"`
* `"python logging basicConfig levels formatter"`
* `"requests timeout exception handling"`
* `"public APIs list no auth github"`
* `"pydantic v2 field_validator"` *(si eliges el reto eutagógico de validators)*
* `"fastapi TestClient pytest"` *(si eliges el reto eutagógico de tests)*

---

Este reto no tiene una única respuesta correcta. Lo que se evalúa es que **integres con coherencia todo lo que ya sabes**, que **investigues con criterio las cuatro áreas nuevas**, y que **documentes tus decisiones** como lo haría cualquier ingeniero de agentes. La Agencia es tuya — dale carácter. 🕶️
