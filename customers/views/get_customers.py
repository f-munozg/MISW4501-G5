import uuid, os, requests
from models.models import db, Customer, CustomerJsonSchema
from flask import request
from flask_restful import Resource

class GetCustomers(Resource):
    def get(self):
        seller_user_id = request.args.get('seller_user_id')
        seller_id = request.args.get('seller_id')
        status = request.args.get('status')
        query = []
        if status and status != "" and status == "available":
            query.append(Customer.assigned_seller == None)
        
        if seller_user_id and seller_user_id != "":
            try:
                uuid.UUID(seller_user_id)
            except: 
                return {"message": "invalid user id"}, 400
        
            url_sellers = os.environ.get("SELLERS_ID", "http://localhost:4002")
            url = f"{url_sellers}/sellers/seller?user_id={seller_user_id}"
            headers = {} #"Authorization": self.token}
            response = requests.request("GET", url, headers=headers)

            if response.status_code != 200:
                return response.json(), response.status_code

            seller_returned_id = response.json()["seller"]["id"]
            query.append(Customer.assigned_seller == seller_returned_id)

        if seller_id and seller_id != "":
            try:
                uuid.UUID(seller_id)
            except:
                return {"message": "invalid seller id"}, 400
            
            query.append(Customer.assigned_seller == seller_id)

        customers = db.session.query(Customer).filter(*query).all()

        json_customers = CustomerJsonSchema(
            many = True,
        ).dump(customers)

        return {
            "customers": json_customers
        }, 200
