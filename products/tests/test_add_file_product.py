import unittest
import os
import io
import uuid
import pandas as pd
from unittest.mock import patch
# from flask_jwt_extended import create_access_token
from app import create_app
from sqlalchemy.exc import IntegrityError

class TestUploadProducts(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        self.app = create_app()
        self.app.testing = True
        self.client = self.app.test_client()
        self.app_context = self.app.app_context()
        self.app_context.push()
        # self.jwt_token = create_access_token(identity="test_user")

    def tearDown(self):
        self.app_context.pop()

    def create_excel_file(self, data_dict):
        df = pd.DataFrame(data_dict)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
            df.to_excel(writer, index=False)
        output.seek(0)
        return output

    def test_upload_products_missing_provider_id(self):
        file = self.create_excel_file({
            "name": ["Producto A"],
            "description": ["Desc"],
            "storage_conditions": ["Fresco"],
            "product_features": ["Feature"],
            "unit_value": [10.5],
            "estimated_delivery_time": ["2025-05-01"],
            "category": ["FARMACIA"]
        })

        response = self.client.post(
            "/products/upload",
            data={"file": (file, "productos.xlsx")},
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid or missing provider_id", response.json["message"])

    def test_upload_products_invalid_file_type(self):
        response = self.client.post(
            "/products/upload",
            data={
                "provider_id": str(uuid.uuid4()),
                "file": (io.BytesIO(b"no es excel"), "archivo.txt")
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid file format", response.json["message"])

    def test_upload_products_missing_required_columns(self):
        file = self.create_excel_file({
            "name": ["Producto A"]
        })
        response = self.client.post(
            "/products/upload",
            data={
                "provider_id": str(uuid.uuid4()),
                "file": (file, "productos.xlsx")
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Missing required columns", response.json["message"])

    def test_upload_products_invalid_category(self):
        file = self.create_excel_file({
            "name": ["Producto A"],
            "description": ["Desc"],
            "storage_conditions": ["Fresco"],
            "product_features": ["Feature"],
            "unit_value": [10.5],
            "estimated_delivery_time": ["2025-05-01"],
            "category": ["ZAPATOS"]
        })
        response = self.client.post(
            "/products/upload",
            data={
                "provider_id": str(uuid.uuid4()),
                "file": (file, "productos.xlsx")
            },
            content_type="multipart/form-data"
        )
        self.assertEqual(response.status_code, 400)
        self.assertIn("Invalid category", response.json["message"])

    @patch("models.models.db.session.bulk_save_objects")
    @patch("models.models.db.session.commit")
    def test_upload_products_success(self, mock_commit, mock_bulk_save_objects):
        file = self.create_excel_file({
            "name": ["Producto A"],
            "description": ["Desc"],
            "storage_conditions": ["Fresco"],
            "product_features": ["Feature"],
            "unit_value": [10.5],
            "estimated_delivery_time": ["2025-05-01"],
            "category": ["FARMACIA"],
            "photo": ["https://example.com/photo.jpg"]
        })

        response = self.client.post(
            "/products/upload",
            data={
                "provider_id": str(uuid.uuid4()),
                "file": (file, "productos.xlsx")
            },
            content_type="multipart/form-data"
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["products_saved"], 1)
        self.assertIn("Upload completed", response.json["message"])

    @patch("models.models.db.session.bulk_save_objects")
    @patch("models.models.db.session.commit")
    @patch("models.models.db.session.rollback")
    def test_upload_products_integrity_error(self, mock_rollback, mock_commit, mock_bulk_save_objects):
        mock_commit.side_effect = IntegrityError("stmt", "params", Exception("unique violation"))

        file = self.create_excel_file({
            "name": ["Producto A"],
            "description": ["Desc"],
            "storage_conditions": ["Fresco"],
            "product_features": ["Feature"],
            "unit_value": [10.5],
            "estimated_delivery_time": ["2025-05-01"],
            "category": ["FARMACIA"],
            "photo": ["https://example.com/photo.jpg"]
        })

        response = self.client.post(
            "/products/upload",
            data={
                "provider_id": str(uuid.uuid4()),
                "file": (file, "productos.xlsx")
            },
            content_type="multipart/form-data"
        )

        self.assertEqual(response.status_code, 409)
        self.assertIn("Database integrity error", response.json["message"])

