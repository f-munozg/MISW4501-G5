import unittest
import os
from unittest.mock import patch, MagicMock
from uuid import uuid4
from app import create_app

class TestDeleteLegalRule(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.rule_id = str(uuid4())
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("views.delete_legal_rule.db.session")
    def test_delete_legal_rule_success(self, mock_db):
        mock_rule = MagicMock()
        mock_db.query.return_value.filter_by.return_value.one.return_value = mock_rule

        response = self.client.delete(f"/rules/legal/delete/{self.rule_id}")
        self.assertEqual(response.status_code, 200)
        self.assertIn("eliminada", response.json["message"])

    @patch("views.delete_legal_rule.db.session")
    def test_delete_legal_rule_not_found(self, mock_db):
        from sqlalchemy.orm.exc import NoResultFound
        mock_db.query.return_value.filter_by.return_value.one.side_effect = NoResultFound()

        response = self.client.delete(f"/rules/legal/delete/{self.rule_id}")
        self.assertEqual(response.status_code, 404)

    def test_delete_legal_rule_invalid_id(self):
        response = self.client.delete("/rules/legal/delete/invalid-id")
        self.assertEqual(response.status_code, 400)
