"""Charts for the README. Run: python -m src.charts (after src.model)."""
from __future__ import annotations

import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from .model import OUT, implied_terminal_asp, load_config, project

SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_2 = "#52514e"
GRID = "#e4e3df"
BLUE = "#2a78d6"     # categorical slot 1
ORANGE = "#eb6834"   # categorical slot 2

plt.rcParams.update({
    "figure.facecolor": SURFACE, "axes.facecolor": SURFACE,
    "axes.edgecolor": GRID, "axes.labelcolor": INK_2, "text.color": INK,
    "xtick.color": INK_2, "ytick.color": INK_2, "font.size": 10,
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "axes.axisbelow": True, "grid.color": GRID, "grid.linewidth": 0.8,
})


def earnings_split(cfg):
    rows = project(cfg, "base")
    yrs = [r["year"] for r in rows]
    total = [r["operating_income"] for r in rows]
    core = [r["core_ebit"] for r in rows]
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.fill_between(yrs, core, total, color=ORANGE, alpha=0.18, linewidth=0)
    ax.plot(yrs, total, color=BLUE, lw=2, marker="o", ms=6, label="Operating income (reported)")
    ax.plot(yrs, core, color=ORANGE, lw=2, marker="o", ms=6, label="Core operating income (ex-45X)")
    ax.axhline(0, color=INK_2, lw=0.8)
    ax.text(2027.1, (total[1] + core[1]) / 2, "45X credit", color=INK_2, fontsize=9, va="center")
    ax.set_title("Base case: core earnings must replace 45X as it phases out (2030-32)",
                 loc="left", fontsize=11, color=INK)
    ax.set_ylabel("$bn")
    ax.legend(frameon=False, loc="upper left")
    fig.tight_layout()
    fig.savefig(OUT / "charts" / "earnings_split.png", dpi=160)
    plt.close(fig)


def value_by_scenario(summary):
    price = summary["share_price"]
    names = ["bear", "base", "bull"]
    vals = [summary["scenarios"][n]["per_share"] for n in names]
    labels = ["Bear", "Base", "Bull"]
    weighted = summary["probability_weighted_value"]
    fig, ax = plt.subplots(figsize=(7, 4))
    bars = ax.bar(labels, vals, color=BLUE, width=0.5)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 6, f"${v:.0f}  ({v / price - 1:+.0%})",
                ha="center", color=INK, fontsize=9)
    ax.axhline(price, color=INK_2, lw=1.2, ls="--")
    ax.text(-0.3, price + 5, f"Current price ${price:.0f}", color=INK_2, fontsize=9, ha="left")
    ax.set_title(f"DCF value per share (probability-weighted ${weighted:.0f})",
                 loc="left", fontsize=11, color=INK)
    ax.set_ylabel("$ per share")
    ax.grid(axis="x", visible=False)
    ax.set_ylim(0, max(vals) * 1.15)
    fig.tight_layout()
    fig.savefig(OUT / "charts" / "value_by_scenario.png", dpi=160)
    plt.close(fig)


def asp_path(cfg):
    rows = project(cfg, "base")
    yrs = [r["year"] for r in rows]
    implied = implied_terminal_asp(cfg)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.plot(yrs, [r["asp_per_w"] * 100 for r in rows], color=BLUE, lw=2, marker="o", ms=6,
            label="Base-case blended ASP")
    refs = [(38.0, "Section 232 minimum import price for modules (before duty)"),
            (36.0, "Recent US bookings (H1 2026, incl. adjusters)"),
            (implied * 100, f"Market-implied 2032 ASP ({implied * 100:.1f}c)"),
            (30.0, "Average price in contracted backlog")]
    for y, txt in refs:
        ax.axhline(y, color=INK_2, lw=0.9, ls=":")
        ax.text(2025.9, y + 0.25, txt, color=INK_2, fontsize=8.5)
    ax.set_title("What the share price assumes about pricing", loc="left", fontsize=11, color=INK)
    ax.set_ylabel("US cents per watt")
    ax.set_ylim(27, 40)
    ax.legend(frameon=False, loc="lower right")
    fig.tight_layout()
    fig.savefig(OUT / "charts" / "asp_path.png", dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    cfg = load_config()
    (OUT / "charts").mkdir(parents=True, exist_ok=True)
    summary = json.loads((OUT / "summary.json").read_text())
    earnings_split(cfg)
    value_by_scenario(summary)
    asp_path(cfg)
    print("charts written to output/charts/")
