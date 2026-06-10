"""Header de marca: badge con logo, wordmark, kicker, sello de actualización y refrescar."""
from __future__ import annotations

import base64
import datetime as _dt
from pathlib import Path

import streamlit as st

# assets/ vive en src/app/assets/logo_laroka.png (junto a ui/)
_LOGO_PATH = Path(__file__).resolve().parents[2] / "assets" / "logo_laroka.png"

_MESES = [
    "", "enero", "febrero", "marzo", "abril", "mayo", "junio",
    "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre",
]


def _logo_html() -> str:
    """Badge con el logo si existe; si no, monograma 'LR' de respaldo."""
    if _LOGO_PATH.exists():
        try:
            b64 = base64.b64encode(_LOGO_PATH.read_bytes()).decode("ascii")
            return (
                '<div class="lr-badge">'
                f'<img src="data:image/png;base64,{b64}" alt="La Roka"></div>'
            )
        except Exception:
            pass
    return '<div class="lr-badge"><div class="fallback">LR</div></div>'


def _fmt_fecha(fecha: _dt.datetime) -> str:
    # %I es hora en formato 12 horas, %M son los minutos, y %p es AM/PM
    # Usamos .lower() para que quede "am" o "pm" en minúsculas
    hora_12 = fecha.strftime("%I:%M %p").lower()

    # Si la hora tiene un cero a la izquierda (ej. "06:00 am"), se lo quitamos opcionalmente
    if hora_12.startswith("0"):
        hora_12 = hora_12[1:]

    return f"{fecha.day} {_MESES[fecha.month]} {fecha.year} {hora_12}"


def render_header(fecha_corte: _dt.datetime) -> None:
    """Pinta la barra superior de marca.

    Incluye un botón "Refrescar" que limpia la caché de datos y re-ejecuta la app.
    """
    col_brand, col_stamp, col_btn = st.columns([6, 3, 1], vertical_alignment="center")

    with col_brand:
        st.markdown(
            f"""
            <div class="lr-brand">
              {_logo_html()}
              <div class="lr-wm">
                <div class="kicker">Expendio de Carnes</div>
                <h1>La <em>Roka</em> · Toma de Pedidos</h1>
                <div class="sub">Sugerencia de compra dirigida por datos</div>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_stamp:
        st.markdown(
            f"""
            <div class="lr-stamp">
              <span class="live">Datos del corte</span><br>
              última transacción
              <b>{_fmt_fecha(fecha_corte)}</b>
              <span title="Fecha y hora de la última transacción (venta) registrada en el sistema — es el máximo de la fecha de venta."
                    style="cursor:help;display:inline-block;width:15px;height:15px;line-height:14px;
                           text-align:center;border:1px solid #e8a33d;border-radius:50%;
                           font-size:10px;font-weight:700;color:#e8a33d;margin-left:6px">i</span>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with col_btn:
        if st.button("⟳", help="Refrescar datos", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    st.markdown('<div class="lr-divider"></div>', unsafe_allow_html=True)
