# First Solar (FSLR): Long

**Price $186 (13 Oct 2026) · Base-case value $238 (+28%) · Probability-weighted $224 (+20%)**

Most of First Solar's profit today comes from a tax credit, and the market
prices the stock as if that profit disappears when the credit phases out in
2030–32. This model separates the two earnings streams and argues that new
contracts signed under the Section 232 import floor rebuild the core business
before the credit runs out.

The full written pitch is in [`pitch.pdf`](pitch.pdf).

![Earnings split](output/charts/earnings_split.png)

## The thesis in three points

1. **The market is pricing the 45X cliff, not the repricing.** On 2026
   guidance, the Section 45X manufacturing credit ($2.10–2.19bn) is about 86%
   of gross profit, and the business makes a small operating loss without it.
   The credit steps down from 2030 and ends after 2032. At $186 the market
   values everything except the 45X stream and net cash at about $9bn.
2. **Contracted pricing is about to reset upwards.** The 45.1 GW backlog is
   worth about $13.6bn, or roughly $0.30/W. Recent US bookings came in at about
   $0.36/W, and from 4 December 2026 imported modules face a $0.38/W minimum
   import price plus duty under Section 232. As old contracts roll off, blended
   selling prices should rise towards the level of new bookings.
3. **The share price only needs modest repricing to work.** The current price
   implies a 2032 blended selling price of about $0.325/W: above the backlog
   average but below what First Solar is already signing in the US.

![ASP path](output/charts/asp_path.png)

## Valuation

DCF as at 31 Dec 2026: core free cash flow and 45X cash for 2027–32 are
discounted at 10%, plus a terminal value on core earnings only (2% growth, no
45X).

| Scenario | 2032 ASP | Value / share | vs price |
|---|---:|---:|---:|
| Bear (25%) | $0.280/W | $82 | −56% |
| Base (50%) | $0.360/W | $238 | +28% |
| Bull (25%) | $0.390/W | $337 | +81% |
| **Probability-weighted** | | **$224** | **+20%** |

![Value by scenario](output/charts/value_by_scenario.png)

**Base-case sensitivity: value per share by 2032 ASP and WACC**

| WACC \ 2032 ASP | $0.30 | $0.32 | $0.34 | $0.36 | $0.38 | $0.40 |
|---|---:|---:|---:|---:|---:|---:|
| 9% | 158 | 193 | 228 | 263 | 298 | 333 |
| 10% | 148 | 178 | 208 | **238** | 268 | 299 |
| 11% | 139 | 166 | 192 | 219 | 245 | 272 |
| 12% | 132 | 156 | 179 | 203 | 226 | 250 |

**Calibration check:** the base case reproduces 2026 guidance (net sales
$5.05bn, gross profit $2.50bn, 45X $2.15bn), and its 2027 EPS of $24.4 sits
within 1% of the $24.30 consensus.

## What would make me wrong

- **Section 232 is diluted, delayed or challenged.** Then imports set the price
  again and the repricing never comes. This is the bear case.
- **Bookings stay weak.** H1 2026 bookings were 2.8 GW against 7.6 GW sold, and
  management says some customers are waiting for policy clarity. If the backlog
  keeps shrinking, volume falls before price rises.
- **45X is cut early.** The phase-down is statutory, but it is a political
  target. Ending the credit after 2028 would cost about $44 a share in the base
  case.
- **Securities litigation.** A class action over earlier tariff disclosures
  (E.D.N.Y. 26-cv-03787, class period Feb 2025 to Feb 2026) is at an early
  stage. It is a cost and headline risk, not a threat to the business model.

## Catalysts

- **Q3 2026 results** (late October). Bookings volume and price are the numbers
  to watch.
- **4 December 2026:** Section 232 minimum import prices and duties take effect.
- **Contract announcements in 2027** that show where new US prices are clearing.
- **Mid-2027:** phase 2 of the South Carolina finishing facility, which raises
  the US share of output and so the 45X earned per GW.

## How the model works

```
config/assumptions.yml   every input, by scenario, with sources in comments
src/model.py             projections, DCF, implied-ASP solver, sensitivity
src/charts.py            the charts above
tests/test_model.py      checks the 2026 calibration and the solver
output/                  projection CSVs per scenario, summary.json, charts
```

```bash
pip install -r requirements.txt
python -m src.model     # prints valuations, writes output/
python -m src.charts    # redraws charts
python -m pytest -q
```

Earnings are split into **core** (revenue − cost of sales − opex, taxed at 21%)
and **45X** (US output × ~$0.167/W × the statutory phase-down, untaxed and sold
at a 4% discount). The $0.167/W is calibrated from guidance: $2.10–2.19bn of
credits on 12.6–13.1 GW of US production. The terminal value is floored at zero,
because a business that cannot profit without 45X would cut capacity rather
than lose money indefinitely.

**Simplifications:** interest income, the India business's separate economics,
and quarterly timing are ignored. 2026 cost per watt includes about $0.016/W of
one-off underutilisation, start-up and tariff costs, which fall away from 2027.

## Sources

- First Solar Q2 2026 results and 8-K (30 July 2026): guidance, balance sheet, backlog
- First Solar Q2 2026 earnings presentation: backlog value, bookings and pricing ([Investing.com summary](https://www.investing.com/news/company-news/first-solar-q2-2026-slides-show-57-margin-136b-backlog-93CH-4826361))
- Section 232 proclamation on polysilicon and derivatives, effective 4 Dec 2026 ([Hunton](https://www.hunton.com/insights/legal/us-imposes-new-tariffs-and-minimum-import-prices-on-polysilicon-and-solar-products))
- Section 45X rates and phase-down ([Beancount summary](https://beancount.io/blog/2026/05/12/section-45x-advanced-manufacturing-production-credit-obbba-battery-solar-critical-minerals-per-unit-2026-phase-out-guide))
- Consensus estimates ([Barchart via inkl](https://www.inkl.com/news/earnings-preview-what-to-expect-from-first-solars-report)) and valuation context ([TIKR](https://www.tikr.com/blog/first-solar-has-lost-43-from-its-june-high-goldman-sachs-sees-51-upside))
- Class action details ([pv magazine USA](https://pv-magazine-usa.com/2026/06/29/first-solar-hits-legal-headwinds-as-shareholders-file-tariff-related-class-action/))
- US market data ([SEIA Solar Market Insight Q3 2026](https://seia.org/research-resources/solar-market-insight-report-q3-2026/))

*Personal research for educational purposes. Not investment advice.*
