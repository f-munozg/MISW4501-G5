from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models.models import db, Rule, TypeRule, ProductCategory
from sqlalchemy.orm.exc import NoResultFound
import uuid

class UpdateLegalRule(Resource):
    def put(self, rule_id):
        try:
            rule_uuid = uuid.UUID(rule_id)
        except ValueError:
            return {"message": "ID de regla inválido"}, 400

        data = request.json
        required_fields = ["country", "category_product", "description"]
        missing = [f for f in required_fields if f not in data or data[f] is None]
        if missing:
            return {"message": f"Faltan campos requeridos: {', '.join(missing)}"}, 400

        try:
            rule = db.session.query(Rule).filter_by(id=rule_uuid, type_rule=TypeRule.LEGAL).one()
        except NoResultFound:
            return {"message": "Regla legal no encontrada"}, 404

        try:
            rule.country = data["country"]
            rule.category_product = ProductCategory(data["category_product"])
            rule.description = data["description"]
            db.session.commit()
        except (ValueError, KeyError):
            return {"message": "Datos inválidos en el cuerpo de la solicitud"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"message": "Error al actualizar la regla"}, 500

        return {"message": "Regla legal actualizada exitosamente"}, 200
