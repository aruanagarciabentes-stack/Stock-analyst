import sys
import io
import importlib
from contextlib import contextmanager
import streamlit as st

# Import your 6 cleanly renamed quantitative engines
import Corr_hedgEngine as che
import BusinessQ_Engine as bqe
import FinancialH_Engine as fhe
import management_insider_engine as mie
import QuantativeNewsFeed as qnf
import Valuation_MomentumMetric as vmm

@contextmanager
def capture_terminal_output():
    """
    Intercepts all print() statements executed by the underlying engines
    and redirects them cleanly into our Streamlit web interface.
    """
    new_stdout = io.StringIO()
    old_stdout = sys.stdout
    sys.stdout = new_stdout
    try:
        yield new_stdout
    finally:
        sys.stdout = old_stdout

# ==========================================
# STREAMLIT UI CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Stock Analyst AFO",
    page_icon="🪖",
    layout="wide"
)

# Dark theme structural accents (FIXED: Changed unsafe_with_html to unsafe_allow_html)
st.markdown("""
<style>
    .reportview-container {
        background-color: #0b0f19;
    }
    .stCodeBlock {
        background-color: #0f172a !important;
        border: 1px solid #1e293b !important;
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)

st.title("🛡️ Institutional Portfolio Intelligence Station")
st.markdown("Designed for aggressive growth research inside a tax-free Stocks and Shares ISA.")
st.markdown("---")

# Sidebar Control Console
st.sidebar.title("🔍 Workspace Control")
target_ticker = st.sidebar.text_input("ENTER TICKER SYMBOL", "IONQ").upper().strip()
run_analysis = st.sidebar.button("Execute Quantitative Run", type="primary")

if target_ticker:
    st.sidebar.success(f"Target locked: **{target_ticker}**")
else:
    st.sidebar.warning("Input a valid stock ticker to initialize.")

# ==========================================
# CORE EXECUTION MATRIX
# ==========================================
if run_analysis and target_ticker:
    st.header(f"📊 Quantitative Intelligence Dossier: {target_ticker}")
    
    # Generate 6 interactive tabs matching your engines
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
        "🔄 Correlation & Hedging",
        "🏥 Financial Health",
        "📈 Business Quality",
        "👥 Management & Insiders",
        "📰 Sentiment News Feed",
        "📊 Valuation & Momentum"
    ])
    
    # --- TAB 1: CORRELATION & HEDGING ---
    with tab1:
        st.subheader("Statistical Tracking & Safe-Haven Discovery")
        with st.spinner("Calculating correlation matrices..."):
            with capture_terminal_output() as output:
                try:
                    # Run the pipeline function in your correlation engine
                    che.run_correlation_pipeline(target_ticker)
                except Exception as e:# pylint: disable=broad-exception-caught
                    print(f"❌ Correlation Engine Error: {e}")
            st.code(output.getvalue(), language="text")

    # --- TAB 2: FINANCIAL HEALTH ---
    with tab2:
        st.subheader("Balance Sheet, Liquidity & Solvency Analysis")
        with st.spinner("Ingesting fundamental statements..."):
            with capture_terminal_output() as output:
                try:
                    # Dynamically inject the user's ticker and reload the file
                    fhe.ticker_symbol = target_ticker
                    importlib.reload(fhe)
                except Exception as e:# pylint: disable=broad-exception-caught
                    print(f"❌ Financial Health Engine Error: {e}")
            st.code(output.getvalue(), language="text")

    # --- TAB 3: BUSINESS QUALITY ---
    with tab3:
        st.subheader("Profitability Margins & Operational Moat Audit")
        with st.spinner("Extracting margin metrics..."):
            with capture_terminal_output() as output:
                try:
                    # Dynamically inject the user's ticker and reload the file
                    bqe.ticker_symbol = target_ticker
                    importlib.reload(bqe)
                except Exception as e:# pylint: disable=broad-exception-caught
                    print(f"❌ Business Quality Engine Error: {e}")
            st.code(output.getvalue(), language="text")

    # --- TAB 4: MANAGEMENT & INSIDERS ---
    with tab4:
        st.subheader("Insider Trade Monitoring & Executive Stewardship")
        with st.spinner("Tracking SEC Form 4 and 13F files..."):
            with capture_terminal_output() as output:
                try:
                    # Dynamically inject the user's ticker and reload the file
                    mie.ticker_symbol = target_ticker
                    importlib.reload(mie)
                except Exception as e:# pylint: disable=broad-exception-caught
                    print(f"❌ Management Insider Engine Error: {e}")
            st.code(output.getvalue(), language="text")

    # --- TAB 5: SENTIMENT NEWS FEED ---
    with tab5:
        st.subheader("Live Sentiment Compounding & Market News")
        with st.spinner("Filtering live media channels..."):
            with capture_terminal_output() as output:
                try:
                    # Dynamically inject the user's ticker and reload the file
                    qnf.ticker_symbol = target_ticker
                    importlib.reload(qnf)
                except Exception as e:# pylint: disable=broad-exception-caught
                    print(f"❌ News Feed Engine Error: {e}")
            st.code(output.getvalue(), language="text")

    # --- TAB 6: VALUATION & MOMENTUM ---
    with tab6:
        st.subheader("Pricing Multiples & Technical Trend Alignment")
        with st.spinner("Analyzing technical momentum..."):
            with capture_terminal_output() as output:
                try:
                    # Dynamically inject the user's ticker and reload the file
                    vmm.ticker_symbol = target_ticker
                    importlib.reload(vmm)
                except Exception as e:# pylint: disable=broad-exception-caught
                    print(f"❌ Valuation Momentum Engine Error: {e}")
            st.code(output.getvalue(), language="text")

else:
    # Landing Page State
    st.info("💡 Input an equity ticker on the sidebar and click 'Execute Quantitative Run' to initialize the intelligence station!")

