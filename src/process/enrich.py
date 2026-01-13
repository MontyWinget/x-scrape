"""
Data Enrichment Module

Responsibilities:
- Add synthetic timestamps (documented assumption)
- Derive basic time-based features for downstream aggregation

This module performs NO cleaning or feature engineering.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
from loguru import logger


def add_synthetic_timestamps(
    df: pd.DataFrame,
    hours: int = 24,
    seed: int = 42,
    timestamp_col: str = "timestamp",
) -> pd.DataFrame:
    """
    Add synthetic timestamps uniformly distributed over the last `hours`.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame.
    hours : int
        Time window (in hours) over which timestamps are generated.
    seed : int
        Random seed for reproducibility.
    timestamp_col : str
        Name of the timestamp column to create.

    Returns
    -------
    pd.DataFrame
        DataFrame with synthetic timestamp column added.
    """
    logger.info(
        f"Adding synthetic timestamps uniformly over last {hours} hours"
    )

    rng = np.random.default_rng(seed)
    now = datetime.utcnow()

    # Uniformly sample seconds in [0, hours * 3600)
    offsets = rng.uniform(0, hours * 3600, size=len(df))

    df[timestamp_col] = [
        now - timedelta(seconds=float(s)) for s in offsets
    ]

    return df


def add_time_features(
    df: pd.DataFrame,
    timestamp_col: str = "timestamp",
) -> pd.DataFrame:
    """
    Add basic time-derived features for aggregation and analysis.

    Adds:
    - hour
    - date
    - minute_bucket (5-min buckets)

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame with timestamp column.
    timestamp_col : str
        Name of the timestamp column.

    Returns
    -------
    pd.DataFrame
        Enriched DataFrame with time features.
    """
    if timestamp_col not in df.columns:
        raise ValueError(f"Timestamp column '{timestamp_col}' not found")

    ts = pd.to_datetime(df[timestamp_col], utc=True)

    df["date"] = ts.dt.date
    df["hour"] = ts.dt.hour

    # 5-minute buckets (useful for low-memory aggregation)
    df["minute_bucket"] = (ts.dt.minute // 5) * 5

    logger.info("Time-based features added")

    return df
