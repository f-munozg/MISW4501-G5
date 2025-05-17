import unittest, os
from flask import Flask
from flask_restful import Api
from views.optimize_purchases import OptimizePurchases
from models.models import StockMovementType, Product
from unittest.mock import patch, MagicMock

class GetSellerTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(OptimizePurchases, '/stock/optimize_purchases')
        self.app = app.test_client()  
        self.app.testing = True 


    @patch("models.models.db.session")
    def test_optimize_purchases(self, mock_db_session):
        mock_db_session.query.return_value.filter.return_value.all.return_value = [
            Product(id = "abcde")
        ]
        mock_db_session.query.return_value.filter.return_value.group_by.return_value.first.return_value = {
                    "quantity":1,
                    "threshold":2,
                    "product_id":"abcde"
                }
        
        mock_db_session.query.return_value.filter.return_value.group_by.return_value.all.return_value =    [
                MagicMock(
                    movement_type= StockMovementType.INGRESO,
                    total = 1
                ),
                MagicMock(
                    movement_type= StockMovementType.SALIDA,
                    total= 2
                )
            ]
        

        response = self.app.get('/stock/optimize_purchases')

        self.assertEqual(response.status_code, 200)

    @patch("models.models.db.session")
    def test_optimize_purchases_no_products_found(self, mock_db_session):
        mock_db_session.query = MagicMock()

        response = self.app.get('/stock/optimize_purchases?product_id=26ad00d3-9f2f-45d7-b773-36a5b277a178&provider_id=26ad00d3-9f2f-45d7-b773-36a5b277a178')

        self.assertEqual(response.status_code, 404)

    @patch("models.models.db.session")
    def test_optimize_purchases_invalid_product_id(self, mock_db_session):
        mock_db_session.query = MagicMock()

        response = self.app.get('/stock/optimize_purchases?product_id=26ad00d3-9f2f-45d7-b773-36a5b277a17')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"message": "invalid product id"})

    @patch("models.models.db.session")
    def test_optimize_purchases_invalid_provider_id(self, mock_db_session):
        mock_db_session.query = MagicMock()

        response = self.app.get('/stock/optimize_purchases?provider_id=26ad00d3-9f2f-45d7-b773-36a5b277a17')

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"message": "invalid provider id"})