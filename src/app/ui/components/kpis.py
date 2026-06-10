"""Tarjetas KPI estilizadas (HTML custom acorde al prototipo)."""
from __future__ import annotations

import html

import streamlit as st


def _cop(valor: float) -> str:
    """Formatea pesos colombianos con punto de miles: 454450 -> $454.450."""
    try:
        entero = int(round(float(valor)))
    except (TypeError, ValueError):
        entero = 0
    return "$" + f"{entero:,}".replace(",", ".")


def _card(valor: str, etiqueta: str, color: str, tip: str = "") -> str:
    h = f'<span class="h" title="{html.escape(tip)}">ⓘ</span>' if tip else ""
    return (
        f'<div class="lr-kpi {color}">'
        f'<div class="v">{html.escape(valor)}</div>'
        f'<div class="l">{html.escape(etiqueta)}{h}</div>'
        f"</div>"
    )


def render_kpis(kpis: dict) -> None:
    """Pinta las 4 tarjetas resumen.

    Espera un dict con: a_pedir, criticos, valor_pedido, capital_congelado.
    En `app.py`, `a_pedir` y `valor_pedido` se recalculan desde el DF EDITADO para
    que estas tarjetas reflejen en vivo las cantidades que ajusta la cajera.
    """
    a_pedir = kpis.get("a_pedir", 0)
    criticos = kpis.get("criticos", 0)
    valor_pedido = kpis.get("valor_pedido", 0.0)
    capital_congelado = kpis.get("capital_congelado", 0.0)

    cols = st.columns(4)
    tarjetas = [
        _card(str(a_pedir), "A pedir hoy", "red"),
        _card(str(criticos), "Crítico · riesgo agotado", "gold"),
        _card(
            _cop(valor_pedido),
            "Valor estimado del pedido",
            "green",
            "Suma del costo estimado de las cantidades sugeridas.",
        ),
        _card(
            _cop(capital_congelado),
            "Capital congelado (estancados)",
            "gray",
            "Dinero invertido en producto que no rota (estancado).",
        ),
    ]
    for col, html_card in zip(cols, tarjetas):
        with col:
            st.markdown(html_card, unsafe_allow_html=True)
