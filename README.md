# 🛒 La Roka — Motor de Sugerencia de Pedidos

> **De comprar "a ojo" a comprar dirigido por datos.** Un motor analítico que le dice al minimarket
> *qué pedir y cuánto* cada semana, evitando la merma, el capital congelado y los quiebres de stock.

![status](https://img.shields.io/badge/estado-MVP%20en%20desarrollo-f5a623)
![python](https://img.shields.io/badge/Python-3.11-3776ab)
![polars](https://img.shields.io/badge/Polars-DataFrames-cd792c)
![parquet](https://img.shields.io/badge/Storage-Parquet-50abdf)
![streamlit](https://img.shields.io/badge/UI-Streamlit-ff4b4b)

---

## 📌 Descripción ejecutiva

Minimarket de barrio con **+100 proveedores** que toman pedido **cada 7 días**. Hoy la compra se decide a
memoria, revisando físicamente las estanterías (~8 h/semana). Eso genera tres fugas de dinero: **merma**
en perecederos, **capital atrapado** en sobre-stock y **ventas perdidas** por quiebres.

Este proyecto reemplaza la intuición por un **modelo de revisión periódica (*order-up-to*)**: calcula los
**Días de Inventario** de cada producto, lo clasifica con un semáforo y sugiere la cantidad exacta a pedir,
todo presentado en una **app tabular rápida** que la cajera usa y exporta a WhatsApp.

---

## 💸 El problema en pesos — y cómo el dato lo previene

| Compra tradicional (a ojo) | Compra dirigida por datos |
|----------------------------|---------------------------|
| Repone "lo vendido" sin mirar el stock → **sobre-stock** | Llena solo hasta el **nivel objetivo** (`max(0, S − Stock)`) |
| Perecederos de venta lenta se **dañan** (~$1,64M/año, 90% en Fruver) | Detecta **ESTANCADO** y dispara alerta de merma para rotar a tiempo |
| Se vuelve a comprar lo que no rota (**$770K** re-comprados estando estancados) | Marca **ESTANCADO** y sugiere pedir **0** → libera capital |
| Se olvidan productos de alta rotación → **agotados** | Marca **CRÍTICO** (<3 días) y prioriza la compra urgente |
| ~8 h/semana revisando estantería | Lista de acción lista en minutos, ordenada por urgencia |

> 📊 **Los números están verificados con datos** (ene–may 2026), no supuestos. Ver el análisis completo en
> [`docs/4_hallazgos_analisis.md`](docs/4_hallazgos_analisis.md): el problema es real, está concentrado
> (90% en Fruver) y el propio proceso de compra lo causa.

**Ejemplo real (corte 2026-06-06):** la *Costilla Ahumada* vende 3 kg/día y tiene stock para **<1 día** →
el motor sugiere pedir **24 kg** antes de quebrar. La *Yuca* tiene **60 días** de inventario en un producto
que no dura 15 → sugiere **0** y alerta de merma.

---

## 🧠 La lógica en 30 segundos

```
Venta Diaria  →  Días de Inventario = Stock ÷ Venta Diaria  →  Semáforo  →  Sugerido
```

| Estado | Días de Inventario | Acción |
|--------|--------------------|--------|
| 🔴 CRÍTICO | < 3 | Pedir ya (compra agresiva con buffer) |
| 🟡 NORMAL | 3 – 14 | Completar hasta el nivel objetivo |
| ⚫ ESTANCADO | > 14 | No pedir (+ alerta de merma si es perecedero) |

> **Ventanas dinámicas:** perecederos se promedian a **14 días** (miran el presente); estables a **90 días**
> (miran la historia). Detalle completo en [`docs/3_logica_de_negocio.md`](docs/3_logica_de_negocio.md).

---

## 🛠️ Stack tecnológico

| Capa | Tecnología | Por qué |
|------|-----------|---------|
| Ingesta / Transformación | **Python + Polars** | Rápido y expresivo sobre cientos de miles de filas |
| Almacenamiento analítico | **Parquet** (arquitectura medallón bronze → plata → oro) | Columnar, comprimido, lectura directa |
| Modelo | Esquema estrella (Dim/Fact) | Ver [`docs/2_arquitectura_de_datos.md`](docs/2_arquitectura_de_datos.md) |
| App / UI | **Streamlit** | 100% Python, MVP en días, tabla editable + export a WhatsApp |

---

## 📁 Estructura del repositorio

```
laRoka-pedidos/
├── README.md                          # este archivo
├── App-Pedidos.vbs                    # lanzador: abre la app en Chrome (sin consola)
├── Crear-Acceso-Directo.vbs           # crea el acceso directo en el escritorio
├── docs/
│   ├── 1_documentacion_proyecto.md    # justificación, dolores, alcance, KPIs
│   ├── 2_arquitectura_de_datos.md     # modelo estrella + DBML + Mermaid ER
│   ├── 3_logica_de_negocio.md         # fórmulas (LaTeX) + flujos de decisión
│   ├── 4_hallazgos_analisis.md        # análisis exploratorio que valida el problema
│   ├── practica_analitica.md          # cuaderno de práctica de criterio analítico
│   └── prototipo_visual.html          # mockup de la app (abrir en navegador)
└── src/
    └── app/                           # app Streamlit de pedidos (capas: data · domain · services · ui)
        ├── app.py                     # entrypoint
        ├── domain/                    # reglas de negocio + contratos (esquema)
        ├── data/                      # repositorio de datos (parquet, intercambiable)
        ├── services/                  # motor de reabastecimiento + fachada PedidoService
        └── ui/                        # componentes Streamlit (header, filtros, tabla, KPIs, export)
```

> ℹ️ El **ETL** (arquitectura medallón bronze → plata → oro) que produce los `.parquet` que la app consume
> vive en un módulo aparte y se versionará por separado. Este repositorio contiene **la aplicación**.

---

## 🎯 Resultados esperados (KPIs)

| Objetivo | Métrica | Meta |
|----------|---------|------|
| Reducir merma en perecederos | Pérdidas + devoluciones, variación mensual | **−20%** |
| Reducir capital atrapado | Capital en riesgo de productos estancados | Tendencia ↓ |
| Pedido data-driven | Cobertura ↑ · SKUs críticos sin reabastecer ↓ | — |
| Adopción / precisión | Sugerido vs comprado real (`fact_compras`) | Cierre de brecha |

---

## 🚀 Cómo ejecutarlo

Requiere **Python 3.11+**. Desde la raíz del repositorio:

```bash
# 1) Entorno virtual
python -m venv .venv
# Windows:  .venv\Scripts\activate
# Linux/Mac: source .venv/bin/activate

# 2) Dependencias
pip install -r requirements.txt

# 3) Levantar la app (desde la RAÍZ del repo)
streamlit run src/app/app.py
```

> ✅ **Arranca sin datos.** Si no encuentra los `.parquet`, la app levanta en **modo muestra** con datos de
> ejemplo, para que puedas verla funcionando de inmediato.

### Conectar tus propios datos

La fuente de datos es **intercambiable** (patrón repositorio). Para apuntar a tus `.parquet`:

```bash
# Windows (PowerShell)
$env:ROKA_DATA_DIR = "D:/ruta/a/tus/parquet"
# Linux/Mac
export ROKA_DATA_DIR=/ruta/a/tus/parquet
streamlit run src/app/app.py
```

El esquema que la app espera de cada tabla está documentado en
[`src/app/domain/contracts.py`](src/app/domain/contracts.py). Para usar **otra fuente** (SQL, API, etc.) basta
con implementar la interfaz `FuenteDatos` ([`src/app/data/repository.py`](src/app/data/repository.py)) — no
hay que tocar la UI ni el motor.

### 🖱️ Lanzador sin consola (Windows)

Para que un cajero abra la app con doble clic (Chrome, sin ventana de terminal): ejecuta una vez
`Crear-Acceso-Directo.vbs` (crea el acceso directo en el escritorio) y luego usa `App-Pedidos.vbs`.

> 🔎 Vista previa de la interfaz sin instalar nada: abre [`docs/prototipo_visual.html`](docs/prototipo_visual.html) en el navegador.

---

## 📚 Documentación

- 📄 [Documentación del proyecto](docs/1_documentacion_proyecto.md)
- 🗂️ [Arquitectura de datos](docs/2_arquitectura_de_datos.md)
- 🧮 [Lógica de negocio](docs/3_logica_de_negocio.md)
