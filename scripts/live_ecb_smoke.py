from __future__ import annotations

import sys
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "app"))

import engine  # noqa: E402


def main() -> None:
    history = engine._download_ecb_history()

    required = {"USD", "GBP", "JPY", "CHF"}
    missing = sorted(required - set(history.columns))
    if missing:
        raise RuntimeError(f"ECB history is missing expected currencies: {', '.join(missing)}")

    if len(history) < 1000:
        raise RuntimeError(f"ECB history is unexpectedly short: {len(history)} rows")

    latest = pd.Timestamp(history.index.max())
    today = pd.Timestamp(datetime.now(timezone.utc).date())
    age_days = (today - latest.normalize()).days
    if age_days < 0 or age_days > 14:
        raise RuntimeError(
            f"Latest ECB observation looks stale or invalid: {latest.date()} ({age_days} days old)"
        )

    # Reuse the successfully downloaded history to verify cross-rate construction.
    engine._download_ecb_history = lambda: history
    start = latest - pd.Timedelta(days=90)
    data = engine.fetch_market_data(
        "EUR",
        ["USD/EUR", "GBP/EUR"],
        start,
        latest,
        rules=dict(engine.DEFAULT_RULES),
    )

    if not data["USD/EUR"]["close"].notna().all():
        raise RuntimeError("USD/EUR contains missing derived rates")
    if not data["GBP/EUR"]["close"].notna().all():
        raise RuntimeError("GBP/EUR contains missing derived rates")

    print(
        "LIVE ECB SMOKE TEST OK | "
        f"rows={len(history)} | latest={latest.date()} | "
        f"USD/EUR={data['USD/EUR']['close'].iloc[-1]:.8f}"
    )


if __name__ == "__main__":
    main()
