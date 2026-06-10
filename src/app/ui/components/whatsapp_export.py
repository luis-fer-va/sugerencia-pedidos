"""Exportación del pedido a texto de WhatsApp (con botón de copiar y link)."""
from __future__ import annotations

import datetime as _dt
import urllib.parse

import pandas as pd
import streamlit as st

from src.app.domain.contracts import ColsSalida


def _fmt_cantidad(cantidad: float, unidad: str) -> str:
    """kg con coma y 2 decimales; 'uni' (u otra) como entero."""
    u = str(unidad).strip().lower()
    if u == "uni":
        return f"{int(round(float(cantidad)))} {unidad}"
    # kg (default): coma decimal
    txt = f"{float(cantidad):.2f}".replace(".", ",")
    return f"{txt} {unidad}"


def _construir_texto(df: pd.DataFrame, proveedor: str, fecha: _dt.date) -> tuple[str, int]:
    """Arma el mensaje con SOLO las filas con sugerido > 0. Devuelve (texto, n_items)."""
    pedido = df[pd.to_numeric(df[ColsSalida.SUGERIDO], errors="coerce").fillna(0) > 0]
    pedido = pedido.sort_values(ColsSalida.NOMBRE)

    lineas = [
        f"• {row[ColsSalida.NOMBRE]} — *{_fmt_cantidad(row[ColsSalida.SUGERIDO], row[ColsSalida.UNIDAD])}*"
        for _, row in pedido.iterrows()
    ]
    cuerpo = "\n".join(lineas) if lineas else "(sin ítems por pedir)"
    fecha_txt = fecha.strftime("%d/%m/%Y")

    texto = (
        "🛒 *PEDIDO LA ROKA*\n"
        f"🏪 Proveedor: {proveedor}\n"
        f"📅 {fecha_txt}\n\n"
        f"{cuerpo}\n\n"
        f"Total ítems: {len(lineas)}\n"
        "Gracias 🙏"
    )
    return texto, len(lineas)


def render_whatsapp(df_editado: pd.DataFrame, proveedor: str, fecha: _dt.date | None = None) -> None:
    """Muestra la vista previa del pedido y un botón para abrir WhatsApp."""
    if fecha is None:
        fecha = _dt.date.today()
    prov = proveedor or "Todos"

    st.markdown('<div class="lr-section">Pedido para WhatsApp</div>', unsafe_allow_html=True)

    if df_editado is None or df_editado.empty:
        st.info("Aún no hay productos para armar el pedido.")
        return

    texto, n = _construir_texto(df_editado, prov, fecha)

    # st.code ya trae botón de copiar nativo.
    st.code(texto, language=None)

    if n > 0:
        url = "https://wa.me/?text=" + urllib.parse.quote(texto)
        st.link_button("📲 Enviar por WhatsApp", url, width="content")
    else:
        st.caption("No hay ítems con cantidad > 0. Ajusta el sugerido en la tabla.")
