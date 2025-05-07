import math
from datetime import datetime
from flask_restful import Resource
from flask import request
from models.models import db, Route, RouteStop, Truck, RouteType, RouteStatus, StopStatus

class CreateRouteDelivery(Resource):
    def post(self):

        data = request.json

        required_fields = [ "orders"]

        
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        # get orders
        orders = data.get("orders")

        # check orders already on routes
        trucks = db.session.query(Truck).filter(Truck.available == True).all()

        if len(trucks) <= 0: 
            return {
                "message": "no available trucks"
            }, 409
        print('orders:', len(orders))
        i = 0
        for t in trucks:
            print('i:', i)
            print('capacity:', t.capacity)
            limit = int(i+t.capacity)
            if limit >= len(orders):
                limit = len(orders)
            
            route = Route(
                type = RouteType.ENTREGA,
                status = RouteStatus.CREADA,
                attendant = t.id,
                date_route = datetime.now(),
                updated_at = datetime.now()
            )
            db.session.add(route)
            db.session.commit()
            print('gets -> ',i, ':', limit )
            truck_orders = orders[i:limit]
            for order in truck_orders:
                stop = RouteStop(
                    eta = 1,
                    customer_id = order.get("customer_id"),
                    route_id = route.id,
                    status = StopStatus.PENDIENTE,
                    optional = False
                )
                db.session.add(stop)
            i = limit
            print('i again:', i)
            if i >= len(orders):
                break

        db.session.commit()

        return "pong", 200
