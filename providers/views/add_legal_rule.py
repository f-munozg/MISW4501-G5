from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models.models import db, Rule, TypeRule, ProductCategory
from sqlalchemy.orm.exc import NoResultFound

class AddLegalRule(Resource):
    def post(self):
        data = request.json

        required_fields = [
            "country", "category_product", "description"
        ]

        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            return {"message": f"Faltan campos requeridos: {', '.join(missing_fields)}"}, 400

        try:
            category_product = ProductCategory(data["category_product"])
        except ValueError:
            return {"message": f"Categoria de producto inválido. Opciones: {[e.value for e in ProductCategory]}"}, 400

        regla = Rule(
            country = data["country"],
            type_rule = TypeRule.LEGAL,
            category_product = category_product,
            description = data["description"]
        )

        try:
            db.session.add(regla)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Error al guardar la regla en la base de datos."}, 500

        return {
            "message": "Regla legal creada exitosamente", 
            "id": str(regla.id)
        }, 201
