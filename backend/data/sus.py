import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_mercedes_cota_dataset(num_rows=10000, output_file='mercedes_cota_2022_2024.csv'):
    """
    Generate streamlined F1 dataset for Mercedes at COTA (2022-2024).
    Only essential columns for dashboard and ML models.
    """
    
    print(f"🏎️  Generating Mercedes COTA dataset (2022-2024) with {num_rows} rows...")
    print("=" * 70)
    
    # Season configurations
    SEASONS = {
        2022: {
            'HAM': {'skill': 0.93, 'tire_mgmt': 0.95, 'car_perf': 0.82},
            'RUS': {'skill': 0.87, 'tire_mgmt': 0.85, 'car_perf': 0.82},
            'date': datetime(2022, 10, 23, 14, 0, 0),
            'base_lap': 96.5,
            'weather': 'Clear',
            'base_temp': 28
        },
        2023: {
            'HAM': {'skill': 0.93, 'tire_mgmt': 0.95, 'car_perf': 0.88},
            'RUS': {'skill': 0.89, 'tire_mgmt': 0.87, 'car_perf': 0.88},
            'date': datetime(2023, 10, 22, 14, 0, 0),
            'base_lap': 94.2,
            'weather': 'Cloudy',
            'base_temp': 24
        },
        2024: {
            'HAM': {'skill': 0.93, 'tire_mgmt': 0.94, 'car_perf': 0.90},
            'RUS': {'skill': 0.90, 'tire_mgmt': 0.88, 'car_perf': 0.90},
            'date': datetime(2024, 10, 20, 14, 0, 0),
            'base_lap': 92.8,
            'weather': 'Clear',
            'base_temp': 30
        }
    }
    
    # Tire specifications
    COMPOUND_LIFE = {'Soft': 22, 'Medium': 34, 'Hard': 46, 'Intermediate': 30, 'Wet': 35}
    COMPOUND_PACE = {'Soft': 1.0, 'Medium': 0.973, 'Hard': 0.942, 'Intermediate': 0.87, 'Wet': 0.81}
    COMPOUND_WARMUP = {'Soft': 1, 'Medium': 2, 'Hard': 3, 'Intermediate': 2, 'Wet': 1}
    COMPOUND_CLIFF = {'Soft': 0.82, 'Medium': 0.78, 'Hard': 0.73, 'Intermediate': 0.80, 'Wet': 0.78}
    
    # Race strategies
    STRATEGIES = {
        'One-Stop': {'stops': 1, 'plan': [('Medium', 28), ('Hard', 28)]},
        'Two-Stop': {'stops': 2, 'plan': [('Soft', 14), ('Medium', 22), ('Hard', 20)]},
        'Undercut': {'stops': 2, 'plan': [('Medium', 16), ('Medium', 18), ('Hard', 22)]}
    }
    
    COTA_LAPS = 56
    data = []
    row_id = 0
    
    print(f"📊 Generating data for 2022-2024 seasons...")
    
    for year in [2022, 2023, 2024]:
        season = SEASONS[year]
        print(f"\n🏁 {year}: {season['date'].strftime('%B %d, %Y')}")
        
        for driver_code in ['HAM', 'RUS']:
            driver = season[driver_code]
            
            # Strategy selection
            if year == 2022:
                strategy_name = 'One-Stop' if driver_code == 'HAM' else 'Two-Stop'
            else:
                strategy_name = random.choice(['Two-Stop', 'Undercut'])
            
            strategy = STRATEGIES[strategy_name]
            print(f"   → {driver_code}: {strategy_name}")
            
            # Initial state
            position = 3 if driver_code == 'HAM' else (5 if year == 2022 else 4)
            compound = strategy['plan'][0][0]
            stint_lap = 0
            stint_num = 0
            tire_wear = 0.0
            tire_temp = 55.0
            fuel = 110 - random.random() * 2
            power = 94 + random.random() * 4
            mode = 'Neutral'
            prev_lap = season['base_lap'] + (1 - driver['skill']) * 3
            lap_times = [prev_lap]
            pits = 0
            flag = 'Green'
            incident_active = False
            
            # Strategic vars
            pos_change = 0
            undercut_window = False
            cliff_reached = False
            energy = 100.0
            drs_active = False
            
            # Pit windows
            pit_windows = []
            for i in range(strategy['stops']):
                pit_windows.append((COTA_LAPS // (strategy['stops'] + 1)) * (i + 1) + random.randint(-2, 2))
            
            # Weather
            weather = season['weather']
            rain = 0.0
            temp = season['base_temp'] + random.random() * 4
            
            # Simulate race
            for lap in range(1, COTA_LAPS + 1):
                if row_id >= num_rows:
                    break
                
                stint_lap += 1
                
                # Weather evolution
                if random.random() < 0.03:
                    if weather == 'Clear' and random.random() > 0.7:
                        weather = 'Cloudy'
                    elif weather == 'Cloudy' and random.random() > 0.5:
                        weather = 'Light Rain' if random.random() > 0.5 else 'Clear'
                
                rain = (0.6 + random.random() * 1.2) if 'Rain' in weather else 0.0
                temp = season['base_temp'] + random.random() * 6 + (3 if weather == 'Clear' else 0) - (2 if rain > 0 else 0)
                
                # Safety car/flags
                if random.random() < 0.015 and not incident_active and lap > 8:
                    flag = 'Safety Car' if random.random() > 0.65 else 'Yellow'
                    incident_active = True
                elif incident_active and random.random() < 0.28:
                    flag = 'Green'
                    incident_active = False
                
                # Tire temperature
                if stint_lap <= COMPOUND_WARMUP[compound]:
                    tire_temp = min(92, 55 + stint_lap * 14)
                else:
                    tire_temp = (92 if compound in ['Soft', 'Medium'] else 87) + np.random.normal(0, 2.8) - (6 if rain > 0 else 0)
                tire_temp = np.clip(tire_temp, 45, 112)
                temp_optimal = 1.0 if 86 <= tire_temp <= 96 else 0.96
                
                # Tire wear
                wear_rate = {'Aggressive': 1.38, 'Defensive': 0.72, 'Neutral': 1.0}[mode]
                mgmt_factor = 1.0 - (driver['tire_mgmt'] - 0.85) * 0.55
                abrasion = (temp - 42) / 24
                
                wear_prog = 0.7 + 0.19 * (stint_lap ** 1.48) * wear_rate * mgmt_factor
                wear_prog *= (1 + abrasion + (fuel - 50) / 95 + rain * 0.12)
                tire_wear = min(100, tire_wear + wear_prog)
                
                # Tire cliff
                if tire_wear > COMPOUND_CLIFF[compound] * 100:
                    cliff_reached = True
                    cliff_penalty = (tire_wear - COMPOUND_CLIFF[compound] * 100) * 0.18
                else:
                    cliff_reached = False
                    cliff_penalty = 0
                
                tire_life = max(0, COMPOUND_LIFE[compound] - stint_lap - tire_wear / 7.5)
                
                # Pit decision
                pit_flag = False
                pit_reason = ''
                
                if strategy_name == 'Undercut' and lap in pit_windows[:1]:
                    pit_flag = True
                    pit_reason = 'Undercut'
                    undercut_window = True
                elif any(abs(lap - w) <= 2 for w in pit_windows) and tire_wear > 68 and pits < strategy['stops']:
                    pit_flag = True
                    pit_reason = 'Window'
                elif tire_wear > 90 or cliff_reached:
                    pit_flag = True
                    pit_reason = 'Emergency'
                elif rain > 1.2 and compound not in ['Intermediate', 'Wet']:
                    pit_flag = True
                    pit_reason = 'Weather'
                elif flag == 'Safety Car' and stint_lap > 12 and pits < strategy['stops'] and random.random() < 0.75:
                    pit_flag = True
                    pit_reason = 'SC'
                
                # Execute pit
                if pit_flag and pits < strategy['stops'] + 1:
                    pits += 1
                    stint_num += 1
                    stint_lap = 0
                    tire_wear = 0.0
                    tire_temp = 55.0
                    cliff_reached = False
                    
                    if rain > 1.0:
                        compound = 'Intermediate'
                    elif stint_num < len(strategy['plan']):
                        compound = strategy['plan'][stint_num][0]
                    else:
                        remaining = COTA_LAPS - lap
                        compound = 'Soft' if remaining < 22 else ('Medium' if remaining < 35 else 'Hard')
                
                # Fuel
                fuel = max(9, fuel - (1.68 - (0.18 if mode == 'Defensive' else 0) + random.random() * 0.22))
                
                # Energy
                if mode == 'Aggressive':
                    energy = max(0, energy - random.uniform(3.2, 5.8))
                else:
                    energy = min(100, energy + random.uniform(1.2, 3.5))
                
                # Engine power
                power_base = 94 + driver['skill'] * 6.5
                power_mod = {'Aggressive': 1.07, 'Defensive': 0.93, 'Neutral': 1.0}[mode]
                flag_mod = 0.52 if flag == 'Safety Car' else (0.73 if flag == 'Yellow' else 1.0)
                
                power = (power_base * power_mod * flag_mod * driver['car_perf'] *
                        (1 - tire_wear / 420) * (1 + energy / 100 * 0.06) + np.random.normal(0, 1.1))
                power = np.clip(power, 42, 100)
                
                # Throttle
                throttle = np.clip(power + np.random.normal(0, 3.2), 0, 100)
                
                # Lap time
                base = season['base_lap'] + (1 - driver['skill']) * 4.2
                fuel_effect = (110 - fuel) * 0.038
                comp_effect = (1 - COMPOUND_PACE[compound]) * 6.2
                if stint_lap <= COMPOUND_WARMUP[compound]:
                    comp_effect += 1.8 * (COMPOUND_WARMUP[compound] - stint_lap + 1)
                
                wear_effect = tire_wear * 0.058 + cliff_penalty
                temp_effect = (1 - temp_optimal) * 2.8
                rain_effect = rain * 6.2
                flag_effect = 30 if flag == 'Safety Car' else (13 if flag == 'Yellow' else 0)
                pit_effect = 23.5 if pit_flag else 0
                mode_effect = {'Aggressive': -0.65, 'Defensive': 1.1, 'Neutral': 0}[mode]
                drs_effect = 0.38 if drs_active else 0
                
                lap_time = (base - fuel_effect + comp_effect + wear_effect + temp_effect +
                           rain_effect + flag_effect + pit_effect + mode_effect - drs_effect +
                           np.random.normal(0, 0.55))
                
                delta = lap_time - prev_lap
                prev_lap = lap_time
                lap_times.append(lap_time)
                
                # Momentum (5-lap rolling slope)
                momentum = (lap_times[-1] - lap_times[-6]) / 5 if len(lap_times) > 5 else 0
                
                # Speed
                speed = ((225 + driver['skill'] * 38) * COMPOUND_PACE[compound] * temp_optimal *
                        (1 - tire_wear / 260) * (1 - rain / 14) *
                        (0.45 if flag == 'Safety Car' else (0.66 if flag == 'Yellow' else 1.0)) +
                        np.random.normal(0, 5.8))
                
                # Position changes
                if pit_flag:
                    pos_change -= random.randint(1, 2)
                elif undercut_window and stint_lap < 4:
                    pos_change += 1
                elif cliff_reached:
                    pos_change -= 1
                
                position = max(1, min(20, (3 if driver_code == 'HAM' else (5 if year == 2022 else 4)) - pos_change))
                
                # Interval
                if position == 1:
                    interval = 0.0
                else:
                    base_gap = (position - 1) * 2.8
                    tire_gap = (tire_wear - 32) * 0.09 if tire_wear > 32 else 0
                    interval = max(0, base_gap + tire_gap + random.uniform(-1.8, 1.8))
                
                # DRS
                drs_status = 'Active' if (interval < 1.0 and flag == 'Green' and lap > 2) else 'Inactive'
                drs_active = drs_status == 'Active'
                
                # Incidents
                incident_msg = ''
                if flag != 'Green':
                    if flag == 'Safety Car':
                        incident_msg = f"Safety Car deployed - Incident on track"
                    elif flag == 'Yellow':
                        incident_msg = f"Yellow flag - Turn {random.randint(1, 20)}"
                
                # Recommended strategy with confidence
                if tire_wear > 68 or cliff_reached:
                    rec_mode = 'Defensive'
                    confidence = min(95, 70 + tire_wear * 0.3)
                elif position <= 3 and interval > 5 and tire_wear < 48:
                    rec_mode = 'Aggressive'
                    confidence = min(92, 65 + (100 - tire_wear) * 0.25)
                else:
                    rec_mode = 'Neutral'
                    confidence = 75 + random.uniform(-10, 10)
                
                # Push/degradation warnings
                if delta < -0.45 and tire_wear < 62 and not cliff_reached:
                    push_msg = 'PUSH'
                elif delta > 2.0 and stint_lap > 14:
                    push_msg = 'DEGRADATION WARNING'
                elif tire_wear > 72 or cliff_reached or fuel < 22:
                    push_msg = 'CONSERVE'
                else:
                    push_msg = 'MAINTAIN'
                
                # Win probability (Monte Carlo style)
                pos_factor = (20 - position + 1) / 20
                tire_factor = 1 - (tire_wear / 125)
                win_prob = max(0, min(1, pos_factor * tire_factor * driver['skill'] * 
                                     driver['car_perf'] * (1 - rain / 18)))
                
                # Create streamlined row
                row = {
                    # Core identifiers
                    'timestamp': (season['date'] + timedelta(milliseconds=(lap - 1) * int(season['base_lap'] * 1000) + random.randint(0, 3500))).isoformat(),
                    'season': year,
                    'driver': driver_code,
                    'lap_number': lap,
                    
                    # Position & race info
                    'position': position,
                    'interval_gap': round(interval, 3),
                    'flag_status': flag,
                    'incident_message': incident_msg,
                    
                    # Lap performance
                    'lap_time': round(lap_time, 3),
                    'push_signal': push_msg,
                    
                    # Tires
                    'tyre_compound': compound,
                    'stint_lap_count': stint_lap,
                    'tyre_wear_pct': round(tire_wear, 2),
                    'tyre_temp_C': round(tire_temp, 1),
                    
                    # Engine & speed
                    'engine_power_pct': round(power, 2),
                    'throttle_pct': round(throttle, 2),
                    'speed_kph': round(speed, 1),
                    'drs_status': drs_status,
                    
                    # Weather
                    'weather_condition': weather,
                    'rainfall_mm': round(rain, 2),
                    'air_temperature_C': round(temp, 1),
                    
                    # ML features
                    'fuel_load_kg': round(fuel, 2)
                }
                
                data.append(row)
                row_id += 1
                
                # Mode evolution
                if random.random() < 0.14:
                    mode = rec_mode
                
                # Reset windows
                if stint_lap > 5:
                    undercut_window = False
            
            if row_id >= num_rows:
                break
        
        if row_id >= num_rows:
            break
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Stats
    print("\n" + "=" * 70)
    print("📈 Dataset Statistics:")
    print("=" * 70)
    print(f"Total Rows:          {len(df)}")
    print(f"Columns:             {len(df.columns)}")
    print(f"Seasons:             {sorted(df['season'].unique())}")
    print(f"Drivers:             {sorted(df['driver'].unique())}")
    print(f"Avg Lap Time:        {df['lap_time'].mean():.3f}s")
    
    print("\n🛞 Compound Usage:")
    print(df['tyre_compound'].value_counts())
    
    print("\n📋 All Columns:")
    print(", ".join(df.columns))
    
    # Save
    df.to_csv(output_file, index=False)
    print("\n" + "=" * 70)
    print(f"✅ Saved: {output_file}")
    print(f"📦 Size: {len(df)} rows × {len(df.columns)} columns")
    print("=" * 70)
    
    return df

if __name__ == "__main__":
    df = generate_mercedes_cota_dataset(num_rows=10000, output_file='mercedes_cota_2022_2024.csv')
    
    print("\n🔍 Sample (Key Columns):")
    cols = ['season', 'lap_number', 'driver', 'position', 'lap_time', 'tyre_compound', 
            'tyre_wear_pct', 'recommended_mode', 'recommendation_confidence', 'push_signal']
    print(df[cols].head(10).to_string(index=False))