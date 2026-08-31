[← Volver al índice](CharlaCiberseguridad.md) · [Laboratorio](../lab/README.md) · [Despliegue en Railway](guia-despliegue-railway.md)

# Guía de resolución del CTF (SQLi en "Intranet Ficticia")

Esta guía es el punto de entrada para la tarea del **15–16 ago** del
cronograma: hacer la primera resolución completa del reto, cronometrando
el tiempo real. Cada reto tiene su propia guía detallada — sigue cada
paso en orden, sin saltarte el "por qué", es lo que después vas a
explicar en vivo el 28 de agosto.

## Las 5 guías, una por reto

| # | Reto | Dificultad | Para tu demo en vivo | Guía |
|---|------|------------|:---:|------|
| 1 | Bypass de autenticación | Fácil | ✅ | [guia-reto1-bypass-login.md](guia-reto1-bypass-login.md) |
| 2 | Extracción con UNION (hash de admin) | Medio | ✅ | [guia-reto2-union-hash.md](guia-reto2-union-hash.md) |
| 3 | Transferencia sin protección CSRF | Medio | reserva | [guia-reto3-csrf.md](guia-reto3-csrf.md) |
| 4 | Buscador vulnerable (UNION a ciegas de columnas) | Medio | audiencia | [guia-reto4-buscador-union.md](guia-reto4-buscador-union.md) |
| 5 | Blind boolean-based SQLi | Avanzado | audiencia | [guia-reto5-blind-boolean.md](guia-reto5-blind-boolean.md) |

Los retos 1 y 2 son el **ejercicio principal** y el 3 el **ejercicio de
reserva** de [ejercicios-practicos.md](ejercicios-practicos.md) — son los
que cubre tu demo en vivo. Los retos 4 y 5 son contenido adicional
pensado para que la audiencia profundice por su cuenta después de la
charla, pero conviene resolverlos una vez para poder responder preguntas.

---

## 0. Antes de empezar

**Prerrequisitos:**
- Laboratorio instalado ([lab/README.md](../lab/README.md), pasos 1 y 2 ya
  hechos: `migrate` + `seed_lab` corridos al menos una vez).
- Navegador abierto (Chrome/Edge/Firefox, cualquiera sirve).
- Un cronómetro (celular, o el de Windows) — parte del objetivo de esta
  sesión es medir cuánto toma realmente, no solo verificar que funciona.

**Levantar el servidor en modo vulnerable:**

```powershell
cd "C:\Users\JONA\Desktop\Charla AIEP\lab"
$env:LAB_MODE = "vulnerable"
.\.venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000
```

> Si al ejecutar `python.exe` PowerShell dice que no reconoce la ruta,
> es casi siempre porque la terminal no está parada en `lab` (revisa con
> `Get-Location`). El `cd` con ruta completa de arriba soluciona eso sin
> importar dónde estuviera parada antes la terminal.

**Alternativa más cómoda para la demo en vivo/grabación** (activa el venv
una vez y después solo escribes `python`, se ve más limpio en pantalla):

```powershell
cd "C:\Users\JONA\Desktop\Charla AIEP\lab"
.\.venv\Scripts\Activate.ps1
$env:LAB_MODE = "vulnerable"
python manage.py runserver 127.0.0.1:8000
```

Vas a ver `(.venv)` al inicio del prompt cuando esté activo. Para
desactivar: `deactivate`.

Deja esa ventana abierta (ahí se ve el log de cada request, útil para
mostrar en la charla). Abre en el navegador: **http://127.0.0.1:8000/retos/**
(el hub lista los 5 retos).

Vas a ver el login con el logo y tu firma en el pie. Justo encima del
formulario debe aparecer la etiqueta roja **"● Modo práctica (CTF)"**. Si
en cambio aparece la etiqueta verde "Versión corregida", revisa que hayas
definido `$env:LAB_MODE` **antes** de lanzar `runserver` (no se puede
cambiar en caliente, hay que reiniciar el servidor).

▶️ **Inicia el cronómetro ahora**, y sigue con
[guia-reto1-bypass-login.md](guia-reto1-bypass-login.md).

---

## Checklist de capturas de pantalla

Guárdalo para la tarea del **17–18 ago** (segunda resolución + capturas).
Una captura por punto, mostrando **el formulario con el payload escrito**
y **la respuesta del servidor**:

- [ ] Login con datos inválidos normales → banner rojo (línea base) — [Reto 1](guia-reto1-bypass-login.md)
- [ ] Comilla simple → banner ámbar de error SQL — [Reto 1](guia-reto1-bypass-login.md)
- [ ] `admin' -- ` → banner verde con la flag — [Reto 1](guia-reto1-bypass-login.md)
- [ ] UNION → banner verde con el hash de la contraseña — [Reto 2](guia-reto2-union-hash.md)
- [ ] Código vulnerable (`_login_vulnerable` en views.py)
- [ ] Mismo bypass en modo `secure` → banner rojo "Credenciales inválidas" — [Reto 1](guia-reto1-bypass-login.md)
- [ ] Login legítimo en modo `secure` → banner verde "Bienvenido, juan.perez" — [Reto 1](guia-reto1-bypass-login.md)
- [ ] Código corregido (`_login_secure` en views.py)
- [ ] (opcional) Transferencia sin CSRF → flag — [Reto 3](guia-reto3-csrf.md)
- [ ] (opcional) UNION en buscador → documento confidencial — [Reto 4](guia-reto4-buscador-union.md)
- [ ] (opcional) Blind boolean → flag extraída con el script — [Reto 5](guia-reto5-blind-boolean.md)

## Plantilla para cronometrar

| Intento | Fecha | Reto 1 (bypass) | + Reto 2 (UNION) | Notas |
|---|---|---|---|---|
| 1 (15–16 ago) | | | | |
| 2 (17–18 ago) | | | | |

## Errores comunes al practicar

- **El bypass no funciona y esperabas que sí:** confirma que el servidor
  esté realmente en `LAB_MODE=vulnerable` — la página lo indica arriba
  del formulario. `runserver` no relee la variable de entorno si ya
  estaba corriendo: hay que pararlo (`Ctrl+C`) y volver a lanzarlo.

Cada guía de reto tiene además su propia sección de errores comunes
específicos de ese endpoint (ej. CSRF del formulario de login en el
[Reto 1](guia-reto1-bypass-login.md)).

## Siguiente paso del cronograma

Con esta guía corrida al menos una vez y los tiempos anotados, sigue con
**17–18 ago**: segunda resolución cronometrada + capturas de cada paso
(usa el checklist de arriba).
