import unittest
import os
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app
from sqlalchemy.exc import IntegrityError

class TestAddLegalRule(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("models.models.db.session")
    def test_add_legal_rule_success(self, mock_db_session):
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        response = self.client.post(
            "/rules/legal/add",
            data=json.dumps({
                "country": "Colombia",
                "category_product": "Farmacia",
                "description": "Los productos farmaceuticos deben pasar por INVIMA"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json["message"], "Regla legal creada exitosamente")
        mock_db_session.add.assert_called_once()
        mock_db_session.commit.assert_called_once()

    @patch("models.models.db.session")
    def test_add_legal_rule_integrity_error(self, mock_db_session):
        mock_db_session.add = MagicMock()
        mock_db_session.commit.side_effect = IntegrityError("x", "y", "z")

        response = self.client.post(
            "/rules/legal/add",
            data=json.dumps({
                "country": "Colombia",
                "category_product": "Farmacia",
                "description": "Duplicado"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json["message"], "Error al guardar la regla en la base de datos.")

    def test_add_legal_rule_missing_fields(self):
        response = self.client.post(
            "/rules/legal/add",
            data=json.dumps({
                "country": "Colombia",
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Faltan campos requeridos", response.json["message"])

    def test_add_legal_rule_invalid_category_product(self):
        response = self.client.post(
            "/rules/legal/add",
            data=json.dumps({
                "country": "Colombia",
                "category_product": "Pruebas",
                "description": "Test"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Categoria de producto inválido", response.json["message"])