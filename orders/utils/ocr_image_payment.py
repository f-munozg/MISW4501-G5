import requests
import base64
import re

OCR_API_KEY = 'K87267883388957'
OCR_API_URL = 'https://api.ocr.space/parse/image'

def extract_amount_from_image(image_base64):
    """Extrae el monto de pago de una imagen usando OCR.Space"""
    try:
        image_data = base64.b64decode(image_base64)
        
        response = requests.post(
            OCR_API_URL,
            files={'image': ('receipt.jpg', image_data, 'image/jpeg')},
            data={
                'apikey': OCR_API_KEY,
                'language': 'spa',
                'isOverlayRequired': False
            },
            timeout=30
        )
        response.raise_for_status()
        result = response.json()
        
        if not result.get('ParsedResults'):
            return None
            
        parsed_text = result['ParsedResults'][0]['ParsedText']
        
        amount_pattern = re.compile(r'\$\s*(\d{1,3}(?:[.,\s]?\d{3})*(?:[.,]\d{1,2})?)', re.IGNORECASE)
        amounts = amount_pattern.findall(parsed_text)
        
        if not amounts:
            return None
            
        amount_str = amounts[0]
        
        clean_amount = amount_str.replace('$', '').strip()
        clean_amount = clean_amount.replace('o', '0').replace('ó', '0')
        
        if '.' in clean_amount and ',' in clean_amount:
            # Caso: 1.000,00 → eliminar puntos, convertir coma a punto
            clean_amount = clean_amount.replace('.', '').replace(',', '.')
        elif ',' in clean_amount:
            # Caso: 1,000.00 o 1,000
            if clean_amount.count(',') == 1 and len(clean_amount.split(',')[1]) == 2:
                clean_amount = clean_amount.replace(',', '.')
            else:
                clean_amount = clean_amount.replace(',', '')
        elif '.' in clean_amount:
            # Caso: 1.000.00
            if clean_amount.count('.') > 1 or len(clean_amount.split('.')[-1]) != 2:
                clean_amount = clean_amount.replace('.', '')
        
        try:
            return float(clean_amount)
        except ValueError:
            return None
            
    except Exception as e:
        print(f"Error en OCR: {str(e)}")
        return None