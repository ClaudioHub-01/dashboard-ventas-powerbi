"""
Dibuja una REFERENCIA de cómo debería verse la página "Resumen" del dashboard
(año 2025), para guiar la construcción en Power BI. No reemplaza al dashboard real.

Uso:
    python scripts/referencia_visual.py
"""
from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyBboxPatch  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

from valores_control import cargar, indicadores  # noqa: E402

RAIZ = Path(__file__).resolve().parents[1]
AZUL, NARANJO, GRIS, FONDO = "#1F4E79", "#E07A5F", "#5B6475", "#F5F6F8"
MESES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
millones = FuncFormatter(lambda x, _: f"${x / 1e6:.0f}M")


def _panel(fig, rect, titulo=None):
    x, y, w, h = rect
    fig.patches.append(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0,rounding_size=0.008",
                                      transform=fig.transFigure, facecolor="white", edgecolor="#E3E6EC", zorder=-5))
    if titulo:
        fig.text(x + 0.012, y + h - 0.035, titulo, fontsize=11, weight="bold", color="#1D2433")


def main() -> None:
    h = cargar()
    v = h["Ventas"]
    ent = v[v["Estado"] == "Entregado"]
    ind, ant = indicadores(v, 2025), indicadores(v, 2024)
    metas = h["Metas"]
    metas["Fecha"] = metas["Fecha"].astype("datetime64[ns]")
    ind["% Cumplimiento Meta"] = ind["Ventas Netas"] / metas[metas["Fecha"].dt.year == 2025]["MetaVentas"].sum()

    fig = plt.figure(figsize=(16, 9), facecolor=FONDO)
    fig.text(0.02, 0.945, "Ventas · Tienda online", fontsize=22, weight="bold", color="#1D2433")
    fig.text(0.02, 0.915, "Página Resumen · Año 2025 · todos los canales", fontsize=11, color=GRIS)
    for i, s in enumerate(["Año: 2025 ▾", "Canal: Todos ▾", "Región: Todas ▾"]):
        _panel(fig, (0.60 + i * 0.13, 0.915, 0.12, 0.05))
        fig.text(0.61 + i * 0.13, 0.932, s, fontsize=10, color=GRIS)

    tarjetas = [
        ("Ventas Netas", f"${ind['Ventas Netas'] / 1e6:,.1f}M", f"▲ {ind['Ventas Netas'] / ant['Ventas Netas'] - 1:.1%} vs año anterior"),
        ("Pedidos", f"{ind['Pedidos']:,}".replace(",", "."), f"▲ {ind['Pedidos'] / ant['Pedidos'] - 1:.1%} vs año anterior"),
        ("Ticket Promedio", f"${ind['Ticket Promedio']:,.0f}".replace(",", "."), ""),
        ("Margen %", f"{ind['Margen %']:.1%}", ""),
        ("% Cumplimiento Meta", f"{ind['% Cumplimiento Meta']:.1%}", ""),
    ]
    for i, (t, val, sub) in enumerate(tarjetas):
        x = 0.02 + i * 0.195
        _panel(fig, (x, 0.75, 0.185, 0.14))
        fig.text(x + 0.012, 0.86, t, fontsize=10.5, color=GRIS)
        fig.text(x + 0.012, 0.795, val, fontsize=24, weight="bold", color=AZUL)
        if sub:
            fig.text(x + 0.012, 0.765, sub, fontsize=9.5, color="#1E8E3E")

    # línea mensual vs año anterior y meta
    _panel(fig, (0.02, 0.05, 0.6, 0.67), "Ventas netas por mes vs año anterior y meta")
    ax = fig.add_axes([0.06, 0.1, 0.54, 0.54])
    serie = ent.groupby([ent["Fecha"].dt.year, ent["Fecha"].dt.month])["Neto"].sum()
    meta25 = metas[metas["Fecha"].dt.year == 2025]["MetaVentas"].values
    ax.bar(range(12), serie.loc[2025].values, color=AZUL, label="Ventas Netas 2025", width=0.6)
    ax.plot(range(12), serie.loc[2024].values, color=NARANJO, marker="o", lw=2, label="Año anterior")
    ax.plot(range(12), meta25, color=GRIS, ls="--", lw=1.5, label="Meta")
    ax.set_xticks(range(12), MESES)
    ax.yaxis.set_major_formatter(millones)
    ax.spines[["top", "right"]].set_visible(False)
    ax.legend(frameon=False, loc="upper left", fontsize=9)

    # categorías
    _panel(fig, (0.635, 0.39, 0.345, 0.33), "Ventas netas por categoría")
    ax2 = fig.add_axes([0.72, 0.42, 0.24, 0.24])
    cat = ent[ent["Fecha"].dt.year == 2025].groupby("Categoria")["Neto"].sum().sort_values()
    ax2.barh(cat.index, cat.values, color=AZUL)
    ax2.xaxis.set_major_formatter(millones)
    ax2.spines[["top", "right"]].set_visible(False)
    ax2.tick_params(labelsize=9)

    # canal (anillo)
    _panel(fig, (0.635, 0.05, 0.345, 0.32), "Participación por canal")
    ax3 = fig.add_axes([0.66, 0.07, 0.3, 0.24])
    can = ent[ent["Fecha"].dt.year == 2025].groupby("Canal")["Neto"].sum().sort_values(ascending=False)
    _, _, porcentajes = ax3.pie(can.values, labels=can.index, autopct="%1.0f%%", colors=[AZUL, NARANJO, "#3D9970"], startangle=90,
            wedgeprops={"width": 0.42}, pctdistance=0.79, textprops={"fontsize": 9.5})
    for t in porcentajes:
        t.set_color("white")

    fig.text(0.98, 0.012, "Referencia generada con Python — el dashboard real se construye en Power BI Desktop",
             fontsize=8, color=GRIS, ha="right")
    destino = RAIZ / "docs" / "referencia_resumen.png"
    destino.parent.mkdir(exist_ok=True)
    fig.savefig(destino, dpi=110, facecolor=FONDO)
    print(f"Referencia guardada en {destino}")


if __name__ == "__main__":
    main()
