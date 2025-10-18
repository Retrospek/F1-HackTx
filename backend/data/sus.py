import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_mercedes_cota_dataset(num_rows=5000, output_file='mercedes_cota_2022_2024.csv'):
    """
    Generate realistic F1 dataset for Mercedes drivers (HAM & RUS) at COTA 2022-2024.
    Reflects actual Mercedes performance characteristics during these seasons.
    
    Parameters:
    -----------
    num_rows : int
        Target number of rows (default: 5000)
    output_file : str
        Output CSV filename
    """
    
    print(f"🏎️  Generating Mercedes COTA dataset (2022-2024) with {num_rows} rows...")
    print("=" * 70)
    
    # Mercedes drivers with season-specific performance
    SEASONS = {
        2022: {
            'HAM': {'skill': 0.93, 'tire_mgmt': 0.95, 'qualifying_pace': 0.91, 'car_performance': 0.82},  # Porpoising issues
            'RUS': {'skill': 0.87, 'tire_mgmt': 0.85, 'qualifying_pace': 0.88, 'car_performance': 0.82},
            'race_date': datetime(2022, 10, 23, 14, 0, 0),
            'base_lap_time': 96.5,  # Slower due to porpoising/drag issues
            'competitiveness': 0.78,  # 3rd-4th fastest car
        },
        2023: {
            'HAM': {'skill': 0.93, 'tire_mgmt': 0.95, 'qualifying_pace': 0.92, 'car_performance': 0.88},  # Improved car
            'RUS': {'skill': 0.89, 'tire_mgmt': 0.87, 'qualifying_pace': 0.90, 'car_performance': 0.88},
            'race_date': datetime(2023, 10, 22, 14, 0, 0),
            'base_lap_time': 94.2,  # Better pace
            'competitiveness': 0.85,  # 2nd fastest car
        },
        2024: {
            'HAM': {'skill': 0.93, 'tire_mgmt': 0.94, 'qualifying_pace': 0.92, 'car_performance': 0.90},  # Competitive again
            'RUS': {'skill': 0.90, 'tire_mgmt': 0.88, 'qualifying_pace': 0.91, 'car_performance': 0.90},
            'race_date': datetime(2024, 10, 20, 14, 0, 0),
            'base_lap_time': 92.8,  # Fastest of the three years
            'competitiveness': 0.88,  # Fighting for wins
        }
    }
    
    # COTA-specific characteristics
    COTA_TURNS = 20
    COTA_LENGTH_KM = 5.513
    COTA_LAPS = 56  # Standard COTA race distance
    
    # Tyre compounds (COTA typically gets C2, C3, C4)
    COMPOUND_LIFE = {'Soft': 22, 'Medium': 34, 'Hard': 46, 'Intermediate': 30, 'Wet': 35}
    COMPOUND_PACE = {'Soft': 1.0, 'Medium': 0.973, 'Hard': 0.942, 'Intermediate': 0.87, 'Wet': 0.81}
    COMPOUND_WARMUP = {'Soft': 1, 'Medium': 2, 'Hard': 3, 'Intermediate': 2, 'Wet': 1}
    COMPOUND_CLIFF = {'Soft': 0.82, 'Medium': 0.78, 'Hard': 0.73, 'Intermediate': 0.80, 'Wet': 0.78}
    
    STRATEGY_MODES = ['Aggressive', 'Neutral', 'Defensive']
    WEATHER_CONDITIONS = ['Clear', 'Cloudy', 'Light Rain']  # COTA rarely has heavy rain during race
    
    # Mercedes-typical race strategies at COTA
    MERC_STRATEGIES = {
        'One-Stop-Conservative': {'stops': 1, 'compounds': [('Medium', 28), ('Hard', 28)]},
        'One-Stop-Aggressive': {'stops': 1, 'compounds': [('Soft', 18), ('Hard', 38)]},
        'Two-Stop-Standard': {'stops': 2, 'compounds': [('Medium', 18), ('Hard', 20), ('Medium', 18)]},
        'Two-Stop-Soft': {'stops': 2, 'compounds': [('Soft', 14), ('Medium', 22), ('Hard', 20)]},
        'Undercut-Special': {'stops': 2, 'compounds': [('Medium', 16), ('Medium', 18), ('Hard', 22)]},
    }
    
    data = []
    row_id = 0
    
    print(f"📊 Simulating Mercedes drivers at COTA across 3 seasons...")
    
    # Generate data for each season
    for year in [2022, 2023, 2024]:
        season_config = SEASONS[year]
        session_start = season_config['race_date']
        base_lap_time = season_config['base_lap_time']
        
        print(f"\n🏁 {year} Season:")
        print(f"   Race Date: {session_start.strftime('%B %d, %Y')}")
        print(f"   Car Competitiveness: {season_config['competitiveness']:.2%}")
        
        # Weather profile for this season (COTA October weather)
        if year == 2022:
            season_weather = 'Clear'  # Dry race
            base_temp = 28
        elif year == 2023:
            season_weather = 'Cloudy'  # Overcast
            base_temp = 24
        else:  # 2024
            season_weather = 'Clear'  # Hot and sunny
            base_temp = 30
        
        # Simulate both Mercedes drivers
        for driver_code in ['HAM', 'RUS']:
            driver_config = season_config[driver_code]
            
            # Strategy assignment based on year and driver
            if year == 2022:
                # Conservative 2022 due to car issues
                strategy_name = 'One-Stop-Conservative' if driver_code == 'HAM' else 'Two-Stop-Standard'
            elif year == 2023:
                # More aggressive in 2023
                strategy_name = 'Two-Stop-Standard' if driver_code == 'HAM' else 'Two-Stop-Soft'
            else:  # 2024
                # Varied strategies
                strategy_name = random.choice(['One-Stop-Aggressive', 'Two-Stop-Standard', 'Undercut-Special'])
            
            strategy_config = MERC_STRATEGIES[strategy_name]
            print(f"   → {driver_code}: {strategy_name} strategy")
            
            # Initialize driver state
            if driver_code == 'HAM':
                starting_position = 3 if year == 2022 else (2 if year == 2023 else 2)
            else:  # RUS
                starting_position = 5 if year == 2022 else (4 if year == 2023 else 3)
            
            current_position = starting_position
            current_compound = strategy_config['compounds'][0][0]
            stint_lap_count = 0
            stint_number = 0
            tyre_wear = 0.0
            tyre_temp = 55.0
            fuel_load = 110 - random.random() * 2
            engine_power = 94 + random.random() * 4
            strategy_mode = 'Neutral'
            previous_lap_time = base_lap_time + (1 - driver_config['skill']) * 3 + random.random() * 1.5
            lap_times = [previous_lap_time]
            pit_stop_count = 0
            flag_status = 'Green'
            incident_occurred = False
            
            # Strategic variables
            track_position_gained = 0
            undercut_window = False
            overcut_window = False
            tyre_cliff_reached = False
            energy_management = 100.0
            drs_train = False
            
            # Calculate pit windows
            planned_stops = strategy_config['stops']
            compound_plan = strategy_config['compounds']
            pit_windows = []
            base_pit_window = COTA_LAPS // (planned_stops + 1)
            
            for stop_num in range(planned_stops):
                optimal_lap = base_pit_window * (stop_num + 1) + random.randint(-2, 2)
                pit_windows.append(optimal_lap)
            
            # Weather state
            current_weather = season_weather
            rain_intensity = 0.0
            air_temp = base_temp + random.random() * 4
            track_temp = air_temp + 14 + random.random() * 6
            
            # Race simulation
            for lap in range(1, COTA_LAPS + 1):
                if row_id >= num_rows:
                    break
                
                stint_lap_count += 1
                
                # COTA-specific weather evolution
                if random.random() < 0.03:
                    weather_idx = WEATHER_CONDITIONS.index(current_weather)
                    direction = 1 if random.random() > 0.6 else -1
                    new_idx = max(0, min(2, weather_idx + direction))
                    current_weather = WEATHER_CONDITIONS[new_idx]
                
                if 'Rain' in current_weather:
                    rain_intensity = 0.6 + random.random() * 1.2  # Light rain only
                else:
                    rain_intensity = 0.0
                
                # Temperature (COTA Texas heat)
                air_temp = base_temp + random.random() * 6 + (3 if current_weather == 'Clear' else 0) - (2 if 'Rain' in current_weather else 0)
                track_temp = air_temp + 15 + random.random() * 7 - (4 if rain_intensity > 0 else 0)
                
                # Safety car probability (COTA has history of SCs)
                if random.random() < 0.015 and not incident_occurred and lap > 8:
                    flag_status = 'Safety Car' if random.random() > 0.65 else 'Yellow'
                    incident_occurred = True
                elif incident_occurred and random.random() < 0.28:
                    flag_status = 'Green'
                    incident_occurred = False
                
                # Track evolution
                track_evolution_factor = min(1.0, lap * 0.018)
                
                # Tire temperature management
                if stint_lap_count <= COMPOUND_WARMUP[current_compound]:
                    tyre_temp = min(92, 55 + stint_lap_count * 14)
                else:
                    target_temp = 92 if current_compound in ['Soft', 'Medium'] else 87
                    tyre_temp = target_temp + np.random.normal(0, 2.8) - (6 if rain_intensity > 0 else 0)
                
                tyre_temp = np.clip(tyre_temp, 45, 112)
                temp_optimal = 1.0 if 86 <= tyre_temp <= 96 else (0.96 if tyre_temp > 96 else 0.93)
                
                # Tire wear model
                base_wear_rate = {'Aggressive': 1.38, 'Defensive': 0.72, 'Neutral': 1.0}[strategy_mode]
                tire_mgmt_factor = 1.0 - (driver_config['tire_mgmt'] - 0.85) * 0.55
                track_abrasion = (track_temp - 42) / 24  # COTA is abrasive
                fuel_weight_effect = (fuel_load - 50) / 95
                
                wear_progression = 0.7 + 0.19 * (stint_lap_count ** 1.48) * base_wear_rate * tire_mgmt_factor
                wear_progression *= (1 + track_abrasion + fuel_weight_effect + rain_intensity * 0.12)
                
                tyre_wear = min(100, tyre_wear + wear_progression)
                
                # Tire cliff
                if tyre_wear > COMPOUND_CLIFF[current_compound] * 100:
                    tyre_cliff_reached = True
                    cliff_penalty = (tyre_wear - COMPOUND_CLIFF[current_compound] * 100) * 0.18
                else:
                    tyre_cliff_reached = False
                    cliff_penalty = 0
                
                expected_tyre_life = max(0, COMPOUND_LIFE[current_compound] - stint_lap_count - tyre_wear / 7.5)
                
                # Pit stop decision logic
                pit_stop_flag = False
                strategic_reason = ''
                in_pit_window = any(abs(lap - window) <= 2 for window in pit_windows)
                
                if strategy_name == 'Undercut-Special' and lap in pit_windows[:1]:
                    pit_stop_flag = True
                    strategic_reason = 'Undercut attempt'
                    undercut_window = True
                elif in_pit_window and tyre_wear > 68 and pit_stop_count < planned_stops:
                    pit_stop_flag = True
                    strategic_reason = 'Planned pit window'
                elif tyre_wear > 90 or tyre_cliff_reached:
                    pit_stop_flag = True
                    strategic_reason = 'Emergency stop - tire degradation'
                elif rain_intensity > 1.2 and current_compound not in ['Intermediate', 'Wet']:
                    pit_stop_flag = True
                    strategic_reason = 'Weather change - intermediate tires'
                elif flag_status == 'Safety Car' and stint_lap_count > 12 and pit_stop_count < planned_stops:
                    if random.random() < 0.75:
                        pit_stop_flag = True
                        strategic_reason = 'Safety car opportunity'
                
                # Execute pit stop
                if pit_stop_flag and pit_stop_count < planned_stops + 1:
                    pit_stop_count += 1
                    stint_number += 1
                    stint_lap_count = 0
                    tyre_wear = 0.0
                    tyre_temp = 55.0
                    tyre_cliff_reached = False
                    
                    if rain_intensity > 1.0:
                        current_compound = 'Intermediate'
                    else:
                        if stint_number < len(compound_plan):
                            current_compound = compound_plan[stint_number][0]
                        else:
                            remaining_laps = COTA_LAPS - lap
                            current_compound = 'Soft' if remaining_laps < 22 else ('Medium' if remaining_laps < 35 else 'Hard')
                
                # Fuel consumption
                fuel_consumption = 1.68 - (0.18 if strategy_mode == 'Defensive' else 0) + random.random() * 0.22
                fuel_load = max(9, fuel_load - fuel_consumption)
                
                # Energy management
                if strategy_mode == 'Aggressive':
                    energy_management = max(0, energy_management - random.uniform(3.2, 5.8))
                else:
                    energy_management = min(100, energy_management + random.uniform(1.2, 3.5))
                
                # Engine power (Mercedes PU characteristics)
                power_base = 94 + driver_config['skill'] * 6.5
                strategy_power_mod = {'Aggressive': 1.07, 'Defensive': 0.93, 'Neutral': 1.0}[strategy_mode]
                flag_power_mod = 0.52 if flag_status == 'Safety Car' else (0.73 if flag_status == 'Yellow' else 1.0)
                energy_boost = (energy_management / 100) * 0.06
                car_performance = season_config['competitiveness']
                
                engine_power = (power_base * strategy_power_mod * flag_power_mod * car_performance *
                               (1 - tyre_wear / 420) * (1 + energy_boost) + np.random.normal(0, 1.1))
                engine_power = np.clip(engine_power, 42, 100)
                
                # Throttle
                throttle = engine_power + np.random.normal(0, 3.2)
                throttle = np.clip(throttle, 0, 100)
                
                # Lap time calculation (COTA-specific)
                lap_time_base = base_lap_time + (1 - driver_config['skill']) * 4.2
                
                # Effects
                fuel_effect = (110 - fuel_load) * 0.038
                compound_effect = (1 - COMPOUND_PACE[current_compound]) * 6.2
                if stint_lap_count <= COMPOUND_WARMUP[current_compound]:
                    compound_effect += 1.8 * (COMPOUND_WARMUP[current_compound] - stint_lap_count + 1)
                
                wear_effect = tyre_wear * 0.058 + cliff_penalty
                temp_effect = (1 - temp_optimal) * 2.8
                evolution_bonus = track_evolution_factor * 0.85
                weather_effect = rain_intensity * 6.2
                flag_effect = 30 if flag_status == 'Safety Car' else (13 if flag_status == 'Yellow' else 0)
                pit_effect = 23.5 if pit_stop_flag else 0
                strategy_effect = {'Aggressive': -0.65, 'Defensive': 1.1, 'Neutral': 0}[strategy_mode]
                drs_benefit = 0.38 if drs_train else 0
                tire_skill_effect = (driver_config['tire_mgmt'] - 0.85) * 2.2
                
                # COTA sector 1 effect (long straight benefits Mercedes)
                sector1_bonus = 0.15 if driver_code == 'HAM' else 0.1
                
                lap_time = (lap_time_base - fuel_effect + compound_effect + wear_effect + temp_effect -
                           evolution_bonus + weather_effect + flag_effect + pit_effect + strategy_effect -
                           drs_benefit - tire_skill_effect - sector1_bonus + np.random.normal(0, 0.55))
                
                delta_lap_time = lap_time - previous_lap_time
                previous_lap_time = lap_time
                lap_times.append(lap_time)
                
                # Averages
                recent_laps = lap_times[-5:]
                avg_pace = np.mean(recent_laps)
                momentum = (lap_times[-1] - lap_times[-6]) / 5 if len(lap_times) > 5 else 0
                
                # Speed (COTA top speed ~350 km/h)
                base_speed = 225 + driver_config['skill'] * 38
                speed = (base_speed * COMPOUND_PACE[current_compound] * temp_optimal *
                        (1 - tyre_wear / 260) * (1 - rain_intensity / 14) *
                        (0.45 if flag_status == 'Safety Car' else (0.66 if flag_status == 'Yellow' else 1.0)) +
                        np.random.normal(0, 5.8))
                
                # Position changes
                if pit_stop_flag:
                    track_position_gained -= random.randint(1, 2)
                elif undercut_window and stint_lap_count < 4:
                    track_position_gained += 1
                elif tyre_cliff_reached:
                    track_position_gained -= 1
                
                current_position = max(1, min(20, starting_position - track_position_gained))
                
                # Interval gap
                if current_position == 1:
                    interval_gap = 0.0
                else:
                    base_gap = (current_position - 1) * 2.8
                    tire_gap = (tyre_wear - 32) * 0.09 if tyre_wear > 32 else 0
                    interval_gap = max(0, base_gap + tire_gap + random.uniform(-1.8, 1.8))
                
                # DRS
                drs_status = 'Active' if (interval_gap < 1.0 and flag_status == 'Green' and lap > 2) else 'Inactive'
                drs_train = interval_gap < 1.0 and lap > 2
                
                # Incidents
                incident_risk = 0.005 + (0.005 if tyre_cliff_reached else 0) + (0.004 if rain_intensity > 0.8 else 0)
                has_incident = random.random() < incident_risk
                incident_categories = ['Collision', 'Mechanical', 'Track Debris', 'Off-track', 'Tire Puncture', 'Suspension']
                incident_category = random.choice(incident_categories) if has_incident else 'None'
                incident_message = f"{driver_code} - {incident_category} at Turn {random.randint(1, 20)}" if has_incident else ''
                
                # Anomalies
                power_anomaly = abs(engine_power - 95) / 10
                if len(lap_times) > 4:
                    recent_deltas = [abs(lap_times[i] - lap_times[i-1]) for i in range(-4, 0)]
                    racecraft_anomaly = abs(delta_lap_time) / (np.mean(recent_deltas) + 0.18)
                else:
                    racecraft_anomaly = 0.0
                
                # Signals
                if delta_lap_time < -0.45 and tyre_wear < 62 and not tyre_cliff_reached:
                    push_signal = 'PUSH'
                elif tyre_wear > 72 or tyre_cliff_reached or fuel_load < 22:
                    push_signal = 'CONSERVE'
                else:
                    push_signal = 'MAINTAIN'
                
                degradation_warning = (delta_lap_time > 2.0 and stint_lap_count > 14) or tyre_cliff_reached
                
                # Race pace score
                race_pace_score = (100 - (lap_time - base_lap_time) * 2.5 - tyre_wear * 0.38 -
                                 rain_intensity * 5.0 + energy_management * 0.12)
                
                # Win probability
                position_factor = (20 - current_position + 1) / 20
                tire_factor = 1 - (tyre_wear / 125)
                strategy_factor = 0.88 if strategy_name in ['Two-Stop-Standard', 'Undercut-Special'] else 0.83
                win_prob = max(0, min(1, position_factor * tire_factor * strategy_factor *
                                     driver_config['skill'] * car_performance * (1 - rain_intensity / 18)))
                
                # Recommended mode
                if tyre_wear > 68 or tyre_cliff_reached:
                    recommended_mode = 'Defensive'
                elif current_position <= 3 and interval_gap > 5 and tyre_wear < 48:
                    recommended_mode = 'Aggressive'
                else:
                    recommended_mode = 'Neutral'
                
                # Environmental
                humidity = 52 + rain_intensity * 12 + random.random() * 20
                wind_speed = 2.2 + random.random() * 6.5
                
                # Create row
                row = {
                    'session_key': f'RACE_{year}_COTA_{lap}',
                    'season': year,
                    'race_name': 'United States Grand Prix',
                    'circuit': 'Circuit of the Americas',
                    'lap_number': lap,
                    'timestamp': (session_start + timedelta(milliseconds=(lap - 1) * int(base_lap_time * 1000) + random.randint(0, 3500))).isoformat(),
                    'driver': driver_code,
                    'driver_name': 'Lewis Hamilton' if driver_code == 'HAM' else 'George Russell',
                    'team': 'Mercedes',
                    'position': current_position,
                    'interval_gap': round(interval_gap, 3),
                    'strategy_mode': strategy_mode,
                    'recommended_mode': recommended_mode,
                    'race_strategy': strategy_name,
                    'strategic_reason': strategic_reason if pit_stop_flag else '',
                    'tyre_compound': current_compound,
                    'stint_number': stint_number,
                    'stint_lap_count': stint_lap_count,
                    'tyre_wear_pct': round(tyre_wear, 2),
                    'tyre_temp_C': round(tyre_temp, 1),
                    'tyre_cliff_reached': tyre_cliff_reached,
                    'expected_tyre_life': round(expected_tyre_life, 1),
                    'pit_stop_flag': pit_stop_flag,
                    'pit_stop_count': pit_stop_count,
                    'undercut_window': undercut_window,
                    'overcut_window': overcut_window,
                    'lap_time': round(lap_time, 3),
                    'delta_lap_time': round(delta_lap_time, 3),
                    'average_pace_window': round(avg_pace, 3),
                    'momentum_indicator': round(momentum, 4),
                    'engine_power_pct': round(engine_power, 2),
                    'throttle_pct': round(throttle, 2),
                    'energy_management_pct': round(energy_management, 2),
                    'drs_status': drs_status,
                    'speed_kph': round(speed, 1),
                    'fuel_load_kg': round(fuel_load, 2),
                    'air_temperature_C': round(air_temp, 1),
                    'track_temperature_C': round(track_temp, 1),
                    'rainfall_mm': round(rain_intensity, 2),
                    'humidity_pct': round(humidity, 1),
                    'wind_speed_mps': round(wind_speed, 1),
                    'weather_condition': current_weather,
                    'flag_status': flag_status,
                    'incident_category': incident_category,
                    'incident_message': incident_message,
                    'race_pace_score': round(race_pace_score, 2),
                    'win_probability': round(win_prob, 4),
                    'power_anomaly_score': round(power_anomaly, 3),
                    'racecraft_anomaly_score': round(racecraft_anomaly, 3),
                    'push_signal': push_signal,
                    'degradation_warning': degradation_warning,
                    'tire_management_skill': driver_config['tire_mgmt'],
                    'car_competitiveness': season_config['competitiveness']
                }
                
                data.append(row)
                row_id += 1
                
                # Strategy mode changes
                if random.random() < 0.14:
                    if tyre_wear > 63:
                        strategy_mode = 'Defensive'
                    elif current_position <= 3 and not tyre_cliff_reached:
                        strategy_mode = 'Aggressive'
                    else:
                        strategy_mode = recommended_mode
                
                # Reset windows
                if stint_lap_count > 5:
                    undercut_window = False
                    overcut_window = False
            
            if row_id >= num_rows:
                break
        
        if row_id >= num_rows:
            break
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Statistics
    print("\n" + "=" * 70)
    print("📈 Mercedes COTA Dataset Statistics (2022-2024):")
    print("=" * 70)
    print(f"Total Rows:          {len(df)}")
    print(f"Seasons Covered:     {df['season'].nunique()}")
    print(f"Drivers:             {', '.join(df['driver_name'].unique())}")
    print(f"Average Lap Time:    {df['lap_time'].mean():.3f}s")
    print(f"Std Dev Lap Time:    {df['lap_time'].std():.3f}s")
    print(f"Average Tyre Wear:   {df['tyre_wear_pct'].mean():.2f}%")
    print(f"Total Pit Stops:     {df['pit_stop_flag'].sum()}")
    print(f"Undercut Attempts:   {df['undercut_window'].sum()}")
    print(f"Tire Cliff Events:   {df['tyre_cliff_reached'].sum()}")
    print(f"Total Incidents:     {(df['incident_category'] != 'None').sum()}")
    print(f"Safety Car Laps:     {(df['flag_status'] == 'Safety Car').sum()}")
    
    print("\n📊 Data by Season:")
    print(df.groupby('season').size())
    
    print("\n🏎️ Data by Driver:")
    print(df.groupby('driver_name').size())
    
    print("\n🎯 Race Strategy Distribution:")
    print(df['race_strategy'].value_counts())
    
    print("\n🛞 Tyre Compound Usage:")
    print(df['tyre_compound'].value_counts())
    
    # Save CSV
    df.to_csv(output_file, index=False)
    print("\n" + "=" * 70)
    print(f"✅ Dataset saved to: {output_file}")
    print(f"📦 File size: {len(df)} rows × {len(df.columns)} columns")
    print("=" * 70)
    
    return df

if __name__ == "__main__":
    df = generate_mercedes_cota_dataset(num_rows=10000, output_file='mercedes_cota_2022_2024.csv')
    
    print("\n🔍 Sample Data (First 5 Rows - Key Columns):")
    preview_cols = ['season', 'lap_number', 'driver_name', 'position', 'lap_time', 'tyre_compound', 'tyre_wear_pct', 'race_strategy']