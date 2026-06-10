"""App de Toma de Pedidos — La Roka.

Arquitectura desacoplada en capas:
- domain/   : reglas de negocio puras y contratos de datos (sin IO).
- data/     : patrón Repository. Cambiar de fuente de datos = nueva implementación.
- services/ : motor de cálculo (puro) + orquestación (PedidoService).
- ui/       : presentación Streamlit. Solo consume services, nunca toca data/ directo.
"""
