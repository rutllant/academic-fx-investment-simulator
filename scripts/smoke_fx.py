from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

import engine  # noqa: E402


def synthetic_ecb_history() -> pd.DataFrame:
    dates = pd.bdate_range("2024-01-01", periods=180)
    x = np.linspace(0, 6 * np.pi, len(dates))
    return pd.DataFrame(
        {
            "USD": 1.08 + 0.03 * np.sin(x),
            "GBP": 0.85 + 0.02 * np.cos(x / 2),
            "JPY": 155 + 8 * np.sin(x / 3),
            "CHF": 0.95 + 0.02 * np.cos(x),
        },
        index=dates,
    )


def main() -> None:
    engine._download_ecb_history = synthetic_ecb_history

    markets = engine.list_fx_markets("EUR")
    assert "USD/EUR" in markets
    assert "GBP/EUR" in markets
    assert "EUR/EUR" not in markets

    rules = dict(engine.DEFAULT_RULES)
    data = engine.fetch_market_data(
        "EUR",
        ["USD/EUR", "GBP/EUR", "JPY/EUR"],
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-09-30"),
        rules=rules,
    )

    # ECB USD is units of USD per EUR, so one USD in EUR must be its reciprocal.
    history = synthetic_ecb_history()
    first_date = data["USD/EUR"].index[0]
    expected = 1.0 / history.loc[first_date, "USD"]
    actual = data["USD/EUR"].loc[first_date, "close"]
    assert abs(actual - expected) < 1e-12

    # Cross-rate direction: one GBP in USD = USD-per-EUR / GBP-per-EUR.
    cross = engine.fetch_market_data(
        "USD",
        ["GBP/USD"],
        pd.Timestamp("2024-01-01"),
        pd.Timestamp("2024-09-30"),
        rules=rules,
    )
    expected_cross = history.loc[first_date, "USD"] / history.loc[first_date, "GBP"]
    actual_cross = cross["GBP/USD"].loc[first_date, "close"]
    assert abs(actual_cross - expected_cross) < 1e-12

    agent = engine.run_agent_backtest(
        data,
        initial_capital=10000.0,
        commission=0.001,
        rules=rules,
        evaluation_start=pd.Timestamp("2024-04-01"),
        evaluation_end=pd.Timestamp("2024-09-30"),
    )
    assert not agent.equity.empty
    assert np.isfinite(agent.metrics["final_value"])

    random = engine.monte_carlo_random_agents(
        data,
        n_agents=100,
        initial_capital=10000.0,
        commission=0.001,
        decision_every_days=5,
        evaluation_start=pd.Timestamp("2024-04-01"),
        evaluation_end=pd.Timestamp("2024-09-30"),
    )
    assert len(random) == 100
    assert random["final_value"].notna().all()

    holders = engine.hodl_equity(
        data,
        initial_capital=10000.0,
        commission=0.001,
        symbols=["USD/EUR", "GBP/EUR"],
        evaluation_start=pd.Timestamp("2024-04-01"),
        evaluation_end=pd.Timestamp("2024-09-30"),
    )
    assert set(holders) == {"HODL USD", "HODL GBP"}

    print("FX SMOKE TEST OK")


if __name__ == "__main__":
    main()
