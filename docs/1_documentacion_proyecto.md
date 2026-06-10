# 1. Documentación del Proyecto — Motor de Sugerencia de Pedidos "La Roka"

> De **comprar a ojo** a **comprar dirigido por datos**: un motor analítico que le dice al colaborador
> *qué pedir y cuánto*, en minutos, priorizando lo que realmente necesita reabastecer.

---

## 1.1 Resumen

Supermercado con +100 proveedores que toman pedido **cada 7 días** (sábado se pide → lunes llega).
Hoy el pedido se arma a memoria revisando físicamente las estanterías. Este proyecto reemplaza esa intuición por un **modelo de revisión periódica (*order-up-to*)** que calcula la sugerencia de compra por producto a partir de sus **Días de Inventario**, y la presenta en una **app tabular de alta densidad** pensada para que el colaborador decida de un vistazo y exporte el pedido a WhatsApp.

---

## 1.2 Dolores del negocio (el problema en pesos)

| Dolor                                 | Qué pasa hoy                                                                                     | Costo                                                                                             |
| ------------------------------------- | ------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------------------------------- |
| 🥩 **Merma en perecederos**           | Se pide de más en productos de venta lenta → se dañan antes de venderse                          | 📊 **~$2.5M acumulados** (~$80K/mes promedio) en pérdidas registradas — `fact_perdidas`, 31 meses |
| 💰 **Capital atrapado (sobre-stock)** | Se compra no-perecedero "por promo" o sin mirar el stock real → la plata queda inmóvil en bodega | 📊 **~$7.58M inmovilizados hoy** en productos estancados (>14 días de inventario)                 |
| 🚫 **Quiebre de stock**               | Se olvidan productos de alta rotación → agotados                                                 | ❓ **Venta perdida** (no medida: el POS no registra lo que el cliente buscó y no encontró)         |
| ⏱️ **Tiempo operativo**               | Armar el pedido a memoria, estante por estante                                                   | 🗣️ **~8 h/semana** (un turno), reportado por el equipo                                           |

> **Origen de cada cifra:** 📊 medido en datos · 🗣️ reportado por el negocio · ❓ estimado (sin dato directo).
> *Nota sobre devoluciones:* existen ~$35.7M históricos en `fact_devoluciones` (~$1.08M/mes), pero **no son pérdida neta** — buena parte es recuperable (cambio mano a mano / crédito del proveedor). Se trata como **indicador de fricción**, no como merma.

> 📊 **Análisis que valida estos dolores con datos** (ene–may 2026, con cifras y el "arma humeante" de las
> re-compras de producto estancado): ver [`4_hallazgos_analisis.md`](4_hallazgos_analisis.md).

**Causa raíz:** la decisión de compra depende de la memoria de un colaborador, no de la
velocidad real de venta ni del stock disponible.

---

## 1.3 Alcance de la solución

**MVP — Piloto de perecederos** (Fruver / Carnes / Lácteos / Ahumados):
- ✅ Refinar la lógica de reabastecimiento (ventanas dinámicas 14/90, Días de Inventario, semáforo, *order-up-to* ).
- ✅ App Streamlit de toma de pedidos (lista de acción + edición + export a WhatsApp).
- ✅ KPIs base para medir el impacto.

**Por qué perecederos primero:** es donde el stock está **fresco y confiable** (se cuenta semanal) y donde la merma es el dolor #1. Validamos ahí y luego ampliamos.

**Fuera del MVP (backlog):** limpieza de proveedores duplicados en la fuente, captura de frecuencia real por proveedor (quincenal/mensual), estacionalidad, catálogo completo, tablero gerencial de KPIs.

---

## 1.4 ¿Por qué una UI tabular de alta densidad y NO un chatbot de IA?

Se evaluó anexar un chat de IA para "preguntarle a los datos". **Se descartó para el MVP.** El colaborador no necesita conversar; necesita **decidir rápido**. Comparación:

| Criterio                 | 📊 Tabla de alta densidad (elegido)            | 💬 Chatbot de IA                             |
| ------------------------ | ---------------------------------------------- | -------------------------------------------- |
| Velocidad de decisión    | Escanea 20 filas y decide en segundos          | Escribe, espera respuesta, repite            |
| Fricción para el usuario | Mínima: filtrar → revisar → editar → exportar  | Alta: hay que saber *qué* preguntar          |
| Acción directa           | Edita el sugerido y copia el pedido a WhatsApp | Devuelve texto que igual hay que transcribir |
| "¿Por qué este número?"  | Resuelto con **íconos `?`** en cada métrica    | Requiere otra pregunta                       |
| Costo / mantenimiento    | Bajo (lee `.parquet`)                          | Tokens, latencia, prompts, alucinaciones     |
| Confianza del operario   | Ve los números y manda él pedido               | "Caja negra" que cuesta adoptar              |

> **Principio de diseño:** la herramienta debe sentirse como un **checklist inteligente**, no como una
> conversación. Los tooltips `?` cubren el "por qué" de cada cálculo sin sacar a la cajera de su flujo.

---

## 1.5 Objetivos y KPIs

| #   | Objetivo                            | Métrica                                                                                             | Línea base                           | Meta                     |
| --- | ----------------------------------- | --------------------------------------------------------------------------------------------------- | ------------------------------------ | ------------------------ |
| 1   | Reducir merma en perecederos        | `fact_perdidas` + `fact_devoluciones` + merma de inventario, mensual, variación vs período anterior | $2.5M pérdidas · $35.6M devoluciones | **−20%**                 |
| 2   | Reducir capital atrapado            | Σ `capital_en_riesgo` de productos ESTANCADO (>14 días inv.) + nº SKUs estancados                   | Calculable hoy                       | Tendencia ↓              |
| 3   | Pedido data-driven / menos quiebres | (a) cobertura (nº productos surtidos), (b) nº SKUs CRÍTICOS sin reabastecer, (c) tiempo de armado   | Calculable + medible en piloto       | Cobertura ↑ · Críticos ↓ |

| Objetivo Estratégico | Indicadores Clave (KPIs) | Situación Actual | Resultado Esperado |
|---------------------|--------------------------|------------------|--------------------|
| Reducir la merma en perecederos | Pérdidas, devoluciones, merma mensual y variación vs. período anterior | Pérdidas: $2.5M · Devoluciones: $35.6M | Reducir la merma en un 20% |
| Reducir el capital inmovilizado en inventario | Capital en riesgo de productos estancados (>14 días) y cantidad de SKUs estancados | Medible con datos actuales | Mantener una tendencia de reducción sostenida |
| Mejorar la disponibilidad de productos y disminuir quiebres | Cobertura de surtido, cantidad de SKUs críticos sin reabastecer y tiempo de armado de pedidos | Medible mediante piloto | Incrementar cobertura y reducir quiebres de stock |

**Métrica de adopción (clave):** comparar el **sugerido** vs lo **realmente comprado** la semana siguiente
(`fact_compras`) → mide confianza en el sistema y precisión del modelo.

> Nota: el tiempo de armado puede subir levemente al inicio (se analizan más productos que antes se
> ignoraban). Es esperado y deseable: significa que el cliente encontrará lo que busca.
