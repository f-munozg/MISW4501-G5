import pdfkit
from io import BytesIO
from flask import request, send_file, jsonify
from flask_restful import Resource
from services.report_logic import procesar_reporte, procesar_reporte_vendedor
from io import BytesIO
import pandas as pd
from flask import request

class ReporteVentas(Resource):
    def get(self):
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        producto = request.args.get("producto")
        vendedor = request.args.get("vendedor")

        if not fecha_inicio or not fecha_fin:
            return {"error": "fecha_inicio y fecha_fin son requeridos"}, 400

        try:
            data = procesar_reporte(fecha_inicio, fecha_fin, producto, vendedor)
                        
            if isinstance(data, tuple) and len(data) > 0 and isinstance(data[0], dict) and 'message' in data[0]:
                return data[0]['message'], 400
            else:
                return data, 200
        except Exception as e:
            return {"error": str(e)}, 500

class ReporteVentasCSV(Resource):
    def get(self):
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        producto = request.args.get("producto")
        vendedor = request.args.get("vendedor")

        if not fecha_inicio or not fecha_fin:
            return {"error": "fecha_inicio y fecha_fin son requeridos"}, 400

        try:
            data = procesar_reporte(fecha_inicio, fecha_fin, producto, vendedor)

            if not data:
                return {"message": "No hay datos para el rango indicado"}, 404

            df = pd.DataFrame(data)
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return send_file(output, download_name="reporte_ventas.csv", as_attachment=True, mimetype="text/csv")
        except Exception as e:
            return {"error": str(e)}, 500        

class ReporteVentasExcel(Resource):
    def get(self):
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        producto = request.args.get("producto")
        vendedor = request.args.get("vendedor")

        if not fecha_inicio or not fecha_fin:
            return {"error": "fecha_inicio y fecha_fin son requeridos"}, 400

        try:
            data = procesar_reporte(fecha_inicio, fecha_fin, producto, vendedor)

            if not data:
                return {"message": "No hay datos para el rango indicado"}, 404

            df = pd.DataFrame(data)
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name="Reporte")
            output.seek(0)
            return send_file(output, download_name="reporte_ventas.xlsx", as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            return {"error": str(e)}, 500

class ReporteVentasPDF(Resource):
    def get(self):
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        producto = request.args.get("producto")
        vendedor = request.args.get("vendedor")

        if not fecha_inicio or not fecha_fin:
            return {"error": "fecha_inicio y fecha_fin son requeridos"}, 400

        try:
            data = procesar_reporte(fecha_inicio, fecha_fin, producto, vendedor)

            if not data:
                return {"message": "No hay datos para el rango indicado"}, 404

            df = pd.DataFrame(data)
            html = df.to_html(index=False)

            path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
            config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

            pdf_data = pdfkit.from_string(html, False, configuration=config)
            pdf_output = BytesIO(pdf_data)

            return send_file(pdf_output, download_name="reporte_ventas.pdf", as_attachment=True, mimetype="application/pdf" )
        except Exception as e:
            return {"error": str(e)}, 500

class ReporteVendedor(Resource):
    def get(self):
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        seller_id = request.args.get("seller_id")

        if not fecha_inicio or not fecha_fin:
            return {"error": "fecha_inicio y fecha_fin son requeridos"}, 400

        if not seller_id:
            return {"error": "seller_id es requerido"}, 400

        try:
            data = procesar_reporte_vendedor(fecha_inicio, fecha_fin, seller_id)
            
            if isinstance(data, tuple) and len(data) > 0 and isinstance(data[0], dict) and 'message' in data[0]:
                return data[0]['message'], 400
            else:
                return data, 200
        except Exception as e:
            return {"error": str(e)}, 500

class ReporteVendedorCSV(Resource):
    def get(self):
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        seller_id = request.args.get("seller_id")

        if not fecha_inicio or not fecha_fin or not seller_id:
            return {"error": "fecha_inicio, fecha_fin y seller_id son requeridos"}, 400

        try:
            data = procesar_reporte_vendedor(fecha_inicio, fecha_fin, seller_id)
            
            if not data or 'detalle_productos' not in data:
                return {"message": "No hay datos para el rango indicado"}, 404

            df = pd.DataFrame(data['detalle_productos'])
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            return send_file(output, download_name="reporte_vendedor.csv", as_attachment=True, mimetype="text/csv")
        except Exception as e:
            return {"error": str(e)}, 500

class ReporteVendedorExcel(Resource):
    def get(self):
        fecha_inicio = request.args.get("fecha_inicio")
        fecha_fin = request.args.get("fecha_fin")
        seller_id = request.args.get("seller_id")

        if not fecha_inicio or not fecha_fin or not seller_id:
            return {"error": "fecha_inicio, fecha_fin y seller_id son requeridos"}, 400

        try:
            data = procesar_reporte_vendedor(fecha_inicio, fecha_fin, seller_id)
            
            if not data or 'detalle_productos' not in data:
                return {"message": "No hay datos para el rango indicado"}, 404

            # Crear DataFrame para el resumen
            resumen_df = pd.DataFrame([data['resumen']])
            
            # Crear DataFrame para el detalle
            detalle_df = pd.DataFrame(data['detalle_productos'])

            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                resumen_df.to_excel(writer, index=False, sheet_name="Resumen")
                detalle_df.to_excel(writer, index=False, sheet_name="Detalle")
            output.seek(0)
            return send_file(output, download_name="reporte_vendedor.xlsx", as_attachment=True, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        except Exception as e:
            return {"error": str(e)}, 500