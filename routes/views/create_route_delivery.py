import math, os, requests, random
from datetime import datetime
from flask_restful import Resource
from flask import request
from models.models import db, Route, RouteStop, Truck, RouteType, RouteStatus, StopStatus, StopsJsonSchema

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
        
        i = 0
        stops = []
        for t in trucks:
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
            truck_orders = orders[i:limit]
            for order in truck_orders:
                stop = RouteStop(
                    eta = random.randint(0, 25),
                    customer_id = order.get("customer_id"),
                    order_id = order.get("order_id"),
                    route_id = route.id,
                    status = StopStatus.PENDIENTE,
                    optional = False
                )
                db.session.add(stop)
                stops.append(stop)
                t.available = False

                body = {
                    "order_id": order.get("order_id"),
                    "status": "in_transit"
                }
                url_orders = os.environ.get("ORDERS_URL", "http://192.168.20.11:5001")
                url = f"{url_orders}/orders/updateStatus"
                headers = {} #"Authorization": self.token}
                response = requests.request("PUT", url, headers=headers, json=body )

                if response.status_code != 200:
                    return response.json(), response.status_code

            i = limit
            if i >= len(orders):
                break

        db.session.commit()

        json_stops = StopsJsonSchema(many=True).dump(stops)

        return {
            "message": "route created",
            "id": str(route.id),
            "stops": json_stops
        }, 200
