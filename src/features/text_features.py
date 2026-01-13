"""
Text Feature Extraction Module

Responsibilities:
- Convert cleaned text into numerical representations
- Use memory-efficient vectorization (sparse matrices)
- Provide stable, reproducible features for downstream signals

This module performs NO aggregation or trading logic.
"""

from __future__ import annotations

from typing import Tuple, List

import pandas as pd
from loguru import logger
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.sparse import csr_matrix


def build_tfidf_features(
    texts: pd.Series,
    max_features: int = 5000,
    ngram_range: Tuple[int, int] = (1, 2),
    min_df: int = 5,
    max_df: float = 0.9,
    stop_words: str = "english",
) -> Tuple[csr_matrix, List[str], TfidfVectorizer]:
    """
    Build TF-IDF features from text data.

    Parameters
    ----------
    texts : pd.Series
        Cleaned text data.
    max_features : int
        Maximum vocabulary size (controls memory usage).
    ngram_range : tuple[int, int]
        Range of n-grams to consider.
    min_df : int
        Minimum document frequency threshold.
    max_df : float
        Maximum document frequency threshold.
    stop_words : str
        Stop-word language.

    Returns
    -------
    X : csr_matrix
        Sparse TF-IDF feature matrix.
    feature_names : list[str]
        Feature (token) names.
    vectorizer : TfidfVectorizer
        Fitted vectorizer (for reuse or inspection).
    """
    logger.info(
        "Building TF-IDF features | "
        f"max_features={max_features}, "
        f"ngram_range={ngram_range}"
    )

    vectorizer = TfidfVectorizer(
        max_features=max_features,
        ngram_range=ngram_range,
        min_df=min_df,
        max_df=max_df,
        stop_words=stop_words,
        dtype=float,
    )

    X = vectorizer.fit_transform(texts)

    feature_names = vectorizer.get_feature_names_out().tolist()

    logger.info(
        f"TF-IDF matrix built | "
        f"shape={X.shape} | "
        f"sparsity={(1 - X.nnz / (X.shape[0] * X.shape[1])):.2%}"
    )

    return X, feature_names, vectorizer
