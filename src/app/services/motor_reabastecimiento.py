"""Motor de reabastecimiento (modelo *order-up-to*). PURO: sin IO ni Streamlit.

Recibe DataFrames de Polars (con los nombres de `domain.contracts`) y devuelve un único
DataFrame con TODAS las columnas de `ColsSalida`, una fila por producto. No conoce la
fuente de datos ni la UI: se le inyectan los datos y devuelve el cálculo.

Fórmulas (ver domain.reglas para los parámetros):
  ventana      = 14 si perecedero, 90 si no                  (reglas.ventana_dias)
  VD           = ventas_en_ventana / ventana                 (divide por TODOS los días, ceros incluidos)
  dias_inv     = stock / VD                                   (None si VD <= 0)
  colchon      = +2 perecedero / +3 estable                  (reglas.colchon_dias)
  nivel_obj    = VD * (CICLO_DIAS + colchon)
  sugerido     = max(0, nivel_obj - stock)                   (entero si 'uni', 2 dec si 'kg')
  estado       = reglas.clasificar_estado(dias_inv, sugerido)
  alerta_merma = estado == ESTANCADO  AND  es_perecedero
  capital      = stock * costo_estandar
"""
from __future__ import annotations
from datetime import date, timedelta

import polars as pl

from src.app.domain import reglas
from src.app.domain.contracts import (
    ColsProductos,
    ColsStock,
    ColsVentas,
    ColsProveedor,
    ColsSalida,
    COLS_SALIDA,
)


def _ventas_en_ventanas(ventas: pl.DataFrame, fecha_corte: date) -> pl.DataFrame:
    """Suma de cantidad vendida por producto en las dos ventanas (14d y 90d) hasta corte.

    Devuelve id_producto + suma_14 + suma_90 (0.0 si no hubo venta en la ventana).
    """
    desde_14 = fecha_corte - timedelta(days=reglas.VENTANA_PERECEDERO)
    desde_90 = fecha_corte - timedelta(days=reglas.VENTANA_ESTABLE)
    # Una sola pasada: condicionamos la cantidad según caiga en cada ventana.
    # Ventana = [fecha_corte - N, fecha_corte] (ambos extremos incluidos); la VD se obtiene
    # luego dividiendo por N días (ver calcular()), no por el número de días con venta.
    return (
        ventas.filter(
            (pl.col(ColsVentas.FECHA) >= desde_90)
            & (pl.col(ColsVentas.FECHA) <= fecha_corte)
        )
        .group_by(ColsVentas.ID)
        .agg(
            pl.col(ColsVentas.CANTIDAD)
            .filter(pl.col(ColsVentas.FECHA) >= desde_14)
            .sum()
            .alias("_suma_14"),
            pl.col(ColsVentas.CANTIDAD).sum().alias("_suma_90"),
        )
    )


def calcular(
    productos: pl.DataFrame,
    stock: pl.DataFrame,
    ventas: pl.DataFrame,
    proveedor: pl.DataFrame,
    fecha_corte: date,
) -> pl.DataFrame:
    """Calcula la sugerencia de pedido para cada producto. Devuelve ColsSalida."""

    sumas = _ventas_en_ventanas(ventas, fecha_corte)

    df = (
        productos.join(stock, on=ColsProductos.ID, how="left")
        .join(proveedor, on=ColsProductos.ID, how="left")
        .join(sumas, on=ColsProductos.ID, how="left")
    )

    # Nulos -> 0 para no romper las divisiones.
    df = df.with_columns(
        pl.col(ColsStock.CANTIDAD).fill_null(0.0).alias("_stock"),
        pl.col("_suma_14").fill_null(0.0),
        pl.col("_suma_90").fill_null(0.0),
        pl.col(ColsProveedor.PROVEEDOR).fill_null("Sin proveedor"),
        pl.col(ColsStock.DIAS_SIN_VENDER),
        pl.col(ColsProductos.COSTO).fill_null(0.0),
    )

    # Stock efectivo: el POS puede traer stock NEGATIVO (sobreventa / error de inventario).
    # Un stock negativo no debe inflar el sugerido ni el capital, así que se piso en 0.
    df = df.with_columns(
        pl.max_horizontal(pl.lit(0.0), pl.col("_stock")).alias("_stock_efectivo")
    )

    # VD: suma de la ventana correspondiente / días de la ventana (14 o 90, ceros incluidos).
    df = df.with_columns(
        pl.when(pl.col(ColsProductos.ES_PERECEDERO))
        .then(pl.col("_suma_14") / reglas.VENTANA_PERECEDERO)
        .otherwise(pl.col("_suma_90") / reglas.VENTANA_ESTABLE)
        .alias(ColsSalida.VENTA_DIARIA)
    )

    # dias_inventario = stock_efectivo / VD ; None si VD <= 0.
    # Usa stock efectivo (>=0): un stock negativo del POS significa 0 días reales de cobertura
    # (CRÍTICO), no días negativos sin sentido.
    df = df.with_columns(
        pl.when(pl.col(ColsSalida.VENTA_DIARIA) > 0)
        .then(pl.col("_stock_efectivo") / pl.col(ColsSalida.VENTA_DIARIA))
        .otherwise(None)
        .alias(ColsSalida.DIAS_INVENTARIO)
    )

    # colchon -> nivel_objetivo = VD * (CICLO_DIAS + colchon).
    df = df.with_columns(
        pl.when(pl.col(ColsProductos.ES_PERECEDERO))
        .then(reglas.COLCHON_PERECEDERO)
        .otherwise(reglas.COLCHON_ESTABLE)
        .alias("_colchon")
    ).with_columns(
        (pl.col(ColsSalida.VENTA_DIARIA) * (reglas.CICLO_DIAS + pl.col("_colchon")))
        .alias(ColsSalida.NIVEL_OBJETIVO)
    )

    # sugerido = max(0, nivel_objetivo - stock), redondeado según unidad (uni -> entero, kg -> 2 dec).
    df = df.with_columns(
        pl.max_horizontal(
            pl.lit(0.0), pl.col(ColsSalida.NIVEL_OBJETIVO) - pl.col("_stock_efectivo")
        ).alias("_sugerido_bruto")
    ).with_columns(
        pl.when(pl.col(ColsProductos.UNIDAD) == "uni")
        .then(pl.col("_sugerido_bruto").round(0))
        .otherwise(pl.col("_sugerido_bruto").round(2))
        .alias(ColsSalida.SUGERIDO)
    )

    # estado: función pura del semáforo (recibe DI y sugerido).
    df = df.with_columns(
        pl.struct([ColsSalida.DIAS_INVENTARIO, ColsSalida.SUGERIDO])
        .map_elements(
            lambda s: reglas.clasificar_estado(
                s[ColsSalida.DIAS_INVENTARIO], s[ColsSalida.SUGERIDO]
            ).value,
            return_dtype=pl.Utf8,
        )
        .alias(ColsSalida.ESTADO)
    )

    # Invariante de negocio: SOLO los estados de acción (CRÍTICO y REPONER) generan pedido.
    # CUBIERTO ya es 0 por definición; ESTANCADO se fuerza a 0. Esto además neutraliza los
    # productos sin rotación (VD<=0 -> dias_inv None -> ESTANCADO) y el stock negativo del POS,
    # evitando sugeridos fantasma.
    df = df.with_columns(
        pl.when(
            pl.col(ColsSalida.ESTADO).is_in(
                [reglas.Estado.CRITICO.value, reglas.Estado.REPONER.value]
            )
        )
        .then(pl.col(ColsSalida.SUGERIDO))
        .otherwise(0.0)
        .alias(ColsSalida.SUGERIDO)
    )

    # alerta_merma = ESTANCADO y perecedero ; capital = stock_efectivo * costo (sin negativos).
    df = df.with_columns(
        (
            (pl.col(ColsSalida.ESTADO) == reglas.Estado.ESTANCADO.value)
            & pl.col(ColsProductos.ES_PERECEDERO)
        ).alias(ColsSalida.ALERTA_MERMA),
        (pl.col("_stock_efectivo") * pl.col(ColsProductos.COSTO)).alias(ColsSalida.CAPITAL_RIESGO),
        pl.col("_stock").alias(ColsSalida.STOCK),
        pl.col(ColsProductos.COSTO).alias(ColsSalida.COSTO_UNITARIO),
    )

    return df.select(COLS_SALIDA)
