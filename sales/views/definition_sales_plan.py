import uuid
from models.models import db, SalesPlan, PlanPeriod
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class DefinitionSalesPlan(Resource):
    def post(self):
        data = request.json

        required_fields = ["seller_id", "target", "product_id", "period"]

        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        try:
            uuid.UUID(data["seller_id"])
        except: 
            return {"message": "invalid seller id"}, 400
        
        try:
            uuid.UUID(data["product_id"])
        except: 
            return {"message": "invalid product id"}, 400
        
        # Validar periodo
        try:
            period = PlanPeriod[data["period"].upper()]
        except KeyError:
            valid = [period.name for period in PlanPeriod]
            return {
                "message": f"Invalid period '{data['period']}'. Valid options are: {', '.join(valid)}"
            }, 400
        
        existing_plan = db.session.query(SalesPlan).filter_by(
            seller_id=data["seller_id"],
            period=period,
            active=True
        ).first()

        if existing_plan:
            return {
                "message": "An active sales plan already exists for this seller and period."
            }, 409

        salesPlan = SalesPlan(
            seller_id = data["seller_id"],
            target = data["target"],
            product_id = data["product_id"],
            period = period,
            active=True
        )

        try:
            db.session.add(salesPlan)
            db.session.commit()
        except IntegrityError as e:
            db.session.rollback()
            return {
                "message": "Integrity error: possible missing or invalid fields",
                "details": str(e.orig)
            }, 409

        return {
            "message": "Sales period created successfully",
            "id": str(salesPlan.id)
        }, 201
