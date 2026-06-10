"""Componentes de presentación: reciben datos y pintan. Sin lógica de negocio."""

from src.app.ui.components.header import render_header
from src.app.ui.components.filtros import render_filtros
from src.app.ui.components.kpis import render_kpis
from src.app.ui.components.tabla_pedidos import render_tabla
from src.app.ui.components.whatsapp_export import render_whatsapp

__all__ = [
    "render_header",
    "render_filtros",
    "render_kpis",
    "render_tabla",
    "render_whatsapp",
]
