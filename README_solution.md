# Ammeter Testing & Analysis System

## 📌 Overview

This project is a complete Ammeter testing, analysis, and visualization framework.

It simulates or collects measurements from multiple ammeters, analyzes their performance, and provides statistical comparison and a live dashboard.

### The system includes:
- Automated test execution
- Statistical analysis (accuracy, consistency, error rate)
- Visualization of current measurements
- Streamlit dashboard for real-time results
- Logging system for debugging and traceability

---

## ⚙️ Installation

```bash
pip install numpy pandas matplotlib streamlit pyyaml pytest
pip install -r requirements.txt
pip install pytest-json-report
```

---

## 🚀 Running the System

### ▶️ 1. Full System Execution

```bash
python main.py
```

**What it does:**
- Executes AmmeterTestFramework for all configured devices
- Collects raw measurement samples from each ammeter
- Computes statistical metrics (mean, median, std, min, max, etc.)
- Runs the Orchestrator to normalize and process results
- Saves final output to results.json
- Generates and saves per-ammeter measurement plots

**Execution Flow:**
```
AmmeterTestFramework
        ↓
Orchestrator
        ↓
AccuracyAssessment
        ↓
save_raw_plots()
        ↓
results.json generated
```

**Output:**
- Full measurement dataset
- Statistical processing results
- Visualization plots per ammeter

---

### 🧪 2. Run Tests (Pytest)

```bash
pytest -s --json-report --json-report-file=results/pytest_results.json
```

**What it does:**
- Runs all automated unit tests
- Tests framework logic, analysis, and orchestrator
- Validates edge cases (empty data, failures)
- Generates structured JSON report

**Execution Flow:**
```
test_framework tests
        ↓
analysis tests
        ↓
orchestrator tests
        ↓
pytest report
```

**Output:**
- Test validation report
- Pass/fail results per module

---

### 📊 3. Run Analysis Only

```bash
python -m src.run_analysis
```

**What it does:**
- Loads existing results.json
- Computes statistical metrics:
  - Mean
  - Median
  - Standard deviation
  - Accuracy score
- Ranks ammeters by performance
- Saves results to analysis_results.json

**Execution Flow:**
```
results.json
        ↓
AccuracyAssessment
        ↓
statistical computation
        ↓
ranking calculation
        ↓
analysis_results.json
```

**Output:**
- Analytical comparison of ammeters
- Performance ranking table

---

### 📊 4. Run Dashboard (UI)

```bash
streamlit run ui/app.py
```

**What it does:**

Loads:
- results.json
- analysis_results.json
- pytest_results.json

Displays:
- Accuracy comparison table
- Performance ranking
- Raw measurement graphs
- Test results
- Analysis results

**Execution Flow:**
```
results.json + analysis_results.json + pytest_results.json
                    ↓
            Streamlit UI
                    ↓
            Charts + Tables + Graphs
```

**Output:**
- Interactive web dashboard

---

## 🔄 Overall System Flow

```
main.py
   ↓
AmmeterTestFramework (data collection)
   ↓
Orchestrator (coordination)
   ↓
AccuracyAssessment (analysis)
   ↓
results.json + plots
   ↓
Streamlit Dashboard
   ↑
pytest validation layer
```

---

## 📁 Project Structure

```
Test_QA_expanded/
│
├── main.py
├── run_analysis.py
├── pytest.ini
│
├── tests/
│   ├── conftest.py   # Shared pytest fixtures (setup for tests)
│   ├── test_analysis.py
│   └── test_orchestrator.py
│
├── config/
│   └── config.yaml
│
├── ammeters/
│   ├── base_ammeter.py
│   ├── circuitor.py
│   ├── entes.py
│   └── greenlee.py
│
├── src/
│   ├── testing/
│   │   ├── test_framework.py
│   │   ├── orchestrator.py
│   │   ├── accuracy_assessment.py
│   │   ├── error_manager.py
│   │   └── error_simulator.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── ammeter_result.py
│   │   ├── analysis_model.py
│   │   ├── error_models.py
│   │   ├── pipeline_output.py
│   │   ├── sensor_model.py
│   │   └── statistics_model.py
│   │
│   ├── utils/
│   │   ├── logger.py
│   │   ├── config.py
│   │   └── utils.py
│   │
│   └── config/
│       └── constants.py
│
├── ui/
│   └── app.py
│
├── results/
│   ├── results.json
│   ├── analysis_results.json
│   ├── pytest_results.json
│   ├── logs/
│   └── plots/
│
└── README.md
```

---

## 🛠️ Fixed Issues Summary

- ✅ Fixed port mapping between ammeters
- ✅ Fixed missing package initialization (__init__.py)
- ✅ Fixed missing imports (Dict, typing issues)
- ✅ Fixed run_test parameter mismatch
- ✅ Fixed missing return values in pipeline
- ✅ Fixed client/server protocol mismatch
- ✅ Replaced hardcoded config with YAML-driven configuration
- ✅ Added pytest instead of manual execution
- ✅ Fixed threading lifecycle issue
- ✅ Improved logging and traceability

---

## 📌 Notes

- Fully modular and extensible architecture
- Supports multiple ammeter types
- Designed for embedded systems QA workflows
- Built for scalability, debugging, and analysis
