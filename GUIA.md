# Guía paso a paso: construir el dashboard en Power BI

Tiempo estimado: **2 a 4 horas**. Necesitas **Power BI Desktop**, que es gratis: se instala desde Microsoft Store buscando "Power BI Desktop".

Al final tendrás un archivo `.pbix` con 3 páginas (Resumen, Productos y Clientes), además de capturas y un PDF para tu portafolio.

> La imagen [`docs/referencia_resumen.png`](docs/referencia_resumen.png) muestra cómo debería verse aproximadamente la página Resumen.

---

## Paso 1: Cargar los datos

1. Abre Power BI Desktop → **Obtener datos** → **Libro de Excel** → elige `datos/ventas_tienda.xlsx`.
2. Marca las 4 hojas: **Ventas**, **Productos**, **Clientes** y **Metas**.
3. Haz clic en **Transformar datos**, no en "Cargar".

## Paso 2: Revisar los tipos de datos (Power Query)

En cada tabla, haz clic en el ícono de la izquierda del encabezado de cada columna y deja estos tipos:

| Tabla | Columna | Tipo |
|---|---|---|
| Ventas | Fecha | **Fecha** (no "Fecha/hora") |
| Ventas | Cantidad, PrecioUnitario, Descuento, LineaID | Número entero |
| Productos | PrecioLista, CostoUnitario | Número entero |
| Clientes | FechaRegistro | Fecha |
| Metas | Fecha | Fecha |
| Metas | MetaVentas | Número entero |

Luego haz clic en **Cerrar y aplicar**.

## Paso 3: Crear la tabla Calendario

1. Ve a **Modelado** → **Nueva tabla** y pega el bloque `Calendario = ...` del archivo [`powerbi/medidas.dax`](powerbi/medidas.dax).
2. Con la tabla Calendario seleccionada, ve a **Herramientas de tabla** → **Marcar como tabla de fechas** y elige la columna `Date`.
3. Selecciona la columna **Mes** → **Herramientas de columna** → **Ordenar por columna** → **Mes Num**. Así los meses quedan en orden y no alfabéticos.
4. Haz lo mismo con **Día Semana**, ordenándola por **Día Semana Num**.

## Paso 4: Relaciones y tabla de medidas

1. Abre la **Vista de modelo**, que es el tercer ícono de la izquierda. Si Power BI creó relaciones automáticas incorrectas, bórralas.
2. Crea estas 4 relaciones arrastrando un campo sobre el otro. Todas deben ser de **varios a uno (*:1)** y con **dirección de filtro única**:
   - `Ventas[ProductoID]` → `Productos[ProductoID]`
   - `Ventas[ClienteID]` → `Clientes[ClienteID]`
   - `Ventas[Fecha]` → `Calendario[Date]`
   - `Metas[Fecha]` → `Calendario[Date]`
3. **Tabla de medidas:** ve a **Inicio** → **Escribir datos**, ponle de nombre `Medidas` y haz clic en **Cargar**. Ahí vas a guardar todas las medidas, para tenerlas ordenadas.

El modelo queda en **estrella**: `Ventas` en el centro y las tablas de dimensiones alrededor. Esto es lo que un cliente o un reclutador quiere ver.

## Paso 5: Crear las medidas

1. Selecciona la tabla **Medidas** → **Nueva medida**. Copia cada medida de [`powerbi/medidas.dax`](powerbi/medidas.dax), una por una (todo menos el bloque Calendario).
2. Cuando estén todas, borra la columna vacía de la tabla Medidas.
3. Aplica estos formatos desde **Herramientas de medición**:
   - **Moneda, sin decimales:** Ventas Brutas, Descuentos, Ventas Netas, Ticket Promedio, Costo, Margen, Ventas Año Anterior, Meta, Ventas Acumuladas Año.
   - **Porcentaje, 1 decimal:** Margen %, % Descuento, Var % Año Anterior, % Cumplimiento Meta, Tasa Devolución, % Clientes Recurrentes.
   - **Número entero:** Pedidos, Unidades, Pedidos Devueltos, Clientes Activos, Clientes Nuevos, Clientes Recurrentes.

## Paso 6: Aplicar el tema

Ve a **Vista** → **Temas** → **Buscar temas** y elige [`powerbi/tema_tienda.json`](powerbi/tema_tienda.json). Con eso quedan aplicados los colores y el estilo de todas las páginas.

---

## Paso 7: Página 1, "Resumen"

Usa la imagen de referencia como guía.

| Visual | Cómo configurarlo |
|---|---|
| **Título** | Inserta un **Cuadro de texto** con "Ventas · Tienda online". |
| **3 segmentadores** | Campos `Calendario[Año]`, `Ventas[Canal]` y `Clientes[Region]`. En formato, elige el estilo **Desplegable**. |
| **5 tarjetas** | Una tarjeta por medida: Ventas Netas, Pedidos, Ticket Promedio, Margen % y % Cumplimiento Meta. |
| **Texto de variación** | En las tarjetas de Ventas Netas y Pedidos, agrega la medida `Texto Var Año Anterior` como subtítulo o etiqueta de referencia. Dale color con formato condicional usando la medida `Color Var Año Anterior`. |
| **Gráfico combinado** | Usa **Gráfico de columnas agrupadas y de líneas**. Eje X: `Calendario[Mes]`. Columnas: `Ventas Netas`. Líneas: `Ventas Año Anterior` y `Meta`. |
| **Barras por categoría** | Usa **Gráfico de barras agrupadas**. Eje Y: `Productos[Categoria]`. Eje X: `Ventas Netas`. Ordénalo de mayor a menor. |
| **Anillo por canal** | Usa **Gráfico de anillos**. Leyenda: `Ventas[Canal]`. Valores: `Ventas Netas`. |

## Paso 8: Página 2, "Productos"

| Visual | Cómo configurarlo |
|---|---|
| **Matriz** | Filas: `Productos[Categoria]` y, debajo, `Productos[Producto]`. Valores: Ventas Netas, Unidades, Margen %, % Descuento y Tasa Devolución. |
| **Formato condicional** | En la matriz, aplica **barras de datos** a Ventas Netas y **escala de colores** a Margen %. |
| **Top 10 productos** | Usa un gráfico de barras con `Productos[Producto]` y `Ventas Netas`. En el panel de filtros, ve a Producto → **N superior** → 10 → por Ventas Netas. |
| **Dispersión** | Usa **Gráfico de dispersión**. Valores: `Productos[Producto]`. Eje X: `Ventas Netas`. Eje Y: `Margen %`. Leyenda: `Productos[Categoria]`. |

## Paso 9: Página 3, "Clientes"

| Visual | Cómo configurarlo |
|---|---|
| **Tarjetas** | Clientes Activos, Clientes Nuevos y % Clientes Recurrentes. |
| **Nuevos vs recurrentes** | Usa **Columnas apiladas**. Eje X: `Calendario[Mes]`. Valores: `Clientes Nuevos` y `Clientes Recurrentes`. |
| **Ventas por región** | Usa barras con `Clientes[Region]` y `Ventas Netas`. |
| **Día de la semana** | Usa columnas con `Calendario[Día Semana]` y `Ventas Netas`. |
| **Tabla de comunas** | Columnas: `Clientes[Comuna]`, Ventas Netas, Pedidos y Ticket Promedio. Muestra el top 10. |

Agrega en las 3 páginas los mismos segmentadores. Para que funcionen en todas a la vez, ve a **Vista** → **Sincronizar segmentaciones**.

---

## Paso 10: Verificar los números

Con el segmentador de año en **2025** y sin otros filtros, las tarjetas deben mostrar esto:

| Medida | Valor esperado (2025) |
|---|---|
| Ventas Netas | $250.844.330 |
| Pedidos | 4.340 |
| Ticket Promedio | $57.798 |
| Margen % | 50,7% |
| Var % Año Anterior | 23,7% |
| % Cumplimiento Meta | 103,1% |
| Tasa Devolución | 4,4% |
| Clientes Activos | 2.123 |
| Clientes Nuevos | 1.400 |

En **2026**, que tiene datos de enero a octubre, la Var % Año Anterior debe ser **31,1%**, porque compara con enero a octubre de 2025.

Si algún valor no coincide, lo más probable es una relación mal creada (paso 4) o una columna `Fecha` que quedó como "Fecha/hora" (paso 2).

Para ver todos los valores de control, puedes ejecutar `python scripts/valores_control.py`.

## Paso 11: Guardar y preparar el portafolio

1. Guarda el archivo como `powerbi/dashboard_ventas.pbix`.
2. Toma una captura de cada página con la herramienta Recortes de Windows (`Win + Shift + S`) y guárdalas en `docs/`:
   - `resumen.png`
   - `productos.png`
   - `clientes.png`
3. Exporta un PDF desde **Archivo** → **Exportar** → **Exportar a PDF**, y guárdalo como `docs/dashboard_ventas.pdf`.
4. En el `README.md`, reemplaza la imagen de referencia por tu captura real `docs/resumen.png`. Revisa también que los hallazgos coincidan con lo que muestra tu dashboard.
