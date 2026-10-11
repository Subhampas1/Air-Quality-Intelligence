# 🌬️ Air Quality Intelligence & Pollution Risk Analysis Platform

> A professional multi-page Streamlit dashboard for historical air quality analysis across 26 Indian cities (2015–2020), built for the BharatCares data analytics challenge.

---

## Problem Statement

Air pollution is one of the most significant environmental health challenges in India. Despite a growing network of ambient air quality monitoring stations, the collected data is rarely synthesised into accessible, actionable intelligence for decision-makers and environmental practitioners.

This platform transforms raw historical air quality measurements into structured insights: identifying cities and periods with elevated pollution, surfacing patterns in pollutant behaviour, and providing evidence-based recommendations for further investigation.

The platform does **not** provide real-time monitoring, medical advice, or regulatory determinations. It is an analytical support tool grounded in historical data.

---

## Objectives

1. Enable exploration of AQI trends across 13 Indian cities over a 5.5-year historical period.
2. Identify cities and time periods with the highest frequency of elevated AQI observations.
3. Analyse pollutant concentration trends, distributions, and relationships with AQI.
4. Assign transparent, evidence-based risk tiers to cities based on observed AQI frequency.
5. Generate dynamic, data-driven findings and proportional recommendations.
6. Produce a professional, reproducible, and submission-ready analytics deliverable.

---

## Key Features

### Page 1 — Executive Overview
- Data coverage summary and KPI cards (total observations, valid AQI records, mean AQI, % high-AQI)
- National monthly AQI trend line with CPCB threshold reference lines
- City comparison bar chart (median AQI per city, colored by AQI bucket)
- AQI category distribution (% of valid observations in each CPCB bucket)
- Automatically calculated Key Findings, Priority Risks, and Recommended Actions

### Page 2 — City & Temporal Analysis
- Interactive city multi-select and date range filters
- Annual and monthly AQI trend charts per city
- Month × City AQI heatmap
- AQI distribution box plots per city
- Seasonal summary table (Winter / Pre-Monsoon / Monsoon / Post-Monsoon)
- Top-20 highest AQI observations table
- Raw data table (paginated)

### Page 3 — Pollutant Analysis
- Pollutant availability summary (% missing per pollutant)
- Monthly concentration trend per pollutant, by city
- City-level concentration distribution (box plots)
- Full pollutant correlation matrix (12 pollutants + AQI)
- Scatter plot: selected pollutant vs AQI with OLS trendline

### Page 4 — Pollution Risk & Action Center
- Transparent risk tier classification (High / Moderate / Low Concern)
- City risk summary table with multiple AQI threshold metrics
- Frequency of Very Poor / Severe AQI observations bar chart
- Year × Month AQI heatmap
- Most concerning city-month periods (top 15 by median AQI)
- Year-over-year AQI change table per city
- Evidence-linked dynamic findings and recommendations

---

## Dataset Description

### Primary: `city_day.csv`

| Property | Value |
|---|---|
| Rows | 29,531 |
| Columns | 16 |
| Date range | 2015-01-01 to 2020-07-01 |
| Unique cities | 26 |
| AQI coverage | 84.1% of rows have valid AQI (24,850 rows); 15.9% missing |

**Columns:**

| Column | Type | Description |
|---|---|---|
| City | string | Indian city name |
| Date | date | Observation date (YYYY-MM-DD) |
| PM2.5 | float | Particulate Matter < 2.5 µm (µg/m³) |
| PM10 | float | Particulate Matter < 10 µm (µg/m³) |
| NO | float | Nitric Oxide (µg/m³) |
| NO2 | float | Nitrogen Dioxide (µg/m³) |
| NOx | float | Nitrogen Oxides (µg/m³) |
| NH3 | float | Ammonia (µg/m³) |
| CO | float | Carbon Monoxide (mg/m³) |
| SO2 | float | Sulphur Dioxide (µg/m³) |
| O3 | float | Ozone (µg/m³) |
| Benzene | float | Benzene (µg/m³) |
| Toluene | float | Toluene (µg/m³) |
| Xylene | float | Xylene (µg/m³) |
| AQI | float | India CPCB National AQI value |
| AQI_Bucket | string | AQI category (Good / Satisfactory / Moderate / Poor / Very Poor / Severe) |

**Cities (26):** Ahmedabad, Aizawl, Amaravati, Amritsar, Bengaluru, Bhopal, Brajrajnagar, Chandigarh, Chennai, Coimbatore, Delhi, Ernakulam, Gurugram, Guwahati, Hyderabad, Jaipur, Jorapokhar, Kochi, Kolkata, Lucknow, Mumbai, Patna, Shillong, Talcher, Thiruvananthapuram, Visakhapatnam

### Supplementary: `stations.csv`

| Property | Value |
|---|---|
| Rows | 230 |
| Columns | 5 (StationId, StationName, City, State, Status) |
| Purpose | Provides State name and station count per city |
| Limitation | No geographic coordinates — geographic map not implemented |

### Dataset Source

The dataset is referenced from:

> **Kaggle — Air Quality Data in India**
> https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india

_Note: The dataset files were downloaded from this source. Please verify the specific version and any licence terms on the Kaggle dataset page before redistribution._

---

## Data Preparation Methodology

1. **Date parsing:** `Date` column parsed as `datetime64` using `pd.to_datetime(errors='coerce')`. Rows with unparseable dates are dropped and counted.
2. **Type standardisation:** All pollutant and AQI columns cast to `float64`. Non-numeric values become `NaN`.
3. **Missing values:** Retained as `NaN` throughout. Never replaced with zero. All KPIs exclude `NaN` from AQI calculations.
4. **Duplicate removal:** Rows with duplicate `(City, Date)` combinations are identified; first occurrence is retained.
5. **AQI_Bucket validation:** Values not matching the six known CPCB categories are set to `NaN`.
6. **Derived columns added:** `Year`, `Month`, `MonthName`, `Season`, `YearMonth` (Period).
7. **Season mapping:** Winter = Dec–Feb, Pre-Monsoon = Mar–May, Monsoon = Jun–Sep, Post-Monsoon = Oct–Nov.
8. **Station enrichment:** `stations.csv` joined on `City` to add `State` and `StationCount` columns (left join — all city_day rows retained).

---

## KPI Definitions

| KPI | Definition | Denominator |
|---|---|---|
| Total Observations | Count of all rows in filtered dataset | All rows |
| Valid AQI Records | Count of rows where AQI is not null | All rows |
| % AQI Missing | (Total rows − Valid AQI rows) / Total rows × 100 | All rows |
| Cities Covered | Count of distinct City values | All rows |
| Mean AQI | Arithmetic mean of AQI | Valid AQI rows only |
| Median AQI | Median of AQI | Valid AQI rows only |
| Max Observed AQI | Maximum AQI value with city and date | Valid AQI rows only |
| % Obs with AQI > 200 | Rows where AQI > 200 / Valid AQI rows × 100 | Valid AQI rows only |
| % Obs with AQI > 300 | Rows where AQI > 300 / Valid AQI rows × 100 | Valid AQI rows only |
| % Obs with AQI > 400 | Rows where AQI > 400 / Valid AQI rows × 100 | Valid AQI rows only |
| AQI Bucket Distribution | Count and % per CPCB category | Valid AQI rows with non-null AQI_Bucket |

**AQI Scale (India CPCB National AQI):**

| Category | AQI Range |
|---|---|
| Good | 0 – 50 |
| Satisfactory | 51 – 100 |
| Moderate | 101 – 200 |
| Poor | 201 – 300 |
| Very Poor | 301 – 400 |
| Severe | > 400 |

---

## Technology Stack

| Component | Library / Version |
|---|---|
| Dashboard framework | Streamlit ≥ 1.28 |
| Data manipulation | Pandas ≥ 2.0, NumPy ≥ 1.24 |
| Visualisation | Plotly ≥ 5.15 |
| Language | Python 3.9+ |

---

## Installation Instructions

### Prerequisites
- Python 3.9 or later
- pip

### Steps

```bash
# 1. Clone or download the project
git clone <your-repo-url>
cd <project-folder>

# 2. (Recommended) Create and activate a virtual environment
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Ensure datasets are present
# The following files must be in the same directory as air_quality_app.py:
#   city_day.csv
#   stations.csv
```

---

## How to Run

```bash
streamlit run air_quality_app.py
```

The application will open in your default browser at `http://localhost:8501`.

---

## Expected Project Structure

```
project-root/
├── air_quality_app.py       # Main Streamlit application (single file)
├── requirements.txt         # Python dependencies
├── README.md                # This file
├── project_report.docx      # Project report (Word format)
├── city_day.csv             # Primary dataset — DO NOT MODIFY
├── stations.csv             # Station metadata — DO NOT MODIFY
└── screenshots/             # Application screenshots (optional)
    ├── page1_overview.png
    ├── page2_city_temporal.png
    ├── page3_pollutant.png
    └── page4_risk.png
```

---

## Important Assumptions and Limitations

1. **Historical data only:** The dataset covers 2015-01-01 to 2020-07-01. No real-time or near-real-time data is used or implied.
2. **City-level aggregation:** Each row represents a city-level daily observation, not a specific monitoring station within that city. Station-level spatial variation within a city is not captured.
3. **Missing data:** Approximately 35% of rows have no valid AQI value. The missing fraction is higher in 2015–2016. All statistics exclude missing values — they are never imputed as zero.
4. **No geographic map:** `stations.csv` contains no latitude/longitude columns. Geographic mapping has been omitted to avoid fabricated coordinates.
5. **No predictive model:** With 13 cities and significant missing data in early years, the dataset does not support a defensible AQI forecasting model. The platform delivers descriptive analytics only.
6. **AQI scale:** India CPCB National AQI is used throughout. The `AQI_Bucket` values already present in the dataset have been validated against this scale.
7. **Correlation ≠ causation:** Pollutant–AQI correlations are influenced by the mathematical definition of AQI (derived from pollutant sub-indices). High correlation does not imply a single pollutant is the cause of elevated AQI.
8. **Seasonal definitions:** Standard Indian meteorological seasons are applied (Winter, Pre-Monsoon, Monsoon, Post-Monsoon). No statistical significance test has been applied to seasonal differences.
9. **Risk tiers:** Risk classifications (High / Moderate / Low Concern) are analytical indicators based on frequency thresholds. They are not official regulatory determinations.
10. **Year-over-year comparisons:** Only city-year pairs with ≥ 30 valid AQI observations are included in trend comparisons to avoid spurious results from sparse data.

---

## Screenshots

Screenshots are generated from the running application. To capture them:

1. Run the application: `streamlit run air_quality_app.py`
2. Navigate to each page and take a full-page screenshot.
3. Save screenshots to the `screenshots/` directory.

_See the `screenshots/` directory for application visuals (added after launch)._

---

## Dataset Reference

- Rao, Rohan. *Air Quality Data in India*. Kaggle, 2020.
  https://www.kaggle.com/datasets/rohanrao/air-quality-data-in-india

---

## Disclaimer

This platform is built as an educational and analytical project for the BharatCares data analytics challenge. It is not an official air quality monitoring service, medical diagnostic tool, or regulatory instrument. All findings are observational and based on a historical dataset.
