import uuid, os, requests
from models.models import db, Customer, CustomerJsonSchema
from flask import request
from flask_restful import Resource

class CustomersBySeller(Resource):
    def get(self, seller_id):
        if seller_id and seller_id != "":
            try:
                uuid.UUID(seller_id)
            except: 
                return {"message": "invalid seller id"}, 400
        
        url_routes = os.environ.get("ROUTES_URL", "http://localhost:4002")
        url = f"{url_routes}/routes?assignee={seller_id}&status=Confirmada"
        headers = {} #"Authorization": self.token}
        response = requests.request("GET", url, headers=headers)

        if response.status_code != 200:
            return response.json(), response.status_code

        routes= response.json().get("routes")
        if len(routes) > 1:
            return {
                "message": "multiple active routes"
            }, 500
        route_id = routes[0]["id"]
        
        url = f"{url_routes}/routes/{route_id}"
        headers = {} #"Authorization": self.token}
        response = requests.request("GET", url, headers=headers)
        if response.status_code != 200:
            return response.json(), response.status_code

        stops= response.json().get("stops")

        cust_list = [dic["customer_id"] for dic in stops]
        
        customers = db.session.query(Customer).filter(Customer.id.in_(cust_list)).all()

        json_customers = CustomerJsonSchema(
            many = True,
        ).dump(customers)

        return {
            "customers": json_customers
        }, 200
