# User Manual · Academic FX Investment Simulator

This manual is intended for people with no previous investment or foreign-exchange knowledge.

> **Important:** this is an educational simulator. It does not trade real money, does not use leverage, and is not financial advice. ECB rates are informational reference rates, not executable trading prices.

## 1. What does the simulator do?

It compares four approaches to a currency portfolio:

- **Technical agent:** follows mechanical EMA, RSI and MACD rules.
- **Holders:** convert the initial capital into one currency and hold it.
- **Random agents:** make random decisions and act as a control group.
- **Human investors:** decisions made by people can be imported through CSV.

The program performs a **backtest**: it applies these decisions to historical data to see what would have happened. It does not predict the future.

## 2. Basic concepts

**Currency:** a monetary unit such as EUR, USD, GBP, JPY or CHF.

**Exchange rate:** the value of one currency expressed in another. For example, USD/EUR is the value of one US dollar in euros.

**Reference currency:** the currency in which the entire portfolio is valued. If EUR is selected, initial capital, final capital and all positions are expressed in euros.

**CASH:** capital that remains in the reference currency instead of being converted into a selected foreign currency.

## 3. Data source: ECB

The simulator uses daily foreign-exchange reference rates published by the European Central Bank.

The ECB publishes how many units of each foreign currency equal one euro. If a different portfolio reference currency is selected, the simulator derives a **cross rate**.

Hypothetical example:

- 1 EUR = 1.15 USD
- 1 EUR = 0.86 GBP

Then:

**1 GBP ≈ 1.15 / 0.86 = 1.337 USD**

ECB rates are useful for transparent, reproducible academic comparisons, but they do not exactly reproduce broker spreads, slippage, swaps, interest or intraday prices.

## 4. Market and portfolio

### Reference currency

Choose the currency in which the whole portfolio will be measured. EUR is the simplest option for a first test.

### Currencies

Choose the currencies into which the agent may convert part of the portfolio, for example USD, GBP, JPY or CHF.

### Initial capital

Virtual starting capital shared by all comparison groups.

### Conversion cost

A simplified percentage cost for changing currency. It is not intended to match a specific broker fee exactly.

### Dates

These define the backtest period. Earlier observations are also used internally so that EMA, RSI and MACD are available from the start of the evaluation period.

## 5. EMA

EMA means **Exponential Moving Average**.

The simulator compares a short EMA with a long EMA. If EMA20 > EMA50, for example, the rule treats the recent trend as being above the longer-term trend and awards its configured points.

This does not guarantee that the exchange rate will keep rising.

## 6. RSI

RSI means **Relative Strength Index** and ranges from 0 to 100.

If RSI(14) is configured between 50 and 70, the rule awards points while the value remains inside that interval.

## 7. MACD

MACD means **Moving Average Convergence Divergence**.

The simulator awards points when the MACD line is above its signal line. This is a trend/momentum rule, not a forecast.

## 8. Minimum score

Each rule contributes points. A currency is eligible only if its total reaches the configured minimum score.

A higher threshold makes the agent more selective.

## 9. Maximum weight per currency

This limits portfolio concentration.

With 10,000 EUR and a 40% maximum weight, no currency can initially receive more than 4,000 EUR of portfolio value at a rebalance. The remainder may stay in CASH.

## 10. Rebalancing

A rebalance changes portfolio composition.

Example:

- before: USD 40%, GBP 40%, CASH 20%
- after: JPY 40%, CHF 40%, CASH 20%

These changes generate the configured conversion cost.

## 11. Holders

Each holder converts the starting capital into one currency and keeps it until the end.

This provides a passive benchmark for the technical strategy.

## 12. Random agents

Random agents do not use EMA, RSI or MACD.

At each decision date they randomly choose how many currencies to hold and which ones, subject to the same maximum-weight rule as the technical agent.

The simulator can run from 100 to 10,000 random agents.

Decision intervals are every 1, 5, 10 or 20 sessions. With working-day data, 5 sessions is roughly one week and 20 roughly one month.

## 13. Results

**Final capital:** final portfolio value.

**Return:** percentage change in capital.

**Maximum drawdown:** largest decline from a previous portfolio high.

**Volatility:** intensity of return fluctuations. This simulator annualizes daily volatility using 252 sessions.

**Sharpe ratio:** relates return to volatility. It is not a universal grade or a guarantee.

**Rebalances:** number of portfolio changes.

**Percentile:** the technical agent's relative position against the random-agent distribution. A 90th percentile result means it finished above about 90% of the random agents in that experiment; it does not mean a 90% probability of future profit.

## 14. Charts

The **histogram** shows the distribution of random-agent returns and the technical agent's position.

The **technical agent vs holders** chart shows the full path of cumulative return, not only the final result.

## 15. Human investors

The CSV has three columns:

| Column | Meaning |
|---|---|
| participant | Name or code |
| date | Decision date |
| choice | Currency ticker or CASH |

Example:

```csv
participant,date,choice
Person 1,2026-01-02,USD
Person 1,2026-02-02,GBP
Person 1,2026-03-02,CASH
```

The latest decision remains active until a new one is entered.

## 16. Simple learning configuration

| Parameter | Example |
|---|---|
| Reference | EUR |
| Currencies | USD, GBP, JPY, CHF |
| Capital | 10,000 EUR |
| Conversion cost | 0.10% |
| Period | 2 years |
| EMA/RSI/MACD | enabled |
| Holders | USD, GBP, JPY |
| Random agents | 1,000 |
| Random decisions | every 5 sessions |

This is only a teaching example, not an investment recommendation.

## 17. What is not simulated?

Version 0.1.0 does not include:

- leverage;
- short selling;
- margin;
- CFDs or futures;
- variable spreads;
- slippage;
- swaps;
- interest;
- intraday orders.

This simplicity is deliberate so that the academic comparison remains transparent.

## 18. Common interpretation mistakes

**“It made money, therefore it works.”** Not necessarily: compare it with controls and risk.

**“It beat random agents, therefore it always will.”** No: the result applies only to that period and configuration.

**“I can keep tuning parameters until the result looks good.”** Doing this after looking at the test data can create **overfitting**.

## 19. For academic research

Before the main test, freeze and document:

1. simulator version;
2. reference currency;
3. selected currencies;
4. dates;
5. initial capital;
6. conversion cost;
7. EMA, RSI and MACD settings;
8. minimum score;
9. maximum weight;
10. holders;
11. number of random agents;
12. random decision interval.

If rules are changed after observing the result, treat them as a new strategy and test them on another period.

**Manual version:** Academic FX Investment Simulator v0.1.0.
