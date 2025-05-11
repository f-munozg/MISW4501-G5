from datetime import datetime
from flask_restful import Resource

class OptimizeOrder(Resource):
    def post(self):

        # validate data
        # select count(id) from stock where product_id in ( {{order_products}}) group by warehouse_id
        # update stock reserve
        
        return "pong", 200
