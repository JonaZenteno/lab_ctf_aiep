from django.contrib.auth.models import User
from django.test import TestCase, override_settings

from accounts import flags
from accounts.models import DocumentoConfidencial, Empleado, Secreto


class LoginChallengeTests(TestCase):
    """Reto 1/2: el toggle LAB_MODE debe habilitar/deshabilitar el bypass."""

    def setUp(self):
        User.objects.create_user(
            username="admin", password="admin2026",
            is_superuser=True, is_staff=True,
        )
        User.objects.create_user(username="juan.perez", password="juan2026")

    @override_settings(LAB_MODE="vulnerable")
    def test_single_quote_triggers_controlled_sql_error(self):
        response = self.client.post("/login/", {"username": "admin'", "password": "x"})
        self.assertEqual(response.status_code, 500)

    @override_settings(LAB_MODE="vulnerable")
    def test_bypass_reveals_flag_in_vulnerable_mode(self):
        response = self.client.post("/login/", {"username": "admin' -- ", "password": "x"})
        self.assertContains(response, flags.FLAG_1)

    @override_settings(LAB_MODE="vulnerable")
    def test_union_reveals_password_hash_in_vulnerable_mode(self):
        response = self.client.post(
            "/login/",
            {"username": "' UNION SELECT id, password FROM auth_user -- ", "password": "x"},
        )
        self.assertContains(response, flags.FLAG_2)
        self.assertContains(response, "pbkdf2_sha256$")

    @override_settings(LAB_MODE="secure")
    def test_bypass_fails_in_secure_mode(self):
        response = self.client.post("/login/", {"username": "admin' -- ", "password": "x"})
        self.assertNotContains(response, flags.FLAG_1, status_code=401)

    @override_settings(LAB_MODE="secure")
    def test_legit_login_works_in_secure_mode(self):
        response = self.client.post(
            "/login/", {"username": "juan.perez", "password": "juan2026"}
        )
        self.assertContains(response, "juan.perez")

    @override_settings(LAB_MODE="secure")
    def test_admin_real_password_still_shows_flag(self):
        """La corrección no debe romper el login legítimo de admin."""
        response = self.client.post(
            "/login/", {"username": "admin", "password": "admin2026"}
        )
        self.assertContains(response, flags.FLAG_1)


class TransferChallengeTests(TestCase):
    """Reto 3: /transferir/ solo debe responder sin CSRF en modo vulnerable."""

    @override_settings(LAB_MODE="vulnerable")
    def test_transfer_succeeds_without_csrf_in_vulnerable_mode(self):
        response = self.client.post("/transferir/", {"monto": "1", "destino": "x"})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["flag"], flags.FLAG_3)

    @override_settings(LAB_MODE="secure")
    def test_transfer_forbidden_in_secure_mode(self):
        response = self.client.post("/transferir/", {"monto": "1", "destino": "x"})
        self.assertEqual(response.status_code, 403)


class SearchChallengeTests(TestCase):
    """Reto 4: buscador vulnerable a UNION hacia otra tabla."""

    def setUp(self):
        Empleado.objects.create(nombre="Ana Rojas", cargo="Gerenta de Finanzas")
        DocumentoConfidencial.objects.create(titulo="Acta", contenido=f"Flag: {flags.FLAG_4}")

    @override_settings(LAB_MODE="vulnerable")
    def test_union_reveals_confidential_document_in_vulnerable_mode(self):
        response = self.client.get(
            "/buscar/",
            {"q": "x' UNION SELECT titulo, contenido FROM documentos_confidenciales -- "},
        )
        self.assertContains(response, flags.FLAG_4)

    @override_settings(LAB_MODE="secure")
    def test_union_payload_is_treated_as_literal_text_in_secure_mode(self):
        response = self.client.get(
            "/buscar/",
            {"q": "x' UNION SELECT titulo, contenido FROM documentos_confidenciales -- "},
        )
        self.assertNotContains(response, flags.FLAG_4)


class BlindSqliChallengeTests(TestCase):
    """Reto 5: boolean-based blind SQLi solo debe funcionar en modo vulnerable."""

    def setUp(self):
        User.objects.create_user(username="admin", password="x")
        Secreto.objects.create(id=1, valor=flags.FLAG_5)

    @override_settings(LAB_MODE="vulnerable")
    def test_true_condition_flips_response_in_vulnerable_mode(self):
        first_char = flags.FLAG_5[0]
        payload = f"x' OR (SELECT substr(valor,1,1) FROM secretos)='{first_char}' -- "
        response = self.client.get("/verificar/", {"usuario": payload})
        self.assertContains(response, 'class="result no_disponible"')

    @override_settings(LAB_MODE="secure")
    def test_boolean_injection_has_no_effect_in_secure_mode(self):
        response = self.client.get("/verificar/", {"usuario": "x' OR '1'='1"})
        self.assertContains(response, 'class="result disponible"')
        self.assertNotContains(response, 'class="result no_disponible"')
