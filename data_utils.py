"""Small, testable helpers for Yahoo Finance statement shapes."""

import numpy as np
import pandas as pd


def statement_row(frame: pd.DataFrame, *names: str) -> pd.Series:
    """Return the first available financial statement row, with dates ascending."""
    if frame is None or frame.empty:
        return pd.Series(dtype="float64")
    for name in names:
        if name in frame.index:
            row = frame.loc[name]
            if isinstance(row, pd.DataFrame):
                row = row.iloc[0]
            row = pd.to_numeric(row, errors="coerce")
            row.index = pd.to_datetime(row.index)
            return row.sort_index().astype("float64")
    return pd.Series(dtype="float64")


def safe_ratio(numerator: pd.Series, denominator: pd.Series, scale: float = 1.0) -> pd.Series:
    """Align dates, and leave zero or missing denominators unavailable."""
    result = numerator.div(denominator.replace(0, np.nan)).mul(scale)
    return result.replace([np.inf, -np.inf], np.nan)


def display_frame(series_by_name: dict[str, pd.Series]) -> pd.DataFrame:
    result = pd.DataFrame(series_by_name).sort_index(ascending=False)
    result.index.name = "Quarter end"
    return result
