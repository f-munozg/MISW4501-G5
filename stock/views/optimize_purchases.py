import uuid
from flask import request
from flask_restful import Resource
from datetime import datetime, timedelta
from models.models import db, Product, Stock, HistoryStockLog, StockMovementType

class OptimizePurchases(Resource):

    def get(self):
        product_id = request.args.get("product_id")
        provider_id = request.args.get("provider_id")

        # validate ids
        
        query = []

        if product_id and product_id != "":
            try:
                uuid.UUID(product_id)
            except:
                return {"message": "invalid product id"}, 400
            
            query.append(Product.id == product_id)
        
        if provider_id and provider_id != "":
            try:
                uuid.UUID(provider_id)
            except:
                return {"message": "invalid provider id"}, 400
            
            query.append(Product.provider_id == provider_id)
        

        products = db.session.query(Product).filter(*query).all()
        if len(products) == 0:
            return {"message": "no products found"}, 404
        
        
        buy = []
        for product in products:
            # get stock by product
            stock = db.session.query(db.func.sum(Stock.quantity).label("quantity"), 
                                     db.func.sum(Stock.threshold_stock).label("threshold"),
                                     Stock.product_id).filter(Stock.product_id == product.id
                                                              ).group_by(Stock.product_id).first()

            #get last input
            end_date = datetime.now()
            start_date = end_date - timedelta(30)
            movements = db.session.query(HistoryStockLog.movement_type, db.func.sum(HistoryStockLog.quantity).label('total')).filter(
                HistoryStockLog.product_id == product.id, 
                HistoryStockLog.timestamp.between(start_date, end_date)
                ).group_by(HistoryStockLog.movement_type).all()

            inputs = 0
            outputs = 0
            for movement in movements:
                if movement.movement_type == StockMovementType.INGRESO:
                    inputs = movement.total
                else:
                    outputs = movement.total

            if outputs > inputs:
                buy.append(
                    {
                        "product_name": product.name,
                        "suggested_qtty": outputs - inputs,
                        "motive": "Alta demanda previa"
                    }
                ) 

                continue

            if stock.quantity < outputs and outputs > inputs:
                buy.append(
                    {
                        "product_name": product.name,
                        "suggested_qtty": outputs - inputs,
                        "motive": "Alta demanda esperada"
                    }
                ) 

                continue

            if stock.quantity < stock.threshold:
                buy.append(
                    {
                        "product_name": product.name,
                        "suggested_qtty": outputs - inputs,
                        "motive": "Stock bajo"
                    }
                ) 

                continue
                    
        
        return {
            "suggested_purchases": buy
            }, 200

        
