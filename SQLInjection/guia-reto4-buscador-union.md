[← Índice de resolución](guia-resolucion-ctf.md) · [Reto 3](guia-reto3-csrf.md) · [Laboratorio](../lab/README.md)

# Reto 4 — Buscador vulnerable: UNION a ciegas de columnas (Medio)

**URL:** `/buscar/` · **Objetivo:** encontrar un documento confidencial
que no debería aparecer en los resultados de un buscador de empleados.

Este reto es **contenido para la audiencia**, no para tu demo en vivo
(dejaría el horario muy ajustado) — pero vale la pena resolverlo una vez
para poder responder preguntas si alguien te escribe después de la
charla. A diferencia de los Retos 1 y 2, la página **no te dice cuántas
columnas** tiene la consulta: hay que descubrirlo antes de poder extraer
el documento.

---

### Paso 1 — Reconocimiento (búsqueda normal)

Abre **http://127.0.0.1:8000/buscar/** (con el servidor en
`LAB_MODE=vulnerable`) y busca algo normal, como `Ana`, para ver cómo se
ven los resultados cuando todo funciona bien: una tabla con dos columnas
(nombre, cargo).

### Paso 2 — Confirmar la inyección

Busca algo que rompa la sintaxis SQL, como una comilla simple:

```
'
```

**Qué deberías ver:** el banner de error "⚠️ Error en la búsqueda: revisa
la sintaxis." Confirma que el input se concatena directo en la consulta,
igual que en el Reto 1/2 pero en otro endpoint — la vulnerabilidad no
vive solo en el login.

### Paso 3 — Descubrir el número de columnas con ORDER BY

Como acá no se te dice cuántas columnas devuelve la consulta original,
pruebas incrementando el número hasta que uno falle:

```
algo' ORDER BY 1-- 
algo' ORDER BY 2-- 
algo' ORDER BY 3-- 
```

El número anterior al que falla (da error de sintaxis o "columna fuera
de rango") es la cantidad real de columnas. En este laboratorio son 2 —
lo puedes confirmar tú mismo repitiendo estos tres intentos.

### Paso 4 — Construir el UNION hacia la otra tabla

Con el número de columnas confirmado (2), en el campo de búsqueda
escribe:

```
algo' UNION SELECT titulo, contenido FROM documentos_confidenciales -- 
```

**Qué deberías ver:** en la tabla de resultados aparece el título y
contenido de un documento que no tiene nada que ver con empleados —
dentro del contenido está la flag
(`AIEP{sqli_union_columnas_a_ciegas_2026}` por defecto, configurable vía
`LAB_FLAG_4`), que la página también resalta en un banner verde aparte.

**Por qué funciona — la explicación técnica**
(código real en [lab/accounts/views.py](../lab/accounts/views.py)):

```python
def _buscar_vulnerable(q):
    query = f"""
        SELECT nombre, cargo FROM empleados
        WHERE nombre LIKE '%{q}%'
    """
    ...
```

Igual que en el login, el input se concatena directo en el SQL — pero
acá dentro de un `LIKE '%...%'`. El `UNION SELECT` funciona con la misma
lógica del Reto 2: mientras tenga el mismo número de columnas que la
consulta original (`nombre, cargo` → 2 columnas), puede "disfrazar"
cualquier otra tabla dentro de esas dos columnas — en este caso,
`documentos_confidenciales`, una tabla que la aplicación nunca pensó
exponer desde el buscador de empleados.

**Verificación rápida por línea de comandos** (útil si desplegaste en
Railway y quieres confirmar sin usar el navegador):

```powershell
curl -G "https://charlaaiep-production.up.railway.app/buscar/" ´
  --data-urlencode "q=' UNION SELECT titulo, contenido FROM documentos_confidenciales -- "
```

### En modo corregido

```powershell
$env:LAB_MODE = "secure"
```

Con el servidor en modo `secure`, `_buscar_seguro` usa el ORM de Django
(`Empleado.objects.filter(nombre__icontains=q)`), que nunca concatena tu
input dentro de un string SQL — el mismo principio de los Retos 1 y 2.

---

Siguiente: [Reto 5 — Blind boolean-based SQLi](guia-reto5-blind-boolean.md)
