from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models.models import db, Rule, TypeRule, TypeCommercialRule
from sqlalchemy.orm.exc import NoResultFound

class AddCommercialRule(Resource):
    def post(self):
        data = request.json

        required_fields = [
            "country", "type_commercial_rule", "description"
        ]

        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            return {"message": f"Faltan campos requeridos: {', '.join(missing_fields)}"}, 400

        try:
            type_commercial_rule = TypeCommercialRule(data["type_commercial_rule"])
        except ValueError:
            return {"message": f"Tipo de impuesto inválido. Opciones: {[e.value for e in TypeCommercialRule]}"}, 400

        regla = Rule(
            country = data["country"],
            type_rule = TypeRule.COMERCIAL,
            type_commercial_rule = type_commercial_rule,
            description = data["description"]
        )

        try:
            db.session.add(regla)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Error al guardar la regla en la base de datos."}, 500

        return {
            "message": "Regla comercial creada exitosamente", 
            "id": str(regla.id)
        }, 201
