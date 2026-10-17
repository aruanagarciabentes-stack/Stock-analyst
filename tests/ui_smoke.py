"""Exercise the Streamlit controls against live AAPL data."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from streamlit.testing.v1 import AppTest


def main():
    app = AppTest.from_file("Dashboard_App.py").run(timeout=20)
    if app.exception:
        raise AssertionError(f"Landing page failed: {app.exception}")
    app.button[1].click().run(timeout=90)
    if app.exception:
        raise AssertionError(f"Full report failed: {app.exception}")
    for section in (
        "Business quality", "Financial health", "Valuation & momentum",
        "Correlation", "Ownership & earnings", "News sentiment",
    ):
        app.selectbox[0].set_value(section).run(timeout=20)
        if app.exception or app.error:
            raise AssertionError(f"{section}: exceptions={app.exception}, errors={app.error}")
        print(f"PASS UI {section}", flush=True)

    app.text_input[0].set_value("IONQ").run(timeout=20)
    if app.dataframe:
        raise AssertionError("AAPL report remained visible after changing the ticker")
    app.selectbox[0].set_value("Business quality").run(timeout=20)
    app.button[0].click().run(timeout=60)
    if app.exception or app.error or not app.dataframe:
        raise AssertionError("IONQ business report did not render")
    if app.dataframe[0].value.iloc[0]["Revenue"] >= 10_000_000_000:
        raise AssertionError("Business report appears to show AAPL revenue after selecting IONQ")
    print("PASS UI ticker switch AAPL -> IONQ", flush=True)


if __name__ == "__main__":
    main()
