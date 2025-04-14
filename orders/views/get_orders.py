import uuid, os, requests
from models.models import db, Order, OrderJsonSchema
from flask import request
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

class GetOrders(Resource):
    def get(self):

        orders = db.session.query(Order).all()

        jsonOrders = OrderJsonSchema(
            many = True,
        ).dump(orders)

        return {
            "orders": jsonOrders
            
        }, 200
