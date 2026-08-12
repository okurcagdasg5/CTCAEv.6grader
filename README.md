# CTCAE v6.0 Grader

A small local Streamlit application for quickly browsing and grading adverse events
using NCI CTCAE v6.0 / MedDRA 28.0.

The included SQLite database contains **850 CTCAE terms** imported from the
official NCI Excel file (`data/ctcae-v6.0.xlsx`), sheet `CTCAE v6.0 Clean Copy`.

## Fastest way to run on Windows

1. Extract the ZIP.
2. Open the `CTCAE_v6_Grader` folder in Visual Studio Code.
3. Double-click `run.bat`.

Or from the VS Code terminal:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run app.py
```

Your browser should open the local Streamlit application.

## How it works

1. Optionally select a CTCAE System Organ Class.
2. Search/select the adverse event.
3. Open the `Patient value / clinical condition` drop-down.
4. Select the matching official CTCAE v6.0 criterion.
5. The app displays the corresponding Grade.

## Source

National Cancer Institute (NCI), Common Terminology Criteria for Adverse Events
(CTCAE) v6.0, MedDRA 28.0.

Official source workbook is included unchanged in `data/ctcae-v6.0.xlsx`.

## Important

This tool is a reference aid and does **not** replace investigator assessment,
the study protocol, sponsor instructions, or the official NCI CTCAE source.
