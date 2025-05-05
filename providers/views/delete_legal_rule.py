from flask_restful import Resource
from models.models import db, Rule, TypeRule
from sqlalchemy.orm.exc import NoResultFound
import uuid

class DeleteLegalRule(Resource):
    def delete(self, rule_id):
        try:
            rule_uuid = uuid.UUID(rule_id)
        except ValueError:
            return {"message": "ID de regla inválido"}, 400

        try:
            rule = db.session.query(Rule).filter_by(id=rule_uuid, type_rule=TypeRule.LEGAL).one()
            db.session.delete(rule)
            db.session.commit()
            return {"message": "Regla legal eliminada correctamente"}, 200
        except NoResultFound:
            return {"message": "Regla legal no encontrada"}, 404
        except Exception as e:
            db.session.rollback()
            return {"message": "Error al eliminar la regla", "details": str(e)}, 500
