# backend/app.py

from fastapi import FastAPI, HTTPException
import uvicorn
import os
import pandas as pd
import joblib 
from typing import Dict
from pydantic import BaseModel

# --- Global Artifacts (Placeholders) ---
# NOTE: These variables will hold your data and model once loaded later
EMU_DATA = None # Will hold the 2024 Lap/Telemetry DataFrame
MODEL = None 
LE = None # Label Encoder
CURRENT_LAP_INDEX = 0 
MAX_LAP = 0

# --- Pydantic Schema for API Response ---
class LapFeedResponse(BaseModel):
    status: str
    current_lap: int
    raw_lap_time: float
    ML_Recommendation: str
    ML_Confidence: float
    # Define placeholder types for other required dashboard metrics
    throttle_percent: float
    track_temp: float
    rain_amount: float
    
# --- FastAPI Initialization ---
app = FastAPI()

# --- Placeholder Function to Load Everything (Will be implemented after data is gathered)
def load_global_state():
    # When your data extraction runs, this will load all CSVs and ML models
    print("Pre-loading data and ML models... (CURRENTLY PLACEHOLDER)")
    global EMU_DATA, MAX_LAP
    # For now, we load a dummy DataFrame to prevent errors
    EMU_DATA = pd.DataFrame({'lap_number': [1, 2, 3], 'lap_duration': [90.0, 90.1, 90.2], 'track_temp': [30, 31, 32]})
    MAX_LAP = len(EMU_DATA)
    # The actual joblib loading and DataFrame merging logic goes here later.
    

# --- API ROUTES ---

@app.on_event("startup")
def startup_event():
    # This runs once when the server starts
    load_global_state()


@app.get('/api/feed', response_model=LapFeedResponse)
async def get_lap_feed():
    """Returns the next frame of race data and the ML prediction."""
    global CURRENT_LAP_INDEX
    
    if CURRENT_LAP_INDEX >= MAX_LAP:
        return {"status": "Race Finished", "current_lap": MAX_LAP, "raw_lap_time": 0.0, 
                "ML_Recommendation": "N/A", "ML_Confidence": 0.0, "throttle_percent": 0.0, "track_temp": 0.0, "rain_amount": 0.0}

    # NOTE: The actual ML calculation logic will replace these placeholders
    lap_data = EMU_DATA.iloc[CURRENT_LAP_INDEX]
    
    response = {
        "status": "In Progress",
        "current_lap": int(lap_data['lap_number']),
        "raw_lap_time": float(lap_data['lap_duration']),
        "ML_Recommendation": "Neutral", 
        "ML_Confidence": 75.0,
        "throttle_percent": 99.0,
        "track_temp": float(lap_data['track_temp']),
        "rain_amount": 0.0,
    }
    
    CURRENT_LAP_INDEX += 1
    return response

# Example for the Lap Time Graph Data (returns cumulative data)
@app.get('/api/laps/cumulative')
def get_cumulative_laps():
    """Returns all lap data up to the current lap for the graph."""
    global CURRENT_LAP_INDEX
    if CURRENT_LAP_INDEX == 0:
        return []
    
    # Return the data rows already processed
    df_history = EMU_DATA.head(CURRENT_LAP_INDEX)
    
    return df_history[['lap_number', 'lap_duration']].to_dict('list')


# --- Run Server Command (to be executed in the terminal) ---
if __name__ == '__main__':
    uvicorn.run("app:app", host="127.0.0.1", port=5000, reload=True) # Use reload=True for hackathon