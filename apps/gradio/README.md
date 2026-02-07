---
title: Credit Risk Model Demo
emoji: "\U0001F4CA"
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 6.5.1
python_version: "3.12"
app_file: app.py
pinned: false
---

# Credit Risk Model Demo

Interactive demo for training and evaluating credit risk models.

**Live demo:** [huggingface.co/spaces/pkiage/credit_risk_modeling_demo](https://huggingface.co/spaces/pkiage/credit_risk_modeling_demo)

## Local Development

1. Start the API:

   ```bash
   cd apps/api
   uv run uvicorn main:app --reload
   ```

2. Start Gradio:

   ```bash
   cd apps/gradio
   gradio app.py
   ```

## Environment Variables

- `CREDIT_RISK_API_URL`: API base URL (default: `http://localhost:8000`)
