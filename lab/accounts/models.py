from django.db import models


class Empleado(models.Model):
    """Datos de ejemplo para el Reto 4 (buscador vulnerable)."""

    nombre = models.CharField(max_length=100)
    cargo = models.CharField(max_length=100)

    class Meta:
        db_table = "empleados"

    def __str__(self):
        return self.nombre


class DocumentoConfidencial(models.Model):
    """Tabla "ajena" al buscador que el Reto 4 permite alcanzar vía UNION."""

    titulo = models.CharField(max_length=200)
    contenido = models.TextField()

    class Meta:
        db_table = "documentos_confidenciales"

    def __str__(self):
        return self.titulo


class Secreto(models.Model):
    """Valor que el Reto 5 (blind boolean-based SQLi) hay que extraer a ciegas."""

    valor = models.CharField(max_length=200)

    class Meta:
        db_table = "secretos"

    def __str__(self):
        return self.valor
