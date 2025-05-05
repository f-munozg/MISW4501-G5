import unittest
import os
from unittest.mock import patch, MagicMock
from uuid import uuid4
from app import create_app
from sqlalchemy.exc import IntegrityError

class TestUpdateCommercialRule(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

        self.valid_data = {
            "country": "México",
            "type_commercial_rule": "Descuento",
            "description": "Actualización comercial"
        }

        self.rule_id = str(uuid4())

    def tearDown(self):
        self.app_context.pop()

    @patch("views.update_commercial_rule.db.session")
    def test_update_commercial_rule_success(self, mock_db_session):
        mock_rule = MagicMock()
        mock_db_session.query.return_value.filter_by.return_value.one.return_value = mock_rule

        response = self.client.put(
            f"/rules/commercial/update/{self.rule_id}",
            json=self.valid_data
        )

        self.assertEqual(response.status_code, 200)
        self.assertIn("actualizada", response.json["message"])

    @patch("views.update_commercial_rule.db.session")
    def test_update_commercial_rule_not_found(self, mock_db_session):
        from sqlalchemy.orm.exc import NoResultFound
        mock_db_session.query.return_value.filter_by.return_value.one.side_effect = NoResultFound()

        response = self.client.put(
            f"/rules/commercial/update/{self.rule_id}",
            json=self.valid_data
        )
        self.assertEqual(response.status_code, 404)

    def test_update_commercial_rule_invalid_id(self):
        response = self.client.put(
            "/rules/commercial/update/invalid-id",
            json=self.valid_data
        )
        self.assertEqual(response.status_code, 400)

    def test_update_commercial_rule_missing_fields(self):
        response = self.client.put(
            f"/rules/commercial/update/{self.rule_id}",
            json={"country": "México"}
        )
        self.assertEqual(response.status_code, 400)

    @patch("views.update_commercial_rule.db.session")
    def test_update_commercial_rule_integrity_error(self, mock_db_session):
        mock_rule = MagicMock()
        mock_db_session.query.return_value.filter_by.return_value.one.return_value = mock_rule
        mock_db_session.commit.side_effect = IntegrityError("x", "y", "z")

        response = self.client.put(
            f"/rules/commercial/update/{self.rule_id}",
            json=self.valid_data
        )
        self.assertEqual(response.status_code, 500)
