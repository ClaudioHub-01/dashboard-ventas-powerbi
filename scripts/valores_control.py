"""
Calcula con Python los mismos indicadores que las medidas DAX, para comprobar
que el dashboard de Power BI da los valores correctos.

Uso:
    python scripts/valores_control.py
"""
from __future__ import annotations

from pathlib import Path

import pandas as pd

RAIZ = Path(__file__).resolve().parents[1]


def cargar() -> dict[str, pd.DataFrame]:
    hojas = pd.read_excel(RAIZ / "datos" / "ventas_tienda.xlsx", sheet_name=None)
    v = hojas["Ventas"].merge(hojas["Productos"][["ProductoID", "Categoria", "CostoUnitario"]], on="ProductoID")
    v["Fecha"] = pd.to_datetime(v["Fecha"])
    v["Bruto"] = v["Cantidad"] * v["PrecioUnitario"]
    v["Neto"] = v["Bruto"] - v["Descuento"]
    v["Costo"] = v["Cantidad"] * v["CostoUnitario"]
    hojas["Ventas"] = v
    return hojas


def indicadores(v: pd.DataFrame, anio: int) -> dict:
    a = v[v["Fecha"].dt.year == anio]
    ent = a[a["Estado"] == "Entregado"]
    primera = v[v["Estado"] == "Entregado"].groupby("ClienteID")["Fecha"].min()
    activos = ent["ClienteID"].unique()
    nuevos = int((primera.loc[activos].dt.year == anio).sum())
    pedidos = ent["PedidoID"].nunique()
    dev = a[a["Estado"] == "Devuelto"]["PedidoID"].nunique()
    base_dev = a[a["Estado"].isin(["Entregado", "Devuelto"])]["PedidoID"].nunique()
    return {
        "Ventas Netas": ent["Neto"].sum(),
        "Pedidos": pedidos,
        "Ticket Promedio": ent["Neto"].sum() / pedidos,
        "Margen %": (ent["Neto"].sum() - ent["Costo"].sum()) / ent["Neto"].sum(),
        "Descuentos": ent["Descuento"].sum(),
        "Tasa Devolución": dev / base_dev,
        "Clientes Activos": len(activos),
        "Clientes Nuevos": nuevos,
    }


def main() -> None:
    h = cargar()
    v, metas = h["Ventas"], h["Metas"]
    metas["Fecha"] = pd.to_datetime(metas["Fecha"])
    filas = {}
    for anio in (2024, 2025, 2026):
        ind = indicadores(v, anio)
        meta = metas[(metas["Fecha"].dt.year == anio) & (metas["Fecha"] <= v["Fecha"].max())]["MetaVentas"].sum()
        ind["% Cumplimiento Meta"] = ind["Ventas Netas"] / meta
        filas[anio] = ind
    tabla = pd.DataFrame(filas)
    # igual que SAMEPERIODLASTYEAR: se compara contra los mismos días del año anterior
    ent = v[v["Estado"] == "Entregado"]
    fin = v["Fecha"].max()
    var = [None]
    for anio in (2025, 2026):
        limite = fin.replace(year=anio - 1) if anio == fin.year else pd.Timestamp(anio - 1, 12, 31)
        anterior = ent[(ent["Fecha"].dt.year == anio - 1) & (ent["Fecha"] <= limite)]["Neto"].sum()
        var.append(tabla.loc["Ventas Netas", anio] / anterior - 1)
    tabla.loc["Var % vs año anterior"] = var
    pd.options.display.float_format = lambda x: f"{x:,.4f}" if abs(x) < 10 else f"{x:,.0f}"
    print(tabla.to_string())
    print("\n2026 incluye solo enero a octubre: su Var % se compara con enero a octubre de 2025.")
    ent = v[(v["Estado"] == "Entregado") & (v["Fecha"].dt.year == 2025)]
    print("\nVentas netas 2025 por categoría:")
    print(ent.groupby("Categoria")["Neto"].sum().sort_values(ascending=False).map("{:,.0f}".format).to_string())
    print("\nVentas netas 2025 por canal:")
    print(ent.groupby("Canal")["Neto"].sum().sort_values(ascending=False).map("{:,.0f}".format).to_string())


if __name__ == "__main__":
    main()
