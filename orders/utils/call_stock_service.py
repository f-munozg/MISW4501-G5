import os
import requests

STOCK_URL = os.environ.get("STOCK_URL", "http://192.168.20.11:4003")


def call_stock_service(endpoint, payload):
    try:
        response = requests.post(f"{STOCK_URL}{endpoint}", json=payload)
        return response.status_code, response.json()
    except Exception as e:
        return 500, {"message": "Error connecting to stock service", "details": str(e)}
