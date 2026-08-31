[← Guía completa del CTF](../README.md) · [Índice del material](../SQLInjection/CharlaCiberseguridad.md) · [Ejercicios prácticos](../SQLInjection/ejercicios-practicos.md) · [Guía de resolución](../SQLInjection/guia-resolucion-ctf.md) · [Despliegue en Railway](../SQLInjection/guia-despliegue-railway.md)

# Laboratorio: "Intranet Ficticia"

Entorno Django real (no un mock) con **5 retos de inyección SQL** (más uno
de CSRF) de dificultad creciente, todos con un único interruptor para
pasar de la versión **vulnerable** a la versión **corregida**. Incluye
estética de marca (logo AIEP + firma HubInnova), pistas progresivas en
cada página y una flag distinta por reto, para poder usarlo tanto en
local durante la demo como públicamente (ver
[guía de despliegue en Railway](../SQLInjection/guia-despliegue-railway.md)) para que
la audiencia lo resuelva desde su propio dispositivo.

| # | Reto | Dificultad | URL |
|---|------|------------|-----|
| 1 | Bypass de autenticación | Fácil | `/login/` |
| 2 | Extracción con UNION (hash de admin) | Medio | `/login/` |
| 3 | Transferencia sin protección CSRF | Medio | `/reto3/` |
| 4 | Buscador vulnerable (UNION a ciegas de columnas) | Medio | `/buscar/` |
| 5 | Blind boolean-based SQLi | Avanzado | `/verificar/` |

Los retos 1 y 2 son el **ejercicio principal** y el 3 el **ejercicio de
reserva** de [ejercicios-practicos.md](../SQLInjection/ejercicios-practicos.md) — son
los que cubre tu demo en vivo. Los retos 4 y 5 son contenido adicional
pensado para que la audiencia profundice por su cuenta después de la
charla (ver [guia-resolucion-ctf.md](../SQLInjection/guia-resolucion-ctf.md)).

**El servidor local (`runserver`) es solo para practicar en tu equipo —
nunca lo expongas directo a internet.** Para una URL pública usa el
despliegue de Railway, que ya viene con `DEBUG=False` y manejo de errores
sin filtrar información sensible.

## 1. Puesta en marcha (una sola vez)

```powershell
cd "lab"
python -m venv .venv
.\.venv\Scripts\pip.exe install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_lab
```

`seed_lab` crea dos usuarios de demo en la tabla `auth_user` (idempotente,
se puede correr de nuevo cuando quieras):

| usuario      | password                  | rol      |
|--------------|----------------------------|----------|
| `admin`      | `admin2026`   | superuser (la "flag" del CTF: entrar como este usuario sin la clave) |
| `juan.perez` | `juan2026`    | usuario normal (sirve para mostrar el login legítimo funcionando) |

## 2. Levantar el servidor

Elegir el modo con la variable de entorno `LAB_MODE` **antes** de lanzar
`runserver` (por defecto, si no se define, es `secure`):

```powershell
# Modo vulnerable (para la explotación en vivo)
$env:LAB_MODE = "vulnerable"
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000

# Modo corregido (para mostrar la versión parchada)
$env:LAB_MODE = "secure"
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

Abrir http://127.0.0.1:8000/retos/ — el hub con los 5 retos, la página
muestra el modo activo arriba de cada uno.

> Nota práctica para la demo en vivo: cerrar el servidor (`Ctrl+C`) antes de
> cambiar `$env:LAB_MODE`, porque `runserver` no relee variables de entorno
> en caliente. Ensayar el cambio de modo con antelación para que no tome
> tiempo el día de la charla.

## 3. Guion de explotación — retos 1 a 3 (tu demo en vivo)

Sigue el paso a paso de [ejercicios-practicos.md](../SQLInjection/ejercicios-practicos.md)
y de [guia-resolucion-ctf.md](../SQLInjection/guia-resolucion-ctf.md):

1. **Reconocimiento** — usuario `admin'` (una comilla simple) → mensaje
   controlado de error de base de datos (HTTP 500) que confirma la
   inyección, sin exponer la página de depuración de Django.
2. **Reto 1 — Bypass de autenticación** — usuario `admin' -- ` con
   cualquier contraseña → se revela la flag del reto en un banner verde.
3. **Reto 2 — Extracción con UNION** — usuario
   `' UNION SELECT id, password FROM auth_user -- ` → devuelve el *hash*
   de la contraseña de admin y su propia flag.
4. **Reto 3 — Transferencia sin CSRF** (`/reto3/`) — un botón en pantalla
   ejecuta `POST /transferir/` sin token; funciona igual, revela la flag.

En modo `secure`, los tres retos anteriores dejan de funcionar: el login
solo acepta `admin` / `juan.perez` con su contraseña real vía
`authenticate()`/`login()` de Django, y `/transferir/` responde 403.

## 4. Retos 4 y 5 — contenido adicional para la audiencia

No forman parte de tu demo en vivo (dejarían el horario muy ajustado);
son para que quien quiera profundizar los resuelva por su cuenta:

- **Reto 4** (`/buscar/`) — un buscador, no un login, vulnerable a UNION.
  A diferencia del Reto 2, no se dice cuántas columnas tiene la consulta:
  hay que descubrirlo con `ORDER BY` antes de poder extraer un documento
  de otra tabla.
- **Reto 5** (`/verificar/`) — blind boolean-based SQLi: sin errores, sin
  datos visibles, solo "Disponible"/"No disponible". La página incluye un
  script de ejemplo en Python para automatizar la extracción carácter por
  carácter.

Cada página trae sus propias pistas progresivas (ocultas por defecto, se
despliegan con un clic) — no hace falta explicarlas tú mismo.

## 5. Estructura

```
lab/
  manage.py
  requirements.txt
  Procfile                              comando de arranque para Railway
  .python-version
  intranet/                             proyecto Django (settings con el toggle LAB_MODE)
  accounts/
    flags.py                            las 5 constantes de flag (configurables vía env vars)
    models.py                           Empleado, DocumentoConfidencial, Secreto (retos 4 y 5)
    views.py                            hub_view + las vistas de los 5 retos
    urls.py
    templates/accounts/
      base.html                         header/footer/CSS compartido (marca AIEP/HubInnova)
      hub.html, login.html, reto3.html, buscar.html, verificar.html
    static/accounts/img/                logo-aiep.png, firma-hubinnova.jpg
    management/commands/seed_lab.py     usuarios + datos de los retos 4 y 5
```

Los retos 1, 2, 3 y 5 usan la misma tabla `auth_user` que crea
`django.contrib.auth` (leyéndola con SQL crudo en modo vulnerable, con el
ORM en modo seguro). El Reto 4 usa dos tablas propias
(`empleados`, `documentos_confidenciales`) para mostrar que la inyección
no vive solo en el login.
