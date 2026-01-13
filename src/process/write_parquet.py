"""
Parquet Writer Module

Responsibilities:
- Persist processed data to Parquet format
- Apply compression
- Partition data for efficient downstream access
- Sanitize partition values to ensure cross-platform filesystem safety

This module performs NO cleaning or feature engineering.
"""

from __future__ import annotations

from pathlib import Path
from typing import List

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq
from loguru import logger


def sanitize_partition_values(
    df: pd.DataFrame,
    partition_cols: List[str],
) -> pd.DataFrame:
    """
    Sanitize partition column values to be filesystem-safe.

    This avoids issues with URL-encoded Hive partitions on Windows
    (e.g., '$', spaces, '%', '/').
    """
    for col in partition_cols:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
            .str.upper()
            .str.replace(r"[^\w\-]", "_", regex=True)
        )
    return df


def write_parquet(
    df: pd.DataFrame,
    output_dir: str | Path,
    partition_cols: List[str] | None = None,
    compression: str = "snappy",
) -> None:
    """
    Write DataFrame to a Parquet dataset with optional partitioning.

    Parameters
    ----------
    df : pd.DataFrame
        DataFrame to persist.
    output_dir : str or Path
        Directory where Parquet files will be written.
    partition_cols : list[str], optional
        Columns to partition by (e.g., ["company"]).
    compression : str
        Compression codec (e.g., "snappy", "zstd").

    Returns
    -------
    None
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        f"Writing Parquet dataset to {output_dir} | "
        f"rows: {len(df):,} | "
        f"compression: {compression} | "
        f"partition_cols: {partition_cols}"
    )

    # Sanitize partition values for cross-platform safety
    if partition_cols:
        df = sanitize_partition_values(df, partition_cols)

    # Convert to Arrow Table (memory-efficient)
    table = pa.Table.from_pandas(df, preserve_index=False)

    pq.write_to_dataset(
        table=table,
        root_path=output_dir,
        partition_cols=partition_cols,
        compression=compression,
    )

    logger.info("Parquet write completed successfully")
