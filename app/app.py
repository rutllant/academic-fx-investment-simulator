from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import plotly.express as px
import streamlit as st

from engine import (
    DEFAULT_RULES,
    available_reference_currencies,
    calculate_metrics,
    evaluate_human_decisions,
    fetch_market_data,
    hodl_equity,
    list_fx_markets,
    monte_carlo_random_agents,
    run_agent_backtest,
    validate_rules,
    warmup_bars,
)
from i18n import LANGUAGES, translator

st.set_page_config(page_title="Agent FX · TDR", page_icon="💱", layout="wide")

REFERENCE_CURRENCIES = available_reference_currencies()


@st.cache_data(ttl=3600, show_spinner=False)
def market_catalog(reference_currency: str):
    return list_fx_markets(reference_currency)


def base(symbol: str) -> str:
    return symbol.split("/")[0].split(":")[0]


def default_symbols(catalog: list[str], quote: str) -> list[str]:
    preferred_assets = ["USD", "GBP", "JPY", "CHF", "EUR"]
    preferred = [f"{asset}/{quote}" for asset in preferred_assets if asset != quote]
    chosen = [s for s in preferred if s in catalog]
    if not chosen:
        chosen = catalog[: min(3, len(catalog))]
    return chosen


with st.sidebar:
    language_code = st.selectbox(
        "Idioma / Language",
        options=list(LANGUAGES.keys()),
        format_func=lambda code: LANGUAGES[code],
        index=0,
        key="ui_language",
    )

t = translator(language_code)


def rule_summary(rules: dict) -> str:
    rows = []
    if rules["ema_enabled"]:
        rows.append(
            t(
                "rule_ema_summary",
                points=rules["ema_points"],
                fast=rules["ema_fast"],
                slow=rules["ema_slow"],
            )
        )
    if rules["rsi_enabled"]:
        rows.append(
            t(
                "rule_rsi_summary",
                points=rules["rsi_points"],
                period=rules["rsi_period"],
                minimum=rules["rsi_min"],
                maximum=rules["rsi_max"],
            )
        )
    if rules["macd_enabled"]:
        rows.append(
            t(
                "rule_macd_summary",
                points=rules["macd_points"],
                fast=rules["macd_fast"],
                slow=rules["macd_slow"],
                signal=rules["macd_signal"],
            )
        )
    rows.append(
        t(
            "rule_entry_summary",
            score=rules["min_score"],
            weight=rules["max_weight"] * 100,
        )
    )
    return "\n".join(rows)


st.title(t("app_title"))
st.caption(t("app_caption"))

with st.sidebar:
    st.header(t("section_market"))
    quote = st.selectbox(
        t("quote"),
        REFERENCE_CURRENCIES,
        index=0,
        help=t("quote_help"),
    )

    try:
        catalog = market_catalog(quote)
    except Exception as exc:
        st.error(t("catalog_warning", error=exc))
        st.stop()

    if not catalog:
        st.error(t("no_spot", quote=quote, exchange="ECB"))
        st.stop()

    st.caption(t("markets_available_live", count=len(catalog), quote=quote))

    all_assets = st.checkbox(
        t("select_all"),
        value=False,
        help=t("select_all_help"),
    )
    if all_assets:
        selected = list(catalog)
        st.info(t("selected_markets", count=len(selected)))
    else:
        selected = st.multiselect(
            t("cryptocurrencies"),
            catalog,
            default=default_symbols(catalog, quote),
            help=t("cryptocurrencies_help"),
        )

    capital = st.number_input(
        t("initial_capital", quote=quote),
        min_value=100.0,
        value=10000.0,
        step=500.0,
    )
    commission_pct = st.number_input(
        t("commission"),
        min_value=0.0,
        max_value=2.0,
        value=0.10,
        step=0.01,
    )
    default_end = date.today() - timedelta(days=1)
    default_start = default_end - timedelta(days=365 * 2)
    start = st.date_input(t("start_date"), value=default_start)
    end = st.date_input(t("end_date"), value=default_end)

    st.header(t("section_rules"))
    st.caption(t("rules_caption"))

    ema_enabled = st.checkbox(
        t("activate_ema"),
        value=DEFAULT_RULES["ema_enabled"],
        help=t("ema_help"),
    )
    c1, c2, c3 = st.columns(3)
    ema_fast = c1.number_input(
        t("ema_fast"),
        min_value=2,
        max_value=250,
        value=DEFAULT_RULES["ema_fast"],
        step=1,
        disabled=not ema_enabled,
    )
    ema_slow = c2.number_input(
        t("ema_slow"),
        min_value=3,
        max_value=400,
        value=DEFAULT_RULES["ema_slow"],
        step=1,
        disabled=not ema_enabled,
    )
    ema_points = c3.number_input(
        t("ema_points"),
        min_value=1,
        max_value=10,
        value=DEFAULT_RULES["ema_points"],
        step=1,
        disabled=not ema_enabled,
    )

    rsi_enabled = st.checkbox(
        t("activate_rsi"),
        value=DEFAULT_RULES["rsi_enabled"],
        help=t("rsi_help"),
    )
    c1, c2, c3 = st.columns(3)
    rsi_period = c1.number_input(
        t("rsi_period"),
        min_value=2,
        max_value=100,
        value=DEFAULT_RULES["rsi_period"],
        step=1,
        disabled=not rsi_enabled,
    )
    rsi_min = c2.number_input(
        t("rsi_min"),
        min_value=0.0,
        max_value=99.0,
        value=float(DEFAULT_RULES["rsi_min"]),
        step=1.0,
        disabled=not rsi_enabled,
    )
    rsi_max = c3.number_input(
        t("rsi_max"),
        min_value=1.0,
        max_value=100.0,
        value=float(DEFAULT_RULES["rsi_max"]),
        step=1.0,
        disabled=not rsi_enabled,
    )
    rsi_points = st.number_input(
        t("rsi_points"),
        min_value=1,
        max_value=10,
        value=DEFAULT_RULES["rsi_points"],
        step=1,
        disabled=not rsi_enabled,
    )

    macd_enabled = st.checkbox(
        t("activate_macd"),
        value=DEFAULT_RULES["macd_enabled"],
        help=t("macd_help"),
    )
    c1, c2, c3 = st.columns(3)
    macd_fast = c1.number_input(
        t("macd_fast"),
        min_value=2,
        max_value=100,
        value=DEFAULT_RULES["macd_fast"],
        step=1,
        disabled=not macd_enabled,
    )
    macd_slow = c2.number_input(
        t("macd_slow"),
        min_value=3,
        max_value=200,
        value=DEFAULT_RULES["macd_slow"],
        step=1,
        disabled=not macd_enabled,
    )
    macd_signal = c3.number_input(
        t("macd_signal"),
        min_value=2,
        max_value=100,
        value=DEFAULT_RULES["macd_signal"],
        step=1,
        disabled=not macd_enabled,
    )
    macd_points = st.number_input(
        t("macd_points"),
        min_value=1,
        max_value=10,
        value=DEFAULT_RULES["macd_points"],
        step=1,
        disabled=not macd_enabled,
    )

    max_score = sum(
        points
        for enabled, points in [
            (ema_enabled, int(ema_points)),
            (rsi_enabled, int(rsi_points)),
            (macd_enabled, int(macd_points)),
        ]
        if enabled
    )
    if max_score > 0:
        min_score = st.slider(
            t("min_score"),
            min_value=1,
            max_value=max_score,
            value=min(int(DEFAULT_RULES["min_score"]), max_score),
            help=t("min_score_help"),
        )
    else:
        min_score = 1
        st.error(t("activate_rule_error"))

    max_weight_pct = st.slider(
        t("max_weight"),
        min_value=5,
        max_value=100,
        value=int(DEFAULT_RULES["max_weight"] * 100),
        step=5,
        help=t("max_weight_help"),
    )

    rules = {
        "ema_enabled": ema_enabled,
        "ema_fast": int(ema_fast),
        "ema_slow": int(ema_slow),
        "ema_points": int(ema_points),
        "rsi_enabled": rsi_enabled,
        "rsi_period": int(rsi_period),
        "rsi_min": float(rsi_min),
        "rsi_max": float(rsi_max),
        "rsi_points": int(rsi_points),
        "macd_enabled": macd_enabled,
        "macd_fast": int(macd_fast),
        "macd_slow": int(macd_slow),
        "macd_signal": int(macd_signal),
        "macd_points": int(macd_points),
        "min_score": int(min_score),
        "max_weight": max_weight_pct / 100,
    }

    st.header(t("section_holders"))
    if selected:
        default_n_holders = min(3, len(selected))
        n_holders = st.number_input(
            t("holder_count"),
            min_value=1,
            max_value=len(selected),
            value=default_n_holders,
            step=1,
            help=t("holder_count_help"),
        )
        preferred_holders = [s for s in selected if base(s) in {"USD", "GBP", "JPY", "CHF", "EUR"}]
        preferred_holders += [s for s in selected if s not in preferred_holders]
        holder_assets = st.multiselect(
            t("holder_assets"),
            selected,
            default=preferred_holders[: int(n_holders)],
            max_selections=int(n_holders),
            help=t("holder_assets_help"),
            key=f"holders_{int(n_holders)}_{abs(hash(tuple(selected)))}_{quote}",
        )
        if len(holder_assets) != int(n_holders):
            st.caption(t("holders_missing", count=int(n_holders) - len(holder_assets)))
    else:
        n_holders = 0
        holder_assets = []
        st.caption(t("select_coins_first"))

    st.header(t("section_random"))
    n_random = st.select_slider(
        t("random_agents"),
        options=[100, 500, 1000, 5000, 10000],
        value=1000,
    )
    random_days = st.selectbox(
        t("random_decision"),
        [1, 5, 10, 20],
        index=1,
        format_func=lambda x: t("every_days", days=x),
    )

    run = st.button(t("run_simulation"), type="primary", use_container_width=True)

with st.expander(t("rules_mean_title"), expanded=False):
    st.markdown(rule_summary(rules))
    st.info(t("methodology_info"))

if "results" not in st.session_state:
    st.session_state.results = None

if run:
    if not selected:
        st.error(t("error_select_coin"))
        st.stop()
    if start >= end:
        st.error(t("error_dates"))
        st.stop()
    if len(holder_assets) != int(n_holders):
        st.error(t("error_holders_exact", count=int(n_holders)))
        st.stop()

    try:
        validate_rules(rules)
    except Exception as exc:
        st.error(str(exc))
        st.stop()

    commission = commission_pct / 100
    warmup = warmup_bars(rules)
    fetch_start = pd.Timestamp(start) - pd.Timedelta(days=max(warmup * 2, 90))
    fetch_end = pd.Timestamp(end)

    try:
        with st.status(t("status_running"), expanded=True) as status:
            st.write(t("fetching_ohlcv", count=len(selected)))
            data = fetch_market_data(quote, selected, fetch_start, fetch_end, rules=rules)
            unavailable = [s for s in selected if s not in data]
            if unavailable:
                symbols = ", ".join(unavailable[:10]) + ("..." if len(unavailable) > 10 else "")
                st.write(t("insufficient_data", symbols=symbols))

            usable_holders = [s for s in holder_assets if s in data]
            if len(usable_holders) != len(holder_assets):
                missing = [s for s in holder_assets if s not in data]
                raise ValueError(t("holder_data_error", symbols=", ".join(missing)))

            st.write(t("calculating_agent"))
            agent = run_agent_backtest(
                data,
                capital,
                commission,
                rules=rules,
                evaluation_start=pd.Timestamp(start),
                evaluation_end=pd.Timestamp(end),
            )

            st.write(t("simulating_random", count=f"{n_random:,}"))
            random = monte_carlo_random_agents(
                data,
                n_random,
                capital,
                commission,
                random_days,
                max_weight=rules["max_weight"],
                evaluation_start=pd.Timestamp(start),
                evaluation_end=pd.Timestamp(end),
            )

            st.write(t("calculating_holders", count=len(usable_holders)))
            hodl = hodl_equity(
                data,
                capital,
                commission,
                symbols=usable_holders,
                evaluation_start=pd.Timestamp(start),
                evaluation_end=pd.Timestamp(end),
            )
            status.update(label=t("simulation_complete"), state="complete", expanded=False)

        st.session_state.results = {
            "data": data,
            "agent": agent,
            "random": random,
            "hodl": hodl,
            "capital": capital,
            "quote": quote,
            "commission": commission,
            "rules": rules,
            "holders": usable_holders,
            "selected": list(data),
            "start": pd.Timestamp(start),
            "end": pd.Timestamp(end),
        }
    except Exception as exc:
        st.error(t("simulation_error", error=exc))
        st.stop()

res = st.session_state.results
if res is None:
    st.info(t("initial_prompt"))
    st.stop()

agent = res["agent"]
random = res["random"]
hodl = res["hodl"]
capital = res["capital"]
quote_used = res["quote"]
rules_used = res["rules"]

st.caption(
    t(
        "result_saved",
        coins=len(res["selected"]),
        holders=len(hodl),
        start=agent.equity.index.min().date(),
        end=agent.equity.index.max().date(),
    )
)

m1, m2, m3, m4 = st.columns(4)
m1.metric(
    t("metric_final_capital", quote=quote_used),
    f"{agent.metrics['final_value']:,.0f}",
    f"{agent.metrics['total_return']*100:+.1f}%",
)
m2.metric(t("drawdown"), f"{agent.metrics['max_drawdown']*100:.1f}%")
m3.metric(t("sharpe"), "—" if pd.isna(agent.metrics["sharpe"]) else f"{agent.metrics['sharpe']:.2f}")
m4.metric(t("rebalances"), f"{int(agent.metrics['trades'])}")

st.subheader(t("comparison_random"))
better = int((random["final_value"] > agent.metrics["final_value"]).sum())
percentile = 100 * (1 - better / len(random))
st.write(
    t(
        "random_summary",
        percentile=percentile,
        count=f"{len(random):,}",
        better=f"{better:,}",
    )
)

fig_hist = px.histogram(
    random,
    x="total_return",
    nbins=50,
    labels={"total_return": t("return_label")},
)
fig_hist.add_vline(
    x=agent.metrics["total_return"],
    line_dash="dash",
    annotation_text=t("technical_agent"),
)
fig_hist.update_xaxes(tickformat=".0%")
fig_hist.update_layout(title=t("hist_title"), yaxis_title=t("num_agents"))
st.plotly_chart(fig_hist, use_container_width=True)

st.subheader(t("agent_vs_holders"))
comparison = pd.DataFrame({t("technical_agent"): agent.equity})
for name, series in hodl.items():
    comparison = comparison.join(series, how="outer")
comparison = comparison.sort_index().ffill()
returns_pct = (comparison / capital - 1.0) * 100
fig_ret = px.line(
    returns_pct,
    x=returns_pct.index,
    y=returns_pct.columns,
    labels={"value": t("return_pct"), "index": t("date"), "variable": t("strategy")},
)
fig_ret.add_hline(y=0, line_dash="dot")
fig_ret.update_layout(legend_title_text="", title=t("cumulative_return"))
st.plotly_chart(fig_ret, use_container_width=True)

holder_rows = []
for name, series in hodl.items():
    metrics = calculate_metrics(series, capital)
    holder_rows.append(
        {
            t("strategy"): name,
            t("final_capital", quote=quote_used): metrics["final_value"],
            t("return_label"): metrics["total_return"],
            t("drawdown"): metrics["max_drawdown"],
            t("sharpe"): metrics["sharpe"],
        }
    )
if holder_rows:
    holder_table = pd.DataFrame(holder_rows)
    st.dataframe(
        holder_table.style.format(
            {
                t("final_capital", quote=quote_used): "{:,.2f}",
                t("return_label"): "{:+.2%}",
                t("drawdown"): "{:.2%}",
                t("sharpe"): "{:.2f}",
            }
        ),
        use_container_width=True,
        hide_index=True,
    )

with st.expander(t("used_rules"), expanded=False):
    st.markdown(rule_summary(rules_used))

st.subheader(t("operations_signals"))
tab1, tab2, tab3 = st.tabs([t("tab_rebalances"), t("tab_daily_signals"), t("tab_export")])
with tab1:
    st.dataframe(agent.trades, use_container_width=True)
with tab2:
    st.dataframe(agent.signals.tail(250), use_container_width=True)
with tab3:
    st.download_button(
        t("download_ops"),
        agent.trades.to_csv(index=False).encode("utf-8-sig"),
        "fx_operacions_agent.csv",
        "text/csv",
    )
    st.download_button(
        t("download_random"),
        random.to_csv(index=False).encode("utf-8-sig"),
        "fx_agents_aleatoris.csv",
        "text/csv",
    )
    st.download_button(
        t("download_returns"),
        returns_pct.to_csv().encode("utf-8-sig"),
        "fx_rendibilitat_agent_holders.csv",
        "text/csv",
    )

st.divider()
st.subheader(t("humans"))
st.write(t("humans_intro", weight=rules_used["max_weight"] * 100))

available_bases = [base(s) for s in res["selected"]]
first_date = agent.equity.index.min().date()
first_choices = available_bases[: max(1, min(3, len(available_bases)))]
template_rows = []
for i, choice in enumerate(first_choices, start=1):
    template_rows.append({"participant": f"Persona {i}", "date": str(first_date), "choice": choice})
template = pd.DataFrame(template_rows)
st.download_button(
    t("download_template"),
    template.to_csv(index=False).encode("utf-8-sig"),
    "plantilla_inversors_humans_fx.csv",
    "text/csv",
)
st.caption(t("allowed_choices"))
uploaded = st.file_uploader(t("upload_humans"), type=["csv"])
if uploaded is not None:
    try:
        human = evaluate_human_decisions(
            pd.read_csv(uploaded),
            res["data"],
            capital,
            res["commission"],
            max_weight=rules_used["max_weight"],
            evaluation_start=res["start"],
            evaluation_end=res["end"],
        )
        st.dataframe(human, use_container_width=True)
        st.download_button(
            t("download_human_results"),
            human.to_csv(index=False).encode("utf-8-sig"),
            "resultats_humans_fx.csv",
            "text/csv",
        )
    except Exception as exc:
        st.error(str(exc))

st.caption(t("educational_disclaimer"))
