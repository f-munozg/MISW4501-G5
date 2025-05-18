from flask import Flask, request, jsonify, send_file
import requests
import pandas as pd
import pdfkit
from io import BytesIO
from collections import defaultdict
from datetime import datetime
import uuid, os, requests
from io import BytesIO
from dateutil import parser

# Configuración de URLs con puertos correctos
url_orders = os.environ.get("ORDERS_URL", "http://localhost:5001")
url_routes = os.environ.get("ROUTES_URL", "http://localhost:5005")
url_sales = os.environ.get("SALES_URL", "http://localhost:5006")
url_sellers = os.environ.get("SELLERS_URL", "http://localhost:5007")

# API endpoints
API_ORDERS_FINISHED = f"{url_orders}/orders/orders_finished"
API_PRODUCTS_ORDERS = f"{url_orders}/orders/products_sold"
API_SELLERS_ORDERS = f"{url_orders}/order/sellers_with_orders"
API_SELLERS = f"{url_sellers}/sellers/sellers_by_ids"
API_ROUTES = f"{url_routes}/routes"
API_SALES_PLANS = f"{url_sales}/sales-plans"

# --- Funciones para obtener datos externos ---
def obtener_ventas(params):
    try:
        # Extraemos el seller_id de los params y lo removemos para la llamada al API
        seller_id = params.pop("vendedor", None)
        
        response = requests.get(API_ORDERS_FINISHED, params=params)
        if response.status_code == 200:
            try:
                data = response.json()
                if seller_id:
                    # Filtramos las órdenes por vendedor
                    orders = data.get("orders", [])
                    filtered_orders = [
                        order for order in orders 
                        if order.get("seller_id") == seller_id
                    ]
                    return {"orders": filtered_orders}
                return data
            except ValueError:
                raise Exception("Respuesta no es JSON válida desde ORDERS API")
        else:
            raise Exception(f"ORDERS API error {response.status_code}: {response.text}")
    except Exception as e:
        raise Exception(f"Error al obtener ventas: {str(e)}")

def obtener_productos(params):
    return requests.get(API_PRODUCTS_ORDERS, params=params).json()

def obtener_vendedores(seller_ids):
    return requests.post(API_SELLERS, json={"ids": seller_ids}).json()

def obtener_metas_vendedor(seller_id, fecha_inicio, fecha_fin):
    try:
        params = {
            "seller_id": seller_id,
            "period": determinar_periodo(fecha_inicio, fecha_fin)
        }
        print(f"Consultando metas con params: {params}")
        response = requests.get(API_SALES_PLANS, params=params)
        print(f"Respuesta de metas: {response.status_code}")
        if response.status_code == 404:
            return None
        elif response.status_code == 200:
            plan = response.json().get("sales_plan", {})
            return {
                "target": float(plan.get("target", 0)),
                "product_id": plan.get("product_id"),
                "period": plan.get("period")
            }
        else:
            raise Exception(f"Error al obtener metas: {response.status_code}")
    except Exception as e:
        raise Exception(f"Error al obtener metas del vendedor: {str(e)}")

def determinar_periodo(fecha_inicio, fecha_fin):
    fecha_inicio = datetime.strptime(fecha_inicio, "%Y-%m-%d")
    fecha_fin = datetime.strptime(fecha_fin, "%Y-%m-%d")
    
    diferencia_dias = (fecha_fin - fecha_inicio).days
    
    if diferencia_dias <= 93:  # ~3 meses
        return "TRIMESTRAL"
    elif diferencia_dias <= 186:  # ~6 meses
        return "SEMESTRAL"
    else:
        return "ANUAL"

def obtener_rutas_vendedor(seller_id):
    try:
        params = {
            "assignee_id": seller_id,
            "status": "Confirmada"
        }
        print(f"Consultando rutas con params: {params}")
        response = requests.get(API_ROUTES, params=params)
        print(f"Respuesta de rutas: {response.status_code}")
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"Routes API error {response.status_code}: {response.text}")
    except Exception as e:
        raise Exception(f"Error al obtener rutas del vendedor: {str(e)}")

def procesar_reporte(fecha_inicio, fecha_fin, producto=None, vendedor=None):
    resultado = []
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

    if len(ordenes) == 0:
        return {"message": "No se encontraron ventas en este rango de fechas"}, 404

    productos_data = obtener_productos(params)
    productos_lista = productos_data.get("productos", []) if productos_data else []

    if len(productos_lista) == 0:
        return {"message": "No se encontraron ventas para este producto"}, 404

    seller_ids = list({orden["seller_id"] for orden in ordenes if "seller_id" in orden})

    vendedores_lista = obtener_vendedores(seller_ids)
    vendedores_data = vendedores_lista.get("vendedores", []) if vendedores_lista else []

    if len(vendedores_lista) == 0:
        return {"message": "No se encontraron ventas para este vendedor"}, 404

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

def procesar_reporte_vendedor(fecha_inicio, fecha_fin, seller_id):
    if not seller_id:
        return {"message": "El ID del vendedor es requerido"}, 400

    try:
        total_ventas = 0
        total_ventas_meta = 0
        clientes_atendidos = set()
        clientes_visitados = set()
        productos_vendidos = []
        metas = None

        params = {
            "fecha_inicio": fecha_inicio,
            "fecha_fin": fecha_fin,
            "vendedor": seller_id
        }
        try:
            ventas = obtener_ventas(params)
            ordenes = ventas.get("orders", []) if isinstance(ventas, dict) else []
        except Exception as e:
            print(f"Error al obtener ventas: {str(e)}")
            ordenes = []

        try:
            productos_data = obtener_productos({"fecha_inicio": fecha_inicio, "fecha_fin": fecha_fin})
            productos_lista = productos_data.get("productos", []) if isinstance(productos_data, dict) else []
            productos_map = {p["id"]: p for p in productos_lista}
        except Exception as e:
            print(f"Error al obtener productos: {str(e)}")
            productos_map = {}

        try:
            metas = obtener_metas_vendedor(seller_id, fecha_inicio, fecha_fin)
        except Exception as e:
            print(f"Error al obtener metas: {str(e)}")
            metas = None

        try:
            rutas_data = obtener_rutas_vendedor(seller_id)
            rutas = rutas_data.get("routes", []) if isinstance(rutas_data, dict) else []
            
            # Procesar rutas para obtener clientes visitados
            for ruta in rutas:
                if isinstance(ruta, dict) and "stops" in ruta:
                    for stop in ruta["stops"]:
                        if isinstance(stop, dict) and stop.get("customer_id"):
                            clientes_visitados.add(stop["customer_id"])
        except Exception as e:
            print(f"Error al obtener rutas: {str(e)}")
            rutas = []
        
        for orden in ordenes:
            if not isinstance(orden, dict):
                continue

            try:
                detalle = orden.get("detalle", [])
                valor_orden = 0
                
                for item in detalle:
                    if not isinstance(item, dict):
                        continue
                        
                    prod_id = item.get("product_id")
                    if not prod_id:
                        continue

                    cantidad = float(item.get("quantity", 0))
                    producto = productos_map.get(prod_id, {})
                    valor_unitario = float(producto.get("unit_value", 0))
                    valor_total = cantidad * valor_unitario
                    valor_orden += valor_total

                    if metas and isinstance(metas, dict) and metas.get("product_id") == str(prod_id):
                        total_ventas_meta += valor_total
                    
                    nombre_producto = producto.get("name", "Desconocido")
                    if nombre_producto == "Desconocido" and prod_id:
                        nombre_producto = f"Producto {prod_id}"
                    
                    productos_vendidos.append({
                        "producto": nombre_producto,
                        "fecha_venta": orden.get("date_order"),
                        "cantidad": cantidad,
                        "valor_unitario": valor_unitario,
                        "valor_total": valor_total
                    })

                total_ventas += valor_orden
                
                if orden.get("customer_id"):
                    clientes_atendidos.add(orden.get("customer_id"))
                    
            except Exception as e:
                print(f"Error procesando orden: {str(e)}")
                continue

        porcentaje_cumplimiento = 0
        if metas and isinstance(metas, dict) and metas.get("target", 0) > 0:
            porcentaje_cumplimiento = (total_ventas_meta / float(metas["target"])) * 100

        tasa_conversion = 0
        if len(clientes_visitados) > 0:
            tasa_conversion = (len(clientes_atendidos) / len(clientes_visitados)) * 100
        elif len(clientes_atendidos) > 0:
            tasa_conversion = "N/A" 

        productos_vendidos.sort(key=lambda x: x.get("fecha_venta", "") if x.get("fecha_venta") else "")

        info_plan = {
            "periodo": metas.get("period", "No tiene plan activo") if isinstance(metas, dict) else "No tiene plan activo",
            "producto": productos_map.get(metas.get("product_id", ""), {}).get("name", "No especificado") if isinstance(metas, dict) else "No especificado",
            "meta": float(metas.get("target", 0)) if isinstance(metas, dict) else 0,
            "cumplimiento": f"{round(porcentaje_cumplimiento, 2)}%"
        }

        return {
            "resumen": {
                "total_ventas": round(total_ventas, 2),
                "total_ventas_plan": round(total_ventas_meta, 2),
                "clientes_atendidos": len(clientes_atendidos),
                "clientes_visitados": len(clientes_visitados),
                "tasa_conversion": tasa_conversion,
                "plan": info_plan
            },
            "detalle_productos": productos_vendidos
        }

    except Exception as e:
        print(f"Error general en el reporte: {str(e)}")
        return {"error": str(e)}, 500

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