"""La Roka · Toma de Pedidos — entrypoint Streamlit.

Cómo lanzar (desde la RAÍZ del repo `rokaEtl`):

    streamlit run src/app/app.py

Flujo: header → filtros → KPIs → tabla editable → exportar a WhatsApp.
La UI NO calcula nada: consume `PedidoService`. Si el backend aún no está
disponible, levanta con datos de muestra y muestra un aviso discreto.
"""
from __future__ import annotations

# --- Bootstrap de path: permite `streamlit run src/app/app.py` desde la raíz del repo.
# Streamlit pone `src/app` en sys.path[0], no la raíz; añadimos la raíz para que
# resuelvan los imports absolutos `from src.app...`.
import sys as _sys
from pathlib import Path as _Path

_ROOT = _Path(__file__).resolve().parents[2]  # .../rokaEtl
if str(_ROOT) not in _sys.path:
    _sys.path.insert(0, str(_ROOT))

import datetime as _dt
from dataclasses import astuple

import pandas as pd
import streamlit as st

from src.app.domain.contracts import ColsSalida, Filtros
from src.app.ui import _sample
from src.app.ui.components import (
    render_filtros,
    render_header,
    render_kpis,
    render_tabla,
    render_whatsapp,
)
from src.app.ui.theme import inyectar_estilos

# ---------------------------------------------------------------------------------
# Config de página + tema
# ---------------------------------------------------------------------------------
st.set_page_config(
    page_title="La Roka · Pedidos",
    page_icon="🥩",
    layout="wide",
)
inyectar_estilos()


# ---------------------------------------------------------------------------------
# Servicio (con fallback a muestra)
# ---------------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def _construir_servicio():
    """Instancia PedidoService. Devuelve (servicio|None, modo_muestra: bool)."""
    try:
        from src.app.services.pedido_service import PedidoService  # import diferido

        return PedidoService(), False
    except Exception:  # backend aún no listo / error de construcción
        return None, True


def _filtros_key(f: Filtros) -> tuple:
    """Clave hashable para cachear por contenido de Filtros.

    `Filtros` ahora tiene campos lista (proveedores/categorias) que no son hashables;
    los convertimos a tuplas para poder usarlos como clave de `@st.cache_data`.
    Al reconstruir `Filtros(*fkey)` las tuplas funcionan (el servicio hace `list(...)`).
    """
    return tuple(tuple(v) if isinstance(v, list) else v for v in astuple(f))


@st.cache_data(show_spinner=False)
def _cargar_sugerencias(_servicio_id: int, fkey: tuple) -> pd.DataFrame:
    servicio, _ = _construir_servicio()
    filtros = Filtros(*fkey)
    return servicio.sugerencias(filtros)


@st.cache_data(show_spinner=False)
def _cargar_kpis(_servicio_id: int, fkey: tuple) -> dict:
    servicio, _ = _construir_servicio()
    filtros = Filtros(*fkey)
    return servicio.kpis(filtros)


# ---------------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------------
def main() -> None:
    servicio, modo_muestra = _construir_servicio()

    if modo_muestra:
        st.warning(
            "Mostrando datos de muestra: el motor de pedidos aún no está disponible. "
            "La app funciona, pero los números son de ejemplo.",
            icon="🧪",
        )
        proveedores = _sample.proveedores_muestra()
        categorias = _sample.categorias_muestra()
        fecha_corte = _sample.fecha_corte_muestra()
    else:
        try:
            proveedores = servicio.proveedores()
            categorias = servicio.categorias()
            fecha_corte = servicio.fecha_corte()
        except Exception:
            modo_muestra = True
            st.warning(
                "No se pudieron leer los catálogos del servicio; uso datos de muestra.",
                icon="🧪",
            )
            proveedores = _sample.proveedores_muestra()
            categorias = _sample.categorias_muestra()
            fecha_corte = _sample.fecha_corte_muestra()

    # 1) Header — muestra la fecha y HORA de la última transacción (max fecha_creacion).
    ultima_tx = fecha_corte
    if not modo_muestra:
        try:
            ultima_tx = servicio.ultima_transaccion()
        except Exception:
            ultima_tx = fecha_corte
    render_header(ultima_tx)

    # 2) Filtros — el combobox de Producto se alimenta en cascada (proveedor + categoría).
    if modo_muestra:
        def opciones_producto(provs, cats, perec):
            d = _sample.df_muestra()
            if provs:
                d = d[d[ColsSalida.PROVEEDOR].isin(provs)]
            if cats:
                d = d[d[ColsSalida.CATEGORIA].isin(cats)]
            if perec:
                d = d[d[ColsSalida.ES_PERECEDERO]]
            return sorted(d[ColsSalida.NOMBRE].dropna().unique().tolist())
    else:
        opciones_producto = servicio.nombres_producto

    filtros = render_filtros(proveedores, categorias, opciones_producto)

    # 3) Datos (servicio real o muestra)
    if modo_muestra:
        df = _sample.df_muestra()
        kpis = _sample.kpis_muestra()
        # Filtrado mínimo en muestra para que los toggles "se sientan" vivos.
        df = _filtrar_muestra(df, filtros)
    else:
        sid = id(servicio)
        fkey = _filtros_key(filtros)
        df = _cargar_sugerencias(sid, fkey)
        kpis = _cargar_kpis(sid, fkey)

    # 4) KPIs — placeholder ARRIBA de la tabla. Se rellena DESPUÉS de editar la tabla
    #    para que "Valor estimado del pedido" y "A pedir hoy" reflejen las ediciones.
    kpi_slot = st.container()

    # 5) Tabla editable -> devuelve cantidades ajustadas
    st.markdown('<div class="lr-section">Sugerencia de compra</div>', unsafe_allow_html=True)
    df_editado = render_tabla(df)

    # 4.bis) KPIs reactivos: recalcula desde el DF EDITADO lo que cambia al editar
    #        (valor del pedido = Σ sugerido·costo_unitario; a_pedir = nº filas con sugerido>0).
    #        `criticos` y `capital_congelado` no cambian al editar -> vienen del servicio.
    kpis_vivo = dict(kpis)
    if df_editado is not None and not df_editado.empty:
        sug = pd.to_numeric(df_editado[ColsSalida.SUGERIDO], errors="coerce").fillna(0.0)
        costo = pd.to_numeric(
            df_editado.get(ColsSalida.COSTO_UNITARIO, 0.0), errors="coerce"
        ).fillna(0.0)
        kpis_vivo["valor_pedido"] = float((sug * costo).sum())
        kpis_vivo["a_pedir"] = int((sug > 0).sum())
    with kpi_slot:
        render_kpis(kpis_vivo)

    # 6) Export WhatsApp — etiqueta de proveedor según selección múltiple.
    if not filtros.proveedores:
        prov_label = "Todos los proveedores"
    else:
        prov_label = ", ".join(filtros.proveedores)
    render_whatsapp(df_editado, prov_label, fecha=fecha_corte)


def _filtrar_muestra(df: pd.DataFrame, f: Filtros) -> pd.DataFrame:
    """Filtrado ligero SOLO para el modo muestra (el servicio real lo hace en backend)."""
    from src.app.domain.reglas import Estado

    out = df
    if f.proveedores:
        out = out[out[ColsSalida.PROVEEDOR].isin(f.proveedores)]
    if f.categorias:
        out = out[out[ColsSalida.CATEGORIA].isin(f.categorias)]
    if f.solo_perecederos:
        out = out[out[ColsSalida.ES_PERECEDERO]]
    if f.solo_reponer:
        out = out[out[ColsSalida.ESTADO] == Estado.REPONER.value]
    elif f.solo_accion:
        accion = {Estado.CRITICO.value, Estado.REPONER.value}
        out = out[out[ColsSalida.ESTADO].isin(accion)]
    if f.productos:
        out = out[out[ColsSalida.NOMBRE].isin(f.productos)]
    return out.reset_index(drop=True)


# Streamlit ejecuta el script como módulo top-level (__name__ == "__main__").
main()
