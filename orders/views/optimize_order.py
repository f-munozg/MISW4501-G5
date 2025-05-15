import os
import requests
from models.models import db, Product, OrderProducts, Order
from flask_restful import Resource

class OptimizeOrder(Resource):
    def post(self):
        orders = db.session.query(Order).filter(Order.status == "in_transit").all()
    
        for order in orders:
            order_products = db.session.query(OrderProducts).filter(OrderProducts.order_id == order.id).all()
    
            products = []
            warehouses= {}
            viable_warehouse = ""
            for product in order_products:
                #select count * from stock group by warehouseid where product_id in (list) sort by count
                url_stock = os.environ.get("STOCK_URL", "http://192.168.20.11:5001")
                url = f"{url_stock}/stock/{str(product.product_id)}"
                headers = {} #"Authorization": self.token}
                response = requests.request("GET", url, headers=headers)

                if response.status_code != 200:
                    return response.json(), response.status_code
                
                stock = response.json()["stock"]
                stocks = []
                for item in stock:
                    # only=("id", "product_id", "warehouse_id", "quantity", "reserved_quantity")
                    if item["quantity"]-item["reserved_quantity"] >= product.quantity:
                        warehouses[item["warehouse_id"]] = warehouses.get(item["warehouse_id"], 0) + 1
                        stocks.append(item)
                products.append({"product": product, "stock": stocks})


            #validate quantities to create movement
            viable_warehouse = max(warehouses, key=warehouses.get)
            for item in products:
                product = item["product"]
                if viable_warehouse in [product["warehouse_id"] for product in item["stock"]] and viable_warehouse != str(product.warehouse_id):
                    msg, code = self.transfer(product.product_id, product.warehouse_id, product.quantity, "INGRESO")
                    if code != 201:
                        return msg, code
                    msg, code = self.transfer(product.product_id, viable_warehouse, product.quantity, "SALIDA")
                    if code != 201:
                        return msg, code
            
                    product.warehouse_id = viable_warehouse
                    db.session.commit()

        
        return {"message": "deliveries optimized"}, 200
            

    def transfer(self, product_id, warehouse_id, quantity, movement):
        url_stock = os.environ.get("STOCK_URL", "http://192.168.20.11:5001")
        url = f"{url_stock}/stock/movement"
        headers = {}
        body = {
            "product_id": str(product_id),
            "warehouse_id": str(warehouse_id),
            "quantity": quantity,
            "user": "",
            "movement_type": movement
        }
        response = requests.request("POST", url, headers=headers, json=body)
        
        return response.json(), response.status_code
                

