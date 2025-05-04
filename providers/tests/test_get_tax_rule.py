import unittest
import os
from unittest.mock import patch, MagicMock
from flask import json
from app import create_app
from uuid import uuid4

class TestGetRulesTax(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        self.app_context.pop()

    @patch("views.get_tax_rule.db.session")
    def test_get_tax_rule_success(self, mock_db_session):
        mock_rule = MagicMock()
        mock_rule.id = uuid4()
        mock_rule.country = "Colombia"
        mock_rule.type_tax.value = "Valor Agregado"
        mock_rule.value_tax = 19.0
        mock_rule.description = "Impuesto al valor agregado"

        mock_db_session.query.return_value.filter_by.return_value.all.return_value = [mock_rule]

        response = self.client.get("/rules/tax/get")

        self.assertEqual(response.status_code, 200)
        self.assertIn("rules", response.json)
        self.assertEqual(len(response.json["rules"]), 1)
        self.assertEqual(response.json["rules"][0]["pais"], "Colombia")
        self.assertEqual(response.json["rules"][0]["tipo_impuesto"], "Valor Agregado")

    @patch("views.get_tax_rule.db.session")
    def test_get_tax_rule_empty(self, mock_db_session):
        mock_db_session.query.return_value.filter_by.return_value.all.return_value = []

        response = self.client.get("/rules/tax/get")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["rules"], [])

    @patch("views.get_tax_rule.db.session")
    def test_get_tax_rule_exception(self, mock_db_session):
        mock_db_session.query.side_effect = Exception("DB failed")

        response = self.client.get("/rules/tax/get")

        self.assertEqual(response.status_code, 500)
        self.assertIn("message", response.json)
        self.assertIn("details", response.json)
