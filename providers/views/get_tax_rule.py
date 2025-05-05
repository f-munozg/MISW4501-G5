from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models.models import db, Rule, TypeRule, TipoImpuesto
from sqlalchemy.orm.exc import NoResultFound

class GetTaxRule(Resource):
    def get(self):
        try:
            rules = db.session.query(Rule).filter_by(type_rule=TypeRule.TRIBUTARIA).all()

            response_data = []
            for rule in rules:
                response_data.append({
                    "id": str(rule.id),
                    "pais": rule.country,
                    "tipo_impuesto": rule.type_tax.value,
                    "valor": rule.value_tax,
                    "descripcion": rule.description
                })

            return {"rules": response_data}, 200

        except Exception as e:
            return {"message": "Error al obtener reglas tributarias", "details": str(e)}, 500
