"""Textos de ayuda (one-liners) por métrica.

Se usan como `help=` en `st.column_config` y en las tarjetas KPI. Pensados para
que una cajera entienda cada número sin jerga de inventarios.
"""
from __future__ import annotations

TOOLTIPS: dict[str, str] = {
    "stock_actual": "Lo que hay hoy según el sistema (góndola + bodega).",
    "venta_diaria": (
        "Promedio que se vende por día. Perecederos: últimos 14 días; "
        "estables: 90 días. Cuenta también los días sin venta."
    ),
    "dias_inventario": "Cuántos días te dura lo que tienes = Stock ÷ Venta diaria.",
    "nivel_objetivo": (
        "Cuánto deberías tener para llegar al próximo pedido = "
        "Venta diaria × (7 días + colchón)."
    ),
    "sugerido": "Cuánto pedir hoy = Nivel objetivo − Stock. Nunca menos de 0.",
    "estado": (
        "🔴 Crítico (<3 días) pedir ya · 🟡 Reponer (3–14) completar · "
        "🟢 Cubierto no pedir · ⚫ Estancado (>14) no pedir."
    ),
}
