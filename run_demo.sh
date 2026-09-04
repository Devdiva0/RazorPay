#!/bin/bash
set -e
python -m app.train
echo "Starting API on http://127.0.0.1:8000"
uvicorn app.api:app --host 127.0.0.1 --port 8000 &
API_PID=$!
trap 'kill $API_PID' EXIT
sleep 2
streamlit run app/dashboard.py
