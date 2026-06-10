"""Orquestación: carga datos, corre el motor una vez y sirve a la UI.

`PedidoService` es la fachada que consume la UI de Streamlit. Internamente:
  1. Obtiene los DataFrames de la `FuenteDatos` (inyectada o por factory).
  2. Corre el motor PURO una sola vez y cachea el resultado (ya filtrado a activos).
  3. Aplica filtros de UI sobre la caché y devuelve pandas (la UI lo consume directo).
"""
from __future__ import annotations
from datetime import date

import polars as pl
import pandas as pd

from src.app.data.repository import FuenteDatos
from src.app.data.factory import crear_fuente
from src.app.services import motor_reabastecimiento as motor
from src.app.domain.contracts import (
    ColsProductos,
    ColsSalida,
    COLS_SALIDA,
    Filtros,
)
from src.app.domain import reglas


class PedidoService:
    def __init__(self, fuente: FuenteDatos | None = None) -> None:
        self._fuente: FuenteDatos = fuente if fuente is not None else crear_fuente()
        self._fecha_corte: date = self._fuente.fecha_corte()

        productos = self._fuente.productos()
        stock = self._fuente.stock()
        ventas = self._fuente.ventas()
        proveedor = self._fuente.proveedor_por_producto()

        # Motor una sola vez sobre el catálogo completo...
        resultado = motor.calcular(
            productos, stock, ventas, proveedor, self._fecha_corte
        )
        # ...y se conserva solo lo activo (el catálogo trae inactivos/promos).
        activos = productos.filter(pl.col(ColsProductos.ACTIVO) == True).select(  # noqa: E712
            ColsProductos.ID
        )
        self._df: pl.DataFrame = resultado.join(activos, on=ColsSalida.ID, how="inner")

    # -- filtrado interno ---------------------------------------------------------
    def _aplicar_base(self, f: Filtros) -> pl.DataFrame:
        """Filtros de alcance (proveedor / categoria / perecederos / búsqueda).

        NO aplica solo_accion: eso es responsabilidad de cada consumidor (sugerencias sí,
        kpis no — los kpis necesitan ver estancados).
        """
        df = self._df
        if f.solo_perecederos:
            df = df.filter(pl.col(ColsSalida.ES_PERECEDERO) == True)  # noqa: E712
        if f.proveedores:
            df = df.filter(pl.col(ColsSalida.PROVEEDOR).is_in(list(f.proveedores)))
        if f.categorias:
            df = df.filter(pl.col(ColsSalida.CATEGORIA).is_in(list(f.categorias)))
        if f.productos:
            df = df.filter(pl.col(ColsSalida.NOMBRE).is_in(list(f.productos)))
        if f.busqueda:
            df = df.filter(
                pl.col(ColsSalida.NOMBRE).str.to_lowercase().str.contains(
                    f.busqueda.strip().lower(), literal=True
                )
            )
        return df

    # -- API pública --------------------------------------------------------------
    def sugerencias(self, filtros: Filtros) -> pd.DataFrame:
        """Tabla para la UI: ColsSalida, ordenada por urgencia (DI asc)."""
        df = self._aplicar_base(filtros)
        if filtros.solo_accion:
            df = df.filter(pl.col(ColsSalida.SUGERIDO) > 0)
        if filtros.solo_reponer:
            df = df.filter(pl.col(ColsSalida.ESTADO) == reglas.Estado.REPONER.value)
        # DI ascendente: lo más urgente arriba; nulls (sin venta) al final.
        df = df.sort(ColsSalida.DIAS_INVENTARIO, descending=False, nulls_last=True)
        return df.select(COLS_SALIDA).to_pandas()

    def kpis(self, filtros: Filtros) -> dict:
        """KPIs del alcance filtrado, IGNORANDO solo_accion (para incluir estancados)."""
        df = self._aplicar_base(filtros)
        a_pedir = int(df.filter(pl.col(ColsSalida.SUGERIDO) > 0).height)
        criticos = int(
            df.filter(pl.col(ColsSalida.ESTADO) == reglas.Estado.CRITICO.value).height
        )
        # valor_pedido = sum(sugerido * costo_estandar). El costo unitario no viaja en
        # ColsSalida, así que se recupera del maestro de productos (ver _valor_pedido).
        valor_pedido = self._valor_pedido(df)
        capital_congelado = float(
            df.filter(pl.col(ColsSalida.ESTADO) == reglas.Estado.ESTANCADO.value)
            .select(pl.col(ColsSalida.CAPITAL_RIESGO).sum())
            .item()
            or 0.0
        )
        return {
            "a_pedir": a_pedir,
            "criticos": criticos,
            "valor_pedido": valor_pedido,
            "capital_congelado": capital_congelado,
        }

    def _valor_pedido(self, df: pl.DataFrame) -> float:
        """sum(sugerido * costo_unitario) sobre filas con sugerido > 0.

        El costo unitario ahora viaja en ColsSalida, así no hace falta re-join.
        """
        valor = (
            df.filter(pl.col(ColsSalida.SUGERIDO) > 0)
            .select((pl.col(ColsSalida.SUGERIDO) * pl.col(ColsSalida.COSTO_UNITARIO)).sum())
            .item()
        )
        return float(valor or 0.0)

    def proveedores(self) -> list[str]:
        """Proveedores únicos (todos los productos activos), ordenados. Lista completa para el multiselect."""
        return sorted(self._df[ColsSalida.PROVEEDOR].drop_nulls().unique().to_list())

    def categorias(self) -> list[str]:
        """Categorías únicas (todos los productos activos), ordenadas. Lista completa para el multiselect."""
        return sorted(self._df[ColsSalida.CATEGORIA].drop_nulls().unique().to_list())

    def nombres_producto(
        self,
        proveedores: list[str] | None = None,
        categorias: list[str] | None = None,
        solo_perecederos: bool = True,
    ) -> list[str]:
        """Nombres de producto disponibles para el combobox en cascada.

        Respeta proveedor/categoría/perecederos (NO solo_accion: el desplegable debe
        ofrecer todos los productos de ese alcance, no solo los que toca pedir).
        """
        df = self._df
        if solo_perecederos:
            df = df.filter(pl.col(ColsSalida.ES_PERECEDERO) == True)  # noqa: E712
        if proveedores:
            df = df.filter(pl.col(ColsSalida.PROVEEDOR).is_in(list(proveedores)))
        if categorias:
            df = df.filter(pl.col(ColsSalida.CATEGORIA).is_in(list(categorias)))
        return sorted(df[ColsSalida.NOMBRE].drop_nulls().unique().to_list())

    def fecha_corte(self) -> date:
        return self._fecha_corte

    def ultima_transaccion(self):
        """Fecha y hora de la última venta registrada (para el encabezado)."""
        return self._fuente.ultima_transaccion()
