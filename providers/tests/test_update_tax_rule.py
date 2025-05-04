import unittest
import os
from unittest.mock import patch, MagicMock
from uuid import uuid4
from app import create_app
from sqlalchemy.exc import IntegrityError

class TestUpdateTaxRule(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.valid_data = {
            "country": "Colombia",
            "type_tax": "Valor Agregado",
            "value_tax": 19.0,
            "description": "Actualización regla tributaria"
        }

        self.rule_id = str(uuid4())

    def tearDown(self):
        self.app_context.pop()

    @patch("views.update_tax_rule.db.session")
    def test_update_tax_rule_success(self, mock_db_session):
        mock_rule = MagicMock()
        mock_db_session.query.return_value.filter_by.return_value.one.return_value = mock_rule

        response = self.client.put(
            f"/rules/tax/update/{self.rule_id}",
            json=self.valid_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("Regla tributaria actualizada exitosamente", response.json["message"])
        mock_db_session.commit.assert_called_once()

    @patch("views.update_tax_rule.db.session")
    def test_update_tax_rule_invalid_id(self, mock_db_session):
        response = self.client.put(
            "/rules/tax/update/invalid-uuid",
            json=self.valid_data
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("ID de regla inválido", response.json["message"])

    @patch("views.update_tax_rule.db.session")
    def test_update_tax_rule_not_found(self, mock_db_session):
        from sqlalchemy.orm.exc import NoResultFound
        mock_db_session.query.return_value.filter_by.return_value.one.side_effect = NoResultFound()

        response = self.client.put(
            f"/rules/tax/update/{self.rule_id}",
            json=self.valid_data
        )
        self.assertEqual(response.status_code, 404)
        self.assertIn("no encontrada", response.json["message"])

    @patch("views.update_tax_rule.db.session")
    def test_update_tax_rule_integrity_error(self, mock_db_session):
        mock_rule = MagicMock()
        mock_db_session.query.return_value.filter_by.return_value.one.return_value = mock_rule
        mock_db_session.commit.side_effect = IntegrityError("x", "y", "z")

        response = self.client.put(
            f"/rules/tax/update/{self.rule_id}",
            json=self.valid_data
        )
        self.assertEqual(response.status_code, 500)
        self.assertIn("Error al actualizar", response.json["message"])

    def test_update_tax_rule_missing_fields(self):
        response = self.client.put(
            f"/rules/tax/update/{self.rule_id}",
            json={
                "country": "Colombia",
                "type_tax": "Valor Agregado"
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Faltan campos requeridos", response.json["message"])
