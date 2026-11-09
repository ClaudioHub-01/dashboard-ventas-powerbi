"""
Genera los datos FICTICIOS de una tienda online de ropa de cama y respaldos
(enero 2024 a octubre 2026) en un Excel listo para cargar en Power BI.

Modelo en estrella:
  Ventas    (hechos: una fila por producto dentro de cada pedido)
  Productos (dimensión)
  Clientes  (dimensión)
  Metas     (meta mensual de ventas netas)

Incluye patrones realistas para que el análisis tenga hallazgos:
crecimiento anual, estacionalidad (invierno, CyberDay, Black Friday, Navidad),
descuentos en eventos, devoluciones y clientes recurrentes.

Uso:
    python scripts/generar_datos.py
"""
from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd

SEED = 2026
RAIZ = Path(__file__).resolve().parents[1]
DESTINO = RAIZ / "datos" / "ventas_tienda.xlsx"
INICIO, FIN = date(2024, 1, 1), date(2026, 10, 31)

# (nombre, categoría, precio, costo)
PRODUCTOS = [
    ("Sábana algodón 1,5 plazas", "Sábanas", 17990, 8200), ("Sábana algodón 2 plazas", "Sábanas", 21990, 9900),
    ("Sábana algodón King", "Sábanas", 27990, 12800), ("Sábana microfibra 2 plazas", "Sábanas", 14990, 5900),
    ("Sábana percal 400 hilos 2 plazas", "Sábanas", 39990, 17500), ("Sábana franela 2 plazas", "Sábanas", 24990, 10900),
    ("Plumón 1,5 plazas", "Plumones", 34990, 16900), ("Plumón 2 plazas", "Plumones", 42990, 20500),
    ("Plumón King", "Plumones", 54990, 26800), ("Plumón pluma de ganso 2 plazas", "Plumones", 89990, 45200),
    ("Plumón liviano verano 2 plazas", "Plumones", 29990, 13900),
    ("Almohada fibra", "Almohadas", 9990, 3800), ("Almohada viscoelástica", "Almohadas", 19990, 8700),
    ("Almohada cervical", "Almohadas", 24990, 10500), ("Almohada pluma", "Almohadas", 29990, 13600),
    ("Protector de almohada x2", "Almohadas", 8990, 3300),
    ("Respaldo tapizado 1,5 plazas", "Respaldos", 69990, 36500), ("Respaldo tapizado 2 plazas", "Respaldos", 89990, 46800),
    ("Respaldo tapizado King", "Respaldos", 119990, 63200), ("Respaldo capitoné 2 plazas", "Respaldos", 129990, 67900),
    ("Respaldo madera 2 plazas", "Respaldos", 99990, 54100),
    ("Cubrecama quilt 2 plazas", "Cubrecamas", 32990, 14800), ("Cubrecama quilt King", "Cubrecamas", 39990, 18200),
    ("Cubrecama tejido 2 plazas", "Cubrecamas", 44990, 21300), ("Pie de cama", "Cubrecamas", 15990, 6400),
    ("Toalla de baño", "Toallas", 7990, 3100), ("Toalla de mano", "Toallas", 3990, 1500),
    ("Set toallas x3", "Toallas", 19990, 8300), ("Bata de baño", "Toallas", 24990, 11200),
    ("Protector de colchón 2 plazas", "Accesorios", 22990, 9800), ("Cojín decorativo", "Accesorios", 9990, 3900),
    ("Funda de cojín x2", "Accesorios", 11990, 4600),
]
REGIONES = [  # (región, comunas, peso)
    ("Metropolitana", ["Santiago", "Maipú", "Puente Alto", "Las Condes", "La Florida", "Ñuñoa", "Providencia",
                       "San Bernardo", "Peñalolén", "El Monte", "Talagante"], 54),
    ("Valparaíso", ["Viña del Mar", "Valparaíso", "Quilpué", "Villa Alemana", "San Antonio"], 11),
    ("Biobío", ["Concepción", "Talcahuano", "Los Ángeles", "Chillán"], 8),
    ("O'Higgins", ["Rancagua", "San Fernando", "Rengo"], 5),
    ("Maule", ["Talca", "Curicó", "Linares"], 5),
    ("Araucanía", ["Temuco", "Villarrica", "Angol"], 4),
    ("Coquimbo", ["La Serena", "Coquimbo", "Ovalle"], 4),
    ("Los Lagos", ["Puerto Montt", "Osorno", "Castro"], 4),
    ("Antofagasta", ["Antofagasta", "Calama"], 3),
    ("Otras regiones", ["Arica", "Iquique", "Copiapó", "Valdivia", "Punta Arenas", "Coyhaique"], 2),
]
CANALES = [("Sitio web", 55), ("Instagram", 25), ("Marketplace", 20)]
MEDIOS = [("Webpay", 58), ("Transferencia", 24), ("Mercado Pago", 18)]
CATEGORIA_INVIERNO = {"Plumones": 2.4, "Sábanas": 1.25, "Cubrecamas": 1.4}  # junio-agosto


def _eventos(anio: int) -> dict[date, tuple[float, float]]:
    """Fechas con más demanda: día -> (multiplicador de pedidos, descuento promedio)."""
    ev: dict[date, tuple[float, float]] = {}
    for inicio, dias, mult, desc in [
        (date(anio, 6, 2), 3, 4.0, 0.25),   # CyberDay junio
        (date(anio, 10, 6), 3, 3.5, 0.25),  # CyberMonday octubre
        (date(anio, 11, 27), 4, 3.0, 0.20),  # Black Friday
        (date(anio, 12, 10), 14, 1.8, 0.05),  # Navidad
        (date(anio, 5, 5), 7, 1.5, 0.10),   # Día de la Madre
    ]:
        for i in range(dias):
            ev[inicio + timedelta(days=i)] = (mult, desc)
    return ev


def main() -> None:
    random.seed(SEED)
    productos = pd.DataFrame(PRODUCTOS, columns=["Producto", "Categoria", "PrecioLista", "CostoUnitario"])
    productos.insert(0, "ProductoID", [f"P{i:03d}" for i in range(1, len(productos) + 1)])

    # clientes que se van registrando en el tiempo
    clientes, dias_total = [], (FIN - INICIO).days
    for i in range(1, 4201):
        region, comunas, _ = random.choices(REGIONES, weights=[r[2] for r in REGIONES])[0]
        # más registros a medida que la tienda crece
        registro = INICIO + timedelta(days=int(dias_total * random.random() ** 0.8))
        clientes.append({"ClienteID": f"C{i:05d}", "Region": region, "Comuna": random.choice(comunas),
                         "FechaRegistro": registro,
                         "CanalAdquisicion": random.choices([c[0] for c in CANALES], [c[1] for c in CANALES])[0]})
    clientes_df = pd.DataFrame(clientes).sort_values("FechaRegistro").reset_index(drop=True)
    clientes_df["ClienteID"] = [f"C{i:05d}" for i in range(1, len(clientes_df) + 1)]
    registros = list(zip(clientes_df["ClienteID"], clientes_df["FechaRegistro"]))

    eventos = {}
    for anio in (2024, 2025, 2026):
        eventos.update(_eventos(anio))

    filas, pedido, dia = [], 10000, INICIO
    while dia <= FIN:
        anios = (dia - INICIO).days / 365
        base = 7.5 * (1.28 ** anios)                     # crecimiento ~28% anual
        base *= 1.25 if dia.weekday() in (0, 6) else 1.0  # domingos y lunes más compras online
        mult, desc_evento = eventos.get(dia, (1.0, 0.0))
        n_pedidos = max(0, round(random.gauss(base * mult, (base * mult) ** 0.5)))
        disponibles = [c for c, r in registros if r <= dia] or [registros[0][0]]
        recientes = disponibles[-60:]
        invierno = dia.month in (6, 7, 8)
        for _ in range(n_pedidos):
            pedido += 1
            # 45% compra un cliente recién registrado, el resto clientes existentes (recurrencia)
            cliente = random.choice(recientes) if random.random() < 0.45 else random.choice(disponibles)
            canal = random.choices([c[0] for c in CANALES], [c[1] for c in CANALES])[0]
            medio = random.choices([m[0] for m in MEDIOS], [m[1] for m in MEDIOS])[0]
            estado = random.choices(["Entregado", "Devuelto", "Cancelado"], [92, 4, 4])[0]
            pesos = [(CATEGORIA_INVIERNO.get(p[1], 1.0) if invierno else (0.55 if p[1] == "Plumones" else 1.0))
                     * (0.45 if p[1] == "Respaldos" else 1.0) for p in PRODUCTOS]
            k = random.choices([1, 2, 3], [62, 28, 10])[0]
            elegidos = list(dict.fromkeys(random.choices(range(len(PRODUCTOS)), weights=pesos, k=k)))
            for idx in elegidos:
                pid = productos.loc[idx, "ProductoID"]
                precio = int(productos.loc[idx, "PrecioLista"])
                cantidad = random.choices([1, 2, 3], [80, 16, 4])[0]
                tasa = desc_evento + random.choice([0, 0, 0, 0.05, 0.10]) if desc_evento else random.choice([0] * 8 + [0.05, 0.10])
                descuento = int(round(precio * cantidad * min(tasa, 0.4), -1))
                filas.append({"PedidoID": f"PED-{pedido}", "Fecha": dia, "ClienteID": cliente, "ProductoID": pid,
                              "Cantidad": cantidad, "PrecioUnitario": precio, "Descuento": descuento,
                              "Canal": canal, "MedioPago": medio, "Estado": estado})
            # en invierno, algunos pedidos suman además un plumón
            if invierno and random.random() < 0.18:
                idx = random.choice([i for i, p in enumerate(PRODUCTOS) if p[1] == "Plumones"])
                precio = int(productos.loc[idx, "PrecioLista"])
                filas.append({"PedidoID": f"PED-{pedido}", "Fecha": dia, "ClienteID": cliente,
                              "ProductoID": productos.loc[idx, "ProductoID"], "Cantidad": 1, "PrecioUnitario": precio,
                              "Descuento": int(round(precio * desc_evento, -1)), "Canal": canal, "MedioPago": medio,
                              "Estado": estado})
        dia += timedelta(days=1)

    ventas = pd.DataFrame(filas)
    ventas.insert(0, "LineaID", range(1, len(ventas) + 1))

    # Metas: ventas netas del mismo mes del año anterior + 20% (2024: valor fijo creciente)
    entregadas = ventas[ventas["Estado"] == "Entregado"]
    netas = (entregadas["Cantidad"] * entregadas["PrecioUnitario"] - entregadas["Descuento"])
    mensual = netas.groupby(pd.to_datetime(entregadas["Fecha"]).dt.to_period("M")).sum()
    metas = []
    for periodo in pd.period_range("2024-01", "2026-10", freq="M"):
        anterior = mensual.get(periodo - 12)
        meta = anterior * 1.20 if anterior is not None else mensual.get(periodo, 0) * random.uniform(0.92, 1.08)
        metas.append({"Fecha": periodo.to_timestamp().date(), "MetaVentas": int(round(meta, -4))})
    metas_df = pd.DataFrame(metas)

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(DESTINO, engine="openpyxl") as xl:
        for nombre, df in [("Ventas", ventas), ("Productos", productos), ("Clientes", clientes_df), ("Metas", metas_df)]:
            df.to_excel(xl, sheet_name=nombre, index=False)
            ws = xl.sheets[nombre]
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = max(12, min(40, max(len(str(c.value or "")) for c in col[:200]) + 2))
            for c in ws[1]:
                if c.value in ("Fecha", "FechaRegistro"):
                    for celda in ws[c.column_letter][1:]:
                        celda.number_format = "yyyy-mm-dd"
    print(f"{len(ventas):,} líneas de venta, {ventas['PedidoID'].nunique():,} pedidos, "
          f"{len(clientes_df):,} clientes -> {DESTINO}")


if __name__ == "__main__":
    main()
