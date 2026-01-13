"""
Signal Validation Script

Purpose:
- Validate sentiment aggregation
- Verify confidence intervals and sample filtering
"""

import pyarrow.dataset as ds
from src.signals.aggregate import aggregate_sentiment_signal


PARQUET_PATH = "data/processed/stocktwits_parquet"


def main() -> None:
    dataset = ds.dataset(PARQUET_PATH, format="parquet")
    df = dataset.to_table().to_pandas()

    signals = aggregate_sentiment_signal(
        df,
        window="1H",
        min_samples=20,
    )

    print("Signal aggregation successful")
    print(f"Generated signal points: {len(signals)}")
    print("\nSample signals:")
    print(signals.head())

    print("\nSignal statistics:")
    print(signals[["mean_signal", "ci_lower", "ci_upper", "count"]].describe())


if __name__ == "__main__":
    main()
