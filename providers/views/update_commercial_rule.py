from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError
from models.models import db, Rule, TypeRule, TypeCommercialRule
from sqlalchemy.orm.exc import NoResultFound
import uuid

class UpdateCommercialRule(Resource):
    def put(self, rule_id):
        try:
            rule_uuid = uuid.UUID(rule_id)
        except ValueError:
            return {"message": "ID de regla inválido"}, 400

        data = request.json
        required_fields = ["country", "type_commercial_rule", "description"]
        missing = [f for f in required_fields if f not in data or data[f] is None]
        if missing:
            return {"message": f"Faltan campos requeridos: {', '.join(missing)}"}, 400

        try:
            rule = db.session.query(Rule).filter_by(id=rule_uuid, type_rule=TypeRule.COMERCIAL).one()
        except NoResultFound:
            return {"message": "Regla comercial no encontrada"}, 404

        try:
            rule.country = data["country"]
            rule.type_commercial_rule = TypeCommercialRule(data["type_commercial_rule"])
            rule.description = data["description"]
            db.session.commit()
        except (ValueError, KeyError):
            return {"message": "Datos inválidos en el cuerpo de la solicitud"}, 400
        except IntegrityError:
            db.session.rollback()
            return {"message": "Error al actualizar la regla"}, 500

        return {"message": "Regla comercial actualizada exitosamente"}, 200
