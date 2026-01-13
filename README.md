# x-scrape

**Market Sentiment Pipeline for Indian Stock Discussions**

`x-scrape` is an end-to-end Python data pipeline that ingests short-form social media text related to the Indian stock market and converts it into **time-based sentiment signals with quantified uncertainty**.

The project emphasizes **robust pipeline design, reproducibility, and real-world engineering trade-offs**, rather than perfect data access.

---

## Key Goals

* Ingest Indian stock market–related discussions
* Clean, normalize, and deduplicate noisy text
* Store processed data efficiently in **Parquet**
* Extract numerical text features
* Aggregate sentiment into **trading-oriented signals**
* Quantify uncertainty using confidence intervals

---

## Data Collection Notes & Trade-offs

### Attempted (Primary)

- Selenium-based X/Twitter scraper using a logged-in Chrome profile  
- Tested across multiple Chrome and Chrome-for-Testing versions  
- Ultimately blocked by persistent Chrome DevTools / process creation failures on Windows  

These issues were reproducible and prevented reliable large-scale data ingestion despite extensive debugging.


### Alternatives Explored

- **snscrape**  
  Blocked for market-related queries and returned incomplete results  

- **Nitter-based scraping**  
  Partial success, but unreliable and inconsistent for sustained ingestion  


### Final Decision

A recent public **StockTwits dataset** focused on Indian stock market discussions was used to ensure full end-to-end pipeline completion.

All downstream stages (cleaning, feature extraction, storage, and signal aggregation) are **source-agnostic and unchanged**, allowing the pipeline to be easily reconnected to a live data source in the future.


### Trade-off Summary

- Prioritized **pipeline correctness and reproducibility** over fragile scraping logic  
- Ensured all processing and signal-generation components were exercised end-to-end  
- Accepted a static data source to avoid platform instability and access restrictions  

---

## Pipeline Overview

```
Raw Ingestion
→ Cleaning & Deduplication
→ Temporal Enrichment
→ Parquet Storage (Partitioned)
→ TF-IDF Feature Extraction
→ Signal Aggregation + Confidence Intervals
```

---

## Project Structure

```
x-scrape/
├── src/
│   ├── collect/                 # Data ingestion
│   │   ├── __init__.py
│   │   └── stocktwits_loader.py
│   │   └── twitter_selenium.py # Code for twitter scraping with selenium (not in use)
│   │   └── queries.py          # Queries for twitter scraping (not in use)
│   │
│   ├── process/                 # Cleaning, enrichment & storage
│   │   ├── __init__.py
│   │   ├── clean.py
│   │   ├── enrich.py
│   │   └── write_parquet.py
│   │
│   ├── features/                # Text feature extraction
│   │   ├── __init__.py
│   │   └── text_features.py
│   │
│   ├── signals/                 # Trading signal aggregation
│   │   ├── __init__.py
│   │   └── aggregate.py
│   │
│   └── run_pipeline.py          # Pipeline entry point
│
├── scripts/                     # Manual validation scripts
│   ├── __init__.py
│   ├── validate_parquet.py
│   ├── validate_features.py    
│   └── validate_signals.py
│
├── data/
│   ├── raw/                     # Raw ingestion input
│   │   └── stocktwits_raw.csv
│   │
│   └── processed/               # Generated output (gitignored)
│       └── stocktwits_parquet/
│
├── requirements.txt
├── README.md
└── .gitignore
```

---

## Setup

### 1. Clone & Create Environment

```bash
git clone <repository-url>
cd x-scrape
python -m venv venv
```

Activate the virtual environment:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Running the Pipeline

```bash
python -m src.run_pipeline
```

Output is written to:

```bash
data/processed/stocktwits_parquet/
```

---

## Validation Scripts

To ensure correctness and transparency at each major pipeline stage, lightweight validation scripts are provided.  
These scripts are intended for **manual sanity checks and reproducibility verification**, not full unit testing.

All scripts are executed as Python modules to ensure consistent import resolution.


## Feature Extraction Validation (`validate_features.py`)

```bash
python -m scripts.validate_features
```

## Signals Extraction Validation (`validate_signals.py`)

```bash
python -m scripts.validate_signals
```

---

## Feature Extraction

* TF-IDF with bounded vocabulary
* Unigrams + bigrams
* Sparse, memory-efficient representation

---

## Signal Construction & Uncertainty

| Sentiment | Score |
| --------- | ----- |
| Bullish   | +1    |
| Bearish   | −1    |
| Other     | 0     |

Aggregated over time windows with confidence intervals.

---

## Known Limitations

* Synthetic timestamps (used only for aggregation and uncertainty estimation)
* No real-time ingestion
* Sentiment ≠ price prediction

---

## Summary

This project demonstrates production-style pipeline design, explicit uncertainty handling, and transparent engineering trade-offs. Also, the processed dataset contains ~6,000+ messages, exceeding the minimum volume requirement.
