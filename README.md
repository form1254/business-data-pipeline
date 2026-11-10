# Economic Data Pipeline

A small pipeline that collects EUR/USD exchange rates and World Bank macroeconomic indicators, saves them to a CSV, and displays them in a Streamlit dashboard. A GitHub Action refreshes the data every day.

## What it collects

**Forex (Type = `Forex`)**
- EUR/USD daily closing rate from Yahoo Finance (`EURUSD=X`) via `yfinance`, covering the most recent 14 days of history the API returns.
- Saved as `EUR_USD` (the close) and `USD_EUR` (1 divided by the close, rounded to 4 decimals).
- Because the window is calendar-based, weekends and market holidays mean fewer than 14 rows.

**Macro (Type = `Macro`)**
- Annual data for 1970 to 2024 from the World Bank API via `wbgapi`.
- Countries: USA and Germany (`DEU`).
- Indicators:
  - `GDP_Growth`: GDP growth, annual % (`NY.GDP.MKTP.KD.ZG`)
  - `Inflation`: consumer price inflation, annual % (`FP.CPI.TOTL.ZG`)
- Values are rounded to 2 decimals. Years with no World Bank value are left blank.

## Output

Everything goes into `data/economy_data.csv`, with these columns:

| Column    | Used by        | Notes                                             |
|-----------|----------------|---------------------------------------------------|
| Date      | Both           | Forex: `YYYY-MM-DD HH:MM`. Macro: `YYYY-01-01 00:00` |
| EUR_USD   | Forex          | Forex rows only                                   |
| USD_EUR   | Forex          | Forex rows only                                   |
| Country   | Macro          | Macro rows only (`USA`, `DEU`)                    |
| Metric    | Macro          | Macro rows only (`GDP_Growth`, `Inflation`)       |
| Value     | Macro          | Macro rows only                                   |
| Type      | Both           | `Forex` or `Macro`                                |

Each run rewrites the whole file. The pipeline does not keep a history beyond what the APIs return on that run.

## Project files

- `scraper.py`: fetches both data sets and writes `data/economy_data.csv`.
- `app.py`: Streamlit dashboard. The Forex tab shows the EUR/USD chart and table. The Macro tab lets you pick a metric and one or more countries, then shows a multi-line chart and a table.
- `requirements.txt`: Python dependencies for running locally.
- `.github/workflows/data_pipeline.yaml`: GitHub Action that runs the scraper and commits the updated CSV.

## Automation

The workflow runs every day at 00:00 UTC and can also be started by hand from the Actions tab (**Run workflow**). It:

1. Installs Python 3.11 and the packages `pandas`, `yfinance`, `wbgapi`, and `streamlit`.
2. Runs `python scraper.py`.
3. Commits `data/economy_data.csv` as `github-actions[bot]` if it changed. If there is nothing new, the step exits without error.

The workflow installs packages directly rather than from `requirements.txt`, so keep the two lists in sync when you add a dependency.

## Running locally

```bash
pip install -r requirements.txt

# Fetch fresh data (needs internet access)
python scraper.py

# Start the dashboard
streamlit run app.py
```

The dashboard reads `data/economy_data.csv` from the project folder, so run `streamlit run app.py` from the repository root.

## Limitations

- Only one currency pair and two countries are included. Adding more means changing the lists in `scraper.py` and the dropdowns in `app.py`.
- Macro data stops at 2024 because the code fetches 1970 to 2024 only.
- If the Yahoo Finance request fails, the scraper stops with an error and the CSV is not updated. The macro data is not saved either, because both sets are written together.
