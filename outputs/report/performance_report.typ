#set page(paper: "us-letter", margin: (x: 0.62in, y: 0.58in))
#set text(size: 9pt, fill: rgb("#152033"))
#set par(leading: 0.62em, spacing: 0.5em)

#let navy = rgb("#102033")
#let blue = rgb("#2563eb")
#let green = rgb("#059669")
#let amber = rgb("#d97706")
#let red = rgb("#dc2626")
#let border = rgb("#d8dee8")
#let soft = rgb("#f6f8fb")
#let muted = rgb("#64748b")

#let metric(label, value, note, color: blue) = block(fill: soft, stroke: 0.6pt + border, radius: 7pt, inset: 10pt, width: 100%)[
  #text(size: 7.5pt, fill: muted, weight: "bold", label)
  #v(3pt)
  #text(size: 17pt, fill: color, weight: "bold", value)
  #v(2pt)
  #text(size: 7.4pt, fill: muted, note)
]

#let section(title) = [
  #v(8pt)
  #text(size: 13.3pt, weight: "bold", fill: navy, title)
  #v(4pt)
  #line(length: 100%, stroke: 0.7pt + border)
  #v(6pt)
]

#let cell(body, header: false) = table.cell(
  fill: if header { navy } else { none },
  inset: 5pt,
)[#text(size: if header { 7.2pt } else { 6.9pt }, fill: if header { white } else { rgb("#152033") }, weight: if header { "bold" } else { "regular" }, body)]

#align(center)[
  #text(size: 20pt, weight: "bold", fill: navy, "Trading Performance Evidence Report")
  #v(3pt)
  #text(size: 8.6pt, fill: muted, "Closed-trade ledger review with drawdown, concentration, and risk checks")
]

#v(9pt)
#grid(columns: (1fr, 1fr, 1fr, 1fr), gutter: 8pt,
  metric("Trades", "180", "Closed ledger rows", color: blue),
  metric("Net PnL", "USD -314.44", "After costs in ledger", color: green),
  metric("Max DD", "USD -537.89", "Worst equity decline", color: red),
  metric("Sharpe", "-0.82", "Risk-adjusted return", color: amber),
)

#section("Executive Read")
#grid(columns: (1.05fr, 0.95fr), gutter: 12pt,
[
  This report reviews a closed-trade ledger. It is evidence, not a trading signal. The goal is to make performance, concentration, drawdown, and data-quality risks visible before a strategy is marketed or scaled.

  No result here guarantees future profit. The report is designed to surface overfitting, missing costs, and symbol concentration instead of hiding them behind a single equity curve.
],
[
  #image("dashboard.png", width: 100%)
])

#section("Core Metrics")
#table(
  columns: (1fr, 1fr),
  stroke: 0.45pt + border,
  table.header(cell("Metric", header: true), cell("Value", header: true)),
  cell("Total trades"),
  cell("180"),
  cell("Net PnL"),
  cell("USD -314.44"),
  cell("Return"),
  cell("-3.14%"),
  cell("Win rate"),
  cell("47.78%"),
  cell("Profit factor"),
  cell("0.87"),
  cell("Expectancy"),
  cell("USD -1.75"),
  cell("Average win"),
  cell("USD 24.81"),
  cell("Average loss"),
  cell("USD -26.04"),
  cell("Payoff ratio"),
  cell("0.95"),
  cell("Max drawdown"),
  cell("USD -537.89"),
  cell("Max drawdown pct"),
  cell("-5.37%"),
  cell("Sharpe ratio"),
  cell("-0.82"),
  cell("Best trade"),
  cell("USD 109.03"),
  cell("Worst trade"),
  cell("USD -105.62")
)

#section("Evidence Checklist")
#table(
  columns: (1fr, 1fr, 1fr),
  stroke: 0.45pt + border,
  table.header(cell("check", header: true), cell("status", header: true), cell("evidence", header: true)),
  cell("closed_trade_timestamps"),
  cell("pass"),
  cell("All exit timestamps are on or after entry timestamps."),
  cell("minimum_trade_count"),
  cell("pass"),
  cell("180 trades; configured minimum is 30."),
  cell("fee_coverage"),
  cell("pass"),
  cell("100.0% of trades include non-zero fees."),
  cell("symbol_concentration"),
  cell("review"),
  cell("Top symbol AAPL is 100.0% of trades; limit is 50.0%."),
  cell("exit_time_order"),
  cell("pass"),
  cell("Ledger is sorted by exit timestamp."),
  cell("lookahead_boundary"),
  cell("pass"),
  cell("The report summarizes closed trades only and does not train a predictive model; use at least 1 day(s) of embargo for any future..."),
  cell("survivorship_bias"),
  cell("review"),
  cell("1 symbol(s) present. Confirm the source universe includes delisted or failed names when evaluating broad strategies."),
  cell("multiple_testing"),
  cell("review"),
  cell("If this strategy was selected after many variants, report candidate count and walk-forward results before treating the performa...")
)

#pagebreak()

#section("Charts")
#grid(columns: (1fr, 1fr), gutter: 12pt,
[
  #image("equity_curve.png", width: 100%)
  #v(8pt)
  #image("monthly_returns.png", width: 100%)
],
[
  #image("drawdown.png", width: 100%)
  #v(8pt)
  #image("trade_distribution.png", width: 100%)
])

#section("Breakdowns")
#grid(columns: (1fr, 1fr), gutter: 12pt,
[
  #text(weight: "bold", "Symbol Breakdown")
  #v(5pt)
#table(
  columns: (1fr, 1fr, 1fr, 1fr, 1fr),
  stroke: 0.45pt + border,
  table.header(cell("symbol", header: true), cell("trades", header: true), cell("net_pnl", header: true), cell("win_rate", header: true), cell("avg_trade", header: true)),
  cell("AAPL"),
  cell("180"),
  cell("-314.4428"),
  cell("0.4778"),
  cell("-1.7469")
)
],
[
  #text(weight: "bold", "Recent Monthly Returns")
  #v(5pt)
#table(
  columns: (1fr, 1fr, 1fr, 1fr),
  stroke: 0.45pt + border,
  table.header(cell("month", header: true), cell("start_equity", header: true), cell("end_equity", header: true), cell("monthly_return", header: true)),
  cell("2017-04"),
  cell("9780.2135"),
  cell("9728.9913"),
  cell("-0.0052"),
  cell("2017-05"),
  cell("9704.9668"),
  cell("9746.5524"),
  cell("0.0043"),
  cell("2017-06"),
  cell("9745.0090"),
  cell("9689.8917"),
  cell("-0.0057"),
  cell("2017-07"),
  cell("9685.9117"),
  cell("9653.8326"),
  cell("-0.0033"),
  cell("2017-08"),
  cell("9699.4195"),
  cell("9720.0004"),
  cell("0.0021"),
  cell("2017-09"),
  cell("9745.7108"),
  cell("9762.3190"),
  cell("0.0017"),
  cell("2017-10"),
  cell("9740.1650"),
  cell("9743.3926"),
  cell("0.0003"),
  cell("2017-11"),
  cell("9788.0581"),
  cell("9780.1949"),
  cell("-0.0008"),
  cell("2017-12"),
  cell("9759.8763"),
  cell("9707.1188"),
  cell("-0.0054"),
  cell("2018-01"),
  cell("9720.8627"),
  cell("9685.5572"),
  cell("-0.0036")
)
])

#section("Limitations")
Backtest and trade-log performance can be affected by fees, slippage, survivorship bias, missing trades, overfitting, and market regime changes. A strong report should make those risks visible instead of hiding them.
