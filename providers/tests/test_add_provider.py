import unittest
import os
from unittest.mock import patch, MagicMock
from flask import json
# from flask_jwt_extended import create_access_token
from app import create_app
from sqlalchemy.exc import IntegrityError

class TestAddProvider(unittest.TestCase):
    def setUp(self):
        """Configura la aplicación de prueba."""
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()

        self.app_context = self.app.app_context()
        self.app_context.push()

        # self.jwt_token = create_access_token(identity="test_user")

    def tearDown(self):
        """Elimina el contexto de la aplicación después de cada prueba."""
        self.app_context.pop()

    @patch("models.models.db.session")
    # @patch("flask_jwt_extended.get_jwt_identity")
    def test_create_provider_success(self, mock_db_session):
        """Prueba la creación exitosa de un proveedor."""
        # mock_get_jwt_identity.return_value = "test_user"
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        response = self.client.post(
            "/providers/add",
            # headers={"Authorization": f"Bearer {self.jwt_token}"},
            data=json.dumps({
                "identification_number": "123321123",
                "name": "John Doe",
                "address": "calle 80",
                "countries": ["Colombia", "EEUU"],
                "identification_number_contact": "987654321",
                "name_contact": "Jane Doe",
                "phone_contact": "3213211203",
                "address_contact": "calle 81"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["message"], "provider created successfully")
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch("models.models.db.session")
    # @patch("flask_jwt_extended.get_jwt_identity")
    def test_create_provider_duplicate(self, mock_db_session):
        """Prueba un error al intentar crear un proveedor duplicado."""
        # mock_get_jwt_identity.return_value = "test_user"
        mock_db_session.add = MagicMock()
        mock_db_session.commit.side_effect = IntegrityError("test", "test", "test")

        response = self.client.post(
            "/providers/add",
            # headers={"Authorization": f"Bearer {self.jwt_token}"},
            data=json.dumps({
                "identification_number": "123456",
                "name": "Proveedor Ejemplo",
                "address": "Calle 123",
                "countries": ["Colombia", "México"],
                "identification_number_contact": "78910",
                "name_contact": "Juan Pérez",
                "phone_contact": "123456789",
                "address_contact": "Calle Principal"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json["message"], "provider is already registered")
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch("models.models.db.session")
    # @patch("flask_jwt_extended.get_jwt_identity")
    def test_create_provider_missing_data(self, mock_db_session):
        """Prueba un error cuando faltan datos obligatorios."""
        # mock_get_jwt_identity.return_value = "test_user"
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        response = self.client.post(
            "/providers/add",
            # headers={"Authorization": f"Bearer {self.jwt_token}"},
            data=json.dumps({
                "identification_number": "123456"
            }),  # Falta información clave
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
