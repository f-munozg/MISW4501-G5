import uuid, time, random
from datetime import datetime
import pandas as pd
from flask import request, jsonify
from flask_restful import Resource
from models.models import db, Product, ProductCategory
from sqlalchemy.exc import IntegrityError

ALLOWED_EXTENSIONS = {"csv", "xls", "xlsx"}

class FileUploadProducts(Resource):
    def allowed_file(self, filename):
        return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

    def post(self):
        start_time = time.time()

        # Validar provider_id
        provider_id = request.form.get("provider_id")
        try:
            provider_id = uuid.UUID(provider_id)
        except (ValueError, TypeError):
            return {"message": "Invalid or missing provider_id"}, 400

        # Validar archivo
        file = request.files.get("file")
        if not file or not self.allowed_file(file.filename):
            return {"message": "Invalid file format. Only CSV or Excel files are allowed."}, 400

        try:
            if file.filename.endswith(".csv"):
                df = pd.read_csv(file)
            else:
                df = pd.read_excel(file)
        except Exception as e:
            return {"message": f"Error reading file: {str(e)}"}, 400

        required_columns = {
            "name", "description", "storage_conditions", "product_features",
            "unit_value", "estimated_delivery_time", "category"
        }

        if not required_columns.issubset(df.columns):
            return {
                "message": f"Missing required columns: {required_columns - set(df.columns)}"
            }, 400

        products = []
        errors = []
        skus_seen = set()

        for index, row in df.iterrows():
            sku = f"{provider_id}-{row['name'].strip().lower()}"
            if sku in skus_seen:
                errors.append({"row": index + 2, "error": "Duplicate product name within same provider"})
                continue
            skus_seen.add(sku)

             # Validar categoría
            try:
                category = ProductCategory[row["category"].upper()]
            except KeyError:
                valid = [cat.name for cat in ProductCategory]
                return {
                    "message": f"Invalid category '{row['category']}'. Valid options are: {', '.join(valid)}"
                }, 400
            
            days_to_deliver = random.randint(1,5)
            estimated_delivery_time = datetime(1970, 1, days_to_deliver, 0, 0)

            try:
                product = Product(
                    sku=sku,
                    name=row["name"],
                    description=row["description"],
                    storage_conditions=row["storage_conditions"],
                    product_features=row["product_features"],
                    unit_value=float(row["unit_value"]),
                    estimated_delivery_time=estimated_delivery_time,
                    photo=row["photo"],
                    provider_id=provider_id,
                    category=category
                )
                products.append(product)
            except Exception as e:
                errors.append({"row": index + 2, "error": str(e)})

        if products:
            try:
                db.session.bulk_save_objects(products)
                db.session.commit()
            except IntegrityError as e:
                db.session.rollback()
                return {
                    "message": "Database integrity error while saving products",
                    "details": str(e.orig)
                }, 409

        elapsed = round(time.time() - start_time, 3)
        return {
            "message": "Upload completed",
            "products_saved": len(products),
            "errors": errors,
            "time_elapsed_seconds": elapsed
        }, 200
