import unittest, os
from flask import Flask
from flask_restful import Api
from views.get_sales import GetSales
from unittest.mock import patch, MagicMock

class GetSalesTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(GetSales, '/sales')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_get_sales_not_found(self, mock_db_session):
        mock_db_session.query = MagicMock()
        response = self.app.get('/sales')
        
        self.assertEqual(response.status_code, 204)

    @patch("models.models.db.session")
    def test_get_sales_all_filters(self, mock_db_session):
        mock_db_session.query = MagicMock()
        response = self.app.get('/sales?product=product_1&provider=provider_1&' \
        'category=category_1&initial_date=2022-03-03&final_date=2022-03-03')
        
        self.assertEqual(response.status_code, 204)

    @patch("models.models.db.session")
    def test_get_sales_all_filters_invalid_date(self, mock_db_session):
        mock_db_session.query = MagicMock()
        response = self.app.get('/sales?product=product_1&provider=provider_1&' \
        'category=category_1&initial_date=20-03-03&final_date=2022-03-03')
        
        self.assertEqual(response.status_code, 204)