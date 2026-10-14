"""First Solar (FSLR) long thesis: scenario model and DCF.

The model splits First Solar's earnings into two streams:

* **Core**: module revenue minus cost of sales, opex and tax. This is what the
  manufacturing business earns on its own.
* **45X**: the US advanced-manufacturing production credit, booked as a
  reduction in cost of sales. It is worth ~$0.167 per watt of US output and
  phases down from 2030 to zero in 2033.

The bear argument on First Solar is that almost all of today's profit is 45X.
The bull argument is that new contracts signed under the Section 232 import
floor rebuild core margin before the credit runs out. The model makes that
debate explicit: it values the two streams separately and asks what long-run
selling price the current share price implies.

Run:  python -m src.model          (from the repo root)
"""
from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "config" / "assumptions.yml"
OUT = ROOT / "output"


def load_config(path: Path = CONFIG) -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


@dataclass
class Valuation:
    scenario: str
    pv_core_fcf: float        # PV of core free cash flow, 2027-2032
    pv_45x: float             # PV of 45X cash, 2027-2032
    pv_terminal: float        # PV of core terminal value (from 2033)
    net_cash: float
    equity_value: float
    per_share: float
    upside: float


def project(cfg: dict, name: str, asp_override: list[float] | None = None) -> list[dict]:
    """Year-by-year P&L and cash flow for one scenario ($bn unless stated)."""
    s = cfg["scenarios"][name]
    v = cfg["valuation"]
    c45 = cfg["credit_45x"]
    shares = cfg["market"]["diluted_shares_m"] / 1000  # bn shares
    asp_path = asp_override or s["asp"]
    rows, prev_rev = [], None
    for i, yr in enumerate(cfg["years"]):
        vol = s["volume_gw"][i]
        asp = asp_path[i]
        cost = s["cost_per_w"][i]
        revenue = vol * asp                      # GW x $/W = $bn
        core_gp = vol * (asp - cost)
        us_gw = vol * s["us_share"][i]
        credit = us_gw * c45["per_watt_full"] * c45["phase"].get(yr, 0.0)
        core_ebit = core_gp - s["opex"][i]
        core_nopat = core_ebit * (1 - v["tax_rate"])
        net_income = core_nopat + credit         # excludes interest income
        d_nwc = 0.0 if prev_rev is None else v["nwc_pct_of_revenue_change"] * (revenue - prev_rev)
        core_fcf = core_nopat + s["d_and_a"][i] - s["capex"][i] - d_nwc
        credit_cash = credit * (1 - v["credit_transfer_discount"])
        rows.append({
            "year": yr,
            "volume_gw": vol,
            "us_volume_gw": round(us_gw, 3),
            "asp_per_w": asp,
            "cost_per_w": cost,
            "revenue": revenue,
            "core_gross_profit": core_gp,
            "credit_45x": credit,
            "gross_profit_reported": core_gp + credit,
            "gross_margin_reported": (core_gp + credit) / revenue,
            "core_gross_margin": core_gp / revenue,
            "opex": s["opex"][i],
            "core_ebit": core_ebit,
            "operating_income": core_ebit + credit,
            "credit_share_of_operating_income": credit / (core_ebit + credit) if core_ebit + credit > 0 else float("nan"),
            "net_income": net_income,
            "eps": net_income / shares,
            "core_eps": core_nopat / shares,
            "core_fcf": core_fcf,
            "credit_45x_cash": credit_cash,
            "total_fcf": core_fcf + credit_cash,
        })
        prev_rev = revenue
    return rows


def value(cfg: dict, name: str, asp_override: list[float] | None = None,
          wacc: float | None = None) -> Valuation:
    """DCF as at 31 Dec 2026: discount 2027-2032 cash flows plus core terminal value."""
    v = cfg["valuation"]
    r = wacc if wacc is not None else v["wacc"]
    g = v["terminal_growth"]
    rows = project(cfg, name, asp_override)
    forecast = [row for row in rows if row["year"] >= 2027]
    pv_core = pv_45x = 0.0
    for t, row in enumerate(forecast, start=1):
        df = (1 + r) ** -t
        pv_core += row["core_fcf"] * df
        pv_45x += row["credit_45x_cash"] * df
    last = forecast[-1]
    # Terminal: steady-state core cash flow, capex = D&A, no 45X.
    # Floored at zero: a business that cannot earn a profit without 45X would
    # cut capacity rather than run at a loss forever.
    terminal_fcf = max(last["core_ebit"], 0.0) * (1 - v["tax_rate"]) * (1 + g)
    tv = terminal_fcf / (r - g)
    pv_tv = tv * (1 + r) ** -len(forecast)
    net_cash = cfg["market"]["net_cash_ye2026"]
    equity = pv_core + pv_45x + pv_tv + net_cash
    per_share = equity / (cfg["market"]["diluted_shares_m"] / 1000)
    return Valuation(name, pv_core, pv_45x, pv_tv, net_cash, equity, per_share,
                     per_share / cfg["market"]["share_price"] - 1)


def scaled_asp_path(cfg: dict, terminal_asp: float, name: str = "base") -> list[float]:
    """Keep the scenario's shape but rescale it so 2032 ASP hits `terminal_asp`."""
    path = cfg["scenarios"][name]["asp"]
    start, end = path[0], path[-1]
    k = (terminal_asp - start) / (end - start)
    return [start + (p - start) * k for p in path]


def implied_terminal_asp(cfg: dict, name: str = "base") -> float:
    """Long-run ASP at which the base-case DCF equals today's share price (bisection)."""
    target = cfg["market"]["share_price"]
    lo, hi = 0.20, 0.50
    for _ in range(60):
        mid = (lo + hi) / 2
        if value(cfg, name, scaled_asp_path(cfg, mid, name)).per_share > target:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


def sensitivity(cfg: dict) -> tuple[list[float], list[float], list[list[float]]]:
    """Base-case value per share across 2032 ASP and WACC."""
    asps = [0.30, 0.32, 0.34, 0.36, 0.38, 0.40]
    waccs = [0.09, 0.10, 0.11, 0.12]
    grid = [[value(cfg, "base", scaled_asp_path(cfg, a), w).per_share for a in asps] for w in waccs]
    return asps, waccs, grid


def write_outputs(cfg: dict) -> dict:
    OUT.mkdir(exist_ok=True)
    results = {}
    for name in ("bear", "base", "bull"):
        rows = project(cfg, name)
        with open(OUT / f"projection_{name}.csv", "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0]))
            w.writeheader()
            for row in rows:
                w.writerow({k: (round(x, 4) if isinstance(x, float) else x) for k, x in row.items()})
        results[name] = value(cfg, name)

    weights = cfg["valuation"]["scenario_weights"]
    weighted = sum(results[n].per_share * w for n, w in weights.items())
    implied = implied_terminal_asp(cfg)
    asps, waccs, grid = sensitivity(cfg)

    summary = {
        "share_price": cfg["market"]["share_price"],
        "scenarios": {n: {k: round(x, 3) if isinstance(x, float) else x
                          for k, x in vars(val).items()} for n, val in results.items()},
        "probability_weighted_value": round(weighted, 1),
        "probability_weighted_upside": round(weighted / cfg["market"]["share_price"] - 1, 3),
        "market_implied_2032_asp": round(implied, 4),
        "sensitivity": {"asp_2032": asps, "wacc": waccs,
                        "value_per_share": [[round(x, 1) for x in r] for r in grid]},
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    cfg = load_config()
    s = write_outputs(cfg)
    price = s["share_price"]
    print(f"Share price: ${price:.0f}")
    for n in ("bear", "base", "bull"):
        v = s["scenarios"][n]
        print(f"  {n:<5} ${v['per_share']:>6.0f}  ({v['upside']:+.0%})  "
              f"core FCF {v['pv_core_fcf']:.1f} | 45X {v['pv_45x']:.1f} | TV {v['pv_terminal']:.1f} | cash {v['net_cash']:.1f}")
    print(f"Probability-weighted: ${s['probability_weighted_value']:.0f} ({s['probability_weighted_upside']:+.0%})")
    print(f"Market-implied 2032 ASP: ${s['market_implied_2032_asp']:.3f}/W")
