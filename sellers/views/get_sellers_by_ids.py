from flask import request
from flask_restful import Resource
from models.models import db, Seller
import uuid

class GetSellersByIds(Resource):
    def post(self):
        data = request.get_json()
        ids = data.get("ids", [])

        if not ids or not isinstance(ids, list):
            return {"message": "Debe enviar una lista de IDs"}, 400

        try:
            uuid_ids = [uuid.UUID(i) for i in ids]
        except:
            return {"message": "Lista de IDs inválida"}, 400

        vendedores = db.session.query(Seller).filter(Seller.id.in_(uuid_ids)).all()

        if not vendedores:
            return {"message": "No se encontraron vendedores"}, 404

        resultado = [
            {
                "id": str(v.id),
                "nombre": v.name,
                "identification_number": v.identification_number,
            } for v in vendedores
        ]

        return {"vendedores": resultado}, 200
