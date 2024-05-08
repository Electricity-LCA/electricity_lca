#!/bin/bash

cd "$(dirname "$0")"  # Navigate to the top-level directory
source venv/bin/activate  # Activate virtual environment

# Start API service (running on FastAPI, with uvicorn process manager). We use 3 workers to demonstrate using multiple processes
uvicorn src.microservice.main:app --reload --host 0.0.0.0 --port 8000 --workers=3 &
# Start Streamlit Dashboard
streamlit run src/visualization/visualize.py &