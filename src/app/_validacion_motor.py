"""Autovalidación del motor de reabastecimiento.

Ejecutar desde la raíz del repo como módulo (para que los imports `from src.app...`
resuelvan):

    e:/7.Informe LaRoka/rokaEtl/.venv/Scripts/python.exe -m src.app._validacion_motor

Imprime la fila de productos de referencia con VD, dias_inventario, nivel_objetivo,
sugerido, estado y alerta_merma para comparar contra los valores esperados.
"""
from __future__ import annotations

from src.app.services.pedido_service import PedidoService
from src.app.domain.contracts import ColsSalida, Filtros

OBJETIVO = [
    "costilla ahumada",
    "platano maduro",
    "plátano maduro",
    "cadera especial",
    "yuca",
]


def main() -> None:
    svc = PedidoService()
    print("fecha_corte:", svc.fecha_corte())

    # Sin filtros restrictivos: queremos ver también CUBIERTO / ESTANCADO.
    f = Filtros(solo_perecederos=False, solo_accion=False)
    df = svc.sugerencias(f)

    nombres = df[ColsSalida.NOMBRE].str.lower()
    mask = nombres.apply(lambda n: any(o in n for o in OBJETIVO))
    sel = df[mask]

    cols = [
        ColsSalida.NOMBRE,
        ColsSalida.UNIDAD,
        ColsSalida.STOCK,
        ColsSalida.VENTA_DIARIA,
        ColsSalida.DIAS_INVENTARIO,
        ColsSalida.NIVEL_OBJETIVO,
        ColsSalida.SUGERIDO,
        ColsSalida.ESTADO,
        ColsSalida.ALERTA_MERMA,
    ]
    import pandas as pd

    pd.set_option("display.width", 200)
    pd.set_option("display.max_columns", None)
    print(sel[cols].to_string(index=False))


if __name__ == "__main__":
    main()
