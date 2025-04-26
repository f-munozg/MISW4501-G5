from flask import Flask, request, jsonify, send_file
import requests
import pandas as pd
import pdfkit
from io import BytesIO
from collections import defaultdict
from datetime import datetime
import uuid, os, requests
from io import BytesIO
import pandas as pd
import pdfkit
from dateutil import parser

url_orders = os.environ.get("ORDERS_URL", "http://localhost:5001")
url_sellers = os.environ.get("SELLERS_URL", "http://localhost:5007")

API_ORDERS_FINISHED = f"{url_orders}/orders/orders_finished"
API_PRODUCTS_ORDERS = f"{url_orders}/orders/products_sold"
API_SELLERS_ORDERS = f"{url_orders}/order/sellers_with_orders"
API_SELLERS = f"{url_sellers}/sellers/sellers_by_ids"

# --- Funciones para obtener datos externos ---
def obtener_ventas(params):
    response = requests.get(API_ORDERS_FINISHED, params=params)
    if response.status_code == 200:
        try:
            return response.json()
        except ValueError:
            raise Exception("Respuesta no es JSON válida desde ORDERS API")
    else:
        raise Exception(f"ORDERS API error {response.status_code}: {response.text}")

def obtener_productos(params):
    return requests.get(API_PRODUCTS_ORDERS, params=params).json()

def obtener_vendedores(seller_ids):
    return requests.post(API_SELLERS, json={"ids": seller_ids}).json()

def procesar_reporte(fecha_inicio, fecha_fin, producto=None, vendedor=None):
    params = {
        "fecha_inicio": fecha_inicio,
        "fecha_fin": fecha_fin
    }
    if producto:
        params["producto"] = producto
    if vendedor:
        params["vendedor"] = vendedor

    ventas = obtener_ventas(params)
    ordenes = ventas.get("orders", []) if ventas else []

    seller_ids = list({orden["seller_id"] for orden in ordenes if "seller_id" in orden})

    productos_data = obtener_productos(params)
    productos_lista = productos_data.get("productos", []) if productos_data else []

    vendedores_lista = obtener_vendedores(seller_ids)
    vendedores_data = vendedores_lista.get("vendedores", []) if vendedores_lista else []

    productos_map = {p["id"]: p for p in productos_lista}
    vendedores_map = {v["id"]: v for v in vendedores_data}

    agrupado = defaultdict(lambda: {
        "unidades_vendidas": 0,
        "ingresos": 0.0,
        "fechas": []
    })

    for orden in ordenes:
        vend_id = orden.get("seller_id")
        fecha_str = orden.get("date_order")
        try:
            fecha = parser.parse(fecha_str).date()
        except (ValueError, TypeError):
            fecha = None

        if fecha is None:
            continue

        detalle = orden.get("detalle", []) 
        if detalle is None:
            continue 

        for item in detalle:
            prod_id = item.get("product_id")
            cantidad = item.get("quantity", 0)
            valor_unitario = productos_map.get(prod_id, {}).get("unit_value", 0)

            if cantidad is None:
                cantidad = 0
            if valor_unitario is None:
                valor_unitario = 0.0

            clave = (prod_id, vend_id)
            agrupado[clave]["unidades_vendidas"] += cantidad
            agrupado[clave]["ingresos"] += cantidad * valor_unitario
            agrupado[clave]["fechas"].append(fecha)

    resultado = []
    for (prod_id, vend_id), datos in agrupado.items():
        resultado.append({
            "producto": productos_map.get(prod_id, {}).get("name", prod_id),
            "vendedor": vendedores_map.get(vend_id, {}).get("nombre", vend_id),
            "unidades_vendidas": datos["unidades_vendidas"],
            "ingresos": datos["ingresos"],
            "primera_venta": min(datos["fechas"]).strftime("%Y-%m-%d"),
            "ultima_venta": max(datos["fechas"]).strftime("%Y-%m-%d")
        })

    return resultado

def reporte_ventas_api():
    fecha_inicio = request.args.get("fecha_inicio")
    fecha_fin = request.args.get("fecha_fin")
    producto = request.args.get("producto")
    vendedor = request.args.get("vendedor")

    if not fecha_inicio or not fecha_fin:
        return jsonify({"error": "fecha_inicio y fecha_fin son requeridos"}), 400

    data = procesar_reporte(fecha_inicio, fecha_fin, producto, vendedor)
    return jsonify(data)

def exportar_csv():
    data = procesar_reporte(
        request.args.get("fecha_inicio"),
        request.args.get("fecha_fin"),
        request.args.get("producto"),
        request.args.get("vendedor")
    )
    df = pd.DataFrame(data)
    output = BytesIO()
    df.to_csv(output, index=False)
    output.seek(0)
    return send_file(output, download_name="reporte_ventas.csv", as_attachment=True, mimetype="text/csv")

def exportar_excel():
    data = procesar_reporte(
        request.args.get("fecha_inicio"),
        request.args.get("fecha_fin"),
        request.args.get("producto"),
        request.args.get("vendedor")
    )
    df = pd.DataFrame(data)
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name="Reporte")
    output.seek(0)
    return send_file(output, download_name="reporte_ventas.xlsx", as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

def exportar_pdf():
    try:
        data = procesar_reporte(
            request.args.get("fecha_inicio"),
            request.args.get("fecha_fin"),
            request.args.get("producto"),
            request.args.get("vendedor")
        )
        df = pd.DataFrame(data)
        html = df.to_html(index=False)

        path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
        config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

        pdf_data = pdfkit.from_string(html, False, configuration=config)
        pdf_output = BytesIO(pdf_data)

        return send_file(pdf_output, download_name="reporte_ventas.pdf", as_attachment=True, mimetype="application/pdf")
    except Exception as e:
        print("ERROR EN exportar_pdf:", e)
        return jsonify({"error": str(e)}), 500