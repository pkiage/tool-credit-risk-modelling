# Marimo Notebooks

Interactive Marimo notebooks for credit risk model exploration.

## Prerequisites

```bash
# Activate your virtual environment first
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\Activate.ps1  # Windows PowerShell

# Install marimo
pip install marimo
```

> **Windows:** If `marimo` isn't recognized, use `python -m marimo` instead, or [add Python Scripts to your PATH](https://docs.python.org/3/using/windows.html#finding-the-python-executable).
>
> **macOS/Linux:** You may need `pip3` and `python3` on systems where Python 2 is the default.

## Notebooks

| Notebook | Purpose |
|----------|---------|
| `01_eda.py` | Exploratory data analysis — dataset overview, distributions, correlations |
| `02_model_comparison.py` | Train and compare logistic regression, XGBoost, random forest |
| `03_threshold_optimization.py` | Youden's J threshold walkthrough with interactive slider |
| `04_calibration.py` | Probability calibration assessment and correction |

## Running Locally

```bash
# Interactive editing mode
marimo edit notebooks/01_eda.py

# Read-only app mode
marimo run notebooks/01_eda.py
```

## Deploying to Molab

Each notebook is a standalone `.py` file that can be deployed directly:

```bash
marimo deploy notebooks/01_eda.py
```

## Exporting

```bash
# Export to HTML
marimo export html notebooks/01_eda.py -o output.html

# Export as WASM (client-side)
marimo export html-wasm notebooks/01_eda.py -o output/
```

## Architecture

All notebooks import from the `shared/` layer — no business logic is duplicated.

- **Schemas**: `shared.schemas` (LoanDataset, TrainingConfig, ThresholdResult, etc.)
- **Logic**: `shared.logic` (evaluate_model, find_optimal_threshold, etc.)
- **Constants**: `shared.constants` (feature names, model params, validation bounds)
