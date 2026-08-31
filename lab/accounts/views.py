import re

from django.conf import settings
from django.db import connection
from django.db.utils import Error as DatabaseError
from django.contrib.auth import authenticate, login
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt

from accounts import flags

FLAG_PATTERN = re.compile(r"AIEP\{[^}]+\}")

RESULT_STATUS = {
    "flag": 200,
    "success": 200,
    "invalid": 401,
    "sql_error": 500,
}


def hub_view(request):
    return render(request, "accounts/hub.html", {"mode": settings.LAB_MODE})


FLAG_BY_VALUE = {
    flags.FLAG_1: 1,
    flags.FLAG_2: 2,
    flags.FLAG_3: 3,
    flags.FLAG_4: 4,
    flags.FLAG_5: 5,
}


def comprobar_flag_view(request):
    """Autoverificación: pega una flag y confirma a qué reto pertenece."""
    context = {"mode": settings.LAB_MODE, "flag": "", "reto": None, "checked": False}
    flag = request.GET.get("flag", "").strip()
    if flag:
        context["flag"] = flag
        context["checked"] = True
        context["reto"] = FLAG_BY_VALUE.get(flag)
    return render(request, "accounts/comprobar_flag.html", context)


# --- Reto 1 y 2: bypass de login + extracción con UNION -------------------

def login_view(request):
    context = {"mode": settings.LAB_MODE, "result": None}
    status = 200

    if request.method == "POST":
        username = request.POST.get("username", "")
        password = request.POST.get("password", "")

        if settings.LAB_MODE == "vulnerable":
            context["result"] = _login_vulnerable(username, password)
        else:
            context["result"] = _login_secure(request, username, password)

        status = RESULT_STATUS[context["result"]["type"]]

    return render(request, "accounts/login.html", context, status=status)


def _flag_or_success(username):
    if username == "admin":
        return {"type": "flag", "username": username, "flag": flags.FLAG_1}
    if isinstance(username, str) and username.startswith("pbkdf2_sha256$"):
        return {"type": "flag", "username": username, "flag": flags.FLAG_2}
    return {"type": "success", "username": username}


def _login_vulnerable(username, password):
    """Reto 1/2 (ejercicios-practicos.md): SQLi por f-string.

    NUNCA construir SQL así en código real. Existe únicamente para la
    demo controlada del laboratorio (LAB_MODE=vulnerable). El error de
    base de datos se captura para no filtrar la página de depuración de
    Django (que en producción expondría SECRET_KEY, rutas y variables de
    entorno) — se reemplaza por un mensaje genérico, igual de útil para
    el paso de reconocimiento del reto.
    """
    query = f"""
        SELECT id, username FROM auth_user
        WHERE username = '{username}' AND password = '{password}'
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            user = cursor.fetchone()
    except DatabaseError:
        return {"type": "sql_error"}

    if user:
        return _flag_or_success(user[1])
    return {"type": "invalid"}


def _login_secure(request, username, password):
    """Corrección: ORM + autenticación nativa de Django (hash + parametrizado)."""
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        return _flag_or_success(user.username)
    return {"type": "invalid"}


# --- Reto 3: transferencia sin protección CSRF -----------------------------

def reto3_view(request):
    return render(request, "accounts/reto3.html", {"mode": settings.LAB_MODE})


@csrf_exempt
def transferir_fondos(request):
    """Ejercicio de reserva: endpoint sensible sin protección CSRF real
    cuando LAB_MODE=vulnerable (ver settings.LAB_MODE / SESSION_COOKIE_*).
    En modo seguro, quitar @csrf_exempt sería el primer paso de la corrección;
    aquí se deja el decorador para poder mostrar el contraste sin necesitar
    dos vistas distintas. Responde JSON porque se llama con fetch() desde
    la consola del navegador (ver accounts/reto3.html).
    """
    if settings.LAB_MODE != "vulnerable" or request.method != "POST":
        return JsonResponse({"error": "forbidden"}, status=403)

    monto = request.POST.get("monto", "0")
    destino = request.POST.get("destino", "")
    return JsonResponse({
        "ok": True,
        "mensaje": f"Transferencia simulada de {monto} a '{destino}' — sin validar CSRF ni origen.",
        "flag": flags.FLAG_3,
    })


# --- Reto 4: buscador vulnerable (UNION en otra tabla) ---------------------

def buscar_view(request):
    context = {"mode": settings.LAB_MODE, "q": "", "rows": None, "error": None, "flag": None}
    q = request.GET.get("q", "")
    context["q"] = q

    if q:
        if settings.LAB_MODE == "vulnerable":
            context.update(_buscar_vulnerable(q))
        else:
            context.update(_buscar_seguro(q))

    return render(request, "accounts/buscar.html", context)


def _buscar_vulnerable(q):
    query = f"""
        SELECT nombre, cargo FROM empleados
        WHERE nombre LIKE '%{q}%'
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            rows = cursor.fetchall()
    except DatabaseError:
        return {"error": "Error en la búsqueda: revisa la sintaxis."}

    flag_found = None
    for row in rows:
        for cell in row:
            match = FLAG_PATTERN.search(str(cell))
            if match:
                flag_found = match.group(0)

    return {"rows": rows, "flag": flag_found}


def _buscar_seguro(q):
    from accounts.models import Empleado

    empleados = Empleado.objects.filter(nombre__icontains=q).values_list("nombre", "cargo")
    return {"rows": list(empleados)}


# --- Reto 5: blind boolean-based SQLi --------------------------------------

def verificar_view(request):
    context = {"mode": settings.LAB_MODE, "usuario": "", "resultado": None, "error": None}
    usuario = request.GET.get("usuario", "")
    context["usuario"] = usuario

    if usuario:
        if settings.LAB_MODE == "vulnerable":
            context.update(_verificar_vulnerable(usuario))
        else:
            context.update(_verificar_seguro(usuario))

    return render(request, "accounts/verificar.html", context)


def _verificar_vulnerable(usuario):
    """Solo responde disponible/no-disponible — sin errores visibles ni
    datos reflejados, así que la única forma de extraer algo es a ciegas
    con condiciones booleanas (ver accounts/verificar.html para pistas)."""
    query = f"SELECT 1 FROM auth_user WHERE username = '{usuario}'"
    try:
        with connection.cursor() as cursor:
            cursor.execute(query)
            existe = cursor.fetchone() is not None
    except DatabaseError:
        return {"error": "Hubo un error al verificar. Revisa la sintaxis de tu consulta."}

    return {"resultado": "no_disponible" if existe else "disponible"}


def _verificar_seguro(usuario):
    from django.contrib.auth.models import User

    existe = User.objects.filter(username=usuario).exists()
    return {"resultado": "no_disponible" if existe else "disponible"}
