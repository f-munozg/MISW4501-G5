import unittest
from unittest.mock import patch, MagicMock
from utils.ocr_image_payment import extract_amount_from_image
import base64

class TestOCRImagePayment(unittest.TestCase):

    @patch('utils.ocr_image_payment.requests.post')
    def test_extract_valid_amount(self, mock_post):
        # Simula texto reconocido con un monto
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'ParsedResults': [{
                'ParsedText': 'Total: $ 45.50\nGracias por su compra'
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        dummy_base64 = base64.b64encode(b'test').decode()

        amount = extract_amount_from_image(dummy_base64)
        self.assertEqual(amount, 45.50)

    @patch('utils.ocr_image_payment.requests.post')
    def test_extract_amount_not_found(self, mock_post):
        mock_response = MagicMock()
        mock_response.json.return_value = {
            'ParsedResults': [{
                'ParsedText': 'Gracias por su visita'
            }]
        }
        mock_response.raise_for_status.return_value = None
        mock_post.return_value = mock_response

        dummy_base64 = base64.b64encode(b'test').decode()
        amount = extract_amount_from_image(dummy_base64)
        self.assertIsNone(amount)

    @patch('utils.ocr_image_payment.requests.post')
    def test_ocr_api_error(self, mock_post):
        mock_post.side_effect = Exception("Timeout")

        dummy_base64 = base64.b64encode(b'test').decode()
        amount = extract_amount_from_image(dummy_base64)
        self.assertIsNone(amount)
