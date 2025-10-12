@echo off
echo ===== OSINT Threat Intelligence Pipeline =====
echo.

echo [1/2] Running pipeline to collect and process threat data...
python run_pipeline.py 8.8.8.8

echo.
echo [2/2] Starting web dashboard at http://localhost:5000
echo (Press Ctrl+C to stop the server when finished)
echo.
python app.py