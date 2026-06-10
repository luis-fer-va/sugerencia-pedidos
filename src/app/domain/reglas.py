"""Reglas de negocio del motor de reabastecimiento.

Constantes y funciones PURAS (sin IO, sin dependencias de framework). Este módulo es la
única fuente de verdad de los parámetros del modelo *order-up-to*; cambiar un umbral aquí
se propaga a todo el sistema sin tocar la lógica de cálculo ni la UI.
"""
from __future__ import annotations
from enum import Enum

# --- Ciclo y ventanas de cálculo -------------------------------------------------
CICLO_DIAS: int = 7            # el proveedor toma pedido cada 7 días
VENTANA_PERECEDERO: int = 14   # historia para promediar venta de perecederos
VENTANA_ESTABLE: int = 90      # historia para promediar venta de no perecederos

# --- Colchón de seguridad (días extra sobre el ciclo) ----------------------------
COLCHON_PERECEDERO: int = 2    # perecedero: colchón corto (se daña rápido)
COLCHON_ESTABLE: int = 3       # no perecedero: colchón mayor (no se daña)

# --- Umbrales del semáforo (en días de inventario) -------------------------------
UMBRAL_CRITICO: int = 3        # DI < 3  -> CRÍTICO
UMBRAL_ESTANCADO: int = 14     # DI > 14 -> ESTANCADO

# --- Clasificación de perecederos ------------------------------------------------
# Se compara en minúsculas contra dim_productos.categoria. Reutiliza el criterio ya
# usado por el ETL (productos.py::_add_frecuencia_inventario) y lo amplía.
CATEGORIAS_PERECEDERAS: frozenset[str] = frozenset({
    "res", "cerdo", "pollo", "quesos", "fruver", "menudo res", "ahumados",
    "lacteos", "lácteos", "panaderia", "panadería",
})


class Estado(str, Enum):
    """Estado logístico de un producto (semáforo de decisión)."""
    CRITICO = "CRITICO"      # 🔴 riesgo de agotado, pedir ya
    REPONER = "REPONER"      # 🟡 dentro de rango pero falta para el objetivo
    CUBIERTO = "CUBIERTO"    # 🟢 cubierto, no pedir
    ESTANCADO = "ESTANCADO"  # ⚫ sobre-stock, no pedir (+ posible merma)


def es_categoria_perecedera(categoria: str | None) -> bool:
    """True si la categoría corresponde a un producto perecedero."""
    if not categoria:
        return False
    return categoria.strip().lower() in CATEGORIAS_PERECEDERAS


def ventana_dias(es_perecedero: bool) -> int:
    """Días de historia a promediar según perecibilidad (14 vs 90)."""
    return VENTANA_PERECEDERO if es_perecedero else VENTANA_ESTABLE


def colchon_dias(es_perecedero: bool) -> int:
    """Días de colchón de seguridad según perecibilidad (+2 vs +3)."""
    return COLCHON_PERECEDERO if es_perecedero else COLCHON_ESTABLE


def clasificar_estado(dias_inventario: float | None, sugerido: float) -> Estado:
    """Aplica el semáforo de decisión a partir de los días de inventario.

    - DI < UMBRAL_CRITICO            -> CRITICO
    - DI > UMBRAL_ESTANCADO          -> ESTANCADO
    - en rango y sugerido > 0        -> REPONER
    - en rango y sugerido == 0       -> CUBIERTO
    """
    if dias_inventario is None:
        # Sin venta reciente / sin referencia: se trata como estancado (no pedir auto).
        return Estado.ESTANCADO
    if dias_inventario < UMBRAL_CRITICO:
        return Estado.CRITICO
    if dias_inventario > UMBRAL_ESTANCADO:
        return Estado.ESTANCADO
    return Estado.REPONER if sugerido > 0 else Estado.CUBIERTO
