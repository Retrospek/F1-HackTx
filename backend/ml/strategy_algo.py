# backend/data/ml/strategy_algo.py

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
import joblib
import os
import numpy as np

# --- 0. CONFIGURATION & PATH CORRECTION ---

# Get the directory where this script is located (backend/ml/)
ML_DIR = os.path.dirname(os.path.abspath(__file__))

# Navigate to the data folder and find the CSV
# From: backend/ml/
# To: backend/data/mercedes_cota_2022_2024.csv
DATA_FILE_PATH = os.path.join(ML_DIR, '..', 'data', 'mercedes_cota_2022_2024.csv')

# Ensure the ML directory exists
os.makedirs(ML_DIR, exist_ok=True)

# --- 1. SYNTHETIC STRATEGY LABELING ---

def label_strategy(row):
    """
    Creates synthetic strategy labels based on race conditions.
    
    AGGRESSIVE: Push hard, high tire wear acceptable
    NEUTRAL: Balanced approach
    DEFENSIVE: Conserve tires, manage degradation
    """
    
    # Key factors for strategy decision
    tyre_wear = row['tyre_wear_pct']
    lap_time = row['lap_time']
    position = row['position']
    stint_lap = row['stint_lap_count']
    push_signal = row['push_signal']
    
    # AGGRESSIVE conditions
    if (push_signal == 'PUSH' and tyre_wear < 30) or \
       (position <= 3 and tyre_wear < 40 and stint_lap < 10):
        return 'AGGRESSIVE'
    
    # DEFENSIVE conditions  
    elif (tyre_wear > 60) or \
         (push_signal in ['CONSERVE', 'DEGRADATION WARNING']) or \
         (lap_time > 100):  # Slower laps indicate conservation
        return 'DEFENSIVE'
    
    # NEUTRAL (default)
    else:
        return 'NEUTRAL'

# --- 2. MODEL CREATION FUNCTION ---

def create_ml_artifacts():
    """
    Loads COTA 2022/2023 data, creates strategy labels, and trains the 
    Confidence Classifier model, saving the artifacts for FastAPI.
    """
    
    print(f"🔍 Looking for CSV at: {DATA_FILE_PATH}")
    
    try:
        # Load the CSV
        df_all = pd.read_csv(DATA_FILE_PATH)
        print(f"✅ Loaded CSV successfully! Shape: {df_all.shape}")
        print(f"   Columns: {list(df_all.columns)}")
    except FileNotFoundError:
        print(f"🚨 CRITICAL ERROR: CSV file not found at: {DATA_FILE_PATH}")
        print(f"   Current working directory: {os.getcwd()}")
        print(f"   ML_DIR: {ML_DIR}")
        return
    except Exception as e:
        print(f"🚨 ERROR loading CSV: {e}")
        return

    # --- 3. FILTER TRAINING DATA (2022 & 2023) ---
    df_train = df_all[df_all['season'].isin([2022, 2023])].copy()
    print(f"\n📊 Training data filtered: {len(df_train)} rows from 2022-2023")
    
    if len(df_train) == 0:
        print("🚨 ERROR: No training data found for 2022-2023!")
        return

    # --- 4. CREATE STRATEGY LABELS ---
    df_train['strategy'] = df_train.apply(label_strategy, axis=1)
    
    print("\n📋 Strategy Distribution:")
    print(df_train['strategy'].value_counts())

    # --- 5. PREPARE FEATURES ---
    FEATURES = [
        'lap_number',
        'position', 
        'lap_time',
        'tyre_wear_pct',
        'stint_lap_count',
        'engine_power_pct',
        'speed_kph',
        'fuel_load_kg',
        'air_temperature_C'
    ]
    
    # Check if all features exist
    missing_features = [f for f in FEATURES if f not in df_train.columns]
    if missing_features:
        print(f"🚨 ERROR: Missing features in CSV: {missing_features}")
        return
    
    X = df_train[FEATURES]
    y = df_train['strategy']

    # --- 6. ENCODE LABELS ---
    le = LabelEncoder()
    y_encoded = le.fit_transform(y)
    
    print(f"\n🏷️  Encoded strategy classes: {list(le.classes_)}")

    # --- 7. TRAIN MODEL ---
    print("\n🤖 Training Random Forest model...")
    model = RandomForestClassifier(
        n_estimators=100,
        max_depth=10,
        random_state=42,
        class_weight='balanced'  # Handle class imbalance
    )
    
    model.fit(X, y_encoded)
    
    # Get feature importance
    feature_importance = pd.DataFrame({
        'feature': FEATURES,
        'importance': model.feature_importances_
    }).sort_values('importance', ascending=False)
    
    print("\n📊 Feature Importance:")
    print(feature_importance.to_string(index=False))

    # --- 8. SAVE ARTIFACTS ---
    model_path = os.path.join(ML_DIR, 'strategy_model.joblib')
    encoder_path = os.path.join(ML_DIR, 'label_encoder.joblib')
    features_path = os.path.join(ML_DIR, 'model_features.joblib')
    
    joblib.dump(model, model_path)
    joblib.dump(le, encoder_path)
    joblib.dump(FEATURES, features_path)
    
    print("\n✅ Model training complete!")
    print(f"📁 Artifacts saved to: {ML_DIR}/")
    print(f"   - {model_path}")
    print(f"   - {encoder_path}")
    print(f"   - {features_path}")

# --- EXECUTION ---
if __name__ == '__main__':
    print("="*60)
    print("🏎️  F1 STRATEGY MODEL TRAINER")
    print("="*60)
    create_ml_artifacts()
    print("="*60)