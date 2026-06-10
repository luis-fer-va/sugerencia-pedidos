"""Tabla editable de pedidos (st.data_editor).

Solo la columna "Sugerido" es editable; el resto va en modo lectura. Devuelve el
DataFrame con las cantidades que la cajera dejó (mismo esquema COLS_SALIDA, con la
columna `sugerido` actualizada).
"""
from __future__ import annotations

import pandas as pd
import streamlit as st

from src.app.domain.contracts import ColsSalida
from src.app.domain.reglas import Estado
from src.app.ui.tooltips import TOOLTIPS

# Punto de color por estado: viaja antepuesto al nombre del producto (semáforo del prototipo).
_ESTADO_PUNTO: dict[str, str] = {
    Estado.CRITICO.value: "🔴",
    Estado.REPONER.value: "🟡",
    Estado.CUBIERTO.value: "🟢",
    Estado.ESTANCADO.value: "⚫",
}

# Columna interna de presentación (nombre con punto de color + alerta de merma).
_C_NOMBRE_VIS = "_nombre_vis"


def _punto_estado(valor: object) -> str:
    return _ESTADO_PUNTO.get(str(valor), "")


def render_tabla(df: pd.DataFrame) -> pd.DataFrame:
    """Renderiza la tabla y devuelve el df con `sugerido` editado.

    El df de entrada NO se calcula aquí: ya viene listo del servicio.
    """
    if df is None or df.empty:
        st.info("No hay productos que mostrar con los filtros actuales.")
        return df if df is not None else pd.DataFrame()

    base = df.reset_index(drop=True).copy()

    # Columna de presentación: punto de color del estado + ⚠️ de merma + nombre.
    vis = base.copy()
    merma = base.get(ColsSalida.ALERTA_MERMA, pd.Series(False, index=base.index)).fillna(False).astype(bool)
    nombres_vis = []
    for nombre, estado, m in zip(base[ColsSalida.NOMBRE], base[ColsSalida.ESTADO], merma):
        punto = _punto_estado(estado)
        prefijo = punto + (" ⚠️" if bool(m) else "")
        nombres_vis.append((prefijo + " " + str(nombre)).strip())
    vis[_C_NOMBRE_VIS] = nombres_vis

    # Orden y subconjunto de columnas a mostrar.
    # NOTA: Categoría y Proveedor se OCULTAN aquí a propósito (ya están en los filtros,
    #       generaban ruido). El Estado tampoco se muestra como columna: ahora viaja como
    #       punto de color antepuesto al nombre del producto.
    cols_vis = [
        _C_NOMBRE_VIS,
        ColsSalida.STOCK,
        ColsSalida.VENTA_DIARIA,
        ColsSalida.DIAS_INVENTARIO,
        ColsSalida.NIVEL_OBJETIVO,
        ColsSalida.SUGERIDO,
    ]
    vista = vis[cols_vis]

    column_config = {
        # pinned=True congela "Producto" a la izquierda al hacer scroll horizontal.
        _C_NOMBRE_VIS: st.column_config.TextColumn("Producto", width="large", pinned=True),
        ColsSalida.STOCK: st.column_config.NumberColumn(
            "Stock actual", help=TOOLTIPS["stock_actual"], format="%.2f",
        ),
        ColsSalida.VENTA_DIARIA: st.column_config.NumberColumn(
            "Venta diaria", help=TOOLTIPS["venta_diaria"], format="%.2f",
        ),
        ColsSalida.DIAS_INVENTARIO: st.column_config.NumberColumn(
            "Días de inventario", help=TOOLTIPS["dias_inventario"], format="%.1f",
        ),
        ColsSalida.NIVEL_OBJETIVO: st.column_config.NumberColumn(
            "Nivel objetivo", help=TOOLTIPS["nivel_objetivo"], format="%.2f",
        ),
        ColsSalida.SUGERIDO: st.column_config.NumberColumn(
            "Sugerido de compra ✏️",
            help=TOOLTIPS["sugerido"],
            min_value=0.0,
            step=0.5,
            format="%.2f",
        ),
    }

    # Todo deshabilitado salvo "sugerido".
    disabled = [c for c in cols_vis if c != ColsSalida.SUGERIDO]

    editado = st.data_editor(
        vista,
        column_config=column_config,
        disabled=disabled,
        hide_index=True,
        width="stretch",
        key="tabla_pedidos",
    )

    # Leyenda del semáforo (el estado ya no es columna: se lee por el punto de color).
    # La nota de ⚠️ merma solo se muestra si hay productos en riesgo en la vista actual
    # (la merma aplica a perecederos ESTANCADOS, normalmente ocultos en "solo lo que toca pedir").
    leyenda = "🔴 Crítico (<3 días) · 🟡 Reponer (3–14 días) · 🟢 Cubierto · ⚫ Estancado"
    if bool(merma.any()):
        leyenda += "  ·  ⚠️ merma = perecedero estancado en riesgo de dañarse"
    st.caption(leyenda)

    # Reconstruye el df original con el sugerido editado (clamp a >= 0).
    salida = base.copy()
    sug_edit = pd.to_numeric(editado[ColsSalida.SUGERIDO], errors="coerce").fillna(0.0)
    salida[ColsSalida.SUGERIDO] = sug_edit.clip(lower=0.0).values
    return salida
