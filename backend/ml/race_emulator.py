# backend/ml/race_emulator.py

import pandas as pd
import joblib
import os
import numpy as np
from datetime import datetime

# --- CONFIGURATION ---
ML_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE_PATH = os.path.join(ML_DIR, '..', 'data', 'mercedes_cota_2022_2024.csv')

# Load trained model artifacts
MODEL = joblib.load(os.path.join(ML_DIR, 'strategy_model.joblib'))
LABEL_ENCODER = joblib.load(os.path.join(ML_DIR, 'label_encoder.joblib'))
FEATURES = joblib.load(os.path.join(ML_DIR, 'model_features.joblib'))

# --- LOAD 2024 RACE DATA ---
def load_2024_race_data():
    """Load Hamilton's 2024 COTA race data for emulation"""
    df = pd.read_csv(DATA_FILE_PATH)
    ham_2024 = df[(df['season'] == 2024) & (df['driver'] == 'HAM')].copy()
    ham_2024 = ham_2024.sort_values('lap_number').reset_index(drop=True)
    
    print(f"✅ Loaded 2024 COTA race: {len(ham_2024)} laps for Hamilton")
    return ham_2024

# --- STRATEGY PREDICTION WITH CONFIDENCE ---
def predict_strategy_with_confidence(lap_data):
    """
    Predict strategy recommendation with confidence scores for each category
    
    Returns:
        dict: {
            'recommended_strategy': 'AGGRESSIVE',
            'confidence_scores': {
                'AGGRESSIVE': 0.65,
                'NEUTRAL': 0.25,
                'DEFENSIVE': 0.10
            }
        }
    """
    # Prepare features
    X = lap_data[FEATURES].values.reshape(1, -1)
    
    # Get prediction probabilities
    probabilities = MODEL.predict_proba(X)[0]
    
    # Get the recommended strategy (highest probability)
    predicted_class = MODEL.predict(X)[0]
    recommended_strategy = LABEL_ENCODER.inverse_transform([predicted_class])[0]
    
    # Create confidence scores dictionary
    confidence_scores = {
        strategy: float(prob) 
        for strategy, prob in zip(LABEL_ENCODER.classes_, probabilities)
    }
    
    return {
        'recommended_strategy': recommended_strategy,
        'confidence_scores': confidence_scores
    }

# --- EXTRACT DASHBOARD DATA FOR EACH LAP ---
def extract_lap_dashboard_data(lap_row, prev_lap_row=None):
    """
    Extract all dashboard-relevant data for a single lap
    
    Returns complete dashboard payload including:
    - Strategy recommendation
    - Weather info
    - Incident messages
    - Lap time metrics
    - Engine power
    - Position & compound
    - Tire life expectancy
    """
    
    # 1. STRATEGY RECOMMENDATION
    strategy_rec = predict_strategy_with_confidence(lap_row)
    
    # 2. WEATHER DATA
    weather = {
        'condition': lap_row['weather_condition'],
        'rainfall_mm': float(lap_row['rainfall_mm']),
        'air_temperature_C': float(lap_row['air_temperature_C']),
        'is_raining': lap_row['rainfall_mm'] > 0
    }
    
    # 3. RACE INCIDENTS
    incidents = {
        'flag_status': lap_row['flag_status'],
        'incident_message': lap_row['incident_message'] if pd.notna(lap_row['incident_message']) else None,
        'has_incident': lap_row['flag_status'] != 'Green'
    }
    
    # 4. LAP TIME ANALYSIS
    lap_time_data = {
        'current_lap_time': float(lap_row['lap_time']),
        'lap_number': int(lap_row['lap_number'])
    }
    
    # Calculate delta if previous lap exists
    if prev_lap_row is not None:
        delta = lap_row['lap_time'] - prev_lap_row['lap_time']
        lap_time_data['delta_to_previous'] = float(delta)
        lap_time_data['delta_status'] = 'improving' if delta < 0 else 'degrading'
        
        # Push/conserve signal based on delta
        if delta < -0.5:
            lap_time_data['signal'] = 'PUSH - Delta improving!'
        elif delta > 2.0:
            lap_time_data['signal'] = 'WARNING - Degradation detected'
        else:
            lap_time_data['signal'] = 'MAINTAIN - Stable pace'
    else:
        lap_time_data['delta_to_previous'] = 0.0
        lap_time_data['delta_status'] = 'baseline'
        lap_time_data['signal'] = 'MAINTAIN'
    
    # 5. ENGINE POWER
    engine = {
        'engine_power_pct': float(lap_row['engine_power_pct']),
        'throttle_pct': float(lap_row['throttle_pct'])
    }
    
    # 6. POSITION & COMPOUND
    position_data = {
        'current_position': int(lap_row['position']),
        'tyre_compound': lap_row['tyre_compound']
    }
    
    # 7. TIRE LIFE EXPECTANCY
    tire_data = {
        'tyre_wear_pct': float(lap_row['tyre_wear_pct']),
        'stint_lap_count': int(lap_row['stint_lap_count']),
        'tyre_temp_C': float(lap_row['tyre_temp_C']),
        'expected_life_remaining': None,  # Calculate below
        'tire_health_status': None  # Calculate below
    }
    
    # Calculate expected tire life (simplified model)
    wear = tire_data['tyre_wear_pct']
    if wear < 30:
        tire_data['expected_life_remaining'] = 'High (20+ laps)'
        tire_data['tire_health_status'] = 'GOOD'
    elif wear < 60:
        tire_data['expected_life_remaining'] = 'Medium (10-20 laps)'
        tire_data['tire_health_status'] = 'FAIR'
    elif wear < 80:
        tire_data['expected_life_remaining'] = 'Low (5-10 laps)'
        tire_data['tire_health_status'] = 'DEGRADING'
    else:
        tire_data['expected_life_remaining'] = 'Critical (<5 laps)'
        tire_data['tire_health_status'] = 'CRITICAL'
    
    # 8. ADDITIONAL TELEMETRY
    telemetry = {
        'speed_kph': float(lap_row['speed_kph']),
        'drs_status': lap_row['drs_status'],
        'fuel_load_kg': float(lap_row['fuel_load_kg']),
        'interval_gap': float(lap_row['interval_gap'])
    }
    
    # COMPLETE DASHBOARD PAYLOAD
    dashboard_data = {
        'timestamp': lap_row['timestamp'],
        'lap_number': int(lap_row['lap_number']),
        'driver': lap_row['driver'],
        'season': int(lap_row['season']),
        
        # Main sections
        'strategy_recommendation': strategy_rec,
        'weather': weather,
        'incidents': incidents,
        'lap_time_analysis': lap_time_data,
        'engine': engine,
        'position': position_data,
        'tire_life': tire_data,
        'telemetry': telemetry
    }
    
    return dashboard_data

# --- EMULATE ENTIRE 2024 RACE ---
def emulate_2024_race():
    """
    Process all laps of Hamilton's 2024 race and return dashboard data for each lap
    
    Returns:
        list: List of dashboard data dictionaries (one per lap)
    """
    # Load data
    ham_2024 = load_2024_race_data()
    
    race_data = []
    prev_lap = None
    
    print(f"\n🏁 Starting 2024 COTA race emulation...")
    print("="*70)
    
    for idx, row in ham_2024.iterrows():
        lap_data = extract_lap_dashboard_data(row, prev_lap)
        race_data.append(lap_data)
        
        # Print summary for each lap
        lap_num = lap_data['lap_number']
        strategy = lap_data['strategy_recommendation']['recommended_strategy']
        confidence = lap_data['strategy_recommendation']['confidence_scores'][strategy]
        position = lap_data['position']['current_position']
        tire_health = lap_data['tire_life']['tire_health_status']
        
        print(f"Lap {lap_num:2d} | P{position} | Strategy: {strategy:10s} ({confidence:.1%}) | Tires: {tire_health}")
        
        # Store for next iteration
        prev_lap = row
    
    print("="*70)
    print(f"✅ Race emulation complete! Processed {len(race_data)} laps\n")
    
    return race_data

# --- EXPORT TO JSON ---
def export_race_data_to_json(race_data, output_path='race_2024_emulation.json'):
    """Export race data to JSON for frontend consumption"""
    import json
    
    output_file = os.path.join(ML_DIR, output_path)
    
    with open(output_file, 'w') as f:
        json.dump(race_data, f, indent=2, default=str)
    
    print(f"📁 Race data exported to: {output_file}")
    return output_file

# --- MAIN EXECUTION ---
if __name__ == '__main__':
    print("\n" + "="*70)
    print("🏎️  F1 2024 COTA RACE EMULATOR - Lewis Hamilton")
    print("="*70 + "\n")
    
    # Run emulation
    race_data = emulate_2024_race()
    
    # Export to JSON
    export_race_data_to_json(race_data)
    
    # Show sample data for first lap
    print("\n📊 SAMPLE DASHBOARD DATA (Lap 1):")
    print("="*70)
    import json
    print(json.dumps(race_data[0], indent=2, default=str))