[← Volver al índice](CharlaCiberseguridad.md) · [Laboratorio](../lab/README.md) · [Guía de resolución](guia-resolucion-ctf.md)

# Guía: publicar el CTF en Railway para la audiencia

Esta guía despliega la misma app de [lab/](../lab/README.md) — con la
estética de AIEP + HubInnova ya integrada — en una URL pública, para que
los asistentes a la charla la resuelvan desde su propio celular/notebook
durante o después de la exposición.

**Antes de empezar, dos decisiones de seguridad que ya están tomadas en
el código, pero que debes respetar al configurar las variables:**
- El despliegue público corre **siempre en `LAB_MODE=vulnerable`** — es
  justamente el reto que la audiencia va a resolver. No hay datos reales
  de nadie ahí, solo dos usuarios de demo.
- **`DEBUG=False` es obligatorio en producción.** El paso de
  reconocimiento (comilla simple → error SQL) ya no depende de la página
  de depuración de Django — ahora es un mensaje controlado — así que
  apagar `DEBUG` no rompe el reto, y evita exponer `SECRET_KEY`, rutas
  del servidor y otras variables de entorno a cualquiera en internet.

## 1. Prerrequisitos

- Cuenta en [railway.app](https://railway.app) (gratuita para empezar;
  revisa el plan vigente al momento de desplegar, Railway ajusta sus
  límites de tanto en tanto).
- Node.js/npm, que ya tienes instalado — se usa solo para instalar el
  CLI de Railway:

```powershell
npm install -g @railway/cli
railway login
```

`railway login` abre el navegador para autenticarte; no necesitas tener
el proyecto en GitHub — el CLI sube el contenido de la carpeta
directamente.

## 2. Generar un SECRET_KEY de producción

Nunca reutilices la clave de desarrollo que trae el repo. Genera una
nueva:

```powershell
cd "C:\Users\JONA\Desktop\Charla AIEP\lab"
.\.venv\Scripts\python.exe -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copia el resultado, lo vas a pegar como variable de entorno en el
siguiente paso.

## 3. Crear el proyecto en Railway y desplegar

```powershell
cd "C:\Users\JONA\Desktop\Charla AIEP\lab"
railway init
railway up
```

`railway init` te pide un nombre para el proyecto (ej. `intranet-ctf`).
`railway up` empaqueta la carpeta `lab/` (Railway detecta
`requirements.txt` + `Procfile` automáticamente, no hace falta
configuración adicional) y arranca el primer deploy.

## 4. Configurar variables de entorno

Puedes hacerlo por CLI o desde el dashboard (railway.app → tu proyecto →
pestaña *Variables*). Por CLI:

```powershell
railway variables --set "LAB_MODE=vulnerable"
railway variables --set "DEBUG=False"
railway variables --set "SECRET_KEY=PEGA_AQUI_LA_CLAVE_GENERADA"
railway variables --set "SECURE_COOKIES=True"
```

`ALLOWED_HOSTS` y `CSRF_TRUSTED_ORIGINS` los terminas de configurar en
el paso 5, una vez que sepas el dominio público que te asignó Railway.

*(Opcional)* hay 5 flags, una por reto, cada una configurable por su
propia variable si quieres personalizarlas (si no seteas nada, se usan
las que trae el código por defecto):

```powershell
railway variables --set "LAB_FLAG=AIEP{tu_flag_reto1_2026}"
railway variables --set "LAB_FLAG_2=AIEP{tu_flag_reto2_2026}"
railway variables --set "LAB_FLAG_3=AIEP{tu_flag_reto3_2026}"
railway variables --set "LAB_FLAG_4=AIEP{tu_flag_reto4_2026}"
railway variables --set "LAB_FLAG_5=AIEP{tu_flag_reto5_2026}"
```

## 5. Generar el dominio público y cerrarlo con ALLOWED_HOSTS

En el dashboard: tu servicio → *Settings* → *Networking* → *Generate
Domain*. Te da algo como `intranet-ctf-production.up.railway.app`.

Con ese dominio, termina de configurar:

```powershell
railway variables --set "ALLOWED_HOSTS=intranet-ctf-production.up.railway.app"
railway variables --set "CSRF_TRUSTED_ORIGINS=https://intranet-ctf-production.up.railway.app"
```

Guardar variables dispara un redeploy automático. Espera ~1 minuto y
abre `https://tu-dominio/retos/` — deberías ver el hub con los 5 retos,
el logo de AIEP y tu firma en el pie, en "Modo práctica (CTF)".

> Si ves "Bad Request (400)" es casi siempre `ALLOWED_HOSTS` mal
> configurado (dominio incorrecto o falta redeploy). Si ves un error
> genérico de servidor sin la página de Django, revisa `railway logs`.

## 6. Probar el flujo completo antes de compartir el link

Repite el guion de [guia-resolucion-ctf.md](guia-resolucion-ctf.md)
contra la URL pública, no solo local, para **los 5 retos** — no solo el
bypass del Reto 1. Es fácil que algo funcione en local (SQLite del
`.venv`) y falle en Railway si te saltaste una variable de entorno, así
que vale la pena resolver cada uno una vez contra la URL real:
reconocimiento (comilla simple), Reto 1 (bypass), Reto 2 (UNION), Reto 3
(botón de transferencia), Reto 4 (buscador + `ORDER BY`) y Reto 5 (blind
boolean — al menos confirma que "Disponible"/"No disponible" cambian con
`x' OR '1'='1`, no hace falta correr el script completo).

## 7. El día de la charla

- Flujo elegido: el reto queda **"para la casa"**. No compite con tus
  30–40 minutos en el escenario ni necesita que nadie te muestre
  evidencia de haberlo resuelto — queda como experiencia personal de
  quien quiera intentarlo.
- En el bloque de **cierre y buenas prácticas** (minuto ~35, ver
  [CharlaCiberseguridad.md](CharlaCiberseguridad.md)) muestra el link
  corto/QR apuntando a `/retos/` (el hub) y explica en una frase qué van
  a encontrar ("el mismo login que vieron en la demo, más un par de retos
  extra si quieren profundizar"). No hace falta darles el payload de los
  retos 1-3 — ya lo vieron en tu resolución en vivo. Los retos 4 y 5 traen
  sus propias pistas en pantalla para quien se anime con algo más difícil.
- `railway logs --follow` en una ventana aparte (antes/después de la
  charla) te deja confirmar que la gente efectivamente está entrando,
  sin necesitar que nadie te reporte nada.
- Cada reinicio/redeploy del contenedor empieza con base de datos limpia
  (solo los dos usuarios de `seed_lab`), así que no hay riesgo de que un
  participante "ensucie" el estado para los demás — es SQLite efímero
  dentro del contenedor, no un volumen persistente.

## 7bis. Límite de gasto del workspace

Para evitar cobros extra mientras el CTF queda público, conviene
configurar un límite de uso en el workspace de Railway (aplica a todos
los proyectos del workspace):

```powershell
railway usage limit update --soft 6 --hard 10
railway usage limit status
```

Si el hard limit se activa, todos los servicios del workspace se
desconectan hasta que subas el límite o lo elimines
(`railway usage limit remove --yes`) — después Railway reintenta
reiniciar los servicios solo, o se relanzan manualmente desde el
dashboard / `railway up`.

## 8. Después del evento — dar de baja el despliegue

No dejes el CTF corriendo indefinidamente sin necesidad: es una app
deliberadamente vulnerable expuesta a internet.

```powershell
railway down
```

O bórralo desde el dashboard (proyecto → *Settings* → *Delete Project*).
Si quieres conservarlo para reusarlo en una futura charla, al menos
regenera `SECRET_KEY` y las 5 `LAB_FLAG*` antes del próximo evento.
