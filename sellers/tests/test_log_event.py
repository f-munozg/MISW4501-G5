import unittest, os
from flask import Flask
from flask_restful import Api
from models.models import Seller
from views.log_event import LogEvent
from unittest.mock import patch, MagicMock

class LogEventTestCase(unittest.TestCase):
    def setUp(self):
        os.environ["TESTING"] = "true"
        app = Flask(__name__)
        api = Api(app)
        api.add_resource(LogEvent, '/sellers/log_event')
        self.app = app.test_client()  
        self.app.testing = True 

    @patch("models.models.db.session")
    def test_log_event(self, mock_db_session):
        mock_db_session.add.return_value = MagicMock()
        mock_db_session.commit.return_value = MagicMock()

        data = {
            "name": "fake event",
            "start_date": "2025-12-25",
            "end_date": "2025-12-31",
            "location": "4.596370, -74.109829"
        }

        response = self.app.post("/sellers/log_event", json=data)

        self.assertEqual(response.status_code, 201)

    @patch("models.models.db.session")
    def test_log_event_missing_fields(self, mock_db_session):
        mock_db_session.add.return_value = MagicMock()
        mock_db_session.commit.return_value = MagicMock()

        data = {
            "name": "fake event",
            "start_date": "2025-12-25",
            "end_date": "2025-12-31"
        }

        response = self.app.post("/sellers/log_event", json=data)

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json, {"message": "Missing required fields: location"})

    