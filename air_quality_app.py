"""
Air Quality Intelligence & Pollution Risk Analysis Platform
============================================================
Multi-page Streamlit dashboard — 26 Indian cities, 2015–2020.
Primary dataset : city_day.csv  (29,531 rows, 16 columns)
Supplementary   : stations.csv (230 rows — City/State/StationId, no coordinates)
AQI Scale       : India CPCB National AQI (6 buckets, Good–Severe)
Disclaimer      : Analytical support tool using historical data only.
                  Not an official regulatory service or medical system.
"""

import os
import warnings

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

warnings.filterwarnings("ignore")

# ── Constants ────────────────────────────────────────────────────────────────

AQI_COLORS = {
    "Good":         "#16a34a",
    "Satisfactory": "#ca8a04",
    "Moderate":     "#ea580c",
    "Poor":         "#dc2626",
    "Very Poor":    "#7c3aed",
    "Severe":       "#4c0519",
}
AQI_BUCKET_ORDER = ["Good", "Satisfactory", "Moderate", "Poor", "Very Poor", "Severe"]

SEASON_MAP = {
    12: "Winter",       1: "Winter",        2: "Winter",
    3:  "Pre-Monsoon",  4: "Pre-Monsoon",   5: "Pre-Monsoon",
    6:  "Monsoon",      7: "Monsoon",        8: "Monsoon",   9: "Monsoon",
    10: "Post-Monsoon", 11: "Post-Monsoon",
}

POLLUTANT_UNITS = {
    "PM2.5": "µg/m³", "PM10": "µg/m³",
    "NO":    "µg/m³", "NO2":  "µg/m³", "NOx": "µg/m³",
    "NH3":   "µg/m³", "SO2":  "µg/m³", "O3":  "µg/m³",
    "CO":    "mg/m³",
    "Benzene": "µg/m³", "Toluene": "µg/m³", "Xylene": "µg/m³",
}
POLLUTANTS = list(POLLUTANT_UNITS.keys())

DATA_DIR       = os.path.dirname(os.path.abspath(__file__))
CITY_DAY_PATH  = os.path.join(DATA_DIR, "city_day.csv")
STATIONS_PATH  = os.path.join(DATA_DIR, "stations.csv")

# ── Premium CSS ──────────────────────────────────────────────────────────────

GLOBAL_CSS = """
<style>
/* ── Reset & base ─────────────────────────────────────────── */
html, body, [class*="css"] {
    font-family: -apple-system, "Segoe UI", system-ui, BlinkMacSystemFont, sans-serif;
}

/* ── App background ───────────────────────────────────────── */
.stApp { background: #F6F8FB; }
section[data-testid="stSidebar"] > div { background: #0F1923; }

/* ── Hide Streamlit chrome ────────────────────────────────── */
#MainMenu, footer { visibility: hidden; }
/* Keep header visible but hide internal deploy/menu chrome,
   while showing the sidebar collapse toggle. */
header { visibility: visible; background: transparent !important;
         box-shadow: none !important; }
header [data-testid="stToolbar"],
header [data-testid="stDecoration"],
header [data-testid="stStatusWidget"],
header [data-testid="stAppViewBlockContainer"] > div:first-child { visibility: hidden; }
/* ── Sidebar collapse/expand button ──────────────────────── */
[data-testid="stSidebarCollapseButton"] {
    visibility: visible !important;
    opacity: 1 !important;
    pointer-events: auto !important;
    position: fixed !important;
    top: 10px !important;
    left: 10px !important;
    z-index: 9999 !important;
    background: #0F766E !important;
    border: none !important;
    border-radius: 6px !important;
    width: 32px !important;
    height: 32px !important;
    display: flex !important;
    align-items: center !important;
    justify-content: center !important;
    cursor: pointer !important;
    box-shadow: 0 2px 8px rgba(15,118,110,0.25) !important;
    transition: background 0.15s ease !important;
}
[data-testid="stSidebarCollapseButton"]:hover {
    background: #0D9488 !important;
}
[data-testid="stSidebarCollapseButton"] svg {
    stroke: #FFFFFF !important;
    width: 16px !important;
    height: 16px !important;
}

/* ── Sidebar text / controls ─────────────────────────────── */
section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
section[data-testid="stSidebar"] .stRadio label { color: #CBD5E1 !important; }
section[data-testid="stSidebar"] .stRadio [data-testid="stMarkdownContainer"] p {
    font-size: 0.82rem; letter-spacing: 0.02em;
}
section[data-testid="stSidebar"] hr { border-color: #1E2D3D !important; }
section[data-testid="stSidebar"] [data-testid="stSidebarNav"] { display: none; }

/* ── Sidebar nav radio ────────────────────────────────────── */
section[data-testid="stSidebar"] .stRadio > div {
    gap: 2px;
}
section[data-testid="stSidebar"] .stRadio label div p {
    font-size: 0.88rem !important;
    padding: 6px 0;
}

/* ── Main content padding ─────────────────────────────────── */
.block-container {
    padding-top: 1.6rem !important;
    padding-bottom: 2rem !important;
    max-width: 1280px;
}

/* ── Page header band ─────────────────────────────────────── */
.page-header {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 20px 24px 16px;
    margin-bottom: 20px;
}
.page-header h1 {
    font-size: 1.45rem !important;
    font-weight: 700;
    color: #0F1923 !important;
    margin: 0 0 4px !important;
    letter-spacing: -0.02em;
}
.page-header p {
    font-size: 0.84rem;
    color: #64748B;
    margin: 0;
    line-height: 1.5;
}
.page-header .badge {
    display: inline-block;
    background: #F1F5F9;
    border: 1px solid #CBD5E1;
    color: #475569;
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.04em;
    padding: 2px 8px;
    border-radius: 4px;
    text-transform: uppercase;
    margin-right: 6px;
}

/* ── KPI card grid ────────────────────────────────────────── */
.kpi-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 12px;
    margin-bottom: 20px;
}
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 16px 18px;
    display: flex;
    flex-direction: column;
    gap: 4px;
}
.kpi-label {
    font-size: 0.72rem;
    font-weight: 600;
    letter-spacing: 0.06em;
    text-transform: uppercase;
    color: #94A3B8;
}
.kpi-value {
    font-size: 1.65rem;
    font-weight: 700;
    letter-spacing: -0.03em;
    color: #0F1923;
    line-height: 1.1;
}
.kpi-sub {
    font-size: 0.72rem;
    color: #94A3B8;
    margin-top: 2px;
}
.kpi-accent { color: #0F766E; }

/* ── Section heading ──────────────────────────────────────── */
.section-heading {
    font-size: 0.78rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    color: #94A3B8;
    margin: 20px 0 10px;
    border-bottom: 1px solid #E2E8F0;
    padding-bottom: 6px;
}

/* ── Chart card ───────────────────────────────────────────── */
.chart-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 4px 4px 0;
    margin-bottom: 12px;
}

/* ── Insight card ─────────────────────────────────────────── */
.insight-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-left: 3px solid #0F766E;
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 10px;
}
.insight-title {
    font-size: 0.88rem;
    font-weight: 600;
    color: #0F1923;
    margin-bottom: 6px;
}
.insight-value {
    font-size: 0.82rem;
    color: #0F766E;
    font-weight: 600;
    margin-bottom: 4px;
}
.insight-body {
    font-size: 0.80rem;
    color: #475569;
    line-height: 1.55;
}
.insight-rec {
    font-size: 0.78rem;
    color: #64748B;
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px dashed #E2E8F0;
}
.insight-caveat {
    font-size: 0.72rem;
    color: #94A3B8;
    margin-top: 4px;
    font-style: italic;
}

/* ── Risk badge ───────────────────────────────────────────── */
.risk-high     { color: #991B1B; background: #FEF2F2; border: 1px solid #FECACA;
                 padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight:600; }
.risk-moderate { color: #92400E; background: #FFFBEB; border: 1px solid #FDE68A;
                 padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight:600; }
.risk-low      { color: #166534; background: #F0FDF4; border: 1px solid #BBF7D0;
                 padding: 2px 8px; border-radius: 4px; font-size: 0.75rem; font-weight:600; }

/* ── Metric override ──────────────────────────────────────── */
[data-testid="stMetricValue"] { font-size: 1.5rem !important; font-weight: 700 !important; color: #0F1923 !important; }
[data-testid="stMetricLabel"] { font-size: 0.72rem !important; color: #94A3B8 !important;
                                 font-weight: 600 !important; letter-spacing: 0.04em !important; text-transform: uppercase; }

/* ── DataFrame ────────────────────────────────────────────── */
[data-testid="stDataFrame"] { border-radius: 8px; overflow: hidden; border: 1px solid #E2E8F0; }

/* ── Expander ─────────────────────────────────────────────── */
details[data-testid="stExpander"] {
    background: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 8px;
    padding: 0 4px; margin-bottom: 8px;
}
details[data-testid="stExpander"] summary { font-size: 0.84rem; font-weight: 600; color: #334155; }

/* ── Sidebar brand ────────────────────────────────────────── */
.sidebar-brand {
    padding: 20px 0 14px;
    border-bottom: 1px solid #1E2D3D;
    margin-bottom: 8px;
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
}
.sidebar-logo-mark {
    width: 36px;
    height: 36px;
    background: rgba(15, 118, 110, 0.15);
    border: 1px solid rgba(15, 118, 110, 0.30);
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.sidebar-brand-text {
    display: flex;
    flex-direction: column;
    gap: 2px;
}
.sidebar-brand-title {
    font-size: 0.65rem !important;
    font-weight: 800 !important;
    letter-spacing: 0.16em !important;
    text-transform: uppercase !important;
    color: #E2E8F0 !important;
    line-height: 1.2 !important;
}
.sidebar-brand-sub {
    font-size: 0.60rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.10em !important;
    text-transform: uppercase !important;
    color: #0F766E !important;
    line-height: 1.2 !important;
}
.sidebar-coverage {
    font-size: 0.70rem;
    color: #64748B;
    margin-top: 2px;
    line-height: 1.5;
}

/* ── Warning / info overrides ─────────────────────────────── */
[data-testid="stAlert"] { border-radius: 8px; font-size: 0.82rem; }

/* ── Selectbox / multiselect ──────────────────────────────── */
[data-testid="stSelectbox"] label,
[data-testid="stMultiSelect"] label,
[data-testid="stDateInput"] label {
    font-size: 0.75rem !important;
    font-weight: 600 !important;
    letter-spacing: 0.04em !important;
    text-transform: uppercase !important;
    color: #94A3B8 !important;
}

/* ── App header ───────────────────────────────────────────── */
.app-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 10px;
    padding: 12px 20px;
    margin-bottom: 18px;
    flex-wrap: wrap;
    gap: 8px;
}
.app-header-left {
    display: flex;
    align-items: center;
    gap: 12px;
}
.app-header-icon {
    width: 32px;
    height: 32px;
    background: #F0FDF9;
    border: 1px solid #CCFBF1;
    border-radius: 8px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
}
.app-header-identity {
    display: flex;
    flex-direction: column;
    gap: 1px;
}
.app-header-name {
    font-size: 1.15rem;
    font-weight: 700;
    color: #0F1923;
    letter-spacing: -0.02em;
    line-height: 1.2;
}
.app-header-label {
    font-size: 0.65rem;
    font-weight: 700;
    letter-spacing: 0.12em;
    text-transform: uppercase;
    color: #94A3B8;
    line-height: 1;
}
.app-header-right {
    display: flex;
    align-items: center;
    gap: 10px;
    flex-wrap: wrap;
}
.app-header-badge {
    display: inline-block;
    background: #F0FDF9;
    border: 1px solid #CCFBF1;
    color: #0F766E;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    padding: 3px 9px;
    border-radius: 20px;
}
.app-header-period {
    font-size: 0.78rem;
    font-weight: 600;
    color: #334155;
}
.app-header-stats {
    font-size: 0.72rem;
    color: #94A3B8;
}
.app-header-divider {
    width: 1px;
    height: 18px;
    background: #E2E8F0;
    display: inline-block;
}
</style>
"""

# ── App header ───────────────────────────────────────────────────────────────

_ICON_SVG = (
    '<svg width="16" height="16" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">'
    '<circle cx="8" cy="8" r="7" stroke="#0F766E" stroke-width="1.5"/>'
    '<path d="M4 11 L6.5 7.5 L8.5 9.5 L11 6" stroke="#0F766E" stroke-width="1.5"'
    ' stroke-linecap="round" stroke-linejoin="round"/>'
    '<circle cx="11" cy="6" r="1.2" fill="#0F766E"/>'
    '</svg>'
)


def render_app_header(meta: dict) -> None:
    """
    Render a compact, horizontal application identity header.

    Displays: icon · 'Air Quality Intelligence' · 'POLLUTION ANALYTICS PLATFORM'
    on the left, and a 'HISTORICAL DATA' badge + dataset period on the right.

    Uses actual dates from the loaded metadata — never hardcoded.
    """
    d_min = meta["date_min"].strftime("%b %Y")
    d_max = meta["date_max"].strftime("%b %Y")
    n_rows   = f"{meta['total_rows']:,}"
    n_cities = meta["n_cities"]

    st.markdown(
        f'<div class="app-header">'
        # ── Left ──────────────────────────────────────────────
        f'<div class="app-header-left">'
        f'  <div class="app-header-icon">{_ICON_SVG}</div>'
        f'  <div class="app-header-identity">'
        f'    <span class="app-header-name">Air Quality Intelligence</span>'
        f'    <span class="app-header-label">Pollution Analytics Platform</span>'
        f'  </div>'
        f'</div>'
        # ── Right ─────────────────────────────────────────────
        f'<div class="app-header-right">'
        f'  <span class="app-header-badge">Historical Data</span>'
        f'  <span class="app-header-divider"></span>'
        f'  <span class="app-header-period">{d_min} – {d_max}</span>'
        f'  <span class="app-header-divider"></span>'
        f'  <span class="app-header-stats">{n_rows} records · {n_cities} cities</span>'
        f'</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


# ── Design helpers ────────────────────────────────────────────────────────────

def _chart_style(fig, title: str = "", height: int = 380) -> go.Figure:
    """Apply consistent premium chart styling to any Plotly figure."""
    fig.update_layout(
        title=dict(text=title, font=dict(size=13, color="#334155", weight=600), x=0, pad=dict(l=4, t=4)),
        height=height,
        margin=dict(l=36, r=16, t=44 if title else 16, b=36),
        paper_bgcolor="white",
        plot_bgcolor="white",
        font=dict(family="-apple-system, 'Segoe UI', system-ui, sans-serif", size=11, color="#334155"),
        legend=dict(
            bgcolor="rgba(255,255,255,0.95)",
            bordercolor="#E2E8F0",
            borderwidth=1,
            font=dict(size=11),
        ),
        xaxis=dict(
            gridcolor="#F1F5F9", linecolor="#E2E8F0", linewidth=1,
            tickfont=dict(size=10, color="#64748B"),
            title_font=dict(size=11, color="#64748B"),
        ),
        yaxis=dict(
            gridcolor="#F1F5F9", linecolor="#E2E8F0", linewidth=1,
            tickfont=dict(size=10, color="#64748B"),
            title_font=dict(size=11, color="#64748B"),
        ),
        hoverlabel=dict(
            bgcolor="white", bordercolor="#E2E8F0",
            font=dict(size=12, color="#0F1923"),
        ),
    )
    return fig


def page_header(title: str, subtitle: str, badge: str = "") -> None:
    badge_html = f'<span class="badge">{badge}</span> ' if badge else ""
    st.markdown(
        f'<div class="page-header">'
        f'<h1>{badge_html}{title}</h1>'
        f'<p>{subtitle}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )


def section_heading(label: str) -> None:
    st.markdown(f'<div class="section-heading">{label}</div>', unsafe_allow_html=True)


def kpi_cards(items: list) -> None:
    """
    items: list of (label, value, subtext, accent)
    accent=True uses teal color for the value.
    """
    cols_html = ""
    for label, value, subtext, accent in items:
        val_class = "kpi-value kpi-accent" if accent else "kpi-value"
        cols_html += (
            f'<div class="kpi-card">'
            f'<span class="kpi-label">{label}</span>'
            f'<span class="{val_class}">{value}</span>'
            f'<span class="kpi-sub">{subtext}</span>'
            f'</div>'
        )
    st.markdown(f'<div class="kpi-grid">{cols_html}</div>', unsafe_allow_html=True)


def render_insight(insight: dict, index: int) -> None:
    st.markdown(
        f'<div class="insight-card">'
        f'<div class="insight-title">{index}. {insight["finding"]}</div>'
        f'<div class="insight-value">{insight["value"]}</div>'
        f'<div class="insight-body">'
        f'{insight["interpretation"]}'
        f'</div>'
        f'<div class="insight-rec"><b>Next step:</b> {insight["recommendation"]}</div>'
        f'<div class="insight-caveat">{insight["caveat"]}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )


def chart_card(fig, key: str) -> None:
    """Wrap a Plotly chart in a white card and render it."""
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, key=key)
    st.markdown('</div>', unsafe_allow_html=True)


def empty_state(message: str) -> None:
    st.markdown(
        f'<div style="background:#F8FAFC;border:1px dashed #CBD5E1;border-radius:8px;'
        f'padding:24px;text-align:center;color:#94A3B8;font-size:0.85rem;">{message}</div>',
        unsafe_allow_html=True,
    )


# ── Data loading ──────────────────────────────────────────────────────────────

@st.cache_data(show_spinner="Loading datasets…")
def load_data():
    if not os.path.exists(CITY_DAY_PATH):
        st.error(f"Dataset not found: {CITY_DAY_PATH}")
        st.stop()

    df = pd.read_csv(CITY_DAY_PATH)

    expected = {"City", "Date", "AQI", "AQI_Bucket"} | set(POLLUTANTS)
    missing  = expected - set(df.columns)
    if missing:
        st.error(f"city_day.csv is missing columns: {missing}")
        st.stop()

    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    invalid_dates = df["Date"].isna().sum()

    for col in POLLUTANTS + ["AQI"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    if invalid_dates > 0:
        df = df.dropna(subset=["Date"])

    before = len(df)
    df = df.drop_duplicates(subset=["City", "Date"], keep="first")
    dupes_dropped = before - len(df)

    df["City"]       = df["City"].str.strip()
    df["AQI_Bucket"] = df["AQI_Bucket"].str.strip()
    df.loc[~df["AQI_Bucket"].isin(set(AQI_BUCKET_ORDER)) & df["AQI_Bucket"].notna(), "AQI_Bucket"] = np.nan

    df["Year"]      = df["Date"].dt.year.astype("Int64")
    df["Month"]     = df["Date"].dt.month.astype("Int64")
    df["MonthName"] = df["Date"].dt.strftime("%b")
    df["Season"]    = df["Month"].map(SEASON_MAP)
    df["YearMonth"] = df["Date"].dt.to_period("M")

    station_info = pd.DataFrame(columns=["City", "State", "StationCount"])
    if os.path.exists(STATIONS_PATH):
        try:
            sdf = pd.read_csv(STATIONS_PATH, encoding="utf-8-sig")
            sdf.columns = sdf.columns.str.strip()
            sdf["City"] = sdf["City"].str.strip()
            stn_count  = sdf.groupby("City").size().reset_index(name="StationCount")
            state_map  = sdf.groupby("City")["State"].first().reset_index()
            station_info = stn_count.merge(state_map, on="City", how="left")
        except Exception:
            pass

    if not station_info.empty:
        df = df.merge(station_info[["City", "State", "StationCount"]], on="City", how="left")
    else:
        df["State"] = np.nan
        df["StationCount"] = np.nan

    valid_aqi  = df["AQI"].notna().sum()
    total_rows = len(df)
    meta = {
        "total_rows":         total_rows,
        "valid_aqi_rows":     int(valid_aqi),
        "pct_aqi_missing":    round((total_rows - valid_aqi) / total_rows * 100, 1),
        "date_min":           df["Date"].min(),
        "date_max":           df["Date"].max(),
        "n_cities":           df["City"].nunique(),
        "duplicates_dropped": dupes_dropped,
        "cities":             sorted(df["City"].unique().tolist()),
        "station_info":       station_info,
    }
    return df, station_info, meta


# ── KPI calculations ──────────────────────────────────────────────────────────

def calculate_kpis(df: pd.DataFrame) -> dict:
    total_rows = len(df)
    aqi_df     = df.dropna(subset=["AQI"])
    valid_aqi  = len(aqi_df)
    if total_rows == 0:
        return {"error": "No data available for selected filters."}

    kpis = {
        "total_rows":       total_rows,
        "valid_aqi_rows":   valid_aqi,
        "pct_aqi_missing":  round((total_rows - valid_aqi) / total_rows * 100, 1),
        "n_cities":         df["City"].nunique(),
        "date_min":         df["Date"].min(),
        "date_max":         df["Date"].max(),
        "mean_aqi":         round(aqi_df["AQI"].mean(),   1) if valid_aqi else None,
        "median_aqi":       round(aqi_df["AQI"].median(), 1) if valid_aqi else None,
        "max_aqi": None, "max_aqi_city": None, "max_aqi_date": None,
        "min_aqi": None, "min_aqi_city": None, "min_aqi_date": None,
        "pct_above_200": None, "pct_above_300": None, "pct_above_400": None,
        "aqi_bucket_dist": {},
    }
    if valid_aqi:
        idx_max = aqi_df["AQI"].idxmax()
        kpis["max_aqi"]      = round(aqi_df.loc[idx_max, "AQI"], 1)
        kpis["max_aqi_city"] = aqi_df.loc[idx_max, "City"]
        kpis["max_aqi_date"] = aqi_df.loc[idx_max, "Date"].strftime("%d %b %Y")
        idx_min = aqi_df["AQI"].idxmin()
        kpis["min_aqi"]      = round(aqi_df.loc[idx_min, "AQI"], 1)
        kpis["min_aqi_city"] = aqi_df.loc[idx_min, "City"]
        kpis["min_aqi_date"] = aqi_df.loc[idx_min, "Date"].strftime("%d %b %Y")
        kpis["pct_above_200"] = round((aqi_df["AQI"] > 200).sum() / valid_aqi * 100, 1)
        kpis["pct_above_300"] = round((aqi_df["AQI"] > 300).sum() / valid_aqi * 100, 1)
        kpis["pct_above_400"] = round((aqi_df["AQI"] > 400).sum() / valid_aqi * 100, 1)
        bc = aqi_df["AQI_Bucket"].value_counts()
        kpis["aqi_bucket_dist"] = {
            b: {"count": int(bc.get(b, 0)), "pct": round(bc.get(b, 0) / valid_aqi * 100, 1)}
            for b in AQI_BUCKET_ORDER
        }
    return kpis


def calculate_city_summary(df: pd.DataFrame) -> pd.DataFrame:
    records = []
    for city, cdf in df.groupby("City"):
        v = cdf["AQI"].dropna()
        n = len(v)
        records.append({
            "City":          city,
            "Total Obs":     len(cdf),
            "Valid AQI Obs": n,
            "Median AQI":    round(v.median(), 1) if n else None,
            "Mean AQI":      round(v.mean(),   1) if n else None,
            "% AQI > 200":   round((v > 200).sum() / n * 100, 1) if n else None,
            "% AQI > 300":   round((v > 300).sum() / n * 100, 1) if n else None,
            "% AQI > 400":   round((v > 400).sum() / n * 100, 1) if n else None,
        })
    return pd.DataFrame(records).sort_values("Median AQI", ascending=False, na_position="last")


def calculate_monthly_trend(df: pd.DataFrame) -> pd.DataFrame:
    aqi_df = df.dropna(subset=["AQI"]).copy()
    if aqi_df.empty:
        return pd.DataFrame()
    monthly = (
        aqi_df.groupby("YearMonth")
        .agg(MedianAQI=("AQI", "median"), Count=("AQI", "count"))
        .reset_index()
    )
    monthly["Date"] = monthly["YearMonth"].dt.to_timestamp()
    return monthly.sort_values("Date")


def calculate_seasonal_summary(df: pd.DataFrame) -> pd.DataFrame:
    aqi_df = df.dropna(subset=["AQI"])
    if aqi_df.empty:
        return pd.DataFrame()
    order   = ["Winter", "Pre-Monsoon", "Monsoon", "Post-Monsoon"]
    summary = (
        aqi_df.groupby(["City", "Season"])
        .agg(MedianAQI=("AQI", "median"), Count=("AQI", "count"))
        .reset_index()
    )
    summary["Season"] = pd.Categorical(summary["Season"], categories=order, ordered=True)
    return summary.sort_values(["City", "Season"])


# ── Insights engine ───────────────────────────────────────────────────────────

def _aqi_to_bucket(v: float) -> str:
    if pd.isna(v):    return "Unknown"
    if v <= 50:       return "Good"
    if v <= 100:      return "Satisfactory"
    if v <= 200:      return "Moderate"
    if v <= 300:      return "Poor"
    if v <= 400:      return "Very Poor"
    return "Severe"


def generate_insights(df: pd.DataFrame, min_obs: int = 30) -> list:
    insights = []
    caveat   = "Analytical observation from historical data (2015–2020). Not an official regulatory determination."
    aqi_df   = df.dropna(subset=["AQI"])

    if len(aqi_df) < min_obs:
        insights.append({
            "finding":        "Insufficient data for insights",
            "value":          f"{len(aqi_df)} valid AQI observations",
            "location":       "All selected cities",
            "period":         "Selected date range",
            "interpretation": "Fewer than the minimum required observations for reliable insights.",
            "recommendation": "Broaden the city selection or date range.",
            "caveat":         caveat,
        })
        return insights

    # Insight 1 — city with highest median AQI
    city_medians = (
        aqi_df.groupby("City").filter(lambda g: len(g) >= min_obs)
        .groupby("City")["AQI"].median()
    )
    if not city_medians.empty:
        wc   = city_medians.idxmax()
        wmed = round(city_medians.max(), 1)
        n    = int(aqi_df[aqi_df["City"] == wc]["AQI"].count())
        insights.append({
            "finding":        f"{wc} has the highest median AQI among cities with sufficient data",
            "value":          f"Median AQI {wmed} · {n:,} valid observations",
            "location":       wc,
            "period":         f"{df['Date'].min().strftime('%b %Y')} – {df['Date'].max().strftime('%b %Y')}",
            "interpretation": f"Median AQI {wmed} falls in the '{_aqi_to_bucket(wmed)}' category (CPCB scale). Median used to reduce sensitivity to extreme values.",
            "recommendation": f"Review monitoring coverage in {wc} and identify which pollutants are elevated during high-AQI episodes.",
            "caveat":         caveat,
        })

    # Insight 2 — month with highest % AQI > 200
    high = aqi_df[aqi_df["AQI"] > 200]
    if not high.empty:
        mc   = high.groupby("Month")["AQI"].count()
        tc   = aqi_df.groupby("Month")["AQI"].count()
        pct  = (mc / tc * 100).dropna()
        if not pct.empty:
            wm   = int(pct.idxmax())
            wmn  = pd.Timestamp(2020, wm, 1).strftime("%B")
            wpct = round(pct.max(), 1)
            insights.append({
                "finding":        f"{wmn} has the highest proportion of AQI > 200 observations",
                "value":          f"{wpct}% of {wmn} observations exceed AQI 200",
                "location":       "All selected cities",
                "period":         "Across all available years",
                "interpretation": f"{wpct}% of {wmn} observations fell in Poor, Very Poor, or Severe categories. This pattern may reflect seasonal factors but has not been tested for statistical significance.",
                "recommendation": f"Investigate whether elevated {wmn} readings are consistent across cities and years before attributing a cause.",
                "caveat":         caveat,
            })

    # Insight 3 — city with most Severe observations
    severe = aqi_df[aqi_df["AQI_Bucket"] == "Severe"]
    if not severe.empty:
        sc  = severe.groupby("City")["AQI"].count()
        wsc = sc.idxmax()
        sn  = int(sc.max())
        insights.append({
            "finding":        f"{wsc} has the most recorded Severe AQI observations",
            "value":          f"{sn:,} observations with AQI > 400",
            "location":       wsc,
            "period":         f"{aqi_df['Date'].min().strftime('%b %Y')} – {aqi_df['Date'].max().strftime('%b %Y')}",
            "interpretation": f"AQI > 400 is classified as Severe (CPCB). {wsc} recorded {sn:,} such observations.",
            "recommendation": f"Review historical pollutant data for {wsc} during Severe episodes to identify consistently elevated pollutants.",
            "caveat":         caveat,
        })

    # Insight 4 — YoY trend (most recent comparable pair)
    for ya, yb in [(2018, 2019), (2019, 2020)]:
        ya_df = aqi_df[aqi_df["Year"] == ya]
        yb_df = aqi_df[aqi_df["Year"] == yb]
        if len(ya_df) < min_obs or len(yb_df) < min_obs:
            continue
        ma   = round(ya_df["AQI"].median(), 1)
        mb   = round(yb_df["AQI"].median(), 1)
        chg  = round(mb - ma, 1)
        dire = "increased" if chg > 0 else "decreased"
        if abs(chg) >= 5:
            insights.append({
                "finding":        f"Median AQI {dire} from {ya} to {yb}",
                "value":          f"{ya}: {ma} → {yb}: {mb}  ({chg:+.1f})",
                "location":       "All selected cities",
                "period":         f"{ya} vs {yb}",
                "interpretation": f"Overall median AQI {dire} by {abs(chg):.1f} points. City composition and data availability may differ between years.",
                "recommendation": f"Compare the same cities with complete data in both {ya} and {yb} before drawing trend conclusions.",
                "caveat":         caveat,
            })
        break

    # Insight 5 — monitoring gap
    miss_pct = df.groupby("City").apply(lambda g: round(g["AQI"].isna().sum() / len(g) * 100, 1))
    if not miss_pct.empty:
        gc   = miss_pct.idxmax()
        gpct = miss_pct.max()
        if gpct > 30:
            insights.append({
                "finding":        f"{gc} has the highest proportion of missing AQI values",
                "value":          f"{gpct}% of {gc} observations lack a valid AQI reading",
                "location":       gc,
                "period":         "Full dataset period",
                "interpretation": f"{gpct}% of {gc}'s records have no AQI. This limits comparability and may indicate monitoring gaps.",
                "recommendation": f"Review completeness of monitoring data for {gc}, particularly for periods where AQI is absent.",
                "caveat":         caveat,
            })

    return insights


# ── Chart functions ───────────────────────────────────────────────────────────

def chart_monthly_trend(df: pd.DataFrame, title: str = "Historical AQI Trend — Monthly Median"):
    monthly = calculate_monthly_trend(df)
    if monthly.empty:
        return None
    fig = px.line(
        monthly, x="Date", y="MedianAQI",
        labels={"MedianAQI": "Median AQI", "Date": ""},
        custom_data=["Count"],
    )
    fig.update_traces(
        line=dict(color="#0F766E", width=2),
        mode="lines",
        hovertemplate="<b>%{x|%b %Y}</b><br>Median AQI: %{y:.0f}<br>Observations: %{customdata[0]:,}<extra></extra>",
    )
    # Subtle fill
    fig.add_traces(px.area(monthly, x="Date", y="MedianAQI").data)
    fig.data[-1].update(
        fillcolor="rgba(15,118,110,0.06)", line_width=0, hoverinfo="skip", showlegend=False
    )
    for threshold, label, color in [
        (200, "Poor ▸", "#ea580c"),
        (300, "Very Poor ▸", "#dc2626"),
    ]:
        fig.add_hline(
            y=threshold, line_dash="dot", line_color=color, line_width=1,
            annotation_text=label, annotation_position="bottom right",
            annotation_font_size=9, annotation_font_color=color,
        )
    fig.update_xaxes(dtick="M6", tickformat="%b %Y", tickangle=-30)
    fig.update_yaxes(title="Median AQI")
    return _chart_style(fig, title=title, height=340)


def chart_city_comparison(df: pd.DataFrame):
    cs = calculate_city_summary(df).dropna(subset=["Median AQI"])
    if cs.empty:
        return None
    cs["Bucket"] = cs["Median AQI"].apply(_aqi_to_bucket)
    cs = cs.sort_values("Median AQI", ascending=True)
    colors = [AQI_COLORS.get(b, "#94A3B8") for b in cs["Bucket"]]
    fig = go.Figure(go.Bar(
        x=cs["Median AQI"], y=cs["City"], orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        customdata=cs[["Valid AQI Obs", "% AQI > 200"]].values,
        hovertemplate="<b>%{y}</b><br>Median AQI: %{x:.0f}<br>Valid obs: %{customdata[0]:,}<br>% AQI>200: %{customdata[1]:.1f}%<extra></extra>",
    ))
    fig.update_xaxes(title="Median AQI")
    fig.update_yaxes(title="")
    return _chart_style(fig, title="City Comparison — Median AQI", height=460)


def chart_aqi_distribution(df: pd.DataFrame):
    aqi_df = df.dropna(subset=["AQI_Bucket"])
    if aqi_df.empty:
        return None
    total  = len(aqi_df)
    counts = aqi_df["AQI_Bucket"].value_counts()
    fig    = go.Figure()
    for b in AQI_BUCKET_ORDER:
        cnt = counts.get(b, 0)
        pct = round(cnt / total * 100, 1)
        fig.add_trace(go.Bar(
            name=b, x=[pct], y=[""], orientation="h",
            marker_color=AQI_COLORS.get(b, "#ccc"),
            marker_line_width=0,
            text=f"{pct:.0f}%" if pct >= 4 else "",
            textposition="inside",
            textfont=dict(color="white", size=10),
            hovertemplate=f"<b>{b}</b><br>{cnt:,} obs ({pct:.1f}%)<extra></extra>",
        ))
    fig.update_layout(
        barmode="stack", showlegend=True,
        legend=dict(orientation="h", y=-0.35, x=0, font=dict(size=10)),
        xaxis_title="% of valid AQI observations",
        yaxis=dict(showticklabels=False),
    )
    return _chart_style(fig, title="AQI Category Distribution", height=180)


def chart_city_aqi_boxplot(df: pd.DataFrame):
    aqi_df = df.dropna(subset=["AQI"])
    if aqi_df.empty:
        return None
    order = aqi_df.groupby("City")["AQI"].median().sort_values(ascending=False).index.tolist()
    fig   = px.box(
        aqi_df, x="City", y="AQI", color="City",
        category_orders={"City": order},
        labels={"AQI": "AQI", "City": ""},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(showlegend=False, marker_size=3, line_width=1.5)
    fig.add_hline(y=200, line_dash="dot", line_color="#ea580c",
                  annotation_text="AQI 200", annotation_font_size=9)
    fig.update_xaxes(tickangle=-35)
    return _chart_style(fig, title="AQI Distribution by City", height=400)


def chart_monthly_city_heatmap(df: pd.DataFrame):
    aqi_df = df.dropna(subset=["AQI"])
    if aqi_df.empty:
        return None
    pivot = aqi_df.pivot_table(index="Month", columns="City", values="AQI", aggfunc="median")
    labels = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"]
    pivot.index = [labels[m-1] for m in pivot.index]
    fig = px.imshow(
        pivot,
        color_continuous_scale=[(0,"#16a34a"),(0.15,"#ca8a04"),(0.45,"#ea580c"),
                                  (0.65,"#dc2626"),(0.85,"#7c3aed"),(1,"#4c0519")],
        labels=dict(color="Median AQI"), aspect="auto", text_auto=".0f",
    )
    fig.update_traces(textfont=dict(size=9))
    fig.update_coloraxes(colorbar_title="Median AQI", colorbar_thickness=10)
    return _chart_style(fig, title="Median AQI by Month & City", height=360)


def chart_annual_trend_per_city(df: pd.DataFrame, cities: list):
    aqi_df = df[df["City"].isin(cities)].dropna(subset=["AQI"])
    if aqi_df.empty:
        return None
    annual = (
        aqi_df.groupby(["City", "Year"])
        .agg(MedianAQI=("AQI", "median"), Count=("AQI", "count"))
        .reset_index()
    )
    annual = annual[annual["Count"] >= 30]
    if annual.empty:
        return None
    fig = px.line(
        annual, x="Year", y="MedianAQI", color="City", markers=True,
        labels={"MedianAQI": "Median AQI", "Year": "Year"},
        custom_data=["Count"],
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig.update_traces(
        hovertemplate="<b>%{fullData.name}</b> %{x}<br>Median AQI: %{y:.0f}<br>Obs: %{customdata[0]}<extra></extra>",
        marker_size=5,
    )
    fig.update_xaxes(dtick=1, tickangle=-30)
    return _chart_style(fig, title="Annual Median AQI (years with ≥30 valid obs)", height=360)


def chart_pollutant_trend(df: pd.DataFrame, pollutant: str, cities: list):
    sub = df[df["City"].isin(cities)].dropna(subset=[pollutant]).copy()
    if sub.empty:
        return None
    monthly = sub.groupby(["YearMonth","City"])[pollutant].mean().reset_index()
    monthly["Date"] = monthly["YearMonth"].dt.to_timestamp()
    unit = POLLUTANT_UNITS.get(pollutant, "")
    fig  = px.line(
        monthly, x="Date", y=pollutant, color="City",
        labels={pollutant: f"{pollutant} ({unit})", "Date": ""},
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    fig.update_xaxes(dtick="M6", tickformat="%b %Y", tickangle=-30)
    return _chart_style(fig, title=f"{pollutant} — Monthly Mean", height=340)


def chart_pollutant_city_box(df: pd.DataFrame, pollutant: str):
    sub = df.dropna(subset=[pollutant])
    if sub.empty:
        return None
    order = sub.groupby("City")[pollutant].median().sort_values(ascending=False).index.tolist()
    unit  = POLLUTANT_UNITS.get(pollutant, "")
    fig   = px.box(
        sub, x="City", y=pollutant, color="City",
        category_orders={"City": order},
        labels={pollutant: f"{pollutant} ({unit})", "City": ""},
        color_discrete_sequence=px.colors.qualitative.Set2,
    )
    fig.update_traces(showlegend=False, marker_size=3, line_width=1.5)
    fig.update_xaxes(tickangle=-35)
    return _chart_style(fig, title=f"{pollutant} Distribution by City", height=360)


def chart_correlation_heatmap(df: pd.DataFrame):
    cols = [c for c in POLLUTANTS + ["AQI"] if c in df.columns]
    corr = df[cols].corr()
    fig  = px.imshow(
        corr,
        color_continuous_scale=[[0,"#1e3a5f"],[0.5,"#F8FAFC"],[1,"#0F766E"]],
        zmin=-1, zmax=1, text_auto=".2f",
        labels=dict(color="r"), aspect="auto",
    )
    fig.update_traces(textfont=dict(size=8))
    fig.update_coloraxes(colorbar_title="r", colorbar_thickness=10)
    return _chart_style(fig, title="Pollutant Correlation Matrix (Pearson r)", height=480)


def chart_pollutant_aqi_scatter(df: pd.DataFrame, pollutant: str):
    sub = df.dropna(subset=[pollutant, "AQI"])
    if sub.empty:
        return None
    if len(sub) > 3000:
        sub = sub.sample(3000, random_state=42)
    unit = POLLUTANT_UNITS.get(pollutant, "")
    fig  = px.scatter(
        sub, x=pollutant, y="AQI", color="City",
        opacity=0.5,
        labels={pollutant: f"{pollutant} ({unit})", "AQI": "AQI"},
        hover_data={"Date": True},
        color_discrete_sequence=px.colors.qualitative.Safe,
    )
    return _chart_style(fig, title=f"{pollutant} vs AQI  (sample ≤3,000 pts)", height=380)


def chart_risk_bar(city_sum: pd.DataFrame):
    sub = city_sum.dropna(subset=["% AQI > 300"]).sort_values("% AQI > 300", ascending=True)
    if sub.empty:
        return None
    def _color(p):
        if p >= 20: return "#dc2626"
        if p >= 10: return "#ea580c"
        return "#16a34a"
    colors = [_color(p) for p in sub["% AQI > 300"]]
    fig = go.Figure(go.Bar(
        x=sub["% AQI > 300"], y=sub["City"], orientation="h",
        marker=dict(color=colors, line=dict(width=0)),
        customdata=sub[["Valid AQI Obs"]].values,
        hovertemplate="<b>%{y}</b><br>% AQI>300: %{x:.1f}%<br>Valid obs: %{customdata[0]:,}<extra></extra>",
    ))
    for vx, label, col in [(20,"High-concern 20%","#dc2626"),(10,"Moderate-concern 10%","#ea580c")]:
        fig.add_vline(x=vx, line_dash="dot", line_color=col, line_width=1,
                      annotation_text=label, annotation_font_size=9, annotation_font_color=col)
    fig.update_xaxes(title="% of valid obs with AQI > 300")
    return _chart_style(fig, title="Very Poor / Severe Frequency by City", height=440)


def chart_period_heatmap(df: pd.DataFrame):
    aqi_df = df.dropna(subset=["AQI"])
    if aqi_df.empty:
        return None
    pivot = aqi_df.pivot_table(index="Year", columns="Month", values="AQI", aggfunc="median")
    mlabels = {i: m for i, m in enumerate(
        ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"], 1)}
    pivot.columns = [mlabels[c] for c in pivot.columns]
    fig = px.imshow(
        pivot,
        color_continuous_scale=[(0,"#16a34a"),(0.15,"#ca8a04"),(0.45,"#ea580c"),
                                  (0.65,"#dc2626"),(0.85,"#7c3aed"),(1,"#4c0519")],
        labels=dict(color="Median AQI"), aspect="auto", text_auto=".0f",
    )
    fig.update_traces(textfont=dict(size=9))
    fig.update_coloraxes(colorbar_title="Median AQI", colorbar_thickness=10)
    return _chart_style(fig, title="Median AQI — Year × Month", height=300)


def chart_missingness(df: pd.DataFrame):
    miss = pd.DataFrame({
        "Pollutant": POLLUTANTS,
        "Missing %": [round(df[p].isna().mean()*100, 1) if p in df.columns else 100.0 for p in POLLUTANTS],
    }).sort_values("Missing %", ascending=True)
    fig = px.bar(
        miss, x="Missing %", y="Pollutant", orientation="h",
        color="Missing %",
        color_continuous_scale=["#16a34a","#ca8a04","#dc2626"],
        labels={"Missing %": "Missing (%)"},
        range_color=[0, 100],
    )
    fig.update_coloraxes(showscale=False)
    fig.update_traces(marker_line_width=0)
    return _chart_style(fig, title="Missing Data by Pollutant", height=340)


# ── Sidebar & filters ─────────────────────────────────────────────────────────

def sidebar_city_filter(df, key="cities", default_all=True):
    all_cities = sorted(df["City"].unique().tolist())
    selected   = st.sidebar.multiselect(
        "Cities", all_cities,
        default=all_cities if default_all else all_cities[:3],
        key=key,
    )
    if not selected:
        st.sidebar.warning("No city selected — showing all.")
        selected = all_cities
    return selected


def sidebar_date_filter(df, key_prefix="date"):
    d_min = df["Date"].min().date()
    d_max = df["Date"].max().date()
    start = st.sidebar.date_input("From", value=d_min, min_value=d_min, max_value=d_max, key=f"{key_prefix}_s")
    end   = st.sidebar.date_input("To",   value=d_max, min_value=d_min, max_value=d_max, key=f"{key_prefix}_e")
    if start > end:
        st.sidebar.error("Start must be before end.")
        return d_min, d_max
    return start, end


def apply_filters(df, cities, start, end):
    mask = (
        df["City"].isin(cities) &
        (df["Date"].dt.date >= start) &
        (df["Date"].dt.date <= end)
    )
    return df[mask].copy()


def render_sidebar_filters(df, page_key, show_city=True, show_date=True):
    """Render filters under a styled 'Filters' section in sidebar."""
    st.sidebar.markdown('<div class="section-heading" style="color:#475569">Filters</div>', unsafe_allow_html=True)
    cities = sidebar_city_filter(df, key=f"{page_key}_cities") if show_city else sorted(df["City"].unique().tolist())
    start, end = sidebar_date_filter(df, key_prefix=page_key) if show_date else (df["Date"].min().date(), df["Date"].max().date())
    return cities, start, end


# ── Page 1 — Overview ─────────────────────────────────────────────────────────

def page_overview(df: pd.DataFrame, meta: dict):
    page_header(
        "Air Quality Overview",
        f"{meta['n_cities']} cities · "
        f"{meta['date_min'].strftime('%d %b %Y')} – {meta['date_max'].strftime('%d %b %Y')} · "
        "Source: India CPCB via Kaggle",
    )

    kpis = calculate_kpis(df)
    if "error" in kpis:
        st.error(kpis["error"])
        return

    # KPI row
    mean_v    = f"{kpis['mean_aqi']:.1f}"   if kpis['mean_aqi']    else "—"
    pct200_v  = f"{kpis['pct_above_200']:.1f}%" if kpis['pct_above_200'] is not None else "—"
    kpi_items = [
        ("Total Observations",  f"{kpis['total_rows']:,}",      "all records",                           False),
        ("Valid AQI Records",   f"{kpis['valid_aqi_rows']:,}",  f"{100-kpis['pct_aqi_missing']:.1f}% of total", False),
        ("Cities Covered",      str(kpis["n_cities"]),           "city-level daily obs",                  False),
        ("Mean AQI",            mean_v,                          "valid obs only",                        True),
        ("AQI > 200",           pct200_v,                        "Poor / Very Poor / Severe",             True),
    ]
    kpi_cards(kpi_items)

    # Two-column: trend + city comparison
    col_l, col_r = st.columns([1.5, 1], gap="medium")
    with col_l:
        section_heading("Historical Trend")
        fig_trend = chart_monthly_trend(df)
        if fig_trend:
            chart_card(fig_trend, "p1_trend")
        else:
            empty_state("No AQI data available for trend chart.")
    with col_r:
        section_heading("City Comparison")
        fig_city = chart_city_comparison(df)
        if fig_city:
            chart_card(fig_city, "p1_city")
        else:
            empty_state("No city data available.")

    # AQI distribution (full width)
    section_heading("AQI Category Distribution")
    fig_dist = chart_aqi_distribution(df)
    if fig_dist:
        chart_card(fig_dist, "p1_dist")
    if kpis.get("aqi_bucket_dist"):
        cols = st.columns(len(AQI_BUCKET_ORDER))
        for col, b in zip(cols, AQI_BUCKET_ORDER):
            info  = kpis["aqi_bucket_dist"].get(b, {"count": 0, "pct": 0.0})
            color = AQI_COLORS.get(b, "#94A3B8")
            col.markdown(
                f'<div style="text-align:center;padding:8px 4px;">'
                f'<div style="width:10px;height:10px;background:{color};border-radius:2px;margin:0 auto 4px;"></div>'
                f'<div style="font-size:0.70rem;color:#64748B;font-weight:600;">{b}</div>'
                f'<div style="font-size:1.1rem;font-weight:700;color:#0F1923;">{info["pct"]:.1f}%</div>'
                f'<div style="font-size:0.68rem;color:#94A3B8;">{info["count"]:,} obs</div>'
                f'</div>',
                unsafe_allow_html=True,
            )

    # Key Findings
    section_heading("Key Findings")
    insights = generate_insights(df)
    for i, ins in enumerate(insights, 1):
        render_insight(ins, i)

    # Priority areas + recommendations
    col_p, col_a = st.columns(2, gap="medium")
    with col_p:
        section_heading("Priority Areas to Review")
        city_sum  = calculate_city_summary(df)
        high_risk = city_sum[city_sum["% AQI > 300"].fillna(0) >= 20]
        mod_risk  = city_sum[(city_sum["% AQI > 300"].fillna(0) >= 10) & (city_sum["% AQI > 300"].fillna(0) < 20)]
        if high_risk.empty and mod_risk.empty:
            st.markdown('<div class="insight-card" style="border-left-color:#16a34a">'
                        '<div class="insight-title" style="color:#166534">No cities exceed the High-concern threshold</div>'
                        '<div class="insight-body">No city exceeds 20% Very Poor / Severe in the current selection.</div>'
                        '</div>', unsafe_allow_html=True)
        for _, row in high_risk.iterrows():
            st.markdown(
                f'<div class="insight-card" style="border-left-color:#dc2626">'
                f'<div class="insight-title">{row["City"]}</div>'
                f'<div class="insight-value">{row["% AQI > 300"]:.1f}% of valid obs are Very Poor or Severe</div>'
                f'<div class="insight-body">Based on {row["Valid AQI Obs"]:,} valid AQI observations. '
                f'<span class="risk-high">High-Concern</span></div>'
                f'</div>', unsafe_allow_html=True)
        for _, row in mod_risk.iterrows():
            st.markdown(
                f'<div class="insight-card" style="border-left-color:#ea580c">'
                f'<div class="insight-title">{row["City"]}</div>'
                f'<div class="insight-value">{row["% AQI > 300"]:.1f}% of valid obs are Very Poor or Severe</div>'
                f'<div class="insight-body">Based on {row["Valid AQI Obs"]:,} valid AQI observations. '
                f'<span class="risk-moderate">Moderate-Concern</span></div>'
                f'</div>', unsafe_allow_html=True)

    with col_a:
        section_heading("Recommended Actions")
        recs = []
        if not high_risk.empty:
            cities_str = ", ".join(high_risk["City"].tolist())
            recs.append(f"<b>Review data for {cities_str}</b> — highest frequency of Very Poor/Severe episodes. Identify which pollutants are elevated.")
        recs.append("<b>Investigate seasonal drivers</b> — the City & Time page shows AQI by season. Prioritise monitoring before historically high-AQI periods.")
        recs.append("<b>Validate with sub-city data</b> — these are city-level aggregated readings; station-level data would provide spatial context.")
        for rec in recs:
            st.markdown(
                f'<div style="background:#F8FAFC;border:1px solid #E2E8F0;border-radius:8px;'
                f'padding:12px 14px;margin-bottom:8px;font-size:0.82rem;color:#334155;line-height:1.5;">'
                f'{rec}</div>', unsafe_allow_html=True)

    st.markdown(
        '<div style="margin-top:16px;padding:10px 14px;background:#F8FAFC;border:1px solid #E2E8F0;'
        'border-radius:8px;font-size:0.72rem;color:#94A3B8;line-height:1.6;">'
        'Historical data only (2015–2020). Not real-time. City-level observations do not represent '
        'every location within a city. All percentages calculated over valid AQI observations only. '
        'This platform is not an official regulatory service or medical diagnostic system.</div>',
        unsafe_allow_html=True,
    )


# ── Page 2 — City & Time ──────────────────────────────────────────────────────

def page_city_time(df: pd.DataFrame):
    page_header("City & Time Analysis", "Explore AQI patterns across selected cities and time periods.")

    with st.sidebar:
        cities, start, end = render_sidebar_filters(df, "p2")

    fdf = apply_filters(df, cities, start, end)
    if fdf.empty:
        empty_state("No data matches the selected filters. Adjust the city selection or date range.")
        return

    kpis = calculate_kpis(fdf)
    mean_v   = f"{kpis['mean_aqi']:.1f}"          if kpis['mean_aqi']    else "—"
    pct200_v = f"{kpis['pct_above_200']:.1f}%"    if kpis['pct_above_200'] is not None else "—"
    miss_v   = f"{kpis['pct_aqi_missing']:.1f}%"
    d_min_s  = kpis['date_min'].strftime('%d %b %Y') if kpis.get('date_min') else "—"
    d_max_s  = kpis['date_max'].strftime('%d %b %Y') if kpis.get('date_max') else "—"
    kpi_cards([
        ("Total Obs",       f"{kpis['total_rows']:,}",     f"{kpis['n_cities']} cities", False),
        ("Valid AQI",       f"{kpis['valid_aqi_rows']:,}", "non-null AQI rows",          False),
        ("Mean AQI",        mean_v,                         "valid obs only",             True),
        ("AQI > 200",       pct200_v,                       "Poor or worse",              True),
        ("Missing AQI",     miss_v,                         "of total rows",              False),
    ])

    # Coverage table
    section_heading("Data Coverage per City")
    city_sum = calculate_city_summary(fdf)
    with st.expander("Show city coverage table", expanded=False):
        st.dataframe(city_sum, use_container_width=True, hide_index=True)
        st.caption("Comparisons should account for differences in valid observation counts and time periods.")

    # Two charts side by side
    col1, col2 = st.columns(2, gap="medium")
    with col1:
        section_heading("Annual Trend")
        fig_annual = chart_annual_trend_per_city(fdf, cities)
        if fig_annual:
            chart_card(fig_annual, "p2_annual")
        else:
            empty_state("Insufficient data (requires ≥30 valid AQI obs per city-year).")
    with col2:
        section_heading("Monthly Trend")
        fig_monthly = chart_monthly_trend(fdf, title="Monthly Median AQI")
        if fig_monthly:
            chart_card(fig_monthly, "p2_monthly")

    # Full-width heatmap
    section_heading("Month × City Heatmap")
    fig_hm = chart_monthly_city_heatmap(fdf)
    if fig_hm:
        chart_card(fig_hm, "p2_heatmap")

    # Box plot + seasonal side by side
    col3, col4 = st.columns(2, gap="medium")
    with col3:
        section_heading("AQI Distribution by City")
        fig_box = chart_city_aqi_boxplot(fdf)
        if fig_box:
            chart_card(fig_box, "p2_box")
    with col4:
        section_heading("Seasonal Summary")
        st.caption("Winter: Dec–Feb · Pre-Monsoon: Mar–May · Monsoon: Jun–Sep · Post-Monsoon: Oct–Nov. No significance test applied.")
        seasonal = calculate_seasonal_summary(fdf)
        if not seasonal.empty:
            piv = seasonal.pivot_table(index="City", columns="Season", values="MedianAQI").round(1)
            piv = piv.reindex(columns=[c for c in ["Winter","Pre-Monsoon","Monsoon","Post-Monsoon"] if c in piv.columns])
            st.dataframe(piv, use_container_width=True)
            st.caption("Median AQI. NaN = insufficient data.")

    # Top observations
    section_heading("Top 20 Highest AQI Observations")
    top20 = fdf.dropna(subset=["AQI"]).nlargest(20, "AQI")[
        ["City","Date","AQI","AQI_Bucket","PM2.5","PM10","NO2","SO2","O3"]
    ].reset_index(drop=True)
    top20["Date"] = top20["Date"].dt.strftime("%Y-%m-%d")
    st.dataframe(top20, use_container_width=True, hide_index=True)

    # Raw data
    with st.expander(f"Raw data preview  ({len(fdf):,} rows, showing first 500)", expanded=False):
        show_cols = ["City","Date","AQI","AQI_Bucket","PM2.5","PM10","NO","NO2","SO2","O3","CO"]
        avail     = [c for c in show_cols if c in fdf.columns]
        disp      = fdf[avail].copy()
        disp["Date"] = disp["Date"].dt.strftime("%Y-%m-%d")
        st.dataframe(disp.head(500), use_container_width=True, hide_index=True)


# ── Page 3 — Pollutants ───────────────────────────────────────────────────────

def page_pollutants(df: pd.DataFrame):
    page_header(
        "Pollutant Analysis",
        "Concentration trends, city comparisons, distributions, and relationships with AQI. "
        "AQI is mathematically derived from pollutant sub-indices — correlations partly reflect this dependency."
    )

    available = [p for p in POLLUTANTS if p in df.columns]

    with st.sidebar:
        st.sidebar.markdown('<div class="section-heading" style="color:#475569">Pollutant</div>', unsafe_allow_html=True)
        pollutant = st.sidebar.selectbox("Select", available, index=0, key="p3_poll", label_visibility="collapsed")
        cities, start, end = render_sidebar_filters(df, "p3")

    fdf = apply_filters(df, cities, start, end)
    if fdf.empty:
        empty_state("No data matches the selected filters.")
        return

    unit     = POLLUTANT_UNITS.get(pollutant, "")
    pct_miss = round(fdf[pollutant].isna().mean() * 100, 1) if pollutant in fdf.columns else 100.0

    # Pollutant summary bar
    st.markdown(
        f'<div style="background:#FFFFFF;border:1px solid #E2E8F0;border-radius:10px;'
        f'padding:14px 20px;margin-bottom:16px;display:flex;align-items:center;gap:20px;">'
        f'<span style="font-size:1.3rem;font-weight:700;color:#0F1923;">{pollutant}</span>'
        f'<span style="font-size:0.80rem;color:#64748B;">Unit: {unit}</span>'
        f'<span style="font-size:0.80rem;color:{"#dc2626" if pct_miss>50 else "#64748B"};">'
        f'Missing: {pct_miss:.1f}%{"  ⚠ high missingness" if pct_miss>50 else ""}</span>'
        f'</div>',
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns(2, gap="medium")
    with col1:
        section_heading("Concentration Trend")
        fig_trend = chart_pollutant_trend(fdf, pollutant, cities)
        if fig_trend:
            chart_card(fig_trend, "p3_trend")
        else:
            empty_state(f"No valid {pollutant} data for selected filters.")
    with col2:
        section_heading("City Distribution")
        fig_box = chart_pollutant_city_box(fdf, pollutant)
        if fig_box:
            chart_card(fig_box, "p3_box")

    col3, col4 = st.columns(2, gap="medium")
    with col3:
        section_heading("Correlation Matrix")
        st.caption("Pearson r. AQI correlation partly structural — AQI derived from pollutant sub-indices.")
        fig_corr = chart_correlation_heatmap(fdf)
        if fig_corr:
            chart_card(fig_corr, "p3_corr")
    with col4:
        section_heading(f"{pollutant} vs AQI")
        st.caption("Scatter plot downsampled to ≤3,000 points. Correlation does not establish causation.")
        fig_scat = chart_pollutant_aqi_scatter(fdf, pollutant)
        if fig_scat:
            chart_card(fig_scat, "p3_scat")
        else:
            empty_state(f"Insufficient paired {pollutant} / AQI data.")

    with st.expander("Data availability by pollutant", expanded=False):
        fig_miss = chart_missingness(fdf)
        if fig_miss:
            st.plotly_chart(fig_miss, use_container_width=True)
            st.caption("High missing % may indicate sensor not installed or data not collected for that city.")


# ── Page 4 — Risk Center ──────────────────────────────────────────────────────

def page_risk(df: pd.DataFrame):
    page_header(
        "Pollution Risk Center",
        "Cities and periods with elevated AQI frequencies. Risk flags are analytical indicators "
        "from historical data — not official regulatory warnings.",
    )

    with st.sidebar:
        cities, start, end = render_sidebar_filters(df, "p4")

    fdf = apply_filters(df, cities, start, end)
    if fdf.empty:
        empty_state("No data matches the selected filters.")
        return

    # Risk methodology
    with st.expander("Risk methodology & thresholds", expanded=False):
        st.markdown("""
**Risk tiers** are project-defined analytical indicators, not CPCB regulatory categories.

| Tier | Criterion | Basis |
|---|---|---|
| **High-Concern** | > 20% of valid obs with AQI > 300 | Very Poor or Severe (CPCB) |
| **Moderate-Concern** | 10–20% of valid obs with AQI > 300 | |
| **Low-Concern** | < 10% of valid obs with AQI > 300 | |
| **Insufficient Data** | < 30 valid AQI observations | |

Percentages are calculated over **valid (non-null) AQI observations only**.
Thresholds are inclusive at the upper boundary: 20% = High-Concern, 10–19.9% = Moderate-Concern.
        """)

    # City risk summary
    section_heading("City Risk Summary")
    city_sum = calculate_city_summary(fdf)

    def _tier(p):
        if pd.isna(p): return "Insufficient Data"
        if p >= 20:    return "High-Concern"
        if p >= 10:    return "Moderate-Concern"
        return "Low-Concern"

    city_sum["Risk Tier"] = city_sum["% AQI > 300"].apply(_tier)
    disp_cols = ["City","Total Obs","Valid AQI Obs","Median AQI","% AQI > 200","% AQI > 300","% AQI > 400","Risk Tier"]
    st.dataframe(city_sum[disp_cols], use_container_width=True, hide_index=True)

    # Charts
    col1, col2 = st.columns([1.2, 1], gap="medium")
    with col1:
        section_heading("Elevated AQI Frequency by City")
        fig_risk = chart_risk_bar(city_sum)
        if fig_risk:
            chart_card(fig_risk, "p4_risk")
    with col2:
        section_heading("Year × Month AQI Heatmap")
        st.caption("Median AQI across all selected cities.")
        fig_hm = chart_period_heatmap(fdf)
        if fig_hm:
            chart_card(fig_hm, "p4_heatmap")

    # Most concerning periods
    section_heading("Most Concerning Periods")
    aqi_df = fdf.dropna(subset=["AQI"])
    if not aqi_df.empty:
        ps = (
            aqi_df.groupby(["Year","Month","City"])
            .agg(
                MedianAQI=("AQI","median"),
                Count=("AQI","count"),
                PctAbove300=("AQI", lambda x: round((x>300).sum()/len(x)*100,1)),
            ).reset_index()
        )
        ps = ps[ps["Count"] >= 5]
        ps["MonthName"] = ps["Month"].apply(lambda m: pd.Timestamp(2020,m,1).strftime("%b"))
        top = ps.nlargest(15,"MedianAQI")[
            ["City","Year","MonthName","MedianAQI","Count","PctAbove300"]
        ].rename(columns={"MonthName":"Month","MedianAQI":"Median AQI","Count":"Valid Obs","PctAbove300":"% AQI>300"})
        st.dataframe(top.reset_index(drop=True), use_container_width=True, hide_index=True)
        st.caption("City-month combinations with ≥5 valid AQI observations only.")

    # YoY change
    section_heading("Year-over-Year AQI Change")
    yr_sum = (
        fdf.dropna(subset=["AQI"])
        .groupby(["City","Year"])
        .agg(MedianAQI=("AQI","median"), Count=("AQI","count"))
        .reset_index()
    )
    yr_sum = yr_sum[yr_sum["Count"] >= 30]
    yoy    = []
    for city in yr_sum["City"].unique():
        cd = yr_sum[yr_sum["City"]==city].sort_values("Year")
        for i in range(1, len(cd)):
            p, c = cd.iloc[i-1], cd.iloc[i]
            chg  = round(c["MedianAQI"] - p["MedianAQI"], 1)
            yoy.append({
                "City": city, "From": int(p["Year"]), "To": int(c["Year"]),
                "From AQI": round(p["MedianAQI"],1), "To AQI": round(c["MedianAQI"],1),
                "Change": chg,
                "Trend": "Deteriorated" if chg>5 else ("Improved" if chg<-5 else "Stable"),
            })
    if yoy:
        ydf = pd.DataFrame(yoy)
        st.dataframe(ydf, use_container_width=True, hide_index=True)
        st.caption("City-years with ≥30 valid AQI obs only. Changes ≤ ±5 pts classified as Stable.")
    else:
        empty_state("Insufficient annual data for year-over-year comparison with current filters.")

    # Dynamic insights
    section_heading("Evidence-Based Findings")
    insights = generate_insights(fdf)
    for i, ins in enumerate(insights, 1):
        render_insight(ins, i)

    st.markdown(
        '<div style="margin-top:16px;padding:10px 14px;background:#F8FAFC;border:1px solid #E2E8F0;'
        'border-radius:8px;font-size:0.72rem;color:#94A3B8;line-height:1.6;">'
        'Risk flags are based on historical observations (2015–2020). Do not attribute elevated AQI to '
        'specific sources without additional evidence. Not a substitute for regulatory environmental assessment.</div>',
        unsafe_allow_html=True,
    )


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    st.set_page_config(
        page_title="Air Quality Intelligence",
        page_icon="◈",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    st.markdown(GLOBAL_CSS, unsafe_allow_html=True)

    df, station_info, meta = load_data()

    # ── Sidebar ──────────────────────────────────────────────────────────────
    with st.sidebar:
        _LOGO_SVG = (
            '<svg width="20" height="20" viewBox="0 0 16 16" fill="none" xmlns="http://www.w3.org/2000/svg">'
            '<circle cx="8" cy="8" r="7" stroke="#0F766E" stroke-width="1.5"/>'
            '<path d="M4 11 L6.5 7.5 L8.5 9.5 L11 6" stroke="#0F766E" stroke-width="1.5"'
            ' stroke-linecap="round" stroke-linejoin="round"/>'
            '<circle cx="11" cy="6" r="1.2" fill="#0F766E"/>'
            '</svg>'
        )
        st.markdown(
            '<div class="sidebar-brand">'
            f'<div class="sidebar-logo-mark">{_LOGO_SVG}</div>'
            '<div class="sidebar-brand-text">'
            '<span class="sidebar-brand-title">Air Quality</span>'
            '<span class="sidebar-brand-sub">Intelligence Platform</span>'
            '</div>'
            f'<div style="font-size:0.70rem;color:#475569;margin-top:2px;">'
            f'{meta["n_cities"]} cities · {meta["date_min"].strftime("%Y")}–{meta["date_max"].strftime("%Y")}</div>'
            '</div>',
            unsafe_allow_html=True,
        )

        page = st.radio(
            "nav",
            options=["Overview", "City & Time", "Pollutants", "Risk Center"],
            label_visibility="collapsed",
            key="nav",
        )

        st.markdown('<hr style="border-color:#1E2D3D;margin:12px 0 8px;">', unsafe_allow_html=True)
        st.markdown(
            f'<div style="font-size:0.68rem;color:#475569;line-height:1.7;">'
            f'{meta["total_rows"]:,} total records<br>'
            f'{meta["valid_aqi_rows"]:,} valid AQI rows<br>'
            f'{meta["pct_aqi_missing"]}% missing AQI</div>',
            unsafe_allow_html=True,
        )

    # ── App header (rendered once, above every page) ──────────────────────────
    render_app_header(meta)

    # ── Route ─────────────────────────────────────────────────────────────────
    if page == "Overview":
        page_overview(df, meta)
    elif page == "City & Time":
        page_city_time(df)
    elif page == "Pollutants":
        page_pollutants(df)
    elif page == "Risk Center":
        page_risk(df)


if __name__ == "__main__":
    main()
