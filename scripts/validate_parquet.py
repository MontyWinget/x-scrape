"""
Parquet Validation Script

Purpose:
- Verify that the processed Parquet dataset can be read correctly
- Intended for manual sanity checks and debugging
"""

import pyarrow.dataset as ds


PARQUET_PATH = "data/processed/stocktwits_parquet"


def main() -> None:
    dataset = ds.dataset(
        PARQUET_PATH,
        format="parquet",
    )

    table = dataset.to_table()
    df = table.to_pandas()

    print("Parquet dataset loaded successfully")
    print(f"Rows: {len(df):,}")
    print(f"Columns: {list(df.columns)}")
    print("\nSample rows:")
    print(df.head())


if __name__ == "__main__":
    main()
