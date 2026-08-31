[← Volver al índice](CharlaCiberseguridad.md)

# Temas a profundizar (ajustados a tu perfil)

- **Cómo piensa un atacante** — reconocimiento y superficie de ataque; por qué los formularios de login/búsqueda son el primer blanco.
- **Inyección SQL, de la teoría a la práctica** — concatenar strings vs. parametrizar; por qué el ORM de Django previene esto por defecto, y por qué `.raw()`, `.extra()` y `RawSQL()` mal usados reintroducen el riesgo.
- **Autenticación y sesiones** — hashing de contraseñas con `django.contrib.auth.hashers` (PBKDF2 por defecto), `authenticate()`/`login()`, cookies de sesión y CSRF.
- **Defensa en profundidad** — nunca confiar en la validación de frontend, principio de mínimo privilegio a nivel de base de datos, logging y monitoreo básico.
- **Gancho con tu experiencia** — los mismos principios protegen sistemas como SIGE/SAE que administras a diario; un ejemplo real (sin exponer datos sensibles) conecta la charla con la audiencia y refuerza tu credibilidad como expositor.
