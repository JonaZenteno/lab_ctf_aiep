[← Volver al índice](CharlaCiberseguridad.md) · [Guía de resolución del CTF](guia-resolucion-ctf.md)

# Manual de estudio: SQL Injection en profundidad

> Objetivo: entender SQL Injection a fondo — fundamentos, arquitectura,
> defensa y cultura general de ciberseguridad — sin quedarse solo en
> "payloads que funcionan". La meta no es memorizar entradas mágicas,
> sino construir un mapa mental que explique **por qué** aparece la
> vulnerabilidad, **cómo** reconocerla, **qué impacto** puede tener y
> **cómo** diseñar sistemas que la hagan difícil de introducir.
>
> Los ejemplos de este manual son conceptuales. Practícalos únicamente
> en el [laboratorio](../lab/README.md) de este repositorio u otros
> entornos autorizados — nunca contra sistemas de terceros sin permiso
> explícito (ver la nota legal en [preguntas-frecuentes.md](preguntas-frecuentes.md)).

## Índice

1. [Modelo mental fundamental](#1-modelo-mental-fundamental)
2. [Cómo nace una vulnerabilidad](#2-cómo-nace-una-vulnerabilidad)
3. [Datos versus código](#3-datos-versus-código)
4. [Parametrización y consultas preparadas](#4-parametrización-y-consultas-preparadas)
5. [Validación de entrada: qué resuelve y qué no](#5-validación-de-entrada-qué-resuelve-y-qué-no)
6. [Tipos de SQL Injection](#6-tipos-de-sql-injection)
7. [Impacto y evaluación de riesgo](#7-impacto-y-evaluación-de-riesgo)
8. [Defensa en profundidad](#8-defensa-en-profundidad)
9. [Mínimo privilegio](#9-mínimo-privilegio)
10. [Manejo de errores y Fail Secure](#10-manejo-de-errores-y-fail-secure)
11. [ORM, stored procedures y SQL dinámico](#11-orm-stored-procedures-y-sql-dinámico)
12. [Arquitectura y fronteras de confianza](#12-arquitectura-y-fronteras-de-confianza)
13. [Threat modeling](#13-threat-modeling)
14. [Secure by Design y Secure by Default](#14-secure-by-design-y-secure-by-default)
15. [Zero Trust y Assume Breach](#15-zero-trust-y-assume-breach)
16. [Observabilidad, logging y trazabilidad](#16-observabilidad-logging-y-trazabilidad)
17. [SDLC, DevSecOps y Shift Left](#17-sdlc-devsecops-y-shift-left)
18. [Deuda técnica y cadena de suministro](#18-deuda-técnica-y-cadena-de-suministro)
19. [SQL Injection en CTF: cómo pensar los retos](#19-sql-injection-en-ctf-cómo-pensar-los-retos)
20. [IA, chatbots y SQL Injection](#20-ia-chatbots-y-sql-injection)
21. [Linux: cultura general útil](#21-linux-cultura-general-útil)
22. [Preguntas técnicas difíciles y respuestas puente](#22-preguntas-técnicas-difíciles-y-respuestas-puente)
23. [Glosario rápido](#23-glosario-rápido)
24. [Datos interesantes / curiosidades](#24-datos-interesantes--curiosidades)
25. [Preguntas de autoevaluación](#25-preguntas-de-autoevaluación)
26. [Bibliografía y referencias](#26-bibliografía-y-referencias)

---

## 1. Modelo mental fundamental

SQL Injection aparece cuando datos controlados por una persona terminan
influyendo en la **estructura o lógica** de una sentencia SQL. OWASP
describe como causa típica la construcción de consultas dinámicas
mediante concatenación de cadenas con entrada controlada por el usuario.

**Idea central:** el problema no es que el usuario escriba caracteres
especiales. El problema es que la aplicación permite que esos datos sean
**interpretados como parte de las instrucciones SQL**.

Forma simple de explicarlo: la aplicación recibe una entrada, construye
una consulta, la envía al motor de base de datos y utiliza la respuesta.
Si la entrada puede modificar la *intención* de esa consulta, existe un
problema de separación entre datos e instrucciones.

**Pregunta clave:** ¿dónde se perdió la separación entre lo que el
usuario quiere buscar y la instrucción que el programador quería
ejecutar?

## 2. Cómo nace una vulnerabilidad

1. Existe una operación de negocio que necesita consultar la base de datos.
2. La aplicación recibe un valor desde una fuente externa: formulario, URL, API, cookie, cabecera, archivo u otro servicio.
3. Ese valor llega a una parte del código que construye SQL dinámicamente.
4. La aplicación mezcla estructura SQL y datos.
5. El motor recibe una sentencia cuya lógica pudo haber sido alterada por el dato.

Esta secuencia permite revisar código de forma sistemática: localizar
entradas externas, seguir su flujo y preguntar dónde se transforma el
dato en una consulta.

**Pregunta de revisión:** ¿este valor está siendo tratado como un dato
por el mecanismo de acceso a datos, o está siendo incorporado como texto
SQL?

## 3. Datos versus código

Probablemente el concepto más importante de todo el manual. En una
aplicación segura, la **intención** de la consulta la define el programa,
y los valores que entrega el usuario deben ocupar solo **posiciones de
datos**.

**Analogía:** un formulario impreso. El texto de la plantilla representa
la estructura de la consulta; los campos rellenables representan los
parámetros. Escribir en un campo no debería permitir modificar el texto
impreso.

La misma idea aparece en otros contextos: HTML versus contenido (→ XSS),
comandos versus argumentos (→ command injection), plantillas versus
valores, expresiones versus datos. SQL Injection es un caso particular de
una familia más amplia de **problemas de inyección**.

## 4. Parametrización y consultas preparadas

OWASP recomienda las **consultas preparadas con parámetros** como
defensa principal: se define la sentencia y luego se pasan los valores
como parámetros, de forma que el motor pueda distinguir estructura y
datos.

**Qué significa un "marcador" o placeholder:** representa una ubicación
donde se suministrará un valor. No significa "pegar texto aquí" —
significa "esta posición recibirá un dato". En pseudocódigo:

```
SELECT ... WHERE usuario = [PARÁMETRO]
```

La estructura de la consulta queda definida de antemano; el valor se
entrega por un canal separado.

**Por qué funciona:** el beneficio de la parametrización no depende de
reconocer manualmente todos los caracteres o patrones maliciosos. La
protección está en el **mecanismo de construcción de la consulta**: los
valores no pueden redefinir su propia estructura. Es muy distinto de
intentar mantener una lista infinita de entradas prohibidas.

## 5. Validación de entrada: qué resuelve y qué no

La validación comprueba que un dato tenga las características esperadas:
tipo, longitud, formato, rango, conjunto permitido o estructura. Es
excelente para calidad de datos y para reducir entradas inesperadas.

**Pero no sustituye la parametrización.** Una regla puede decir que un
identificador debe ser numérico, y aun así la consulta puede seguir
siendo insegura si se concatena. La defensa estructural sigue siendo la
separación entre código y datos.

OWASP contempla la validación mediante listas permitidas (*allow-lists*)
como defensa **complementaria**, y desaconseja basar la protección
exclusivamente en "escapar" todas las entradas.

**Regla mental:** validar responde "¿este dato tiene el formato
esperado?". Parametrizar responde "¿este dato puede convertirse en
instrucciones?". Son preguntas distintas.

## 6. Tipos de SQL Injection

| Tipo | Descripción |
|---|---|
| **In-band** | La entrada y el resultado usan el mismo canal — la variante más fácil de imaginar (ej. `UNION SELECT`, como en los [Retos 2 y 4](guia-resolucion-ctf.md) de este laboratorio). |
| **Blind / inferencial** | La aplicación no entrega directamente la información. Se reconstruye observando diferencias de comportamiento (respuestas distintas, tiempos distintos) — ver [Reto 5](guia-reto5-blind-boolean.md). |
| **Out-of-band** | La información se obtiene por un canal completamente distinto al de entrada. Menos frecuente, depende de capacidades del motor y del entorno (ver curiosidad en la sección 24). |
| **Error-based** | Mensajes de error detallados revelan información sobre la consulta o el motor. No es la causa raíz — ocultar errores ayuda, pero no reemplaza consultas seguras (ver [Reto 1, paso 2](guia-reto1-bypass-login.md)). |

## 7. Impacto y evaluación de riesgo

SQL Injection puede afectar **confidencialidad, integridad y
disponibilidad**. Una explotación exitosa puede permitir acceso o
manipulación de datos y, dependiendo del contexto y permisos,
operaciones administrativas o incluso efectos sobre el sistema
subyacente.

La gravedad real depende del contexto. Preguntas útiles:

- ¿Qué datos puede alcanzar la cuenta que usa la aplicación?
- ¿Esa cuenta puede escribir, modificar o eliminar?
- ¿Hay datos de otras organizaciones o usuarios?
- ¿Existe segmentación entre aplicación y base de datos?
- ¿Qué controles adicionales detectarían o limitarían el incidente?
- ¿Hay mecanismos de recuperación y copias de seguridad?

**Concepto importante:** una vulnerabilidad técnica y su impacto no son
lo mismo. La **arquitectura** determina cuánto daño puede producir un
fallo.

## 8. Defensa en profundidad

*Defense in Depth* significa no depender de una sola barrera:

- **Código:** consultas preparadas.
- **Datos:** permisos mínimos.
- **Red:** acceso restringido a la base de datos.
- **Aplicación:** autorización y validación.
- **Operaciones:** logging y alertas.
- **Continuidad:** copias de seguridad y recuperación.

Si una capa falla, otra reduce la probabilidad o el impacto del
incidente. Es la respuesta madura a "¿y si el desarrollador se
equivoca?".

## 9. Mínimo privilegio

La cuenta de base de datos de una aplicación debe tener **solo** los
permisos necesarios para su función. Si un servicio únicamente necesita
consultar ciertos datos, no debería usar una cuenta con privilegios
administrativos sobre toda la base. El principio aplica también a
tablas, vistas, operaciones, redes, servicios y sistema operativo.

**Pregunta avanzada:** si la parametrización fallara mañana, ¿qué podría
hacer la cuenta comprometida? Esa pregunta conecta directamente
vulnerabilidad con arquitectura.

## 10. Manejo de errores y Fail Secure

Un sistema *fail secure* intenta mantener condiciones **seguras**, no
condiciones **informativas**, cuando algo falla. Mensajes de error
detallados pueden revelar nombres de tablas, consultas, motores o
información interna — por eso deben quedar en registros internos
protegidos, mientras que la respuesta externa debe ser controlada (así
funciona el [Reto 1](guia-reto1-bypass-login.md) de este laboratorio: un
banner de error controlado, nunca la página de depuración de Django).

Pero un mensaje genérico **no convierte por sí mismo** una aplicación
vulnerable en segura — el criterio principal es qué estado adopta el
sistema ante el fallo.

**Ejemplo con IA:** si un chatbot deja de responder y muestra un mensaje
genérico sin revelar credenciales, trazas o datos internos, eso es
comportamiento *fail secure*. Si el fallo hace que se salte una
autorización, no lo es.

## 11. ORM, stored procedures y SQL dinámico

- **ORM:** abstrae el acceso relacional mediante objetos. Reduce riesgos
  bien usado, pero no elimina la necesidad de entender cómo se
  construyen las consultas — incluso un ORM puede usarse de forma
  insegura si se vuelve a concatenar SQL dinámico dentro de él (`.raw()`,
  `.extra()`, `RawSQL()` en Django).
- **Stored procedures:** pueden ser una defensa válida si reciben
  parámetros de forma segura. No son una garantía automática.
- **SQL dinámico:** no es sinónimo de vulnerabilidad. El problema aparece
  cuando datos no confiables se incorporan a la estructura SQL sin un
  mecanismo seguro.

## 12. Arquitectura y fronteras de confianza

Una *trust boundary* es un punto donde los datos pasan entre componentes
con distintos niveles de confianza: navegador → API, API → servicio
interno, servicio → base de datos, aplicación → proveedor externo.

**Regla útil:** cada frontera debe tratar los datos recibidos como
externos hasta aplicar los controles correspondientes. En SQL Injection,
el recorrido típico es navegador → API → capa de negocio → repositorio →
driver → base de datos.

## 13. Threat modeling

Analizar amenazas **antes o durante** el diseño, no después.

1. Identificar activos (cuentas, datos personales, información financiera, secretos).
2. Identificar actores (usuario, administrador, atacante externo, servicio de terceros).
3. Identificar entradas y fronteras.
4. Identificar amenazas plausibles.
5. Definir controles preventivos y de detección.
6. Evaluar el impacto residual.

**Pregunta provocadora:** ¿la vulnerabilidad apareció cuando alguien
escribió una entrada maliciosa, o mucho antes, cuando se diseñó la forma
de construir consultas?

## 14. Secure by Design y Secure by Default

- **Secure by Design:** la seguridad se incorpora en las decisiones de
  arquitectura y desarrollo desde el comienzo.
- **Secure by Default:** la configuración inicial favorece una postura
  segura, sin que cada desarrollador tenga que recordar activarla.

En SQL Injection, el equivalente cultural es establecer como estándar
del proyecto que el acceso a datos use APIs parametrizadas, y que las
excepciones deban justificarse y revisarse.

## 15. Zero Trust y Assume Breach

- **Zero Trust:** evita asumir que algo es confiable solo por estar
  dentro de la red. Identidad, autorización y contexto se verifican
  siempre, sin importar el origen de la llamada.
- **Assume Breach:** diseñar suponiendo que algún componente eventualmente
  será comprometido. Cambia las preguntas hacia: ¿cómo detectamos el
  incidente?, ¿cómo lo contenemos?, ¿qué permisos tenía el componente?,
  ¿qué evidencia queda?, ¿cómo recuperamos el sistema?

Este concepto conecta directamente con mínimo privilegio: si la API cae,
la base de datos debe sobrevivir gracias a sus propios controles, no
porque "se confiaba" en que la API nunca fallaría.

## 16. Observabilidad, logging y trazabilidad

- **Observabilidad:** entender el comportamiento interno de un sistema a
  partir de logs, métricas y trazas.
- **Trazabilidad:** reconstruir una secuencia de acciones y relacionarla
  con un actor o contexto.

Registrar demasiado poco impide investigar; registrar indiscriminadamente
puede exponer secretos o crear problemas de privacidad.

- Registrar eventos de seguridad relevantes.
- Nunca registrar contraseñas, tokens ni secretos en logs.
- Usar identificadores de correlación para reconstruir flujos.
- Proteger el acceso y la integridad de los registros.
- Definir retención acorde al contexto.

## 17. SDLC, DevSecOps y Shift Left

*Shift Left* = incorporar controles de seguridad más temprano en el
ciclo de desarrollo. *DevSecOps* lleva esa idea a la operación continua.

Para SQL Injection esto significa: guías de codificación segura, revisión
de código enfocada en acceso a datos, pruebas automatizadas, análisis
estático (SAST) cuando corresponda, pruebas dinámicas (DAST) en entornos
controlados, revisión de dependencias, controles de despliegue.

La meta no es añadir burocracia al final — es hacer que el camino seguro
sea el camino normal.

## 18. Deuda técnica y cadena de suministro

La deuda técnica aparece cuando decisiones rápidas generan un costo
futuro (ej. mantener durante años una capa de acceso a datos insegura
"porque funciona"). La cadena de suministro incluye librerías,
frameworks, imágenes de contenedor, herramientas y servicios externos —
una vulnerabilidad en una dependencia puede convertirse en un riesgo
propio.

**Pregunta útil:** ¿qué parte de tu sistema realmente escribiste tú, y
qué parte depende de código de terceros?

## 19. SQL Injection en CTF: cómo pensar los retos

Metodología recomendada — separar observación, hipótesis, prueba y
conclusión:

1. Mapear la funcionalidad: ¿qué hace el reto?
2. Identificar entradas: ¿qué valores controla el participante?
3. Observar respuestas: contenido, estado, comportamiento y errores.
4. Formular una hipótesis sobre el flujo de datos.
5. Probar de forma controlada y no destructiva.
6. Registrar qué evidencia confirma o refuta la hipótesis.
7. Explicar la causa raíz.
8. Proponer la mitigación.
9. Relacionar el hallazgo con arquitectura y mínimo privilegio.

Al terminar cada uno de los 5 retos de este laboratorio, vale la pena
cerrarlo con cuatro preguntas: ¿qué estaba mal?, ¿por qué funcionó la
entrada?, ¿cómo se habría evitado?, ¿qué control adicional habría
reducido el impacto?

**Regla del laboratorio:** el alcance, duración y autorización deben
estar siempre claros. Este CTF nunca es "permiso" para probar sistemas
externos.

## 20. IA, chatbots y SQL Injection

Un chatbot introduce nuevos caminos de entrada: el usuario conversa, el
modelo genera una intención o consulta, una aplicación ejecuta una
operación y la base de datos responde.

**El modelo de lenguaje no debe considerarse una barrera de seguridad.**
Una arquitectura segura aplica controles deterministas *alrededor* del
modelo: autorización, validación, parametrización, límites de operación
y separación de privilegios.

Ejemplo: un usuario pide "buscar pedidos". El modelo puede interpretar la
intención, pero no debería tener libertad para decidir arbitrariamente
qué operaciones administrativas ejecutar — la aplicación traduce esa
intención a operaciones permitidas.

**Idea avanzada:** la IA puede generar o transformar instrucciones, pero
la política de seguridad debe estar **fuera del modelo**, aplicada por
controles que no dependan de que el modelo "se porte bien". Esto es hoy
lo que se llama *function calling* / *tool use*: el modelo solo puede
invocar funciones predefinidas, con permisos acotados y parámetros
validados — mismo principio de mínimo privilegio, aplicado a un agente
de IA (ver curiosidad sobre OWASP LLM01 en la sección 24).

## 21. Linux: cultura general útil

No hace falta una clase completa de Linux — basta con vocabulario que
puede aparecer en preguntas técnicas:

- **Root:** identidad con privilegios administrativos máximos.
- **sudo:** mecanismo para ejecutar acciones puntuales con privilegios elevados.
- **Proceso:** instancia en ejecución de un programa.
- **Daemon / servicio:** proceso que opera en segundo plano.
- **systemd:** sistema de inicialización y gestión de servicios común en distribuciones modernas.
- **Permisos:** lectura, escritura y ejecución, para propietario, grupo y otros.
- **Filesystem:** estructura de archivos, directorios y recursos.
- **Socket:** mecanismo de comunicación entre procesos (o punto de comunicación de red).
- **Port:** punto lógico de comunicación de un servicio de red.
- **Container:** aislamiento de procesos y filesystem sobre el kernel del host (Docker es la plataforma más común).

## 22. Preguntas técnicas difíciles y respuestas puente

**¿Por qué no basta con "escapar" comillas?**
Porque las reglas de escape dependen del contexto, del motor y de cómo
se construye la consulta. La defensa preferida es parametrizar — OWASP
desaconseja fuertemente basar la protección solo en escapar entradas.

**¿Un ORM elimina SQL Injection?**
No automáticamente. Pueden existir rutas de SQL dinámico o APIs que
ejecuten consultas construidas de forma insegura (`.raw()`, `.extra()`).

**¿La validación de entrada elimina SQL Injection?**
No por sí sola. Es complementaria; la defensa principal es la separación
entre estructura SQL y datos mediante parametrización.

**¿Por qué la base de datos no "detecta" al atacante?**
Porque el motor recibe una sentencia y la ejecuta según su sintaxis y
semántica — no conoce la intención original del desarrollador.

**¿Qué pasa si ya parametrizamos y aun así hay una vulnerabilidad?**
Se analiza el contexto: SQL dinámico estructural, permisos excesivos,
componentes vulnerables, autorización, lógica de negocio, configuración,
o una ruta de acceso a datos que no está usando el mecanismo seguro.

**¿Puede SQL Injection terminar en ejecución de comandos?**
En ciertos escenarios y configuraciones, sí, encadenada con capacidades
del motor o del sistema subyacente — no es una consecuencia universal;
depende de qué privilegios tiene el componente comprometido.

**¿Diferencia entre SQL Injection y NoSQL Injection?**
Ambas son parte de la familia de inyección, pero afectan lenguajes o
mecanismos de consulta distintos. La defensa sigue el mismo principio:
no permitir que datos externos se conviertan en instrucciones.

**¿Qué es un CVE?**
Un identificador estandarizado para referirse sin ambigüedad a una
vulnerabilidad o exposición conocida y publicada.

**¿Qué es OWASP?**
Una organización y comunidad dedicada a mejorar la seguridad de
aplicaciones web. Sus *Cheat Sheets* y el *Web Security Testing Guide*
son referencias clave para este tema.

**¿Qué hacer si no se sabe la respuesta?**
Una respuesta profesional: *"No quiero improvisar sobre ese detalle. En
el alcance de este tema, lo importante es X; el punto que planteas
pertenece a Y y se puede profundizar después."* Reconocer el límite es
mejor que inventar.

## 23. Glosario rápido

| Término | Definición |
|---|---|
| **Attack surface** | Conjunto de puntos que un atacante podría usar para interactuar con un sistema. |
| **Authentication** | Proceso de comprobar quién es una entidad. |
| **Authorization** | Proceso de determinar qué puede hacer esa entidad. |
| **CVE** | Identificador público y estandarizado de una vulnerabilidad conocida. |
| **Defense in Depth** | Uso de múltiples controles para reducir probabilidad e impacto. |
| **Fail Secure** | Diseñar los fallos para mantener un estado seguro. |
| **Least Privilege** | Otorgar solo los permisos necesarios. |
| **ORM** | Capa que mapea objetos de una aplicación con estructuras relacionales. |
| **Payload** | Entrada diseñada para provocar un comportamiento concreto en el sistema objetivo. |
| **Prepared Statement** | Sentencia con parámetros separados de la estructura SQL. |
| **SQL dinámico** | SQL cuya estructura se construye durante la ejecución; requiere especial cuidado. |
| **Threat Modeling** | Análisis sistemático de amenazas y controles durante el diseño. |
| **Trust Boundary** | Frontera donde los datos pasan entre contextos con distinta confianza. |
| **Zero Trust** | Modelo que evita conceder confianza implícita y exige verificación explícita. |

## 24. Datos interesantes / curiosidades

- **Out-of-band SQLi usa DNS como canal de fuga.** Cuando ni siquiera hay
  diferencia de comportamiento visible (a diferencia del [Reto 5](guia-reto5-blind-boolean.md)
  de este laboratorio, que sí es observable), algunos motores permiten
  forzar una consulta de red hacia un servidor propio del atacante para
  filtrar datos por un canal completamente distinto al de entrada.
  Funciones históricamente usadas para esto: `UTL_HTTP` en Oracle y
  `xp_dirtree` en SQL Server, ambas capaces de disparar resoluciones DNS
  que terminan revelando datos carácter a carácter en los logs del
  servidor DNS del atacante.
- **Existen buscadores dedicados a encontrar servidores mal configurados.**
  [Shodan](https://www.shodan.io/) es célebre por poder localizar
  servidores con `DEBUG=True` (Django) u otros modos de depuración
  activos en producción — exactamente el error que la
  [guía de despliegue en Railway](guia-despliegue-railway.md) de este
  proyecto evita al forzar `DEBUG=False`.
- **OWASP tiene un Top 10 específico para aplicaciones con LLM.** La
  categoría **LLM01** es *Prompt Injection* — el mismo problema de fondo
  que SQL Injection (datos no confiables que terminan actuando como
  instrucciones), pero aplicado al lenguaje natural que recibe un modelo
  en lugar de a SQL.
- **El "candado" del título de la charla no es solo una metáfora.** El
  Reto 1 de este laboratorio (`admin' -- `) reproduce el mismo tipo de
  fallo de *authentication bypass vía SQLi* documentado en incidentes
  reales de la industria desde los años 2000 — la técnica en sí casi no
  ha cambiado en dos décadas, lo que sí cambió fue la adopción de ORMs y
  consultas parametrizadas como estándar.
- **`UNION SELECT` tiene una restricción matemática simple pero
  poderosa.** Ambas consultas deben devolver exactamente el mismo número
  de columnas — por eso el [Reto 4](guia-reto4-buscador-union.md) obliga
  a "tantear" con `ORDER BY` antes de poder extraer nada: es, en esencia,
  binary search manual sobre el número de columnas.
- **Django hashea contraseñas con PBKDF2 y ~870.000 iteraciones por
  defecto** (visible en el prefijo `pbkdf2_sha256$870000$...` del
  [Reto 2](guia-reto2-union-hash.md)). Ese número de iteraciones existe
  para hacer computacionalmente costoso probar contraseñas por fuerza
  bruta contra un hash filtrado — es la razón por la que "obtener el
  hash" en una filtración real casi nunca es sinónimo de "obtener la
  contraseña" inmediatamente.
- **En Chile, explotar una vulnerabilidad sin autorización es delito
  informático** bajo la Ley 21.459 (vigente desde 2022, reemplazó a la
  antigua Ley 19.223) — motivo por el cual todo el contenido de este
  repositorio se practica exclusivamente contra el
  [laboratorio propio](../lab/README.md).
- **`sqlmap`** puede automatizar la detección y explotación de los cinco
  tipos de inyección de este laboratorio (incluyendo el
  [blind boolean-based del Reto 5](guia-reto5-blind-boolean.md)) sin
  escribir el script de fuerza bruta a mano — es la herramienta estándar
  de la industria para pruebas de penetración autorizadas sobre SQLi.

## 25. Preguntas de autoevaluación

- ¿Cuál es la diferencia esencial entre validar un dato y parametrizar una consulta?
- ¿Qué ocurre conceptualmente cuando datos e instrucciones se mezclan?
- ¿Por qué una aplicación no debería usar una cuenta administrativa de base de datos si solo necesita consultar?
- ¿Cómo ayuda *fail secure* cuando una dependencia deja de responder?
- ¿Qué diferencia existe entre *authentication* y *authorization*?
- ¿Qué es una *trust boundary* dentro de una aplicación web?
- ¿Por qué un ORM no garantiza por sí mismo la ausencia de SQL Injection?
- ¿Qué diferencia hay entre *blind* SQL Injection e *in-band* SQL Injection?
- ¿Qué preguntas harías durante un *threat model* de una aplicación con base de datos?
- ¿Cómo limitarías el impacto si una vulnerabilidad de SQL Injection llegara a producción?
- ¿Qué señales buscarías en logs sin registrar secretos?
- ¿Cómo relacionarías SQL Injection con deuda técnica?
- ¿Qué significa *Assume Breach* aplicado a una aplicación web?
- ¿Qué parte de una arquitectura de chatbot debería aplicar las políticas de seguridad: el modelo o la capa de control?

## 26. Bibliografía y referencias

- OWASP — [SQL Injection Prevention Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/SQL_Injection_Prevention_Cheat_Sheet.html)
- OWASP — [Web Security Testing Guide](https://owasp.org/www-project-web-security-testing-guide/)
- OWASP — [Database Security Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Database_Security_Cheat_Sheet.html)
- OWASP — [Top 10 for Large Language Model Applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/) (referencia de la sección 20)
- [sqlmap](https://sqlmap.org/) — herramienta de explotación automatizada de SQL Injection
