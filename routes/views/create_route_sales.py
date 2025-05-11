import os, requests
from datetime import datetime, timedelta
from flask_restful import Resource
from models.models import db, Route, RouteStop, StopStatus, RouteType, RouteStatus

class CreateRouteSales(Resource):
    def post(self):
        date_limit = datetime.now()+timedelta(-3)
        url_sellers = os.environ.get("SELLERS_URL", "http://192.168.20.11:5001")
        url = f"{url_sellers}/sellers"
        headers = {} #"Authorization": self.token}
        response = requests.request("GET", url, headers=headers)

        if response.status_code != 200:
            return response.json(), response.status_code

        sellers = response.json()["sellers"]
        for seller in sellers:
            seller_id = seller["id"]

            current_route = db.session.query(Route).filter(Route.attendant==seller_id, Route.status==RouteStatus.CONFIRMADA).first()

            if current_route:
                continue
            
            url_customers = os.environ.get("CUSTOMERS_URL", "http://192.168.20.11:5001")
            url = f"{url_customers}/customers?seller_id={seller_id}"
            headers = {} #"Authorization": self.token}
            response = requests.request("GET", url, headers=headers)

            if response.status_code != 200:
                return response.json(), response.status_code
            
            customers = response.json()["customers"]

            if len(customers) <= 0:
                continue

            route = Route(
                type = RouteType.VISITA,
                attendant = seller_id,
                status = RouteStatus.CONFIRMADA,
                date_route = datetime.now()+timedelta(1)
            )

            db.session.add(route)
            db.session.commit()

            for customer in customers:
                cust_id = customer["id"]

                visit = db.session.query(
                    RouteStop
                    ).join(
                        Route, Route.id == RouteStop.route_id
                        ).filter(
                            RouteStop.customer_id == cust_id, RouteStop.status == StopStatus.PENDIENTE,
                            Route.type == RouteType.VISITA, Route.date_route >= date_limit
                            ).first()
                
                if not visit:
                    stop = RouteStop(
                        eta = 1,
                        customer_id = cust_id,
                        route_id = route.id,
                        status = StopStatus.PENDIENTE,
                        optional = False
                    )
                    db.session.add(stop)
                    db.session.commit()

        return {
            "message": "visits created successfully"
        }, 200
