"""Barra de filtros. Devuelve un objeto `Filtros` listo para el servicio.

Patrón de estado: los valores por defecto se siembran en `st.session_state` y los widgets
usan SOLO `key=` (sin `value=`/`default=`). Así "Limpiar filtros" funciona de verdad
(reasigna las keys a su default antes de re-instanciar los widgets) y los defaults se
respetan en el primer render.
"""
from __future__ import annotations

from typing import Callable

import streamlit as st

from src.app.domain.contracts import Filtros

# Keys de session_state para cada widget de filtro.
_K_PROV = "f_proveedores"
_K_CAT = "f_categorias"
_K_PROD = "f_producto"
_K_ACCION = "f_solo_accion"
_K_PEREC = "f_solo_perecederos"
_K_REPONER = "f_solo_reponer"

# Valores por defecto de cada filtro (alineados con Filtros()).
_DEFAULTS: dict[str, object] = {
    _K_PROV: [],
    _K_CAT: [],
    _K_PROD: [],         # multiselect de producto: vacío = todos
    _K_ACCION: False,     # "Solo lo que toca pedir" arranca en ON
    _K_PEREC: False,
    _K_REPONER: False,
}


def _sembrar_defaults() -> None:
    for k, v in _DEFAULTS.items():
        if k not in st.session_state:
            st.session_state[k] = v


def _limpiar_filtros() -> None:
    """Reasigna cada filtro a su default. Corre en on_click (antes de re-instanciar widgets),
    por eso SÍ resetea los multiselect/selectbox/toggles (incluido el combobox de producto)."""
    for k, v in _DEFAULTS.items():
        st.session_state[k] = v.copy() if isinstance(v, list) else v


def render_filtros(
    proveedores: list[str],
    categorias: list[str],
    opciones_producto: Callable[[list[str], list[str], bool], list[str]],
) -> Filtros:
    """Pinta los controles de filtro y devuelve un `Filtros`.

    `opciones_producto(proveedores, categorias, solo_perecederos)` devuelve los nombres de
    producto disponibles para el combobox EN CASCADA (depende de proveedor + categoría).
    """
    _sembrar_defaults()
    st.markdown('<div class="lr-section">Filtros</div>', unsafe_allow_html=True)

    c_prov, c_cat, c_prod = st.columns([1, 1, 1.4])
    with c_prov:
        prov_sel = st.multiselect(
            "Proveedor", options=proveedores,
            placeholder="Todos los proveedores", key=_K_PROV,
        )
    with c_cat:
        cat_sel = st.multiselect(
            "Categoría", options=categorias,
            placeholder="Todas las categorías", key=_K_CAT,
        )

    # Combobox de PRODUCTO en cascada: sus opciones dependen de proveedor + categoría
    # (y de "solo perecederos", que leemos de session_state ya que el toggle está más abajo).
    perec_actual = bool(st.session_state.get(_K_PEREC, True))
    nombres = opciones_producto(list(prov_sel), list(cat_sel), perec_actual)
    # Sanea la selección previa al nuevo alcance: descarta productos que ya no están en
    # las opciones (evita el error de multiselect con valores inexistentes tras la cascada).
    prev = st.session_state.get(_K_PROD, [])
    st.session_state[_K_PROD] = [p for p in prev if p in nombres]
    with c_prod:
        prod_sel = st.multiselect(
            "Producto", options=nombres, placeholder="Todos los productos", key=_K_PROD,
            help="Selección múltiple, en cascada según el proveedor y la categoría elegidos.",
        )

    c_acc, c_per, c_rep, c_clr = st.columns([1, 1, 1, 0.9], vertical_alignment="bottom")
    with c_acc:
        solo_accion = st.toggle(
            "Solo lo que toca pedir",
            help="Oculta lo cubierto y lo estancado (sugerido 0).", key=_K_ACCION,
        )
    with c_per:
        solo_perecederos = st.toggle(
            "Solo perecederos",
            help="Limita al piloto de perecederos (carnes, fruver, lácteos…).", key=_K_PEREC,
        )
    with c_rep:
        solo_reponer = st.toggle(
            "Solo reponer",
            help="Muestra solo los productos en estado REPONER (top-ups menos urgentes).",
            key=_K_REPONER,
        )
    with c_clr:
        st.button(
            "🧹 Limpiar filtros",
            help="Restablece todos los filtros a sus valores por defecto.",
            on_click=_limpiar_filtros, width="stretch",
        )

    return Filtros(
        proveedores=list(prov_sel),
        categorias=list(cat_sel),
        productos=list(prod_sel),
        solo_perecederos=solo_perecederos,
        solo_accion=solo_accion,
        solo_reponer=solo_reponer,
    )
