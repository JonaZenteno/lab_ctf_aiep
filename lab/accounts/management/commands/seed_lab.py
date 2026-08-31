from django.contrib.auth.models import User
from django.core.management.base import BaseCommand

from accounts import flags
from accounts.models import DocumentoConfidencial, Empleado, Secreto

DEMO_USERS = [
    # (username, password, is_superuser)
    ("admin", "admin2026", True),
    ("juan.perez", "juan2026", False),
]

EMPLEADOS = [
    ("Ana Rojas", "Gerenta de Finanzas"),
    ("Pedro Soto", "Analista de Sistemas"),
    ("Camila Vidal", "Jefa de RR.HH."),
]


class Command(BaseCommand):
    help = "Crea/actualiza los datos de demo del laboratorio (idempotente)."

    def handle(self, *args, **options):
        for username, password, is_super in DEMO_USERS:
            user, created = User.objects.get_or_create(
                username=username,
                defaults={"is_superuser": is_super, "is_staff": is_super},
            )
            user.set_password(password)
            user.is_superuser = is_super
            user.is_staff = is_super
            user.save()
            estado = "creado" if created else "actualizado"
            self.stdout.write(self.style.SUCCESS(f"Usuario '{username}' {estado}."))

        for nombre, cargo in EMPLEADOS:
            Empleado.objects.update_or_create(nombre=nombre, defaults={"cargo": cargo})
        self.stdout.write(self.style.SUCCESS(f"{len(EMPLEADOS)} empleados de demo listos (Reto 4)."))

        DocumentoConfidencial.objects.update_or_create(
            titulo="Acta de directorio — confidencial",
            defaults={
                "contenido": f"Presupuesto reservado 2026. Acceso restringido. Flag: {flags.FLAG_4}",
            },
        )
        self.stdout.write(self.style.SUCCESS("Documento confidencial listo (Reto 4)."))

        Secreto.objects.update_or_create(id=1, defaults={"valor": flags.FLAG_5})
        self.stdout.write(self.style.SUCCESS("Secreto listo para extracción a ciegas (Reto 5)."))

        self.stdout.write("")
        self.stdout.write(self.style.WARNING(
            "Credenciales de laboratorio (NO reutilizar fuera del entorno aislado):"
        ))
        for username, password, _ in DEMO_USERS:
            self.stdout.write(f"  {username} / {password}")
