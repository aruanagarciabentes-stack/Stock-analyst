"""Optional live provider smoke test: python tests/live_smoke.py AAPL IONQ."""

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import BusinessQ_Engine as business
import Corr_hedgEngine as correlation
import FinancialH_Engine as financial
import QuantativeNewsFeed as news
import Valuation_MomentumMetric as valuation
import management_insider_engine as ownership


sections = {
    "business": business.analyze,
    "financial": financial.analyze,
    "valuation": valuation.analyze,
    "correlation": correlation.analyze,
    "ownership": ownership.analyze,
    "news": news.analyze,
}


def main():
    failed = 0
    for symbol in sys.argv[1:] or ["AAPL", "IONQ"]:
        for name, function in sections.items():
            started = time.monotonic()
            try:
                result = function(symbol)
                if result is None:
                    raise ValueError("The engine returned no result")
                if name in ("business", "financial"):
                    detail = f"{len(result)} quarters, {int(result.notna().sum().sum())} values"
                elif name == "correlation":
                    detail = f"{len(result['correlations'])} peers"
                elif name == "news":
                    detail = f"{len(result['headlines'])} headlines"
                elif name == "ownership":
                    detail = f"{len(result['insiders'])} insider rows, {len(result['earnings'])} earnings rows"
                else:
                    detail = f"{sum(value is not None for value in result.values())} populated fields"
                print(f"PASS {symbol:8} {name:12} {time.monotonic() - started:.1f}s - {detail}", flush=True)
            except Exception as exc:
                failed += 1
                print(f"FAIL {symbol:8} {name:12} {type(exc).__name__}: {exc}", flush=True)
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
