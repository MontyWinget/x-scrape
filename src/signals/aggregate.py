"""
Signal Aggregation Module

Responsibilities:
- Convert text sentiment into trading-oriented signals
- Aggregate signals over time windows
- Quantify uncertainty via confidence intervals

This module performs NO feature extraction or model training.
"""

from __future__ import annotations

from typing import Optional

import pandas as pd
import numpy as np
from loguru import logger


SENTIMENT_MAP = {
    "Bullish": 1.0,
    "Bearish": -1.0,
}


def map_sentiment_to_score(
    sentiment: pd.Series,
) -> pd.Series:
    """
    Map categorical sentiment labels to numerical scores.
    """
    return sentiment.map(SENTIMENT_MAP).fillna(0.0)


def aggregate_sentiment_signal(
    df: pd.DataFrame,
    time_col: str = "timestamp",
    sentiment_col: str = "sentiment",
    window: str = "1H",
    min_samples: int = 10,
) -> pd.DataFrame:
    """
    Aggregate sentiment into a trading signal with confidence intervals.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame containing timestamps and sentiment labels.
    time_col : str
        Timestamp column name.
    sentiment_col : str
        Sentiment column name.
    window : str
        Pandas time window for aggregation (e.g. '5min', '1H').
    min_samples : int
        Minimum number of samples per window to emit a signal.

    Returns
    -------
    pd.DataFrame
        Aggregated signal with uncertainty bounds.
    """
    logger.info(
        f"Aggregating sentiment signal | window={window}, min_samples={min_samples}"
    )

    df = df.copy()

    # Ensure datetime
    df[time_col] = pd.to_datetime(df[time_col], utc=True)

    # Map sentiment to numerical score
    df["sentiment_score"] = map_sentiment_to_score(df[sentiment_col])

    # Set index for time-based resampling
    df = df.set_index(time_col)

    grouped = df["sentiment_score"].resample(window)

    agg = grouped.agg(
        mean_signal="mean",
        std_signal="std",
        count="count",
    )

    # Drop low-sample windows
    agg = agg[agg["count"] >= min_samples]

    # Standard error
    agg["stderr"] = agg["std_signal"] / np.sqrt(agg["count"])

    # 95% confidence interval
    agg["ci_lower"] = agg["mean_signal"] - 1.96 * agg["stderr"]
    agg["ci_upper"] = agg["mean_signal"] + 1.96 * agg["stderr"]

    agg = agg.reset_index()

    logger.info(
        f"Generated {len(agg):,} aggregated signal points"
    )

    return agg
