from flask import request
from flask_restful import Resource
from flask_sqlalchemy import func
from datetime import datetime, timedelta
from models.models import db, Product, Stock, HistoryStockLog, StockMovementType

class OptimizePurchases(Resource):

    def get(self):
        product_id = request.get("product_id")
        provider_id = request.get("provider_id")

        # validate ids
        
        query = []

        product = db.session.query(Product).filter(Product.id == product_id).first()
        if not product:
            return {}, 404
        
        provider_products = db.session.query(Product).filter(Product.provider_id == provider_id).all()

        if len(provider_products) == 0:
            return {}, 404
        

        products = db.session.query(Product).all()
        # get stock by product
        products = [dic["id"] for dic in products]

        for product in products:
            stock = db.session.query(Stock).filter(Stock.product_id == product.id).all()

            #get last input
            end_date = datetime.now()
            start_date = end_date - timedelta(30)
            movements = db.session.query(HistoryStockLog.movement_type, func.sum(HistoryStockLog.quantity).label('total')).filter(
                HistoryStockLog.product_id == product_id, 
                HistoryStockLog.timestamp.between(start_date, end_date)
                ).group_by(HistoryStockLog.movement_type).all()

            


            if outs > last in
                add = last in
            
            sum outs last month?
                if stock < outs last month && 


        
            -> threshold
                -> purchase last months avg out
            -> outs vs in
                -> purchase difference in outs last month - stock
            


        
