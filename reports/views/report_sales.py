import pdfkit
from io import BytesIO
from flask import request, send_file, jsonify
from flask_restful import Resource
from services.report_logic import procesar_reporte
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