import unittest
import os, uuid
from datetime import datetime
from unittest.mock import patch, MagicMock, PropertyMock
from flask import json
from app import create_app
from models.models import PQR, PQRStatus, PQRSType, Order, pqr_schema, pqrs_schema, db
from sqlalchemy.exc import IntegrityError

class TestPQRS(unittest.TestCase):
    def setUp(self):
        """Configura la aplicación de prueba."""
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()

    def tearDown(self):
        """Limpia después de cada prueba."""
        if hasattr(self, 'app_context'):
            self.app_context.pop()

    def test_get_customer_pqrs_missing_id(self):
        """Debe fallar si no se pasa customer_id"""
        response = self.client.get("/orders/pqrs/getCustomer")
        self.assertEqual(response.status_code, 400)
        self.assertIn("customer_id is required", response.json["message"])

    def test_get_customer_pqrs_invalid_id(self):
        """Debe fallar si el UUID no es válido"""
        response = self.client.get("/orders/pqrs/getCustomer?customer_id=invalid")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid customer_id format", response.json["message"])

    def test_get_customer_pqrs_invalid_type(self):
        """Debe fallar si el tipo de PQR no es válido"""
        test_uuid = str(uuid.uuid4())
        response = self.client.get(f"/orders/pqrs/getCustomer?customer_id={test_uuid}&type=tipo_invalido")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid PQR type", response.json["message"])

    def test_get_customer_pqrs_invalid_status(self):
        """Debe fallar si el estado de PQR no es válido"""
        test_uuid = str(uuid.uuid4())
        response = self.client.get(f"/orders/pqrs/getCustomer?customer_id={test_uuid}&status=estado_invalido")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid PQR status", response.json["message"])

    def test_get_customer_pqrs_invalid_date_format(self):
        """Debe fallar si el formato de fecha no es válido"""
        test_uuid = str(uuid.uuid4())
        response = self.client.get(
            f"/orders/pqrs/getCustomer?customer_id={test_uuid}&start_date=fecha_invalida&end_date=fecha_invalida"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid date format", response.json["message"])

    def test_get_customer_pqrs_missing_end_date(self):
        """Debe fallar si falta end_date cuando se proporciona start_date"""
        test_uuid = str(uuid.uuid4())
        response = self.client.get(
            f"/orders/pqrs/getCustomer?customer_id={test_uuid}&start_date=2024-01-01"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Both start_date and end_date are required", response.json["message"])

    def test_get_customer_pqrs_missing_start_date(self):
        """Debe fallar si falta start_date cuando se proporciona end_date"""
        test_uuid = str(uuid.uuid4())
        response = self.client.get(
            f"/orders/pqrs/getCustomer?customer_id={test_uuid}&end_date=2024-01-01"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Both start_date and end_date are required", response.json["message"])

    def test_get_seller_pqrs_missing_id(self):
        """Debe fallar si no se pasa seller_id"""
        response = self.client.get("/orders/pqrs/getSeller")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "seller_id is required")

    def test_get_seller_pqrs_invalid_id(self):
        """Debe fallar si el UUID no es válido"""
        response = self.client.get("/orders/pqrs/getSeller?seller_id=invalid")
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json["message"], "Invalid seller_id format")

    def test_get_seller_pqrs_invalid_type(self):
        """Debe fallar si el tipo de PQR no es válido"""
        test_uuid = str(uuid.uuid4())
        response = self.client.get(f"/orders/pqrs/getSeller?seller_id={test_uuid}&type=tipo_invalido")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid PQR type", response.json["message"])

    def test_get_seller_pqrs_invalid_status(self):
        """Debe fallar si el estado de PQR no es válido"""
        test_uuid = str(uuid.uuid4())
        response = self.client.get(f"/orders/pqrs/getSeller?seller_id={test_uuid}&status=estado_invalido")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid PQR status", response.json["message"])

    def test_get_seller_pqrs_invalid_date_format(self):
        """Debe fallar si el formato de fecha no es válido"""
        test_uuid = str(uuid.uuid4())
        response = self.client.get(
            f"/orders/pqrs/getSeller?seller_id={test_uuid}&start_date=fecha_invalida&end_date=fecha_invalida"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid date format", response.json["message"])

    def test_get_seller_pqrs_missing_end_date(self):
        """Debe fallar si falta end_date cuando se proporciona start_date"""
        test_uuid = str(uuid.uuid4())
        response = self.client.get(
            f"/orders/pqrs/getSeller?seller_id={test_uuid}&start_date=2024-01-01"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Both start_date and end_date are required", response.json["message"])

    def test_get_seller_pqrs_missing_start_date(self):
        """Debe fallar si falta start_date cuando se proporciona end_date"""
        test_uuid = str(uuid.uuid4())
        response = self.client.get(
            f"/orders/pqrs/getSeller?seller_id={test_uuid}&end_date=2024-01-01"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Both start_date and end_date are required", response.json["message"])

    def test_create_pqr_missing_fields(self):
        """Debe fallar si faltan campos obligatorios"""
        response = self.client.post(
            "/orders/pqrs/addPQRS",
            data=json.dumps({"type": "PETICION"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required fields", response.json["message"])

    def test_create_OrderId_invalid_uuid(self):
        """Prueba cuando el UUID del order no es válido."""
        response = self.client.post(
            "/orders/pqrs/addPQRS",
            data=json.dumps({
                "type": "peticion",
                "title": "title test",
                "description": "description test",
                "order_id": "no-es-un-uuid",
                "customer_id": "86914890-faed-4f2d-b52d-94bc32624f84"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid UUID format", response.json["message"])

    def test_create_CustomerId_invalid_uuid(self):
        """Prueba cuando el UUID del customer no es válido."""
        response = self.client.post(
            "/orders/pqrs/addPQRS",
            data=json.dumps({
                "type": "peticion",
                "title": "title test",
                "description": "description test",
                "order_id": "86914890-faed-4f2d-b52d-94bc32624f84",
                "customer_id": "no-es-un-uuid"
            }),
            content_type="application/json"
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid UUID format", response.json["message"])

    @patch('models.models.db.session')
    def test_create_pqr_order_not_found(self, mock_session):
        """Prueba cuando el order no existe"""
        test_order_id = str(uuid.uuid4())
        test_customer_id = str(uuid.uuid4())
        
        mock_session.query.return_value.filter.return_value.first.return_value = None

        response = self.client.post(
            "/orders/pqrs/addPQRS",
            data=json.dumps({
                "type": "peticion",
                "title": "Test PQR",
                "description": "Test Description",
                "order_id": test_order_id,
                "customer_id": test_customer_id
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 404)
        self.assertIn("Order not found", response.json["message"])

    def test_update_pqr_missing_order_id(self):
        """Debe fallar si falta order_id"""
        test_pqr_id = str(uuid.uuid4())
        response = self.client.put(
            f'/orders/pqrs/updatePQRS/{test_pqr_id}',
            data=json.dumps({"status": "abierto"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("order_id is required", response.json["message"])

    def test_update_pqr_invalid_status_value(self):
        """Debe fallar si el estado proporcionado no es válido"""
        test_pqr_id = str(uuid.uuid4())
        test_order_id = str(uuid.uuid4())
        
        response = self.client.put(
            f'/orders/pqrs/updatePQRS/{test_pqr_id}',
            data=json.dumps({
                "order_id": test_order_id,
                "status": "estado_invalido"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid status", response.json["message"])


    # def test_update_pqr_invalid_seller_id(self):
    #     """Debe fallar si el seller_id no es un UUID válido"""
    #     test_pqr_id = str(uuid.uuid4())
    #     test_order_id = str(uuid.uuid4())
        
    #     response = self.client.put(
    #         f'/orders/pqrs/updatePQRS/{test_pqr_id}',
    #         data=json.dumps({
    #             "order_id": test_order_id,
    #             "seller_id": "id_invalido"
    #         }),
    #         content_type="application/json"
    #     )
    #     self.assertEqual(response.status_code, 400)
    #     self.assertIn("Invalid seller ID format", response.json["message"])

    def test_update_pqr_invalid_order_id(self):
        """Debe fallar si el order_id no es un UUID válido"""
        test_pqr_id = str(uuid.uuid4())
        
        response = self.client.put(
            f'/orders/pqrs/updatePQRS/{test_pqr_id}',
            data=json.dumps({
                "order_id": "id_invalido",
                "status": "en_proceso"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid UUID format", response.json["message"])

    @patch('models.models.db.session')
    def test_delete_pqr_database_error(self, mock_session):
        """Debe manejar errores de base de datos al eliminar PQR"""
        test_pqr_id = str(uuid.uuid4())
        
        mock_pqr = MagicMock()
        mock_pqr.id = test_pqr_id
        mock_session.query.return_value.get.return_value = mock_pqr
        
        mock_session.commit.side_effect = IntegrityError(None, None, None)
        
        response = self.client.delete(f'/orders/pqrs/deletePQRS/{test_pqr_id}')
        self.assertEqual(response.status_code, 500)
        self.assertIn("Database error", response.json["message"])

    def test_delete_pqr_invalid_uuid(self):
        """Debe fallar si el UUID del PQR no es válido"""
        response = self.client.delete('/orders/pqrs/deletePQRS/invalid-uuid')
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid UUID format", response.json["message"])

    def test_update_pqr_invalid_uuid(self):
        """Debe fallar si el UUID del PQR no es válido"""
        response = self.client.put(
            '/orders/pqrs/updatePQRS/invalid-uuid',
            data=json.dumps({
                "order_id": str(uuid.uuid4()),
                "status": "en_proceso"
            }),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid UUID format", response.json["message"])

    @patch('models.models.PQR.query')
    @patch('models.models.db.session')
    def test_delete_pqr_success(self, mock_session, mock_query):
        """Prueba eliminación exitosa de PQR"""
        test_pqr_id = str(uuid.uuid4())
        mock_pqr = MagicMock()
        mock_pqr.id = test_pqr_id
        mock_query.get.return_value = mock_pqr

        response = self.client.delete(f'/orders/pqrs/deletePQRS/{test_pqr_id}')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["message"], "PQR deleted")

    def test_create_pqr_invalid_type(self):
        """Debe fallar si el tipo de PQR no es válido"""
        test_order_id = str(uuid.uuid4())
        test_customer_id = str(uuid.uuid4())
        
        response = self.client.post(
            "/orders/pqrs/addPQRS",
            data=json.dumps({
                "type": "tipo_invalido",
                "title": "Test PQR",
                "description": "Test Description",
                "order_id": test_order_id,
                "customer_id": test_customer_id
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid PQR type", response.json["message"])

    @patch('models.models.db.session')
    def test_create_pqr_database_error(self, mock_session):
        """Debe manejar errores de base de datos al crear PQR"""
        test_order_id = str(uuid.uuid4())
        test_customer_id = str(uuid.uuid4())
        
        mock_order = MagicMock()
        mock_order.customer_id = test_customer_id
        mock_session.query.return_value.filter.return_value.first.return_value = mock_order
        
        mock_session.commit.side_effect = IntegrityError(None, None, None)
        
        response = self.client.post(
            "/orders/pqrs/addPQRS",
            data=json.dumps({
                "type": "peticion",
                "title": "Test PQR",
                "description": "Test Description",
                "order_id": test_order_id,
                "customer_id": test_customer_id
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 500)
        self.assertIn("Database error", response.json["message"])

if __name__ == '__main__':
    unittest.main()
