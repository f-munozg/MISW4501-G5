from flask import request, jsonify, send_file
from flask_restful import Resource
from services.report_logic import procesar_reporte_vendedor
from datetime import datetime
import pandas as pd
from io import BytesIO
import uuid

class ReporteVendedor(Resource):
    def get(self):
        try:
            fecha_inicio = request.args.get("fecha_inicio")
            fecha_fin = request.args.get("fecha_fin")
            seller_id = request.args.get("seller_id")

            if not fecha_inicio or not fecha_fin:
                return {"error": "fecha_inicio y fecha_fin son requeridos"}, 400

            if not seller_id:
                return {"error": "seller_id es requerido"}, 400

            try:
                datetime.strptime(fecha_inicio, "%Y-%m-%d")
                datetime.strptime(fecha_fin, "%Y-%m-%d")
            except ValueError:
                return {"error": "Formato de fecha inválido. Use YYYY-MM-DD"}, 400

            # Validar que seller_id sea un UUID válido
            try:
                uuid.UUID(seller_id)
            except ValueError:
                return {"error": "seller_id debe ser un UUID válido"}, 400

            resultado = procesar_reporte_vendedor(fecha_inicio, fecha_fin, seller_id)
            if isinstance(resultado, tuple):
                return resultado

            return resultado

        except Exception as e:
            return {"error": str(e)}, 500

class ReporteVendedorCSV(Resource):
    def get(self):
        try:
            fecha_inicio = request.args.get("fecha_inicio")
            fecha_fin = request.args.get("fecha_fin")
            seller_id = request.args.get("seller_id")

            if not all([fecha_inicio, fecha_fin, seller_id]):
                return {"message": "Todos los parámetros son requeridos"}, 400

            try:
                datetime.strptime(fecha_inicio, "%Y-%m-%d")
                datetime.strptime(fecha_fin, "%Y-%m-%d")
            except ValueError:
                return {"error": "Formato de fecha inválido. Use YYYY-MM-DD"}, 400

            # Validar que seller_id sea un UUID válido
            try:
                uuid.UUID(seller_id)
            except ValueError:
                return {"error": "seller_id debe ser un UUID válido"}, 400

            resultado = procesar_reporte_vendedor(fecha_inicio, fecha_fin, seller_id)
            if isinstance(resultado, tuple):
                return resultado

            if not resultado["detalle_productos"]:
                return {"message": "No hay datos para exportar"}, 404

            df = pd.DataFrame(resultado["detalle_productos"])
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            
            return send_file(
                output,
                mimetype="text/csv",
                as_attachment=True,
                download_name=f"reporte_vendedor_{seller_id}_{fecha_inicio}_{fecha_fin}.csv"
            )

        except Exception as e:
            return {"error": str(e)}, 500

class ReporteVendedorExcel(Resource):
    def get(self):
        try:
            fecha_inicio = request.args.get("fecha_inicio")
            fecha_fin = request.args.get("fecha_fin")
            seller_id = request.args.get("seller_id")

            if not all([fecha_inicio, fecha_fin, seller_id]):
                return {"message": "Todos los parámetros son requeridos"}, 400

            try:
                datetime.strptime(fecha_inicio, "%Y-%m-%d")
                datetime.strptime(fecha_fin, "%Y-%m-%d")
            except ValueError:
                return {"error": "Formato de fecha inválido. Use YYYY-MM-DD"}, 400

            # Validar que seller_id sea un UUID válido
            try:
                uuid.UUID(seller_id)
            except ValueError:
                return {"error": "seller_id debe ser un UUID válido"}, 400

            resultado = procesar_reporte_vendedor(fecha_inicio, fecha_fin, seller_id)
            if isinstance(resultado, tuple):
                return resultado

            if not resultado["detalle_productos"]:
                return {"message": "No hay datos para exportar"}, 404

            # Crear DataFrame para el resumen
            resumen_data = {
                "Métrica": [
                    "Total Ventas",
                    "Total Ventas Plan",
                    "Clientes Atendidos",
                    "Clientes Visitados",
                    "Tasa Conversión",
                    "Periodo Plan",
                    "Meta",
                    "Cumplimiento"
                ],
                "Valor": [
                    resultado["resumen"]["total_ventas"],
                    resultado["resumen"]["total_ventas_plan"],
                    resultado["resumen"]["clientes_atendidos"],
                    resultado["resumen"]["clientes_visitados"],
                    f"{resultado['resumen']['tasa_conversion']}%",
                    resultado["resumen"]["plan"]["periodo"],
                    resultado["resumen"]["plan"]["meta"],
                    resultado["resumen"]["plan"]["cumplimiento"]
                ]
            }
            df_resumen = pd.DataFrame(resumen_data)
            
            # Crear DataFrame para el detalle
            df_detalle = pd.DataFrame(resultado["detalle_productos"])

            # Crear archivo Excel con múltiples hojas
            output = BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_resumen.to_excel(writer, sheet_name='Resumen', index=False)
                df_detalle.to_excel(writer, sheet_name='Detalle', index=False)

            output.seek(0)
            
            return send_file(
                output,
                mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                as_attachment=True,
                download_name=f"reporte_vendedor_{seller_id}_{fecha_inicio}_{fecha_fin}.xlsx"
            )

        except Exception as e:
            return {"error": str(e)}, 500 