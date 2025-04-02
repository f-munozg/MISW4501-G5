import unittest
import os
from unittest.mock import patch, MagicMock
from flask import json
# from flask_jwt_extended import create_access_token
from app import create_app
from sqlalchemy.exc import IntegrityError

class TestAddProduct(unittest.TestCase):
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
    def test_create_product_success(self, mock_db_session):
        """Prueba la creación exitosa de un producto."""
        # mock_get_jwt_identity.return_value = "test_user"
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        response = self.client.post(
            "/products/add",
            # headers={"Authorization": f"Bearer {self.jwt_token}"},
            data=json.dumps({
                "sku": "ABC123",
                "name": "Producto de ejemplo",
                "unit_value": 19.99,
                "conditions_storage": "Almacenar en un lugar seco",
                "product_features": "Resistente al agua",
                "provider_id": "debedacc-3e31-4003-8986-871637d727af",
                "time_delivery_dear": "2025-04-01",
                "photo": "iVBORw0KGgoAAAANSUhEUgAAA+gAAAPoC...",
                "description": "Este es un producto de prueba."
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["message"], "product created successfully")
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch("models.models.db.session")
    # @patch("flask_jwt_extended.get_jwt_identity")
    def test_create_product_duplicate(self, mock_db_session):
        """Prueba un error al intentar crear un producto duplicado."""
        # mock_get_jwt_identity.return_value = "test_user"
        mock_db_session.add = MagicMock()
        mock_db_session.commit.side_effect = IntegrityError("test", "test", "test")

        response = self.client.post(
            "/products/add",
            # headers={"Authorization": f"Bearer {self.jwt_token}"},
            data=json.dumps({
                "sku": "ABC123",
                "name": "Producto de ejemplo",
                "unit_value": 19.99,
                "conditions_storage": "Almacenar en un lugar seco",
                "product_features": "Resistente al agua",
                "provider_id": "debedacc-3e31-4003-8986-871637d727af",
                "time_delivery_dear": "2025-04-01",
                "photo": "iVBORw0KGgoAAAANSUhEUgAAA+gAAAPoC...",
                "description": "Este es un producto de prueba."
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 409)
        self.assertEqual(response.json["message"], "product is already registered")
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch("models.models.db.session")
    # @patch("flask_jwt_extended.get_jwt_identity")
    def test_create_product_missing_data(self, mock_db_session):
        """Prueba un error cuando faltan datos obligatorios."""
        # mock_get_jwt_identity.return_value = "test_user"
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        response = self.client.post(
            "/products/add",
            # headers={"Authorization": f"Bearer {self.jwt_token}"},
            data=json.dumps({
                "sku": "ABC123",
                "name": "Producto de ejemplo"
            }),  # Falta información clave
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)

if __name__ == "__main__":
    unittest.main()
