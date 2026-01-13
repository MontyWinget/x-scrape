"""
Feature Validation Script

Purpose:
- Validate TF-IDF feature extraction
- Sanity-check matrix shape and sparsity
"""

import pyarrow.dataset as ds
from src.features.text_features import build_tfidf_features


PARQUET_PATH = "data/processed/stocktwits_parquet"


def main() -> None:
    dataset = ds.dataset(PARQUET_PATH, format="parquet")
    df = dataset.to_table().to_pandas()

    X, feature_names, _ = build_tfidf_features(df["text"])

    print("TF-IDF feature extraction successful")
    print(f"Documents: {X.shape[0]}")
    print(f"Features: {X.shape[1]}")
    print(f"Sparsity: {(1 - X.nnz / (X.shape[0] * X.shape[1])):.2%}")
    print("Sample features:", feature_names[:20])


if __name__ == "__main__":
    main()
