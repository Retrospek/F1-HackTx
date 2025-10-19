# backend/app.py (or add to your existing FastAPI app)

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Dict, Optional
import sys
import os

# Add ml directory to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'ml'))

from ml.race_emulator import emulate_2024_race, load_2024_race_data, extract_lap_dashboard_data

app = FastAPI(title="F1 Race Engineer Dashboard API")

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cache race data on startup
RACE_DATA = None

@app.on_event("startup")
async def startup_event():
    """Load and cache race data when API starts"""
    global RACE_DATA
    print("🚀 Loading 2024 COTA race data...")
    RACE_DATA = emulate_2024_race()
    print(f"✅ Cached {len(RACE_DATA)} laps")

# --- API ENDPOINTS ---

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "online",
        "message": "F1 Race Engineer Dashboard API",
        "total_laps": len(RACE_DATA) if RACE_DATA else 0
    }

@app.get("/api/race/info")
async def get_race_info():
    """Get overall race information"""
    if not RACE_DATA:
        raise HTTPException(status_code=503, detail="Race data not loaded")
    
    return {
        "season": RACE_DATA[0]['season'],
        "driver": RACE_DATA[0]['driver'],
        "total_laps": len(RACE_DATA),
        "circuit": "Circuit of the Americas (COTA)"
    }

@app.get("/api/race/lap/{lap_number}")
async def get_lap_data(lap_number: int):
    """
    Get dashboard data for a specific lap
    
    Args:
        lap_number: Lap number (1-56 for COTA)
        
    Returns:
        Complete dashboard data for that lap including:
        - Strategy recommendation with confidence scores
        - Weather conditions
        - Incident messages
        - Lap time analysis
        - Engine power
        - Position & tire compound
        - Tire life expectancy
    """
    if not RACE_DATA:
        raise HTTPException(status_code=503, detail="Race data not loaded")
    
    if lap_number < 1 or lap_number > len(RACE_DATA):
        raise HTTPException(
            status_code=404, 
            detail=f"Lap {lap_number} not found. Valid range: 1-{len(RACE_DATA)}"
        )
    
    return RACE_DATA[lap_number - 1]  # Convert to 0-indexed

@app.get("/api/race/laps")
async def get_all_laps(start_lap: Optional[int] = 1, end_lap: Optional[int] = None):
    """
    Get dashboard data for a range of laps
    
    Args:
        start_lap: Starting lap number (default: 1)
        end_lap: Ending lap number (default: last lap)
        
    Returns:
        List of dashboard data for the specified lap range
    """
    if not RACE_DATA:
        raise HTTPException(status_code=503, detail="Race data not loaded")
    
    if end_lap is None:
        end_lap = len(RACE_DATA)
    
    if start_lap < 1 or end_lap > len(RACE_DATA) or start_lap > end_lap:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid lap range. Valid: 1-{len(RACE_DATA)}"
        )
    
    return RACE_DATA[start_lap - 1:end_lap]

@app.get("/api/race/strategy-summary")
async def get_strategy_summary():
    """
    Get aggregated strategy recommendations across the race
    
    Returns:
        Summary of strategy recommendations with lap ranges
    """
    if not RACE_DATA:
        raise HTTPException(status_code=503, detail="Race data not loaded")
    
    strategy_changes = []
    current_strategy = None
    strategy_start = 1
    
    for lap_data in RACE_DATA:
        lap_num = lap_data['lap_number']
        strategy = lap_data['strategy_recommendation']['recommended_strategy']
        
        if strategy != current_strategy:
            if current_strategy is not None:
                strategy_changes.append({
                    'strategy': current_strategy,
                    'start_lap': strategy_start,
                    'end_lap': lap_num - 1,
                    'duration': lap_num - strategy_start
                })
            current_strategy = strategy
            strategy_start = lap_num
    
    # Add final strategy
    if current_strategy is not None:
        strategy_changes.append({
            'strategy': current_strategy,
            'start_lap': strategy_start,
            'end_lap': len(RACE_DATA),
            'duration': len(RACE_DATA) - strategy_start + 1
        })
    
    return {
        'strategy_changes': strategy_changes,
        'total_changes': len(strategy_changes)
    }

@app.get("/api/race/incidents")
async def get_race_incidents():
    """
    Get all race incidents (yellow flags, safety cars, etc.)
    
    Returns:
        List of all incidents during the race
    """
    if not RACE_DATA:
        raise HTTPException(status_code=503, detail="Race data not loaded")
    
    incidents = []
    
    for lap_data in RACE_DATA:
        if lap_data['incidents']['has_incident']:
            incidents.append({
                'lap_number': lap_data['lap_number'],
                'flag_status': lap_data['incidents']['flag_status'],
                'message': lap_data['incidents']['incident_message'],
                'timestamp': lap_data['timestamp']
            })
    
    return {
        'total_incidents': len(incidents),
        'incidents': incidents
    }

@app.get("/api/race/lap-times")
async def get_lap_times():
    """
    Get all lap times for visualization
    
    Returns:
        Array of lap times with deltas
    """
    if not RACE_DATA:
        raise HTTPException(status_code=503, detail="Race data not loaded")
    
    lap_times = []
    
    for lap_data in RACE_DATA:
        lap_times.append({
            'lap_number': lap_data['lap_number'],
            'lap_time': lap_data['lap_time_analysis']['current_lap_time'],
            'delta': lap_data['lap_time_analysis'].get('delta_to_previous', 0),
            'delta_status': lap_data['lap_time_analysis']['delta_status'],
            'signal': lap_data['lap_time_analysis']['signal']
        })
    
    return lap_times

@app.get("/api/race/tire-history")
async def get_tire_history():
    """
    Get tire wear progression throughout the race
    
    Returns:
        Tire compound changes and wear data
    """
    if not RACE_DATA:
        raise HTTPException(status_code=503, detail="Race data not loaded")
    
    tire_stints = []
    current_compound = None
    stint_start = 1
    
    for lap_data in RACE_DATA:
        lap_num = lap_data['lap_number']
        compound = lap_data['position']['tyre_compound']
        wear = lap_data['tire_life']['tyre_wear_pct']
        
        if compound != current_compound:
            if current_compound is not None:
                tire_stints.append({
                    'compound': current_compound,
                    'start_lap': stint_start,
                    'end_lap': lap_num - 1
                })
            current_compound = compound
            stint_start = lap_num
    
    # Add final stint
    if current_compound is not None:
        tire_stints.append({
            'compound': current_compound,
            'start_lap': stint_start,
            'end_lap': len(RACE_DATA)
        })
    
    # Get wear data
    wear_data = [
        {
            'lap_number': lap['lap_number'],
            'wear_pct': lap['tire_life']['tyre_wear_pct'],
            'compound': lap['position']['tyre_compound'],
            'health_status': lap['tire_life']['tire_health_status']
        }
        for lap in RACE_DATA
    ]
    
    return {
        'tire_stints': tire_stints,
        'wear_progression': wear_data
    }

# --- RUN SERVER ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)