# 4. Hallazgos del Análisis — ¿El problema es real?

> Este proyecto **no** nació de un análisis: nació de **ver** estanterías con producto perecedero
> que se devolvía o se botaba. La primera disciplina de un analista es no dejarse guiar solo por lo que ve, sino **verificarlo con datos**. Este documento es esa verificación.
>
> **Período analizado:** enero–mayo 2026 (5 meses) · **Fuentes:** `fact_perdidas`, `fact_compras`,
> `fact_ventas`, `dim_stock`, `dim_productos`.

---

## 4.1 La pregunta ancla

> **¿Hay un problema de dinero lo bastante grande, y concentrado, como para justificar construir un motor de pedidos? ¿Y los datos confirman lo que el ojo vio en la estantería?**

Todo lo que sigue se juzga contra esa pregunta.

---

## 4.2 ¿Cuánto se pierde? (tamaño del problema)

| Métrica (ene–may 2026) | Valor |
|---|---|
| Pérdida registrada (`fact_perdidas`) | **$684.483** |
| Proyección anualizada (×12/5) | **~$1,64M / año** |
| Pérdida como % de las compras a costo | 2,18% |
| Pérdida como % del ingreso | 0,30% |

**Criterio — un número solo no es ni grande ni pequeño.** $1,64M/año "suena" mucho, pero contra $228M de ingreso es 0,3%. ¿Entonces no importa? Sí importa, y el mejor espejo no es el ingreso sino **el margen**:

> La pérdida de Fruver ($614K) equivale al **8,5% del margen que deja Fruver** en el mismo período
> ($8,04M de margen). Es decir: de cada $100 de utilidad que genera la fruta y verdura, **$8,5 se botan a la basura.** Esa es la cifra que duele y la que justifica el proyecto.

---

## 4.3 ¿Dónde se concentra? (Fruver manda)

| Categoría | Pérdida | % del total |
|---|---|---|
| **Fruver** | $613.973 | **89,7%** |
| Pollo | $34.950 | 5,1% |
| Huevos | $9.980 | 1,5% |
| Resto | $25.580 | 3,7% |

**El ojo tenía razón, y el dato lo amplió:** Fruver no es "una de las que más pierde", es **casi toda la
pérdida** (90%). El piloto del motor debe arrancar aquí.

### Dentro de Fruver — regla de Pareto

Top productos por pérdida (acumulado): **Banano → Plátano → Tomate → Aguacate → Cebolla**.

- **5 productos = 43%** de la merma de Fruver.
- **8 productos = 57%.**

**Criterio — para en el Pareto.** No hay que analizar los 200 SKUs de fruver; el grueso del dolor vive en
~10 productos. El **Banano** es el caso de libro: 76,6 kg perdidos sobre 583,7 comprados = **13% de merma**
(de cada 100 kg que entran, 13 se botan).

---

## 4.4 El giro: hay DOS dolores, no uno

El ojo vio fruta podrida y concluyó "el problema es la merma de perecederos". Cierto, **pero los datos revelaron un segundo problema, distinto y más grande en plata**:

| | 🥩 Merma (se daña y se bota) | 💰 Capital atrapado (no se daña, pero no rota) |
|---|---|---|
| **Dónde** | Perecederos — **Fruver (90%)** | **NO perecederos** — golosinas, abarrotes, aseo, medicamentos |
| **Tamaño** | ~$1,64M/año botados | **$11,5M congelados hoy** (501 SKUs estancados) |
| **Síntoma** | Producto en la caneca | Estantería llena de lo mismo de hace meses |

**Lección clave:** ningún recorrido por la estantería habría mostrado que el capital muerto está en
**no perecederos**. El dato no le dio la razón al ojo: lo **corrigió y lo amplió**. Por eso se verifica.

---

## 4.5 El arma humeante: ¿nosotros causamos el problema?

La pregunta más importante no es *qué* se pierde, sino *si el propio proceso de compra lo causa*. Cruce:
productos estancados (sin venta > 14 días, con stock) **a los que aun así se les volvió a comprar** después
de su última venta:

> **116 productos fueron RE-COMPRADOS después de haber dejado de venderse.**
> **$770.042 gastados en volver a pedir mercancía que no rotaba.**

| Producto | Días sin vender | $ recomprado |
|---|---|---|
| Crema dental Colgate | **462** | $17.230 |
| Queso mozarella en bloque | 321 | $19.200 |
| Cayo (menudo res) | 153 | $32.000 |

Se compró crema dental que llevaba **462 días sin venderse una sola unidad**. Eso no es mala suerte: es **comprar a memoria, sin mirar el dato.** Esta es la causa raíz, en pesos y con nombre propio — y es exactamente lo que el motor frena: pone un ⚫ ESTANCADO y sugiere **pedir 0**.

---

## 4.6 Conclusión

| Pregunta ancla | Respuesta |
|---|---|
| ¿El problema es real y grande? | Sí: ~$1,64M/año en merma (8,5% del margen de Fruver) + $11,5M de capital congelado |
| ¿Está concentrado (= atacable)? | Sí: 90% de la merma en Fruver; ~10 SKUs explican el grueso |
| ¿El ojo acertó? | Parcialmente: acertó en la merma; el dato reveló un segundo dolor (capital atrapado en no perecederos) |
| ¿El proceso causa el problema? | Sí: $770K en re-compras de producto que ya no rotaba |

**El proyecto está justificado por datos, no por intuición.** El motor de pedidos ataca directamente las
dos causas: frena la compra de lo estancado (capital) y dimensiona la compra de perecederos (merma).

