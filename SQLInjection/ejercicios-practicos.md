[← Volver al índice](CharlaCiberseguridad.md)

# Ejercicios prácticos

## Ejercicio principal — SQL Injection: bypass de login

**Escenario:** login de una app Django de ejemplo ("Intranet Ficticia"), en un entorno de laboratorio aislado.

**Código vulnerable (`views.py`):**
```python
from django.db import connection
from django.http import HttpResponse

def login_view(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")

    query = f"""
        SELECT id, username FROM auth_user
        WHERE username = '{username}' AND password = '{password}'
    """
    with connection.cursor() as cursor:
        cursor.execute(query)
        user = cursor.fetchone()

    if user:
        return HttpResponse(f"Bienvenido, {user[1]}")
    return HttpResponse("Credenciales inválidas", status=401)
```

**Explotación paso a paso (solo en el laboratorio, nunca en producción):**
1. **Reconocimiento:** probar una comilla simple `'` en el campo usuario → error de SQL visible → confirma que hay inyección.
2. **Bypass de autenticación:** usuario `admin' -- ` con cualquier contraseña → el `--` comenta el resto de la consulta y la condición de password deja de evaluarse.
3. **(Reserva, si el tiempo alcanza) Extracción de datos con UNION:** `' UNION SELECT id, password FROM auth_user -- `.
4. **Cierre del reto:** acceso como admin sin conocer la contraseña real — esa es la "flag" del CTF.

**Corrección — ORM + autenticación nativa de Django:**
```python
from django.contrib.auth import authenticate, login
from django.http import HttpResponse

def login_view(request):
    username = request.POST.get("username", "")
    password = request.POST.get("password", "")

    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return HttpResponse(f"Bienvenido, {user.username}")
    return HttpResponse("Credenciales inválidas", status=401)
```

**Por qué funciona:** `authenticate()` usa consultas parametrizadas internamente y compara el *hash* de la contraseña, nunca texto plano. Si en algún caso necesitas SQL crudo, usa siempre parámetros: `cursor.execute("SELECT id FROM auth_user WHERE username = %s", [username])` — nunca f-strings ni `.format()`.

---

## Ejercicio de reserva — Autenticación rota / gestión de sesión

**Configuración insegura (`settings.py`):**
```python
SESSION_COOKIE_HTTPONLY = False
CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False

# en una vista:
@csrf_exempt
def transferir_fondos(request):
    ...
```

**Qué se explota:** con `HTTPONLY = False`, un XSS podría robar la cookie de sesión vía JavaScript; sin protección CSRF, un sitio malicioso puede forzar una petición autenticada (ej. transferir fondos) sin que la víctima se entere.

**Corrección:**
```python
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_SECURE = True
# quitar @csrf_exempt salvo excepción justificada (ej. webhook verificado por firma)
```
