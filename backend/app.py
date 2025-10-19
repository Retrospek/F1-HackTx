# backend/app.py

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

# Add the backend directory to Python path
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(backend_dir)

# Import race emulation modules
from ml.race_emulator import emulate_2024_race

# Global Artifacts (defined globally)
EMU_DATA = None       
MODEL = None          
LE = None             
MODEL_FEATURES = None 

# Simulation State (defined globally)
CURRENT_LAP_INDEX = 0 
MAX_LAP = 0
MAX_LAPS_TO_SHOW = 56 # Standard F1 race laps

# Pydantic Model for Race Info
class RaceInfo(BaseModel):
    season: int
    driver: str
    total_laps: int
    emulation_laps: int
    circuit: str

# Initialize FastAPI application
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # Next.js default dev server
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Race Information Endpoint
@app.get("/api/race/info", response_model=RaceInfo)
async def get_race_info():
    """Get static race metadata (total laps, driver name, etc.)."""
    global EMU_DATA, MAX_LAP
    
    # Load emulation data if not already loaded
    if EMU_DATA is None:
        try:
            EMU_DATA = emulate_2024_race()
            MAX_LAP = len(EMU_DATA)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error loading race data: {str(e)}"
            )
    
    return {
        "season": 2024,
        "driver": "Lewis Hamilton",
        "total_laps": 56,  # COTA standard race length
        "emulation_laps": MAX_LAP,
        "circuit": "COTA", 
    }

# Race Feed Endpoint
@app.get("/api/feed")
async def get_next_lap():
    """Provide next lap's race data for dashboard."""
    global CURRENT_LAP_INDEX, EMU_DATA, MAX_LAP
    
    # Ensure race data is loaded
    if EMU_DATA is None:
        try:
            EMU_DATA = emulate_2024_race()
            MAX_LAP = len(EMU_DATA)
        except Exception as e:
            raise HTTPException(
                status_code=500, 
                detail=f"Error loading race data: {str(e)}"
            )
    
    # Check if race is finished
    if CURRENT_LAP_INDEX >= MAX_LAP:
        raise HTTPException(status_code=410, detail="Race finished")
    
    # Get current lap data
    current_lap = EMU_DATA[CURRENT_LAP_INDEX]
    CURRENT_LAP_INDEX += 1
    
    return {
        "flag_status": current_lap.get('incidents', {}).get('flag_status', 'Green'),  # FIXED
        "incident_message": current_lap.get('incidents', {}).get('incident_message', ''),  # FIXED
        "timestamp": current_lap.get('timestamp', ''),
        "current_lap": current_lap.get('lap_number', 0),
        "raw_lap_time": current_lap.get('lap_time_analysis', {}).get('current_lap_time', 0),
        "track_temp": current_lap.get('weather', {}).get('air_temperature_C', 0),
        "rainfall_mm": current_lap.get('weather', {}).get('rainfall_mm', 0),
        "throttle_percent": current_lap.get('engine', {}).get('throttle_pct', 0),
        "current_position": current_lap.get('position', {}).get('current_position', 0),
        "tyre_compound": current_lap.get('position', {}).get('tyre_compound', 'N/A'),
        "stint_lap_count": current_lap.get('tire_life', {}).get('stint_lap_count', 0),  # FIXED
        "tyre_wear_pct": current_lap.get('tire_life', {}).get('tyre_wear_pct', 0),  # FIXED
        "delta_message": current_lap.get('lap_time_analysis', {}).get('signal', 'MAINTAIN'),
        "ML_Recommendation": current_lap.get('strategy_recommendation', {}).get('recommended_strategy', 'NEUTRAL'),
        "ML_Confidence": {
            "AGGRESSIVE": current_lap.get('strategy_recommendation', {}).get('confidence_scores', {}).get('AGGRESSIVE', 0),
            "NEUTRAL": current_lap.get('strategy_recommendation', {}).get('confidence_scores', {}).get('NEUTRAL', 0),
            "DEFENSIVE": current_lap.get('strategy_recommendation', {}).get('confidence_scores', {}).get('DEFENSIVE', 0)
        },
        "status": "Active" if CURRENT_LAP_INDEX < MAX_LAP else "Finished"
    }

# Race Reset Endpoint
@app.post("/api/reset")
async def reset_race():
    """Reset race simulation to starting conditions."""
    global CURRENT_LAP_INDEX, EMU_DATA
    CURRENT_LAP_INDEX = 0
    EMU_DATA = None  # Force reload of race data
    return {"message": "Race reset"}

# Main execution for standalone running
if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )