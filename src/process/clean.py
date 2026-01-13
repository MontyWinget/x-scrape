"""
Data Cleaning Module

Responsibilities:
- Unicode normalization
- Text standardization
- URL / mention / hashtag handling
- Deduplication
- Basic row filtering

This module assumes a standardized ingestion schema.
"""

from __future__ import annotations

import unicodedata
from typing import Iterable

import pandas as pd
import regex as re
from loguru import logger


# ----------------------------
# Regex patterns (compiled once)
# ----------------------------
URL_PATTERN = re.compile(r"https?://\S+|www\.\S+", re.IGNORECASE)
MENTION_PATTERN = re.compile(r"@\w+")
HASHTAG_PATTERN = re.compile(r"#(\w+)")
WHITESPACE_PATTERN = re.compile(r"\s+")


def normalize_unicode(text: str) -> str:
    """
    Normalize Unicode text to NFKC form.
    Handles mixed-width characters and Indian language scripts safely.
    """
    return unicodedata.normalize("NFKC", text)


def clean_text(text: str) -> str:
    """
    Apply standard text cleaning steps.
    """
    text = normalize_unicode(text)
    text = text.lower()

    text = URL_PATTERN.sub("", text)
    text = MENTION_PATTERN.sub("", text)

    # Keep hashtag text, drop the '#' symbol
    text = HASHTAG_PATTERN.sub(r"\1", text)

    text = WHITESPACE_PATTERN.sub(" ", text)
    text = text.strip()

    return text


def clean_dataframe(
    df: pd.DataFrame,
    text_column: str = "text",
    min_length: int = 5,
) -> pd.DataFrame:
    """
    Clean and deduplicate a DataFrame containing social media text.

    Parameters
    ----------
    df : pd.DataFrame
        Input DataFrame (assumes standardized schema).
    text_column : str
        Column containing raw text.
    min_length : int
        Minimum character length after cleaning.

    Returns
    -------
    pd.DataFrame
        Cleaned and deduplicated DataFrame.
    """
    logger.info("Starting data cleaning")

    initial_rows = len(df)

    # Drop null text rows early (cheap + effective)
    df = df.dropna(subset=[text_column])

    # Clean text
    df[text_column] = df[text_column].astype(str).map(clean_text)

    # Drop empty or very short text
    df = df[df[text_column].str.len() >= min_length]

    # Deduplicate on cleaned text
    before_dedup = len(df)
    df = df.drop_duplicates(subset=[text_column])
    deduped = before_dedup - len(df)

    logger.info(
        f"Cleaning complete | "
        f"rows: {initial_rows:,} → {len(df):,} | "
        f"deduplicated: {deduped:,}"
    )

    return df.reset_index(drop=True)
