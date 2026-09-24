from __future__ import annotations

from dataclasses import dataclass
from io import BytesIO
from typing import Dict, Iterable, List, Mapping, Optional, Sequence, Tuple
from urllib.request import Request, urlopen

import numpy as np
import pandas as pd


DEFAULT_RULES = {
    "ema_enabled": True,
    "ema_fast": 20,
    "ema_slow": 50,
    "ema_points": 1,
    "rsi_enabled": True,
    "rsi_period": 14,
    "rsi_min": 50.0,
    "rsi_max": 70.0,
    "rsi_points": 1,
    "macd_enabled": True,
    "macd_fast": 12,
    "macd_slow": 26,
    "macd_signal": 9,
    "macd_points": 1,
    "min_score": 2,
    "max_weight": 0.40,
}

ECB_HISTORY_URL = "https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.csv"

# Current currencies published in the ECB euro foreign-exchange reference-rate table.
# EUR is added separately because the ECB series use EUR as the common base.
ECB_CURRENCIES = [
    "USD", "JPY", "CZK", "DKK", "GBP", "HUF", "PLN", "RON", "SEK", "CHF",
    "ISK", "NOK", "TRY", "AUD", "BRL", "CAD", "CNY", "HKD", "IDR", "ILS",
    "INR", "KRW", "MXN", "MYR", "NZD", "PHP", "SGD", "THB", "ZAR",
]

PREFERRED_CURRENCIES = ["EUR", "USD", "GBP", "JPY", "CHF", "CAD", "AUD", "SEK", "NOK", "DKK"]


@dataclass
class BacktestResult:
    equity: pd.Series
    trades: pd.DataFrame
    signals: pd.DataFrame
    metrics: Dict[str, float]


def available_reference_currencies() -> List[str]:
    """Currencies that can be used as the portfolio/reference currency."""
    ordered = PREFERRED_CURRENCIES + [c for c in ECB_CURRENCIES if c not in PREFERRED_CURRENCIES]
    return ordered


def list_fx_markets(reference_currency: str = "EUR") -> List[str]:
    """Return all available currency holdings expressed in the selected reference currency.

    A symbol such as USD/EUR means: the value of one US dollar expressed in euros.
    Cross rates are derived from the ECB's euro reference-rate table.
    """
    reference = reference_currency.upper().strip()
    supported = {"EUR", *ECB_CURRENCIES}
    if reference not in supported:
        raise ValueError(f"Divisa de referència no suportada: {reference}")

    preferred_assets = ["USD", "GBP", "JPY", "CHF", "EUR", "CAD", "AUD"]
    assets = [c for c in ["EUR", *ECB_CURRENCIES] if c != reference]
    assets.sort(key=lambda c: (preferred_assets.index(c) if c in preferred_assets else 99, c))
    return [f"{asset}/{reference}" for asset in assets]


def validate_rules(rules: Mapping[str, object]) -> None:
    enabled = [
        bool(rules.get("ema_enabled")),
        bool(rules.get("rsi_enabled")),
        bool(rules.get("macd_enabled")),
    ]
    if not any(enabled):
        raise ValueError("Activa almenys una regla tècnica.")
    if int(rules["ema_fast"]) >= int(rules["ema_slow"]):
        raise ValueError("A la regla EMA, el període curt ha de ser inferior al període llarg.")
    if float(rules["rsi_min"]) >= float(rules["rsi_max"]):
        raise ValueError("A la regla RSI, el límit inferior ha de ser menor que el superior.")
    if int(rules["macd_fast"]) >= int(rules["macd_slow"]):
        raise ValueError("Al MACD, la mitjana ràpida ha de tenir un període inferior a la lenta.")
    max_score = sum(
        int(rules[k])
        for enabled_key, k in [
            ("ema_enabled", "ema_points"),
            ("rsi_enabled", "rsi_points"),
            ("macd_enabled", "macd_points"),
        ]
        if bool(rules.get(enabled_key))
    )
    if int(rules["min_score"]) < 1 or int(rules["min_score"]) > max_score:
        raise ValueError(f"La puntuació mínima ha d'estar entre 1 i {max_score}.")
    if not 0 < float(rules["max_weight"]) <= 1:
        raise ValueError("El pes màxim per actiu ha d'estar entre 0% i 100%.")


def warmup_bars(rules: Mapping[str, object]) -> int:
    """Conservative number of daily observations required before evaluation."""
    periods = [5]
    if bool(rules.get("ema_enabled")):
        periods.append(int(rules["ema_slow"]))
    if bool(rules.get("rsi_enabled")):
        periods.append(int(rules["rsi_period"]) + 2)
    if bool(rules.get("macd_enabled")):
        periods.append(int(rules["macd_slow"]) + int(rules["macd_signal"]))
    return max(periods) + 5


def indicators(df: pd.DataFrame, rules: Optional[Mapping[str, object]] = None) -> pd.DataFrame:
    """Calculate editable indicators and the agent score."""
    rules = dict(DEFAULT_RULES if rules is None else rules)
    validate_rules(rules)

    out = df.copy().sort_index()
    close = out["close"].astype(float)
    score = pd.Series(0, index=out.index, dtype=int)

    ema_fast = int(rules["ema_fast"])
    ema_slow = int(rules["ema_slow"])
    out["ema_fast"] = close.ewm(span=ema_fast, adjust=False).mean()
    out["ema_slow"] = close.ewm(span=ema_slow, adjust=False).mean()
    if bool(rules["ema_enabled"]):
        score += (out["ema_fast"] > out["ema_slow"]).astype(int) * int(rules["ema_points"])

    rsi_period = int(rules["rsi_period"])
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / rsi_period, adjust=False, min_periods=rsi_period).mean()
    avg_loss = loss.ewm(alpha=1 / rsi_period, adjust=False, min_periods=rsi_period).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    out["rsi"] = 100 - (100 / (1 + rs))
    out.loc[(avg_loss == 0) & (avg_gain > 0), "rsi"] = 100
    if bool(rules["rsi_enabled"]):
        rsi_ok = (out["rsi"] >= float(rules["rsi_min"])) & (out["rsi"] <= float(rules["rsi_max"]))
        score += rsi_ok.astype(int) * int(rules["rsi_points"])

    macd_fast = int(rules["macd_fast"])
    macd_slow = int(rules["macd_slow"])
    macd_signal = int(rules["macd_signal"])
    ema_m_fast = close.ewm(span=macd_fast, adjust=False).mean()
    ema_m_slow = close.ewm(span=macd_slow, adjust=False).mean()
    out["macd"] = ema_m_fast - ema_m_slow
    out["macd_signal"] = out["macd"].ewm(span=macd_signal, adjust=False).mean()
    if bool(rules["macd_enabled"]):
        score += (out["macd"] > out["macd_signal"]).astype(int) * int(rules["macd_points"])

    out["score"] = score
    return out


def _download_ecb_history() -> pd.DataFrame:
    """Download and parse the ECB historical euro reference-rate CSV."""
    request = Request(
        ECB_HISTORY_URL,
        headers={"User-Agent": "Academic-FX-Investment-Simulator/0.1 (+educational research)"},
    )
    with urlopen(request, timeout=30) as response:
        payload = response.read()

    df = pd.read_csv(BytesIO(payload), na_values=["N/A", ""])
    df.columns = [str(c).strip() for c in df.columns]
    date_col = "Date" if "Date" in df.columns else df.columns[0]
    df[date_col] = pd.to_datetime(df[date_col], errors="coerce")
    df = df.dropna(subset=[date_col]).set_index(date_col).sort_index()
    for col in df.columns:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def _ecb_units_per_euro(history: pd.DataFrame, currency: str) -> pd.Series:
    currency = currency.upper().strip()
    if currency == "EUR":
        return pd.Series(1.0, index=history.index, name="EUR")
    if currency not in history.columns:
        raise ValueError(f"L'ECB no ofereix una sèrie històrica per a {currency}.")
    return history[currency].astype(float)


def fetch_market_data(
    reference_currency: str,
    symbols: Iterable[str],
    start: pd.Timestamp,
    end: pd.Timestamp,
    timeframe: str = "1d",
    rules: Optional[Mapping[str, object]] = None,
) -> Dict[str, pd.DataFrame]:
    """Fetch ECB daily reference rates and derive currency cross rates.

    ECB series are quoted as units of foreign currency per euro. For an asset currency A
    and portfolio/reference currency R, the simulator values one unit of A in R as:

        price(A in R) = ECB(R per EUR) / ECB(A per EUR)

    The ECB publishes one reference observation per working day; therefore this simulator
    uses daily reference rates, not intraday OHLC prices.
    """
    del timeframe  # kept for API compatibility with the crypto simulator

    reference = reference_currency.upper().strip()
    start = pd.Timestamp(start).tz_localize(None) if pd.Timestamp(start).tzinfo is not None else pd.Timestamp(start)
    end = pd.Timestamp(end).tz_localize(None) if pd.Timestamp(end).tzinfo is not None else pd.Timestamp(end)

    history = _download_ecb_history()
    history = history.loc[(history.index >= start) & (history.index <= end)]
    if history.empty:
        raise RuntimeError("L'ECB no ha retornat dades dins del període seleccionat.")

    ref_per_eur = _ecb_units_per_euro(history, reference)
    result: Dict[str, pd.DataFrame] = {}
    errors: List[str] = []

    for symbol in symbols:
        try:
            asset, symbol_reference = symbol.upper().split("/", 1)
        except ValueError:
            errors.append(f"{symbol}: format de parell no vàlid")
            continue

        if symbol_reference != reference:
            errors.append(f"{symbol}: la divisa de referència no coincideix amb {reference}")
            continue
        if asset == reference:
            errors.append(f"{symbol}: actiu i divisa de referència són iguals")
            continue

        try:
            asset_per_eur = _ecb_units_per_euro(history, asset)
            close = (ref_per_eur / asset_per_eur).replace([np.inf, -np.inf], np.nan).dropna()
        except Exception as exc:
            errors.append(f"{symbol}: {exc}")
            continue

        if close.empty:
            errors.append(f"{symbol}: sense dades comunes")
            continue

        # ECB reference rates supply one daily reference value rather than tradable OHLCV.
        # We preserve the familiar DataFrame schema while indicators use only "close".
        df = pd.DataFrame(index=close.index)
        df["open"] = close
        df["high"] = close
        df["low"] = close
        df["close"] = close
        df["volume"] = np.nan
        result[symbol] = indicators(df, rules)

    if not result:
        detail = "; ".join(errors[:5])
        raise RuntimeError(f"No s'han pogut obtenir dades de les divises seleccionades. {detail}")
    return result


def _common_dates(
    data: Dict[str, pd.DataFrame],
    evaluation_start: Optional[pd.Timestamp] = None,
    evaluation_end: Optional[pd.Timestamp] = None,
) -> pd.DatetimeIndex:
    idx = None
    for df in data.values():
        idx = df.index if idx is None else idx.intersection(df.index)
    if idx is None or len(idx) == 0:
        raise ValueError("No hi ha dates comunes entre els actius.")
    idx = idx.sort_values()
    if evaluation_start is not None:
        start = pd.Timestamp(evaluation_start)
        if start.tzinfo is not None:
            start = start.tz_convert(None)
        idx = idx[idx >= start]
    if evaluation_end is not None:
        end = pd.Timestamp(evaluation_end)
        if end.tzinfo is not None:
            end = end.tz_convert(None)
        idx = idx[idx <= end]
    if len(idx) == 0:
        raise ValueError("No hi ha dades comunes dins del període d'avaluació.")
    return idx


def target_weights(
    scores: Dict[str, int],
    min_score: int = 2,
    max_weight: float = 0.40,
) -> Dict[str, float]:
    eligible = [s for s, score in scores.items() if score >= min_score]
    if not eligible:
        return {s: 0.0 for s in scores}
    equal = min(1.0 / len(eligible), max_weight)
    return {s: (equal if s in eligible else 0.0) for s in scores}


def run_agent_backtest(
    data: Dict[str, pd.DataFrame],
    initial_capital: float = 10000.0,
    commission: float = 0.001,
    rules: Optional[Mapping[str, object]] = None,
    evaluation_start: Optional[pd.Timestamp] = None,
    evaluation_end: Optional[pd.Timestamp] = None,
) -> BacktestResult:
    rules = dict(DEFAULT_RULES if rules is None else rules)
    validate_rules(rules)
    symbols = list(data)
    dates = _common_dates(data, evaluation_start, evaluation_end)
    if len(dates) < 5:
        raise ValueError("Període massa curt per executar el backtest.")

    cash = float(initial_capital)
    units = {s: 0.0 for s in symbols}
    previous_weights = {s: 0.0 for s in symbols}
    trades: List[dict] = []
    equity_rows: List[Tuple[pd.Timestamp, float]] = []
    signal_rows: List[dict] = []

    for date in dates:
        prices = {s: float(data[s].loc[date, "close"]) for s in symbols}
        scores = {s: int(data[s].loc[date, "score"]) for s in symbols}
        desired = target_weights(
            scores,
            min_score=int(rules["min_score"]),
            max_weight=float(rules["max_weight"]),
        )

        portfolio_value = cash + sum(units[s] * prices[s] for s in symbols)

        if any(abs(desired[s] - previous_weights[s]) > 1e-12 for s in symbols):
            current_values = {s: units[s] * prices[s] for s in symbols}
            target_values = {s: portfolio_value * desired[s] for s in symbols}
            traded_notional = sum(abs(target_values[s] - current_values[s]) for s in symbols)
            fee = traded_notional * commission
            investable = max(portfolio_value - fee, 0.0)
            target_values = {s: investable * desired[s] for s in symbols}
            units = {s: (target_values[s] / prices[s] if prices[s] > 0 else 0.0) for s in symbols}
            cash = investable - sum(target_values.values())

            trades.append(
                {
                    "date": date,
                    "portfolio_before": portfolio_value,
                    "conversion_cost": fee,
                    **{f"weight_{_base(s)}": desired[s] for s in symbols},
                    **{f"score_{_base(s)}": scores[s] for s in symbols},
                }
            )
            previous_weights = desired.copy()

        value = cash + sum(units[s] * prices[s] for s in symbols)
        equity_rows.append((date, value))
        signal_rows.append(
            {
                "date": date,
                **{f"score_{_base(s)}": scores[s] for s in symbols},
                **{f"rate_{_base(s)}": prices[s] for s in symbols},
            }
        )

    equity = pd.Series(dict(equity_rows), name="Agent tècnic").sort_index()
    metrics = calculate_metrics(equity, initial_capital)
    metrics["trades"] = float(len(trades))
    metrics["fees"] = float(sum(t["conversion_cost"] for t in trades))
    return BacktestResult(
        equity=equity,
        trades=pd.DataFrame(trades),
        signals=pd.DataFrame(signal_rows).set_index("date"),
        metrics=metrics,
    )


def calculate_metrics(equity: pd.Series, initial_capital: float) -> Dict[str, float]:
    equity = equity.dropna().astype(float)
    if equity.empty:
        return {}
    daily = equity.pct_change().dropna()
    total_return = equity.iloc[-1] / initial_capital - 1
    running_max = equity.cummax()
    drawdown = equity / running_max - 1
    annual_vol = daily.std(ddof=1) * np.sqrt(252) if len(daily) > 1 else np.nan
    days = max((equity.index[-1] - equity.index[0]).days, 1)
    annual_return = (equity.iloc[-1] / max(initial_capital, 1e-12)) ** (365 / days) - 1
    sharpe = (daily.mean() / daily.std(ddof=1) * np.sqrt(252)) if len(daily) > 1 and daily.std(ddof=1) > 0 else np.nan
    return {
        "final_value": float(equity.iloc[-1]),
        "total_return": float(total_return),
        "max_drawdown": float(drawdown.min()),
        "annual_volatility": float(annual_vol) if pd.notna(annual_vol) else np.nan,
        "annual_return": float(annual_return),
        "sharpe": float(sharpe) if pd.notna(sharpe) else np.nan,
    }


def hodl_equity(
    data: Dict[str, pd.DataFrame],
    initial_capital: float,
    commission: float = 0.001,
    symbols: Optional[Sequence[str]] = None,
    evaluation_start: Optional[pd.Timestamp] = None,
    evaluation_end: Optional[pd.Timestamp] = None,
) -> Dict[str, pd.Series]:
    symbols = list(symbols if symbols is not None else data.keys())
    missing = [s for s in symbols if s not in data]
    if missing:
        raise ValueError(f"No hi ha dades per als holders: {', '.join(missing)}")

    dates = _common_dates(data, evaluation_start, evaluation_end)
    out: Dict[str, pd.Series] = {}
    for symbol in symbols:
        px = data[symbol].loc[dates, "close"].astype(float)
        capital_after_fee = initial_capital * (1 - commission)
        units = capital_after_fee / px.iloc[0]
        name = f"HODL {_base(symbol)}"
        out[name] = (units * px).rename(name)
    return out


def monte_carlo_random_agents(
    data: Dict[str, pd.DataFrame],
    n_agents: int,
    initial_capital: float,
    commission: float = 0.001,
    decision_every_days: int = 5,
    max_weight: float = 0.40,
    evaluation_start: Optional[pd.Timestamp] = None,
    evaluation_end: Optional[pd.Timestamp] = None,
    seed: int = 42,
) -> pd.DataFrame:
    """Simulate random currency portfolios under the same allocation constraints."""
    symbols = list(data)
    dates = _common_dates(data, evaluation_start, evaluation_end)
    closes = np.column_stack([data[s].loc[dates, "close"].to_numpy(float) for s in symbols])
    returns = closes[1:] / closes[:-1] - 1.0
    n_assets = len(symbols)

    rng = np.random.default_rng(seed)
    cash = np.full(n_agents, float(initial_capital), dtype=float)
    asset_values = np.zeros((n_agents, n_assets), dtype=np.float64)
    max_values = np.full(n_agents, float(initial_capital), dtype=float)
    max_drawdowns = np.zeros(n_agents, dtype=float)

    for day in range(len(returns)):
        if day % max(int(decision_every_days), 1) == 0:
            total_before = cash + asset_values.sum(axis=1)
            k = rng.integers(0, n_assets + 1, size=n_agents)

            priorities = rng.random((n_agents, n_assets), dtype=np.float32)
            order = np.argsort(priorities, axis=1)
            ranks = np.empty_like(order)
            row_idx = np.arange(n_agents)[:, None]
            ranks[row_idx, order] = np.arange(n_assets)
            selected_mask = ranks < k[:, None]

            per_asset = np.zeros(n_agents, dtype=np.float64)
            nonzero = k > 0
            per_asset[nonzero] = np.minimum(1.0 / k[nonzero], float(max_weight))
            new_weights = selected_mask.astype(np.float64) * per_asset[:, None]

            provisional_targets = total_before[:, None] * new_weights
            turnover_notional = np.abs(provisional_targets - asset_values).sum(axis=1)
            fees = turnover_notional * commission
            investable = np.maximum(total_before - fees, 0.0)

            asset_values = investable[:, None] * new_weights
            cash = investable - asset_values.sum(axis=1)

        asset_values *= (1.0 + returns[day][None, :])
        values = cash + asset_values.sum(axis=1)
        max_values = np.maximum(max_values, values)
        dd = values / max_values - 1
        max_drawdowns = np.minimum(max_drawdowns, dd)

    values = cash + asset_values.sum(axis=1)
    final_return = values / initial_capital - 1
    return pd.DataFrame(
        {
            "agent": np.arange(1, n_agents + 1),
            "final_value": values,
            "total_return": final_return,
            "max_drawdown": max_drawdowns,
        }
    )


def evaluate_human_decisions(
    decisions: pd.DataFrame,
    data: Dict[str, pd.DataFrame],
    initial_capital: float,
    commission: float = 0.001,
    max_weight: float = 0.40,
    evaluation_start: Optional[pd.Timestamp] = None,
    evaluation_end: Optional[pd.Timestamp] = None,
) -> pd.DataFrame:
    """Evaluate human currency choices from CSV columns participant,date,choice."""
    required = {"participant", "date", "choice"}
    if not required.issubset(decisions.columns):
        raise ValueError("El CSV ha de tenir les columnes participant,date,choice.")

    common = _common_dates(data, evaluation_start, evaluation_end)
    base_to_symbol = {_base(s).upper(): s for s in data}
    exact_symbols = {s.upper(): s for s in data}

    df = decisions.copy()
    df["date"] = pd.to_datetime(df["date"], errors="coerce").dt.normalize()
    if df["date"].isna().any():
        raise ValueError("Hi ha alguna data del CSV que no es pot interpretar.")
    df["choice"] = df["choice"].astype(str).str.upper().str.strip()

    def normalize_choice(choice: str) -> str:
        if choice == "CASH":
            return "CASH"
        if choice in exact_symbols:
            return exact_symbols[choice]
        if choice in base_to_symbol:
            return base_to_symbol[choice]
        raise ValueError(f"Opció no disponible: {choice}. Usa CASH o una de les divises seleccionades.")

    df["symbol"] = df["choice"].map(normalize_choice)
    prices = pd.DataFrame({s: data[s].loc[common, "close"].astype(float) for s in data})

    results = []
    for participant, pdec in df.groupby("participant"):
        pdec = pdec.sort_values("date")
        cash = float(initial_capital)
        held_symbol = "CASH"
        units = 0.0
        max_value_seen = float(initial_capital)
        max_dd = 0.0
        n_changes = 0

        for current_date in common:
            asset_value = 0.0 if held_symbol == "CASH" else units * float(prices.loc[current_date, held_symbol])
            total = cash + asset_value

            eligible = pdec[pdec["date"] <= current_date]
            desired = eligible.iloc[-1]["symbol"] if not eligible.empty else held_symbol
            if desired != held_symbol:
                target_asset_value = 0.0 if desired == "CASH" else total * float(max_weight)
                turnover = asset_value + target_asset_value
                fee = turnover * commission
                investable = max(total - fee, 0.0)
                target_asset_value = 0.0 if desired == "CASH" else investable * float(max_weight)
                cash = investable - target_asset_value
                units = 0.0 if desired == "CASH" else target_asset_value / float(prices.loc[current_date, desired])
                held_symbol = desired
                n_changes += 1
                total = investable

            max_value_seen = max(max_value_seen, total)
            max_dd = min(max_dd, total / max_value_seen - 1)

        final_asset_value = 0.0 if held_symbol == "CASH" else units * float(prices.loc[common[-1], held_symbol])
        final_value = cash + final_asset_value
        results.append(
            {
                "participant": participant,
                "final_value": final_value,
                "total_return": final_value / initial_capital - 1,
                "max_drawdown": max_dd,
                "changes": n_changes,
            }
        )
    return pd.DataFrame(results)


def _base(symbol: str) -> str:
    return symbol.split("/")[0].split(":")[0]
