@echo off

if "%1"=="build" (
    echo Building Docker image...
    docker build -t xbuddy-api:latest .
    echo Docker image build completed.
) else (
    echo Starting application...
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
)