import sys
import streamlit as st
import os
import json
import pandas as pd
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.config.constants import (
    SAMPLES,
    ERRORS,
    MEAN,
    STD,
    MIN,
    MAX,
    COUNT,
    DEVICE_NAME,
    AMMETER,
)

# =========================================================
# PATHS
# =========================================================
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RESULTS_DIR = os.path.join(ROOT_DIR, "results")

LIVE_FILE = os.path.join(RESULTS_DIR, "results.json")
PYTEST_FILE = os.path.join(RESULTS_DIR, "pytest_results.json")
ANALYSIS_FILE = os.path.join(RESULTS_DIR, "analysis_results.json")

# =========================================================
# LOADERS
# =========================================================
@st.cache_data
def load_json(path):
    if not os.path.exists(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

# =========================================================
# NORMALIZER (SAFE)
# =========================================================
def normalize_result(r):
    return {
        DEVICE_NAME: r.get(AMMETER, "unknown"),
        MEAN: r.get(MEAN, 0),
        STD: r.get(STD, 0),
        MIN: r.get(MIN, 0),
        MAX: r.get(MAX, 0),
        SAMPLES: r.get(SAMPLES, []),
        ERRORS: r.get(ERRORS, 0),
        COUNT: r.get(COUNT, 0),
    }

# =========================================================
# INIT
# =========================================================
st.set_page_config(page_title="Ammeter Dashboard", layout="wide")
st.title("⚡ Ammeter Testing Dashboard")

# =========================================================
# LOAD DATA
# =========================================================
live_data = load_json(LIVE_FILE)
pytest_data = load_json(PYTEST_FILE)
analysis_data = load_json(ANALYSIS_FILE)

results = live_data.get("results", [])

if not isinstance(results, list) or len(results) == 0:
    st.warning("No valid live data found")
    st.stop()

run_id = live_data.get("run_id")
timestamp = live_data.get("timestamp")

if run_id:
    st.caption(f"Run ID: {run_id}")
if timestamp:
    st.caption(f"Timestamp: {timestamp}")

# =========================================================
# DATAFRAME
# =========================================================
normalized = [normalize_result(r) for r in results]
df = pd.DataFrame(normalized)

df["device_name"] = df["device_name"].fillna("unknown").astype(str)

# =========================================================
# METRICS
# =========================================================
df["cv"] = df["std"] / (df["mean"] + 1e-9)
df["range"] = df["max"] - df["min"]
df["error_rate"] = df["errors"] / df["count"].replace(0, 1)

df["accuracy_score"] = 1 / (
    (df["std"] + 1e-6) *
    (1 + df["cv"]) *
    (1 + df["error_rate"]) *
    (1 + df["range"] * 0.01)
)

df = df.replace([float("inf"), -float("inf")], 0)
df = df.dropna(subset=["accuracy_score"])
df = df.sort_values("accuracy_score", ascending=False)

# =========================================================
# TABLE
# =========================================================
st.subheader("📊 Accuracy Table (Live)")
st.dataframe(df, use_container_width=True)

# =========================================================
# MOST RELIABLE
# =========================================================
st.subheader("🏆 Most Reliable (Live)")
if not df.empty:
    st.success(df.iloc[0]["device_name"])
else:
    st.warning("No data")

# =========================================================
# CURRENT MEASUREMENTS
# =========================================================
st.subheader("📈 Current Measurements Comparison")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:
    fig, ax = plt.subplots(figsize=(6, 4))

    for r in normalized:
        samples = r.get("samples", [])
        if samples:
            ax.plot(samples, label=r.get("device_name", "unknown"), linewidth=1)

    ax.set_title("Current Measurements Comparison")
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Current")
    ax.legend()

    st.pyplot(fig)

# =========================================================
# ACCURACY CHART
# =========================================================
st.subheader("📊 Accuracy Score Comparison")

col1, col2, col3 = st.columns([1, 2, 1])

with col2:

    # 🔧 CLEAN DATA (CRITICAL)
    chart_df = df.copy()

    chart_df = chart_df.dropna(subset=["device_name", "accuracy_score"])
    chart_df["device_name"] = chart_df["device_name"].astype(str)
    chart_df["accuracy_score"] = pd.to_numeric(chart_df["accuracy_score"], errors="coerce")

    chart_df = chart_df.dropna(subset=["accuracy_score"])

    # אם אין נתונים בכלל → תראה הודעה
    if chart_df.empty:
        st.warning("No data for accuracy chart")
    else:
        fig, ax = plt.subplots(figsize=(6, 3))

        ax.bar(
            chart_df["device_name"].tolist(),
            chart_df["accuracy_score"].tolist()
        )

        ax.set_title("Ammeter Accuracy")
        ax.set_ylabel("Score")

        plt.xticks(rotation=20)

        st.pyplot(fig)
# =========================================================
# PYTEST
# =========================================================
st.subheader("🧪 Pytest Results")

if pytest_data:
    grouped = {}

    for t in pytest_data.get("tests", []):
        nodeid = t.get("nodeid", "unknown")
        file_name = nodeid.split("::")[0]

        grouped.setdefault(file_name, []).append({
            "test": nodeid,
            "status": t.get("outcome"),
            "error": t.get("call", {}).get("longrepr")
        })

    for file_name, tests in grouped.items():
        st.markdown(f"### 📁 {file_name}")
        st.dataframe(pd.DataFrame(tests), use_container_width=True)
else:
    st.warning("No pytest results found")

# =========================================================
# ANALYSIS
# =========================================================
st.subheader("📊 Analysis Results")

if analysis_data:
    analysis_results = analysis_data.get("results", [])
    comparison = analysis_data.get("comparison", {})

    if analysis_results:
        df_analysis = pd.DataFrame(analysis_results)
        st.dataframe(df_analysis, use_container_width=True)

    st.subheader("🏆 Most Reliable (Analysis)")
    st.success(comparison.get("most_reliable", "N/A"))

    st.subheader("📈 Ranking")
    st.json(comparison.get("ranking", {}))
else:
    st.warning("No analysis data found")

# =========================================================
# DEBUG
# =========================================================
with st.expander("🔍 Live JSON Snapshot"):
    st.json(live_data)