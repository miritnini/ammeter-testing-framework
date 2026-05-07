import re
import streamlit as st
import os
import sys
import json
import pandas as pd
import matplotlib.pyplot as plt
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT_DIR)
from src.config.constants import (
    DEVICE_NAME,
    SAMPLES,
    ERRORS,
    MEAN,
    MEDIAN,
    STD,
    MIN,
    MAX,
    COUNT,
    RANKING
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
# LOAD JSON
# =========================================================
@st.cache_data
def load_json(path):
    if not os.path.exists(path):
        return {}
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except Exception as e:
            print(f"Failed to load JSON from {path}: {e}")
            return {}

live_data = load_json(LIVE_FILE)
pytest_data = load_json(PYTEST_FILE)
analysis_data = load_json(ANALYSIS_FILE)

# =========================================================
# STREAMLIT INIT
# =========================================================
st.set_page_config(page_title="Ammeter Dashboard", layout="wide")
st.title("⚡ Ammeter Testing Dashboard")

# =========================================================
# PARSE LIVE DATA (REGEX)
# =========================================================
parsed_results = []

for r in live_data.get("results", []):
    try:
        device_name = re.search(r"ammeter='(.*?)'", r).group(1)
        samples_str = re.search(r"samples=\[(.*?)\]", r).group(1)
        samples = [float(x.strip()) for x in samples_str.split(",") if x.strip()]
        count = int(re.search(r"count=(\d+)", r).group(1))
        errors = int(re.search(r"errors=(\d+)", r).group(1))
        mean = float(re.search(r"mean=([\d\.]+)", r).group(1))
        median = float(re.search(r"median=([\d\.]+)", r).group(1))
        std = float(re.search(r"std=([\d\.]+)", r).group(1))
        min_val = float(re.search(r"min=([\d\.]+)", r).group(1))
        max_val = float(re.search(r"max=([\d\.]+)", r).group(1))

        parsed_results.append({
            DEVICE_NAME: device_name,
            SAMPLES: samples,
            COUNT: count,
            ERRORS: errors,
            MEAN: mean,
            MEDIAN: median,
            STD: std,
            MIN: min_val,
            MAX: max_val
        })
    except Exception as e:
        print(f"Failed parsing: {e}")

# =========================================================
# CREATE DATAFRAME
# =========================================================
if parsed_results:
    df_live = pd.DataFrame(parsed_results)
else:
    st.warning("No live data found")
    df_live = pd.DataFrame(columns=[
        "device_name", "samples", COUNT, ERRORS,
        MEAN, "median", STD, MIN, MAX
    ])

# =========================================================
# CALCULATE METRICS
# =========================================================
df_live["cv"] = df_live[STD] / (df_live[MEAN] + 1e-9)
df_live["range"] = df_live[MAX] - df_live[MIN]
df_live["error_rate"] = df_live[ERRORS] / df_live[COUNT].replace(0, 1)
df_live["accuracy_score"] = 1 / ((df_live[STD]+1e-6)*(1+df_live["cv"])*(1+df_live["error_rate"])*(1+df_live["range"]*0.01))

df_live = df_live.sort_values("accuracy_score", ascending=False)

# =========================================================
# LIVE DATA TABLE
# =========================================================
st.subheader("📊 Accuracy Table (Live)")
st.dataframe(df_live, use_container_width=True)

st.subheader("🏆 Most Reliable (Live)")
if not df_live.empty:
    st.success(df_live.iloc[0]["device_name"])
else:
    st.warning("No live data available")

# =========================================================
# CURRENT MEASUREMENTS PLOT
# =========================================================
st.subheader("📈 Current Measurements Comparison")
col1, col2, col3 = st.columns([1,2,1])
with col2:
    fig, ax = plt.subplots(figsize=(5,3))
    for _, row in df_live.iterrows():
        ax.plot(row["samples"], label=row["device_name"], linewidth=1)
    ax.set_title("Current Measurements Comparison")
    ax.set_xlabel("Sample Index")
    ax.set_ylabel("Current")
    ax.legend(fontsize=8)
    st.pyplot(fig)

# =========================================================
# ACCURACY SCORE CHART
# =========================================================
st.subheader("📊 Accuracy Score Comparison")
col1, col2, col3 = st.columns([1,2,1])
with col2:
    fig, ax = plt.subplots(figsize=(5,3))
    ax.bar(df_live["device_name"], df_live["accuracy_score"], color='skyblue')
    ax.set_title("Ammeter Accuracy")
    ax.set_ylabel("Score")
    plt.xticks(rotation=20)
    st.pyplot(fig)

# =========================================================
# PYTEST RESULTS
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
            "error": t.get("call", {}).get("longrepr") if t.get("call") else None
        })
    for file_name, tests in grouped.items():
        st.markdown(f"### 📁 {file_name}")
        st.dataframe(pd.DataFrame(tests), use_container_width=True)
else:
    st.warning("No pytest results found")

# =========================================================
# ANALYSIS RESULTS
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
    st.json(comparison.get(RANKING, {}))
else:
    st.warning("No analysis data found")

# =========================================================
# DEBUG LIVE JSON
# =========================================================
with st.expander("🔍 Live JSON Snapshot"):
    st.json(live_data)