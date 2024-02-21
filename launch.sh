#!/bin/bash

source venv/bin/activate

streamlit run src/visualization/visualize.py &
uvicorn src.microservice.main:app --reload --host 0.0.0.0 --port 8000