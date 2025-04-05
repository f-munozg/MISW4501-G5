import unittest, os
from flask import Flask, json
from flask_restful import Api
from views.create_user import CreateUser
from unittest.mock import patch, MagicMock
from sqlalchemy.exc import IntegrityError

class CreateUserTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(CreateUser, '/user')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_create_user(self, mock_db_session):
        mock_db_session.add = MagicMock()
        mock_db_session.commit = MagicMock()

        response = self.app.post('/user',
            data=json.dumps({
                "identification_number": "123321123",
                "name": "John Doe",
                "password": "password123",
                "email": "mail@mail.com",
                "role": "cc4a4702-3d00-4a1f-9474-d8ff331485a7"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 201)
        
        self.assertEqual(response.data.decode(), '{"message": "user created successfully"}\n')


    def test_create_user_with_missing_fields(self):
        
        response = self.app.post('/user',
            data=json.dumps({
                "identification_number": "123321123",
                "name": "John Doe",
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "Missing required fields: ' \
        'password, email, role"}\n')


    def test_create_user_invalid_identification_number(self):
        
        response = self.app.post('/user',
            data=json.dumps({
                "identification_number": "ABCDEF",
                "name": "John Doe",
                "password": "password123",
                "email": "mail@mail.com",
                "role": "cc4a4702-3d00-4a1f-9474-d8ff331485a7"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "Invalid \'identification_number\'.' \
        ' Must be a numeric string."}\n')
        
    def test_create_user_invalid_role_id(self):
        
        response = self.app.post('/user',
            data=json.dumps({
                "identification_number": "123321123",
                "name": "John Doe",
                "password": "password123",
                "email": "mail@mail.com",
                "role": "Admin"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 400)
        
        self.assertEqual(response.data.decode(), '{"message": "Invalid role ID"}\n')

    @patch("models.models.db.session")
    def test_create_user_already_exists(self, mock_db_session):
        mock_db_session.add = MagicMock()
        mock_db_session.commit.side_effect = IntegrityError("test", "test", "test")

        response = self.app.post('/user',
            data=json.dumps({
                "identification_number": "123321123",
                "name": "John Doe",
                "password": "password123",
                "email": "mail@mail.com",
                "role": "cc4a4702-3d00-4a1f-9474-d8ff331485a7"
            }),
            content_type="application/json"
        )
        
        self.assertEqual(response.status_code, 409)
        
        self.assertEqual(response.data.decode(), '{"message": "user is already registered"}\n')




if __name__ == '__main__':
    unittest.main()