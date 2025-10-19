# backend/app.py
import torch
import torch.nn as nn
import torch.nn.functional as F

import os
import sys
import uvicorn
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import pandas as pd

class MDNNetwork(nn.Module):
    def __init__(self, in_dim=140, action_dim=3, latent_dim=64, out_dim=1):
        """
        Args:
            in_dim: Number of input features (after LSTM or raw)
            hidden_dim: Hidden layer size
            num_gaussians: Number of mixture components K
            out_dim: Dimension of the target (e.g., 1 for lap_time)
        """
        super().__init__()
        self.K = action_dim # Otherwise known as the number of possible actions to be taken
                                            # K or the num_gaussians represents the num of modes
        self.out_dim = out_dim

        self.net = nn.Sequential(
            nn.Linear(in_dim, 128),
            nn.ReLU(),
            nn.Linear(128, 64),
            nn.ReLU(),
            nn.Linear(64, latent_dim),
            nn.ReLU() # Threshold at 0
        )

        # Each Gaussian needs mu, sigma, and a mixture weight (pi)
        self.fc_mu = nn.Linear(latent_dim, action_dim * out_dim)
        self.fc_sigma = nn.Linear(latent_dim, action_dim * out_dim)
        self.fc_sigma.bias.data.fill_(0.0)  # so exp(0)=1 as starting sigma

        self.fc_pi = nn.Linear(latent_dim, self.K)

    def forward(self, x):
        h = self.net(x)

        mu = self.fc_mu(h)                         # shape: [B, K*out_dim]
        sigma = torch.exp(self.fc_sigma(h)).clamp(min=1e-3)        # positive std
        pi = F.softmax(self.fc_pi(h), dim=1)       # mixture weights sum to 1

        # reshape for clarity
        mu = mu.view(-1, self.K, self.out_dim)
        sigma = sigma.view(-1, self.K, self.out_dim)
        
        return mu, sigma, pi

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

seq_len = 10
num_features = 14
in_dim = seq_len * num_features
action_dim = 4
out_dim = 1
latent_dim = 64

# Load model
model = MDNNetwork(in_dim=in_dim, action_dim=action_dim, latent_dim=latent_dim, out_dim=out_dim)
model.load_state_dict(torch.load(r"ml/mdn_model_4_nt.pth", map_location="cpu"))
model.eval()

@app.get("/api/tyrecondition")
def get_tyre_class_prediction(data_path: str):
    df = pd.read_csv(data_path)

    df_filtered = df[(df['driver'] == 'HAM') & (df['season'] == 2024)]
    if df_filtered.empty:
        raise HTTPException(status_code=404, detail="No data found for Hamilton at COTA 2024")

    features = df_filtered.drop(columns=[
        "timestamp", "driver", "flag_status", "push_signal",
        "tyre_compound", "drs_status", "weather_condition", "lap_time"
    ])
    features = features.apply(pd.to_numeric, errors='coerce').fillna(0).values

    sequences = []
    for i in range(len(features) - seq_len):
        sequences.append(features[i:i+seq_len])
    sequences = torch.tensor(sequences, dtype=torch.float32)
    sequences = sequences.view(sequences.shape[0], -1)

    with torch.no_grad():
        mu, sigma, pi = model(sequences)

    predicted_class_idx = torch.argmax(pi, dim=1)
    action_map = {0: "MAINTAIN", 1: "PUSH", 2: "CONSERVE", 3: "DEGRADATION WARNING"}
    predicted_actions = [action_map[idx.item()] for idx in predicted_class_idx]

    result = []
    for i in range(len(predicted_actions)):
        result.append({
            "lap_index": i + 1,
            "predicted_action": predicted_actions[i],
            "pi": pi[i].tolist(),
            "mu": mu[i].squeeze().tolist(),
            "sigma": sigma[i].squeeze().tolist()
        })
    print(result)
    return {"driver": "HAM", "circuit": "COTA", "season": 2024, "predictions": result}
# Main execution for standalone running
if __name__ == "__main__":
    uvicorn.run(
        "app:app", 
        host="0.0.0.0", 
        port=8000, 
        reload=True
    )