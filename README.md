# NEPSE Trading Intelligence Dashboard

A production-grade Streamlit app for Nepal Stock Exchange (NEPSE) market analysis with smart money detection and institutional activity proxies.

## Features

- **Multi-source data pipeline** with automatic fallback (NEPSE API → ShareSansar → NepseAlpha → Cache)
- **Smart Money Score (0–100)** — composite institutional activity proxy
- **Order Flow Signals** — buy/sell pressure, persistence scores
- **Anomaly Detection** — volume spikes, turnover anomalies
- **Liquidity Analysis** — volatility rankings, price impact proxies
- **Interactive Plotly charts** — heatmaps, distributions, bubble charts
- **Crash-safe** — never fails, always shows best available data

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Run the app
streamlit run app.py
```

## Project Structure

```
nepse_app/
├── app.py              # Streamlit UI & layout
├── data_engine.py      # Normalization + analytics
├── charts.py           # All Plotly visualisations
├── utils.py            # Shared helpers & caching
├── requirements.txt
└── fetchers/
    ├── __init__.py
    ├── api.py          # NEPSE official API
    ├── sharesansar.py  # ShareSansar scraper
    └── nepsealpha.py   # NepseAlpha scraper
```

## Smart Money Score

| Component | Weight | Description |
|-----------|--------|-------------|
| Price Momentum | 30% | % change percentile rank |
| Volume Spike | 30% | Volume vs market median |
| Persistence | 25% | Magnitude × volume rank |
| Liquidity Impact | 15% | Inverted price impact |

Score range: **0–100** (higher = stronger smart money signal)

## Notes

- Designed for NEPSE trading hours (Sun–Thu, 11:00–15:00 NPT)
- Data refreshes every 5 minutes via Streamlit caching
- Falls back to demo data if all sources are unavailable
- No matplotlib used — all charts are Plotly
