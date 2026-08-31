[← Volver al índice](CharlaCiberseguridad.md)

# Banco de preguntas frecuentes

**Legal y ético**
1. **¿Esto es legal?** Sí, siempre en entorno propio o autorizado (laboratorio, CTF, bug bounty). Sin permiso, es delito informático en Chile (Ley 21.459).
2. **¿Necesito autorización para hacer pentesting en mi trabajo?** Sí, siempre por escrito: alcance, fechas y sistemas incluidos/excluidos antes de cualquier prueba.
3. **¿Qué hago si encuentro una falla por accidente en un sistema ajeno?** No explotarla; reportarla de forma responsable al equipo dueño del sistema.

**Detección y prevención**
4. **¿Cómo detecto esto en mi propio proyecto?** Revisa el código que arme SQL con f-strings/concatenación; usa SAST (ej. Bandit) y prueba caracteres especiales (`'`, `"`, `--`) en los formularios.
5. **¿El ORM de Django es 100% seguro contra SQLi?** Seguro por defecto, pero `.raw()`, `.extra()` y `RawSQL()` mal usados reintroducen el riesgo si concatenan datos del usuario.
6. **¿Aplica solo a Django?** No, el principio (consultas parametrizadas) es igual en Flask/FastAPI/Node/PHP; solo cambia la sintaxis.
7. **¿Un WAF me protege de esto?** Ayuda como capa extra, pero no reemplaza corregir el código; los WAF se pueden evadir.

**Autenticación y sesiones**
8. **¿Basta con "encriptar" las contraseñas?** No; deben ir con *hash* + *salt* (PBKDF2, bcrypt, Argon2), nunca cifradas de forma reversible ni en texto plano.
9. **¿CSRF y SQLi son lo mismo?** No. SQLi inyecta datos en una consulta; CSRF hace que el navegador de la víctima ejecute una acción autenticada sin su consentimiento.
10. **¿Django protege contra CSRF automáticamente?** Sí, con `CsrfViewMiddleware` y `{% csrf_token %}` en los formularios; evita `@csrf_exempt` salvo casos justificados.

**Sobre el reto/demo**
11. **¿Por qué SQLi y no otra vulnerabilidad?** Está entre las más comunes (OWASP Top 10), es fácil de visualizar y su corrección en Django es muy clara.
12. **¿Se puede automatizar esta detección en CI/CD?** Sí, con SAST (Bandit, Semgrep) y DAST (OWASP ZAP) integrados al pipeline.

**Sobre tu experiencia / contexto educativo**
13. **¿Esto aplica a sistemas como SIGE o SAE?** Sí — cualquier sistema que reciba input y arme consultas está expuesto; "nunca confiar en el input" es universal.
14. **¿Cómo empiezo si nunca he hecho seguridad?** Con el OWASP Top 10 y práctica en plataformas legales gratuitas como PortSwigger Web Security Academy o picoCTF.
15. **¿Se necesita ser experto en redes o Linux?** No para lo básico; con fundamentos de programación y HTTP ya se puede entender y prevenir SQLi/CSRF.

**Cierre**
16. **¿Dónde puedo ver el writeup completo?** Este mismo repositorio es el writeup: la [guía completa del CTF](../README.md) en la raíz y la [guía de resolución paso a paso](guia-resolucion-ctf.md) cubren los 5 retos con su explicación técnica.
17. **¿Recomiendas alguna certificación?** Para empezar, cursos gratuitos como PortSwigger Academy; certificaciones (eJPT, OSCP) son un paso posterior.
18. **¿Cómo se relaciona esto con la ciberseguridad "laboral" que ya certificaste?** Esa formación cubre buenas prácticas generales (phishing, contraseñas, dispositivos); esta charla profundiza en el lado técnico de cómo se explota y corrige una falla concreta en código.
