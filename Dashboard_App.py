"""Streamlit entry point for the six independent stock research reports."""

import re
from datetime import datetime, timezone

import streamlit as st

import BusinessQ_Engine as business
import Corr_hedgEngine as correlation
import FinancialH_Engine as financial
import QuantativeNewsFeed as news
import Valuation_MomentumMetric as valuation
import management_insider_engine as ownership


st.set_page_config(page_title="Stock Analyst", page_icon="📈", layout="wide")

SECTIONS = {
    "Business quality": business.analyze,
    "Financial health": financial.analyze,
    "Valuation & momentum": valuation.analyze,
    "Correlation": correlation.analyze,
    "Ownership & earnings": ownership.analyze,
    "News sentiment": news.analyze,
}


@st.cache_data(ttl=900, show_spinner=False)
def get_report(section: str, symbol: str):
    return SECTIONS[section](symbol)


def display_number(value, suffix="", digits=2):
    return "N/A" if value is None else f"{value:,.{digits}f}{suffix}"


def render_table(frame, empty_message="No public data available for this ticker."):
    if frame is None or frame.empty:
        st.info(empty_message)
    else:
        st.dataframe(frame, width="stretch")


def render_report(section, report):
    if section == "Business quality":
        st.caption(f"Quarterly statements · reported currency: {report.attrs.get('currency', 'Unknown')} · YoY compares the same quarter last year; ROE uses TTM net income and average equity across a year.")
        render_table(report)
    elif section == "Financial health":
        st.caption("ROIC estimate = TTM operating income after the reported effective tax rate / average invested capital (debt + equity - cash). Requires five quarters and positive pretax income; missing inputs show N/A.")
        render_table(report)
    elif section == "Valuation & momentum":
        st.subheader(report["company"])
        st.caption(f"Price date: {report['price_date'] or 'unavailable'} · currency: {report['currency']}")
        values = {
            "Last close": display_number(report["price"], digits=2),
            "Trailing P/E": display_number(report["trailing_pe"], "x"),
            "Forward P/E": display_number(report["forward_pe"], "x"),
            "Price / sales": display_number(report["price_to_sales"], "x"),
            "EV / EBITDA": display_number(report["ev_to_ebitda"], "x"),
            "126-session return": display_number(report["return_6m_pct"], "%"),
            "Distance from 200-session average": display_number(report["distance_sma_200_pct"], "%"),
        }
        st.table({"Metric": list(values), "Value": list(values.values())})
    elif section == "Correlation":
        st.caption(f"{report['company']} · {report['sector']} · {report['industry']}")
        st.info(f"Closest observed comparison: {report['closest']}. Lowest observed correlation: {report['least_correlated']}. Correlation is historical and does not establish a hedge or future protection.")
        render_table(report["correlations"])
        st.caption("Pairwise log returns over the last year; each comparison needs at least 60 overlapping daily returns. ^VIX is a market indicator, not an investable security.")
    elif section == "Ownership & earnings":
        st.subheader("Insider transactions")
        if report["buys"] is not None:
            st.caption(f"Among the displayed rows: {report['buys']} acquisitions; {report['sells']} dispositions.")
        render_table(report["insiders"], report.get("insiders_error") or "No insider transactions returned.")
        st.subheader("Institutional holders")
        render_table(report["institutions"], report.get("institutions_error") or "No institutional holder data returned.")
        st.subheader("Reported earnings")
        render_table(report["earnings"], report.get("earnings_error") or "No completed earnings reports returned.")
    elif section == "News sentiment":
        score = report["average_score"]
        st.caption("Simple headline word-count score from -1 to +1. This is an exploratory text indicator, not a forecast.")
        st.metric("Average headline score", display_number(score))
        render_table(report["headlines"], "No recent news was returned for this ticker.")


st.title("Stock Analyst")
st.write("Explore public market data, financial statements, ownership and recent headlines for one ticker.")
st.caption("Source: Yahoo Finance via yfinance. Figures may be delayed, incomplete, or revised; verify before using them in a decision.")

symbol = st.sidebar.text_input("Ticker", value="AAPL", help="Examples: AAPL, IONQ, 0700.HK").strip().upper()
selected = st.sidebar.selectbox("Report", list(SECTIONS))
run_selected = st.sidebar.button("Run selected report", type="primary")
run_all = st.sidebar.button("Run all reports")

if not re.fullmatch(r"[A-Z0-9^.=\-]{1,20}", symbol):
    st.warning("Enter a valid ticker using letters, numbers, dots, dashes, ^ or =.")
    st.stop()

if st.session_state.get("symbol") != symbol:
    st.session_state["symbol"] = symbol
    st.session_state["reports"] = {}

if run_selected or run_all:
    sections = list(SECTIONS) if run_all else [selected]
    for section in sections:
        with st.spinner(f"Loading {section.lower()} for {symbol}..."):
            try:
                result = get_report(section, symbol)
                st.session_state["reports"][section] = {"data": result, "error": None,
                                                       "fetched": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")}
            except Exception as exc:
                st.session_state["reports"][section] = {"data": None, "error": str(exc), "fetched": None}

st.header(f"{symbol} · {selected}")
entry = st.session_state["reports"].get(selected)
if entry is None:
    st.info("Choose a report and click Run selected report, or run all six.")
elif entry["error"]:
    st.error(f"{selected} could not load: {entry['error']}")
else:
    st.caption(f"Retrieved {entry['fetched']}; cached market data expires after 15 minutes.")
    render_report(selected, entry["data"])

ready = [name for name, item in st.session_state["reports"].items() if item["error"] is None]
failed = [name for name, item in st.session_state["reports"].items() if item["error"] is not None]
if ready or failed:
    st.sidebar.caption(f"Loaded: {len(ready)}/6 · Errors: {len(failed)}")
