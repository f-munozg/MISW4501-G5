from flask_restful import Resource
from models.models import db, User, Role, UsersJsonSchema

class GetUsersMovements(Resource):
    def get(self):
        role_names = ["Administrador", "Logistica"]

        users = (db.session.query(User)
                .join(Role, User.role == Role.id)
                .filter(Role.name.in_(role_names))
                .all())       

        json_users = UsersJsonSchema(
            many=True
        ).dump(users)

        return {
            "users": json_users
        }, 200
