from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models.models import db, Rule, TypeRule, TipoImpuesto
from sqlalchemy.orm.exc import NoResultFound

class AddTaxRule(Resource):
    def post(self):
        data = request.json

        required_fields = [
            "country", "type_tax", "value_tax", "description"
        ]

        missing_fields = [field for field in required_fields if field not in data or data[field] is None]
        if missing_fields:
            return {"message": f"Faltan campos requeridos: {', '.join(missing_fields)}"}, 400

        try:
            type_tax = TipoImpuesto(data["type_tax"])
        except ValueError:
            return {"message": f"Tipo de impuesto inválido. Opciones: {[e.value for e in TipoImpuesto]}"}, 400

        try:
            value_tax = float(data["value_tax"])
        except ValueError:
            return {"message": "'valor' debe ser un número válido."}, 400

        regla = Rule(
            country = data["country"],
            type_rule = TypeRule.TRIBUTARIA,
            type_tax = type_tax,
            value_tax = value_tax,
            description = data["description"]
        )

        try:
            db.session.add(regla)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"message": "Error al guardar la regla en la base de datos."}, 500

        return {
            "message": "Regla tributaria creada exitosamente", 
            "id": str(regla.id)
        }, 201
