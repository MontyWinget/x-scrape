"""
Pipeline Runner

Executes the full ingestion → processing → storage pipeline.
"""

from pathlib import Path
from loguru import logger

from src.collect.stocktwits_loader import load_stocktwits_csv
from src.process.clean import clean_dataframe
from src.process.enrich import add_synthetic_timestamps, add_time_features
from src.process.write_parquet import write_parquet


RAW_DATA_PATH = Path("data/raw/stocktwits_raw.csv")
OUTPUT_DIR = Path("data/processed/stocktwits_parquet")


def run() -> None:
    logger.info("Starting market sentiment pipeline")

    df = load_stocktwits_csv(RAW_DATA_PATH)
    df = clean_dataframe(df)
    df = add_synthetic_timestamps(df)
    df = add_time_features(df)

    write_parquet(
        df,
        output_dir=OUTPUT_DIR,
        partition_cols=["company"],
    )

    logger.info("Pipeline completed successfully")


if __name__ == "__main__":
    run()
