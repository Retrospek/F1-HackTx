# backend/app.py (t elevant section, make sure to integrate this into your existing code)

# ... (Previous imports and setup code) ...

# Global Artifacts (defined globally)
EMU_DATA = None       
MODEL = None          
LE = None             
MODEL_FEATURES = None 

# Simulation State (defined globally)
CURRENT_LAP_INDEX = 0 
MAX_LAP = 0
MAX_LAPS_TO_SHOW = 56 # Standard F1 race laps

# ... (The rest of your code) ...

# New Interface for static data
class RaceInfo(BaseModel):
    season: int
    driver: str
    total_laps: int
    emulation_laps: int
    circuit: str

# FIX: Add the new metadata endpoint
@app.get("/api/race/info", response_model=RaceInfo)
async def get_race_info():
    """Get static race metadata (total laps, driver name, etc.)."""
    global MAX_LAP

    if EMU_DATA is None:
        # Raise 503 if data isn't loaded yet (frontend needs to handle this)
        raise HTTPException(status_code=503, detail="Race data not yet loaded.")
    
    # We are simulating COTA 2024 for Hamilton
    return {
        "season": 2024,
        "driver": "Lewis Hamilton",
        "total_laps": 56, # Hard-coded correct COTA laps
        "emulation_laps": MAX_LAP,
        "circuit": "COTA", 
    }

# ... (The rest of your routes and __main__ block) ...