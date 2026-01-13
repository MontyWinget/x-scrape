"""
StockTwits CSV Loader

Responsibility:
- Load raw StockTwits CSV data
- Validate required schema
- Standardize column names
- Attach source metadata

This module performs NO cleaning or feature engineering.
"""

from pathlib import Path
import pandas as pd
from loguru import logger

REQUIRED_COLUMNS = {"company", "tweet", "sentiment"}


def load_stocktwits_csv(path: str | Path) -> pd.DataFrame:
    """
    Load StockTwits dataset from CSV and standardize schema.

    Parameters
    ----------
    path : str or Path
        Path to raw StockTwits CSV file.

    Returns
    -------
    pd.DataFrame
        DataFrame with standardized columns:
        - company
        - text
        - sentiment
        - source
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"StockTwits CSV not found at: {path}")

    logger.info(f"Loading StockTwits data from {path}")

    df = pd.read_csv(path)

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # Standardize column names
    df = df.rename(columns={"tweet": "text"})

    # Attach source metadata
    df["source"] = "stocktwits"

    # Enforce column order (helps downstream consistency)
    df = df[["company", "text", "sentiment", "source"]]

    logger.info(f"Loaded {len(df):,} StockTwits records")

    return df
