# Healthcare Analytics Dashboard

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/UI-Streamlit-FF4B4B.svg)](https://streamlit.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

An interactive **health informatics portfolio dashboard** built with Python and Streamlit. Explore synthetic inpatient-style encounters through KPIs, operational trends, data quality checks, and lightweight explainable “AI” insights.

> **Disclaimer:** All default data are **synthetic** and for education/portfolio use only. This app is **not** for clinical decision-making.

![Dashboard preview](docs/screenshots/01_overview.png)

*Add screenshots under `docs/screenshots/` after running locally (see [Screenshots](#screenshots)).*

---

## Highlights

| Page | What you see |
|------|----------------|
| **Overview** | Distinct patients, avg LOS, 30-day readmission %, avg cost, avg wait |
| **Patient Trends** | Admissions over time, diagnosis mix, department utilization, age groups |
| **Operational Insights** | Wait, cost, LOS, and readmission trends |
| **Data Quality** | Missing values, duplicate IDs, invalid ages, impossible dates |
| **AI Insights** | Rule-based narratives + Isolation Forest anomaly screening |

**Built-in features:** sidebar filters (date, department, diagnosis, gender, age group), Plotly charts, CSV export of the filtered slice.

---

## Quick start

```powershell
git clone https://github.com/karimabushbak/healthcare-analytics-dashboard.git
cd healthcare-analytics-dashboard
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m streamlit run app.py
```

Open the URL Streamlit prints (usually `http://localhost:8501`).

On first run, the app creates `data/healthcare_records.csv` automatically if it does not exist (~4,000 synthetic rows with intentional data-quality defects).

---

## Tech stack

- **Streamlit** — multipage UI
- **Pandas** — transforms and exports
- **Plotly** — interactive charts
- **NumPy** — synthetic data generation
- **scikit-learn** — `IsolationForest` for multivariate anomaly detection

---

## Data model (synthetic default)

| Column | Description |
|--------|-------------|
| `patient_id` | Encounter identifier (may repeat for duplicate/visit scenarios) |
| `age`, `gender` | Demographics |
| `diagnosis`, `department` | Clinical / operational grouping |
| `admission_date`, `discharge_date` | Encounter window |
| `length_of_stay` | Days between admission and discharge |
| `readmission_30_days` | 30-day readmission flag |
| `treatment_cost` | Cost proxy |
| `insurance_type`, `outcome` | Payer and disposition |
| `wait_time_minutes` | Access metric |
| `data_quality_issue` | Semicolon-separated QA flags (`None`, `missing_field`, etc.) |

Regenerate the synthetic CSV anytime:

```bash
python utils/generate_synthetic_data.py
```

### Optional: your own CSV

Point the loader at a de-identified file with the **same column names** (order does not matter):

```powershell
$env:HEALTHCARE_DASHBOARD_CSV = "C:\path\to\your_encounters.csv"
python -m streamlit run app.py
```

Do **not** commit PHI to a public repository. Use only data you are authorized to analyze.

---

## Project structure

```
health/
├── app.py                         # Landing page
├── requirements.txt
├── data/
│   └── healthcare_records.csv     # Synthetic data (auto-created)
├── pages/
│   ├── 1_Overview.py
│   ├── 2_Patient_Trends.py
│   ├── 3_Operational_Insights.py
│   ├── 4_Data_Quality.py
│   └── 5_AI_Insights.py
└── utils/
    ├── data_loader.py             # Cached CSV load
    ├── generate_synthetic_data.py
    ├── filters.py
    ├── kpis.py
    ├── data_quality.py
    └── insights.py
```

---

## Screenshots

Capture these after running the app and save under `docs/screenshots/`:

1. `01_overview.png` — KPI cards
2. `02_patient_trends.png` — volume and mix charts
3. `03_operations.png` — wait / cost / LOS / readmission
4. `04_data_quality.png` — profiling panels
5. `05_ai_insights.png` — insights + anomalies

---

## Health informatics angle

- Secondary use of **administrative** data for operations and quality reporting  
- Metric definitions aligned with common management questions (LOS, readmission proxy, cost, access)  
- **Data governance** patterns: completeness, validity, duplicate identifiers  
- Responsible analytics: synthetic defaults, clear disclaimers, explainable insight layer  

---

## License

MIT — see [LICENSE](LICENSE). Synthetic data only by default; you are responsible for compliance if you plug in real data.
