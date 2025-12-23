@echo off
echo Starting Financial Analysis Crew Application...
echo Ensure Docker Desktop is running.

if not exist .env (
    echo WARNING: .env file not found! Application may fail if API keys are missing.
)

docker-compose up --build
pause
