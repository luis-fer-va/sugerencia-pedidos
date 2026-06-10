"""Datos de muestra (fallback) para que la UI levante sin el backend real.

Se usa SOLO desde `app.py` dentro de un try/except cuando `PedidoService` aún no
está disponible. El esquema replica EXACTAMENTE `COLS_SALIDA`.
"""
from __future__ import annotations

import datetime as _dt

import pandas as pd

from src.app.domain.contracts import COLS_SALIDA, ColsSalida
from src.app.domain.reglas import Estado


def df_muestra() -> pd.DataFrame:
    """DataFrame de 4 filas que cubre los 4 estados del semáforo."""
    filas = [
        {
            ColsSalida.ID: 101,
            ColsSalida.NOMBRE: "Costilla Ahumada",
            ColsSalida.CATEGORIA: "Ahumados",
            ColsSalida.CATEGORIA_N2: "Cerdo",
            ColsSalida.UNIDAD: "kg",
            ColsSalida.ES_PERECEDERO: True,
            ColsSalida.PROVEEDOR: "Ahumados del Valle",
            ColsSalida.STOCK: 2.94,
            ColsSalida.VENTA_DIARIA: 3.03,
            ColsSalida.DIAS_INVENTARIO: 1.0,
            ColsSalida.NIVEL_OBJETIVO: 27.3,
            ColsSalida.SUGERIDO: 24.0,
            ColsSalida.ESTADO: Estado.CRITICO.value,
            ColsSalida.ALERTA_MERMA: False,
            ColsSalida.DIAS_SIN_VENDER: 0,
            ColsSalida.CAPITAL_RIESGO: 0.0,
            ColsSalida.COSTO_UNITARIO: 18000.0,
        },
        {
            ColsSalida.ID: 102,
            ColsSalida.NOMBRE: "Plátano Maduro",
            ColsSalida.CATEGORIA: "Fruver",
            ColsSalida.CATEGORIA_N2: "Verduras",
            ColsSalida.UNIDAD: "kg",
            ColsSalida.ES_PERECEDERO: True,
            ColsSalida.PROVEEDOR: "Fruver Rebarato",
            ColsSalida.STOCK: 42.8,
            ColsSalida.VENTA_DIARIA: 5.37,
            ColsSalida.DIAS_INVENTARIO: 8.0,
            ColsSalida.NIVEL_OBJETIVO: 48.3,
            ColsSalida.SUGERIDO: 5.5,
            ColsSalida.ESTADO: Estado.REPONER.value,
            ColsSalida.ALERTA_MERMA: False,
            ColsSalida.DIAS_SIN_VENDER: 0,
            ColsSalida.CAPITAL_RIESGO: 0.0,
            ColsSalida.COSTO_UNITARIO: 2200.0,
        },
        {
            ColsSalida.ID: 103,
            ColsSalida.NOMBRE: "Cadera Especial",
            ColsSalida.CATEGORIA: "Res",
            ColsSalida.CATEGORIA_N2: "Cortes finos",
            ColsSalida.UNIDAD: "kg",
            ColsSalida.ES_PERECEDERO: True,
            ColsSalida.PROVEEDOR: "Diana Corporation",
            ColsSalida.STOCK: 7.75,
            ColsSalida.VENTA_DIARIA: 0.81,
            ColsSalida.DIAS_INVENTARIO: 9.6,
            ColsSalida.NIVEL_OBJETIVO: 7.3,
            ColsSalida.SUGERIDO: 0.0,
            ColsSalida.ESTADO: Estado.CUBIERTO.value,
            ColsSalida.ALERTA_MERMA: False,
            ColsSalida.DIAS_SIN_VENDER: 1,
            ColsSalida.CAPITAL_RIESGO: 0.0,
            ColsSalida.COSTO_UNITARIO: 28000.0,
        },
        {
            ColsSalida.ID: 104,
            ColsSalida.NOMBRE: "Yuca",
            ColsSalida.CATEGORIA: "Fruver",
            ColsSalida.CATEGORIA_N2: "Tubérculos",
            ColsSalida.UNIDAD: "kg",
            ColsSalida.ES_PERECEDERO: True,
            ColsSalida.PROVEEDOR: "Fruver Rebarato",
            ColsSalida.STOCK: 13.16,
            ColsSalida.VENTA_DIARIA: 0.22,
            ColsSalida.DIAS_INVENTARIO: 60.6,
            ColsSalida.NIVEL_OBJETIVO: 1.8,
            ColsSalida.SUGERIDO: 0.0,
            ColsSalida.ESTADO: Estado.ESTANCADO.value,
            ColsSalida.ALERTA_MERMA: True,
            ColsSalida.DIAS_SIN_VENDER: 47,
            ColsSalida.CAPITAL_RIESGO: 39480.0,
            ColsSalida.COSTO_UNITARIO: 3000.0,
        },
    ]
    df = pd.DataFrame(filas, columns=COLS_SALIDA)
    return df.sort_values(ColsSalida.DIAS_INVENTARIO).reset_index(drop=True)


def kpis_muestra() -> dict:
    """KPIs coherentes con `df_muestra()`."""
    return {
        "a_pedir": 2,
        "criticos": 1,
        "valor_pedido": 454450.0,
        "capital_congelado": 39480.0,
    }


def fecha_corte_muestra() -> _dt.date:
    """Fecha de corte de los datos de muestra."""
    return _dt.date(2026, 6, 6)


def proveedores_muestra() -> list[str]:
    return ["Ahumados del Valle", "Diana Corporation", "Fruver Rebarato"]


def categorias_muestra() -> list[str]:
    return ["Ahumados", "Fruver", "Res"]
