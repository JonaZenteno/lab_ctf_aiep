[← Índice de resolución](guia-resolucion-ctf.md) · [Laboratorio](../lab/README.md) · [Despliegue en Railway](guia-despliegue-railway.md)

# Reto 1 — Bypass de autenticación (Fácil)

**URL:** `/login/` · **Objetivo:** entrar como `admin` sin conocer su clave.

Antes de empezar, revisa **"0. Antes de empezar"** en el
[índice de resolución](guia-resolucion-ctf.md) para levantar el servidor
en `LAB_MODE=vulnerable`. Abre **http://127.0.0.1:8000/login/**.

Vas a ver el login con dos campos, `usuario` y `contraseña`. Justo encima
del formulario debe aparecer la etiqueta roja **"● Modo práctica
(CTF)"**.

---

### Paso 1 — Reconocimiento visual (~1 min)

Prueba primero con datos inventados, ej. `usuario=x`, `contraseña=x`, y
confirma el comportamiento "normal": aparece un banner rojo
"⛔ Credenciales inválidas" (HTTP 401). Esto establece la línea base:
sabemos cómo se ve un intento fallido *normal*, para poder notar cuando
algo se comporta distinto.

### Paso 2 — Confirmar la inyección con una comilla simple (~2 min)

En el campo **usuario** escribe literalmente:

```
admin'
```

Deja la contraseña con cualquier valor y envía el formulario.

**Qué deberías ver:** un banner ámbar "⚠️ Error de base de datos: sintaxis
SQL inválida..." (HTTP 500) — no el banner rojo de credenciales
inválidas. Es un mensaje controlado, no la página de depuración de
Django: en el laboratorio local eso es solo estética, pero en el
despliegue público ([guia-despliegue-railway.md](guia-despliegue-railway.md))
es lo que evita filtrar `SECRET_KEY` y otras variables internas a
cualquiera en internet.

**Por qué pasa esto — la explicación técnica:**

La vista arma la consulta así (código real en
[lab/accounts/views.py](../lab/accounts/views.py)):

```python
query = f"""
    SELECT id, username FROM auth_user
    WHERE username = '{username}' AND password = '{password}'
"""
```

El servidor toma literalmente lo que escribiste y lo pega dentro de las
comillas de la consulta SQL. Con `admin'`, la consulta que realmente se
ejecuta queda así:

```sql
SELECT id, username FROM auth_user
WHERE username = 'admin'' AND password = 'x'
```

La comilla extra rompe la sintaxis: ahora hay tres comillas seguidas
donde SQLite espera un cierre y una continuación coherente, y la
consulta queda mal formada → error de sintaxis SQL.

**Por qué importa este paso (aunque no "logra" nada por sí solo):** un
error de SQL visible es la señal más clásica de que el input del usuario
está siendo interpretado como código, no como dato. Es el primer paso de
cualquier explotación real de inyección SQL: encontrar el punto donde la
app "confía" en lo que escribiste.

### Paso 3 — Construir y ejecutar el bypass de autenticación (~3 min)

Ahora, en el campo **usuario**, escribe:

```
admin' -- 
```
*(nota el espacio después de `--`; en SQLite y Postgres es buena práctica
dejarlo — en MySQL es obligatorio)*

Contraseña: **cualquier cosa**, no importa (ej. `x`). Envía el formulario.

**Qué deberías ver:** un banner verde "🚩 ¡Bypass exitoso!" con la flag
del reto en un recuadro oscuro, status 200. Estás autenticado como
`admin` sin haber escrito su clave.

**Por qué funciona — paso a paso:**

La consulta que se arma es:

```sql
SELECT id, username FROM auth_user
WHERE username = 'admin' -- ' AND password = 'x'
```

Dos cosas pasan a la vez:

1. `--` es un comentario de línea en SQL: todo lo que sigue en esa misma
   línea (` ' AND password = 'x'`) deja de ser parte de la consulta.
   Elimina por completo la verificación de contraseña.
2. Lo que realmente ejecuta la base de datos es:
   ```sql
   SELECT id, username FROM auth_user WHERE username = 'admin'
   ```
   Es decir: "dame el usuario que se llama admin", sin condición de
   contraseña. Como `admin` existe en la tabla, la consulta devuelve una
   fila y la vista concluye que el login fue exitoso.

**El concepto detrás:** esto se llama *comment injection* o
*authentication bypass vía SQLi*. No estás "adivinando" la contraseña —
estás modificando la pregunta que la aplicación le hace a la base de
datos para que la contraseña deje de importar.

**Esta es la flag del reto:** llegaste a la sesión de `admin` sin conocer
su clave real, y la página te la muestra en pantalla
(`AIEP{sqli_bypass_admin_sin_clave_2026}` por defecto — configurable vía
`LAB_FLAG`, ver [lab/accounts/views.py](../lab/accounts/views.py)). Anota tu
tiempo total hasta aquí (ver plantilla de cronometraje en el
[índice](guia-resolucion-ctf.md)).

---

## Extra recomendado para la charla — detectarlo con SAST (Bandit)

Tu público es ingeniería en ciberseguridad, no solo desarrolladores: les va
a interesar más ver la **herramienta real** que detecta esto que otro
payload a mano. Bandit (mencionado en
[preguntas-frecuentes.md](preguntas-frecuentes.md) #4) es un SAST de
Python — lo instalas una vez en el venv del lab:

```powershell
cd "C:\Users\JONA\Desktop\Charla AIEP\lab"
.\.venv\Scripts\pip.exe install bandit
.\.venv\Scripts\bandit.exe accounts/views.py
```

Salida real contra este código (verificada, no es un ejemplo inventado):

```
>> Issue: [B608:hardcoded_sql_expressions] Possible SQL injection vector
   through string-based query construction.
   Severity: Medium   Confidence: Low   CWE: CWE-89
   Location: .\accounts/views.py:85   (dentro de _login_vulnerable)
   Location: .\accounts/views.py:154  (dentro de _buscar_vulnerable)
   Location: .\accounts/views.py:202  (dentro de _verificar_vulnerable)
```

**El punto para la charla:** Bandit señala exactamente las 3 funciones que
arman SQL con f-strings (Retos 1/2, 4 y 5) — y no dice absolutamente nada
de `_login_secure` ni `_buscar_seguro`, que están a pocas líneas de
distancia **en el mismo archivo** y usan el ORM. No necesitas reiniciar el
servidor ni cambiar `LAB_MODE` para este demo: el antes/después están los
dos en el mismo archivo, uno al lado del otro. Es la forma más rápida de
mostrar "esto es lo que un pipeline de CI/CD atraparía antes de que llegue
a producción" (FAQ #12).

---

## Verificar que la corrección funciona

Esta parte no está cronometrada, pero es igual de importante: le da a la
charla su segunda mitad ("la otra cara: cómo se corrige").

**Reinicia el servidor en modo seguro** (`Ctrl+C` en la terminal del
servidor, luego):

```powershell
$env:LAB_MODE = "secure"
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Recarga http://127.0.0.1:8000/login/ — la etiqueta debe cambiar a la
verde **"● Versión corregida"**.

### Repetir el bypass (debe fallar)

Prueba de nuevo `admin' -- ` con cualquier contraseña.

**Qué deberías ver:** el mismo banner rojo "⛔ Credenciales inválidas"
(401) de cualquier intento inválido — no hay flag ni banner verde.

**Por qué ahora falla — leyendo el código corregido**
([lab/accounts/views.py](../lab/accounts/views.py), función `_login_secure`):

```python
def _login_secure(request, username, password):
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return _flag_or_success(user.username)
    return {"type": "invalid"}
```

`authenticate()` nunca concatena tu input dentro de un string SQL. Por
dentro, usa el ORM de Django, que separa **siempre** el texto de la
consulta de los valores (consultas parametrizadas / *prepared
statements*): el driver de base de datos recibe la consulta con
marcadores de posición y los valores por otro canal, así que no existe
forma de que `admin' --` "se escape" de ser un valor y se convierta en
código SQL. Además, compara contra el *hash* de la contraseña, nunca
contra texto plano — por eso ni siquiera un `' OR '1'='1` serviría para
falsificar la comparación de password.

### Confirmar que el login legítimo sí funciona

Con usuario `juan.perez` y contraseña `juan2026`
(ver [lab/README.md](../lab/README.md) para la lista completa de usuarios de
demo): debe responder con el banner verde "✅ Bienvenido, juan.perez".
Si en cambio pruebas con `admin` y su clave real
(`admin2026`), vas a ver el mismo banner de flag de arriba —
tiene sentido: la flag se revela cada vez que el login exitoso es como
`admin`, sin importar si fue por el bug o por la clave correcta.

Esto es clave para el argumento de la charla: la corrección **no rompe la
funcionalidad**, solo cierra la puerta que no debía estar abierta.

## Errores comunes de este reto

- **"Forbidden (403) CSRF verification failed"** al enviar el formulario:
  asegúrate de no haber recargado la página con datos en caché de otra
  sesión; recarga `/login/` de cero antes de reintentar (el token CSRF
  cambia por sesión).
- **El login legítimo falla en modo `secure`:** revisa que estés
  escribiendo la contraseña exacta de [lab/README.md](../lab/README.md) —
  son sensibles a mayúsculas/símbolos.
- **El login legítimo (usuario y contraseña reales) da "Credenciales
  inválidas" en modo `vulnerable`:** esto es esperado, no un bug. La
  consulta cruda compara tu contraseña en texto plano contra la columna
  `password` de `auth_user`, que Django siempre guarda hasheada
  (`pbkdf2_sha256$...`) — nunca van a calzar. En modo `vulnerable` solo
  funcionan los payloads de inyección (`admin' -- `, el `UNION`, etc.);
  para probar un login normal hay que cambiar a `LAB_MODE=secure`.

---

Siguiente: [Reto 2 — Extracción con UNION](guia-reto2-union-hash.md)
