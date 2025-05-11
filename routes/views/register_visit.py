from flask import request
from datetime import datetime
from flask_restful import Resource
from models.models import db, RouteStop, Route, StopStatus, RouteType, StopResult, RouteStatus

class RegisterVisit(Resource):
    def post(self):
        # validate data
        data = request.json

        required_fields = [ "customer_id", "observations", "status", "result"]

        
        missing_fields = [field for field in required_fields if field not in data or not data[field]]
        if missing_fields:
            return {
                "message": f"Missing required fields: {', '.join(missing_fields)}"
            }, 400
        
        
        customer_id = data.get("customer_id")
        # find stop
        stop = db.session.query(RouteStop).join(Route, Route.id == RouteStop.route_id).filter(RouteStop.customer_id == customer_id, 
                                                  RouteStop.status == StopStatus.PENDIENTE,
                                                  Route.type == RouteType.VISITA).first()
        
        if not stop:
            return {"message": "invalid customer to register visit"}, 400
        
        # update data
        status = data.get("status")
        result = data.get("result")
        if status == "done":
            stop.status = StopStatus.COMPLETADA
        if status == "failed":
            stop.status = StopStatus.FALLIDA

        if result == "order":
            stop.result = StopResult.PEDIDO
        if result == "reserve":
            stop.result = StopResult.RESERVA
        
        stop.observations = data.get("observations")
        # save
        db.session.commit()
        # if last stop, finish route
        stops = db.session.query(RouteStop).filter(RouteStop.route_id == stop.route_id,
                                                   RouteStop.status == StopStatus.PENDIENTE).all()
        if len(stops) <= 0:
            route = db.session.query(Route).filter(Route.id == stop.route_id).first()
            route.status = RouteStatus.COMPLETADA
            db.session.commit()
        return {"message": "visit registered successfully"}, 200
