[← Índice de resolución](guia-resolucion-ctf.md) · [Reto 1](guia-reto1-bypass-login.md) · [Laboratorio](../lab/README.md)

# Reto 2 — Extracción con UNION (Medio)

**URL:** `/login/` (mismo formulario que el Reto 1) · **Objetivo:**
extraer el *hash* de la contraseña de `admin` sin usar el bypass.

Este reto es opcional para tu primera resolución, pero vale la pena
practicarlo porque suele impresionar más en una demo en vivo que el
bypass solo. Requiere el mismo servidor en `LAB_MODE=vulnerable` del
[Reto 1](guia-reto1-bypass-login.md) — no hace falta reiniciarlo si ya lo
tienes corriendo.

---

### El payload (~5 min si el tiempo alcanza)

En el campo **usuario** de `/login/`, escribe:

```
' UNION SELECT id, password FROM auth_user -- 
```

Contraseña: cualquier cosa. Envía.

**Qué deberías ver:** un banner verde "✅ Bienvenido," seguido de algo
como `pbkdf2_sha256$870000$...$...` — en el lugar donde normalmente
aparece el nombre de usuario, ahora aparece el **hash** de la contraseña
de `admin`, junto con la flag del reto
(`AIEP{sqli_union_extrae_el_hash_2026}` por defecto, configurable vía
`LAB_FLAG_2`).

**Por qué funciona:**

`UNION SELECT` permite combinar el resultado de dos consultas `SELECT`
distintas, **siempre que tengan el mismo número de columnas** (acá la
consulta original pide 2: `id, username`, así que la nuestra también debe
pedir 2). La consulta resultante es:

```sql
SELECT id, username FROM auth_user WHERE username = ''
UNION
SELECT id, password FROM auth_user -- ' AND password = 'x'
```

La primera mitad (`WHERE username = ''`) no devuelve nada — no existe un
usuario con nombre vacío. La segunda mitad, gracias al `UNION`, sí
devuelve filas: pide `id, password` pero las "disfraza" en las mismas
columnas que la app espera (`id, username`), así que la vista las muestra
sin saber que en realidad está mostrando contraseñas.

**Por qué obtienes un *hash* y no la clave en texto plano:** porque
Django guarda las contraseñas siempre hasheadas (PBKDF2 por defecto,
nunca texto plano), incluso en este laboratorio. Es justo la situación
real de una filtración de base de datos: el atacante rara vez obtiene la
clave directamente, obtiene el hash y tendría que intentar crackearlo
offline. Vale la pena mencionar esto en la charla — refuerza por qué
hashear contraseñas importa incluso cuando "todo lo demás" ya falló.

### En modo corregido

Este payload usa el mismo endpoint y la misma función vulnerable que el
Reto 1 (`_login_vulnerable`), así que la corrección es idéntica: en
`LAB_MODE=secure`, `_login_secure` usa `authenticate()` (ORM +
consultas parametrizadas) y el `UNION SELECT` deja de tener efecto —
solo se acepta `username`/`password` como valores literales, nunca como
código SQL. Ver el detalle completo en la sección "Verificar que la
corrección funciona" del [Reto 1](guia-reto1-bypass-login.md).

---

Siguiente: [Reto 3 — Transferencia sin CSRF](guia-reto3-csrf.md)
