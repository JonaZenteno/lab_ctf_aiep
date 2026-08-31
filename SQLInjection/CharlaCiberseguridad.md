# Rompiendo el candado: de la explotación al parche

*(Alternativas: "De Atacante a Defensor: La Doble Vida de una Vulnerabilidad Web" · "Inyectando dudas: la vida secreta de una consulta SQL")*

## Descripción (para entregar al organizador)

Charla práctica orientada a estudiantes de primer año de Ingeniería en Ciberseguridad e Ingeniería en Informática que profundiza en los fundamentos de la seguridad web mediante la resolución guiada de un reto tipo CTF centrado en una vulnerabilidad común (inyección SQL o falla de autenticación). Se abordará el proceso completo con nivel técnico: identificación del problema a nivel de protocolo HTTP y consulta SQL, explotación controlada en un entorno de laboratorio y, finalmente, la corrección desde la perspectiva del desarrollador —con ejemplos concretos de código en Python/Django—, cerrando con buenas prácticas aplicables a cualquier proyecto web.

**Duración estimada:** 30–40 minutos + preguntas
**Formato:** Expositiva con demo en vivo (o video de respaldo)
**Público objetivo:** Estudiantes de primer año de AIEP de las carreras de Ingeniería en Ciberseguridad e Ingeniería en Informática. Ya traen fundamentos de programación y redes de su malla, por lo que el nivel técnico puede ser más exigente que el de una charla genérica para "desarrolladores en general": se puede profundizar en protocolo HTTP, sintaxis SQL y estructura del código Django sin necesidad de simplificar en exceso.

---

## Perfil del expositor

**Jonathan Zenteno G.** — Ingeniero Informático y Facilitador SENCE (REUF) en Desarrollo de Software y Programación, con 8+ años en infraestructura tecnológica educativa. Maestro Guía en formación dual (Programación y Redes) y formación en ciberseguridad (Poder Judicial, MINEDUC). Actualmente Ingeniero Informático en SLEP Los Álamos y Secretario Técnico en la Cámara Chilena de Inteligencia Artificial.

---

## Objetivo de la charla

Que la audiencia entienda **cómo piensa un atacante** frente a una vulnerabilidad web común, y **cómo se traduce ese conocimiento en decisiones de diseño seguro** al desarrollar una aplicación. Al ser estudiantes de Ciberseguridad e Informática, el objetivo incluye conectar la explotación con los mecanismos subyacentes (consultas SQL, sesiones HTTP, hashing) y no solo con el resultado visible del ataque.

---

## Estructura de contenido sugerida

1. **Introducción (5 min)** — Por qué la seguridad no es "un área aparte" sino parte del desarrollo.
2. **Contexto del reto (5 min)** — Presentación del CTF elegido: qué aplicación/entorno se ataca y qué se busca lograr (la "flag").
3. **Resolución en vivo (15 min)** — Reconocimiento del punto débil → explotación paso a paso → obtención del resultado.
4. **La otra cara: cómo se corrige (10 min)** — Mostrar el mismo caso desde el código (ej. uso de ORM de Django vs. queries manuales, validación de inputs, manejo de sesiones/CSRF).
5. **Cierre y buenas prácticas (5 min)** — Checklist de seguridad aplicable a proyectos propios. Cerrar mostrando el link/QR del [CTF público](guia-despliegue-railway.md) (5 retos: los 3 que viste en vivo, más 2 avanzados para quien quiera profundizar) para que quien quiera lo resuelva por su cuenta después de la charla (sin evidencia ni entrega requerida).

---

## Material del proyecto

- [Guía completa del CTF](../README.md) — punto de entrada recomendado: los 5 retos con solución y explicación, más datos interesantes
- [Manual de estudio](manual-de-estudio.md) — SQL Injection en profundidad: fundamentos, arquitectura, defensa y cultura general
- [Temas a profundizar](temas-a-profundizar.md) — contenidos técnicos ajustados a tu perfil
- [Ejercicios prácticos](ejercicios-practicos.md) — ejercicio principal (SQLi) y de reserva (autenticación rota), con código
- [Banco de preguntas frecuentes](preguntas-frecuentes.md) — 18 preguntas típicas con respuesta corta
- [Laboratorio](../lab/README.md) — app Django real (vulnerable/corregida) para practicar
- [Guía de resolución paso a paso](guia-resolucion-ctf.md) — cada paso del reto con su explicación técnica
- [Guía de despliegue en Railway](guia-despliegue-railway.md) — publica el CTF (con logo AIEP y firma HubInnova) para resolverlo desde tu propio dispositivo

---

## Notas
- El enfoque recomendado es **explotación + corrección**, no solo el "hackeo" — esto le da valor pedagógico y conecta directamente con tu experiencia como Maestro Guía.
- Todo el contenido técnico puede prepararse con herramientas que ya usas (Python, Django, SQL), sin necesidad de herramientas de pentesting avanzadas.
- Al ser estudiantes de primer año de Ciberseguridad e Informática (no una audiencia genérica de "desarrolladores web"), no es necesario simplificar en exceso: se puede nombrar la sintaxis SQL real, mostrar la consulta vulnerable completa, hablar de parámetros preparados/ORM con su nombre técnico y referenciar conceptos que ya vieron en su malla (protocolo HTTP, bases de datos, lógica de programación) en lugar de dar rodeos conceptuales.