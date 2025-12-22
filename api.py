# api.py
import sys
import os
import json
import uuid
import threading
from datetime import datetime
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional

# Import CrewAI logic
from crew import create_financial_crew
from config import REPORTS_DIR

# Ensure stdout encodes correctly
sys.stdout.reconfigure(encoding='utf-8')

app = FastAPI(title="Financial Analysis API")

# Setup CORS for Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all for development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Job Store (In-Memory)
jobs: Dict[str, Dict[str, Any]] = {}

class AnalysisRequest(BaseModel):
    symbol: str

def run_analysis_task(task_id: str, symbol: str):
    """
    Background worker to run the financial crew.
    """
    print(f"[{task_id}] Starting analysis for {symbol}")
    jobs[task_id]["status"] = "running"
    
    try:
        # Create and run crew
        crew = create_financial_crew(symbol.upper())
        inputs = {
            "stock_symbol": symbol.upper(),
            "analysis_date": datetime.now().strftime("%Y-%m-%d"),
        }
        
        # This blocks until completion
        result = crew.kickoff(inputs=inputs)
        
        # Save to file (as per original main.py logic)
        report_filename = os.path.join(
            REPORTS_DIR,
            f"{symbol.upper()}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        os.makedirs(REPORTS_DIR, exist_ok=True)
        
        with open(report_filename, 'w') as f:
            json.dump({
                "symbol": symbol.upper(),
                "analysis_date": datetime.now().isoformat(),
                "report": str(result),
            }, f, indent=2)
            
        jobs[task_id]["status"] = "completed"
        jobs[task_id]["result"] = str(result)
        jobs[task_id]["report_file"] = report_filename
        print(f"[{task_id}] Analysis complete for {symbol}")
        
    except Exception as e:
        print(f"[{task_id}] Error: {e}")
        jobs[task_id]["status"] = "failed"
        jobs[task_id]["error"] = str(e)

@app.post("/analyze")
async def analyze(request: AnalysisRequest, background_tasks: BackgroundTasks):
    task_id = str(uuid.uuid4())
    jobs[task_id] = {
        "status": "pending",
        "symbol": request.symbol,
        "submitted_at": datetime.now().isoformat()
    }
    
    background_tasks.add_task(run_analysis_task, task_id, request.symbol)
    
    return {"task_id": task_id, "status": "pending"}

@app.get("/status/{task_id}")
async def get_status(task_id: str):
    if task_id not in jobs:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return jobs[task_id]

@app.get("/health")
async def health():
    return {"status": "ok"}
