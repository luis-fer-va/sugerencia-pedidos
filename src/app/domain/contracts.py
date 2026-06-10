"""Contratos entre capas: nombres de columnas, esquema de salida y filtros.

Única fuente de verdad del esquema. La capa `data/` debe ENTREGAR los esquemas de entrada
y `services/` produce el ESQUEMA DE SALIDA que consume la UI. Si la fuente cambia, solo el
Repository se adapta a estos nombres; el resto del sistema no se entera.
"""
from __future__ import annotations
from dataclasses import dataclass, field


# ---------------------------------------------------------------------------------
# Esquema de ENTRADA — lo que toda implementación de FuenteDatos debe devolver.
# ---------------------------------------------------------------------------------
class ColsProductos:
    ID = "id_producto"
    NOMBRE = "nombre_producto"
    CATEGORIA = "categoria"
    CATEGORIA_N2 = "categoria_nivel_2"
    UNIDAD = "unidad_medida"            # 'kg' | 'uni'
    ES_PERECEDERO = "es_perecedero"     # bool
    COSTO = "costo_estandar"
    ULT_COMPRA = "ultimo_precio_compra"
    ACTIVO = "esta_activo"              # bool


class ColsStock:
    ID = "id_producto"
    CANTIDAD = "cantidad_actual"
    ULT_VENTA = "fecha_u_venta"
    DIAS_SIN_VENDER = "dias_sin_vender"


class ColsVentas:
    ID = "id_producto"
    FECHA = "fecha"
    CANTIDAD = "cantidad"


class ColsProveedor:
    ID = "id_producto"
    PROVEEDOR = "proveedor"


# ---------------------------------------------------------------------------------
# Esquema de SALIDA — lo que PedidoService entrega a la UI (pandas DataFrame).
# Una fila por producto en alcance. La UI NUNCA calcula; solo formatea/pinta.
# ---------------------------------------------------------------------------------
class ColsSalida:
    ID = "id_producto"
    NOMBRE = "nombre_producto"
    CATEGORIA = "categoria"
    CATEGORIA_N2 = "categoria_nivel_2"
    UNIDAD = "unidad_medida"
    ES_PERECEDERO = "es_perecedero"
    PROVEEDOR = "proveedor"
    STOCK = "stock_actual"
    VENTA_DIARIA = "venta_diaria"
    DIAS_INVENTARIO = "dias_inventario"
    NIVEL_OBJETIVO = "nivel_objetivo"
    SUGERIDO = "sugerido"
    ESTADO = "estado"                  # valores de domain.reglas.Estado
    ALERTA_MERMA = "alerta_merma"      # bool: ESTANCADO y perecedero
    DIAS_SIN_VENDER = "dias_sin_vender"
    CAPITAL_RIESGO = "capital_en_riesgo"
    COSTO_UNITARIO = "costo_unitario"  # costo unit. para recalcular el valor del pedido en la UI


COLS_SALIDA: list[str] = [
    ColsSalida.ID, ColsSalida.NOMBRE, ColsSalida.CATEGORIA, ColsSalida.CATEGORIA_N2,
    ColsSalida.UNIDAD, ColsSalida.ES_PERECEDERO, ColsSalida.PROVEEDOR,
    ColsSalida.STOCK, ColsSalida.VENTA_DIARIA, ColsSalida.DIAS_INVENTARIO,
    ColsSalida.NIVEL_OBJETIVO, ColsSalida.SUGERIDO, ColsSalida.ESTADO,
    ColsSalida.ALERTA_MERMA, ColsSalida.DIAS_SIN_VENDER, ColsSalida.CAPITAL_RIESGO,
    ColsSalida.COSTO_UNITARIO,
]


# ---------------------------------------------------------------------------------
# Filtros que la UI pasa al servicio.
# ---------------------------------------------------------------------------------
@dataclass
class Filtros:
    # Listas vacías = sin filtro (todos). Permiten selección múltiple en la UI.
    proveedores: list[str] = field(default_factory=list)
    categorias: list[str] = field(default_factory=list)
    productos: list[str] = field(default_factory=list)   # nombres exactos (multiselect en cascada)
    solo_perecederos: bool = True       # MVP: piloto perecederos
    solo_accion: bool = True            # oculta CUBIERTO y ESTANCADO (sugerido 0)
    solo_reponer: bool = False          # solo estado REPONER (top-ups menos urgentes)
    busqueda: str | None = None         # texto libre sobre nombre_producto
