import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random

def generate_f1_dataset(num_rows=5000, output_file='f1_synthetic_dataset_5000.csv'):
    """
    Generate a realistic F1 synthetic dataset with complex race strategies and tire management.
    
    Parameters:
    -----------
    num_rows : int
        Target number of rows (default: 5000)
    output_file : str
        Output CSV filename
    """
    
    print(f"🏎️  Generating F1 synthetic dataset with {num_rows} rows...")
    print("=" * 70)
    
    # Driver configuration with realistic skill levels and team performance
    DRIVERS = [
        {'name': 'VER', 'team': 'Red Bull Racing', 'skill': 0.95, 'tire_mgmt': 0.93, 'qualifying_pace': 0.96},
        {'name': 'PER', 'team': 'Red Bull Racing', 'skill': 0.88, 'tire_mgmt': 0.85, 'qualifying_pace': 0.89},
        {'name': 'LEC', 'team': 'Ferrari', 'skill': 0.92, 'tire_mgmt': 0.88, 'qualifying_pace': 0.94},
        {'name': 'SAI', 'team': 'Ferrari', 'skill': 0.87, 'tire_mgmt': 0.90, 'qualifying_pace': 0.88},
        {'name': 'HAM', 'team': 'Mercedes', 'skill': 0.93, 'tire_mgmt': 0.95, 'qualifying_pace': 0.92},
        {'name': 'RUS', 'team': 'Mercedes', 'skill': 0.89, 'tire_mgmt': 0.87, 'qualifying_pace': 0.90},
        {'name': 'NOR', 'team': 'McLaren', 'skill': 0.90, 'tire_mgmt': 0.89, 'qualifying_pace': 0.91},
        {'name': 'PIA', 'team': 'McLaren', 'skill': 0.86, 'tire_mgmt': 0.86, 'qualifying_pace': 0.87},
        {'name': 'ALO', 'team': 'Aston Martin', 'skill': 0.88, 'tire_mgmt': 0.94, 'qualifying_pace': 0.87},
        {'name': 'STR', 'team': 'Aston Martin', 'skill': 0.84, 'tire_mgmt': 0.82, 'qualifying_pace': 0.85}
    ]
    
    # Tyre compound specifications with realistic degradation profiles
    COMPOUND_LIFE = {'Soft': 20, 'Medium': 32, 'Hard': 48, 'Intermediate': 28, 'Wet': 35}
    COMPOUND_PACE = {'Soft': 1.0, 'Medium': 0.975, 'Hard': 0.945, 'Intermediate': 0.88, 'Wet': 0.82}
    COMPOUND_WARMUP = {'Soft': 1, 'Medium': 2, 'Hard': 3, 'Intermediate': 2, 'Wet': 1}  # Laps to optimal temp
    COMPOUND_CLIFF = {'Soft': 0.85, 'Medium': 0.80, 'Hard': 0.75, 'Intermediate': 0.82, 'Wet': 0.80}  # Performance cliff %
    
    STRATEGY_MODES = ['Aggressive', 'Neutral', 'Defensive']
    WEATHER_CONDITIONS = ['Clear', 'Cloudy', 'Light Rain', 'Heavy Rain']
    
    # Race strategy configurations
    STINT_STRATEGIES = {
        'One-Stop': {'stops': 1, 'compounds': [('Medium', 25), ('Hard', 33)]},
        'Two-Stop': {'stops': 2, 'compounds': [('Soft', 15), ('Medium', 20), ('Hard', 23)]},
        'Aggressive-Two': {'stops': 2, 'compounds': [('Soft', 12), ('Soft', 18), ('Medium', 28)]},
        'Conservative-One': {'stops': 1, 'compounds': [('Hard', 28), ('Medium', 30)]},
        'Undercut': {'stops': 2, 'compounds': [('Medium', 14), ('Medium', 22), ('Hard', 22)]},
        'Overcut': {'stops': 2, 'compounds': [('Medium', 20), ('Hard', 18), ('Hard', 20)]},
    }
    
    # Initialize data storage
    data = []
    session_start = datetime(2025, 10, 18, 14, 0, 0)
    row_id = 0
    
    # Global weather state
    current_weather = 'Clear'
    rain_intensity = 0.0
    air_temp = 28 + random.random() * 5
    track_temp = air_temp + 12 + random.random() * 5
    
    # Track characteristics
    TRACK_EVOLUTION = 0.02  # Lap time improvement per lap due to rubber buildup
    NUM_LAPS = 58
    PIT_LOSS = 22.5  # Time lost in pit stop
    
    print(f"📊 Simulating {len(DRIVERS)} drivers over {NUM_LAPS} laps...")
    print(f"🎯 Implementing complex race strategies with undercuts/overcuts...")
    
    # Assign race strategies to drivers
    driver_strategies = {}
    for idx, driver in enumerate(DRIVERS):
        # Top teams get more strategic options
        if idx < 4:  # Top 4 qualify at front
            strategy_pool = ['Two-Stop', 'Aggressive-Two', 'Undercut', 'Overcut']
        elif idx < 6:
            strategy_pool = ['Two-Stop', 'One-Stop', 'Undercut']
        else:
            strategy_pool = ['One-Stop', 'Conservative-One', 'Two-Stop']
        
        selected_strategy = random.choice(strategy_pool)
        driver_strategies[driver['name']] = {
            'name': selected_strategy,
            'config': STINT_STRATEGIES[selected_strategy].copy(),
            'pit_windows': []
        }
        
        print(f"   → {driver['name']} ({driver['team']}): {selected_strategy} strategy")
    
    # Simulate race for each driver
    for driver_idx, driver in enumerate(DRIVERS):
        # Initialize driver state
        starting_position = driver_idx + 1
        current_position = starting_position
        current_compound = driver_strategies[driver['name']]['config']['compounds'][0][0]
        stint_lap_count = 0
        stint_number = 0
        tyre_wear = 0.0
        tyre_temp = 50.0  # Temperature in Celsius
        fuel_load = 110 - random.random() * 3
        engine_power = 95 + random.random() * 5
        strategy_mode = 'Neutral'
        previous_lap_time = 90 + (1 - driver['skill']) * 5 + random.random() * 2
        lap_times = [previous_lap_time]
        pit_stop_count = 0
        flag_status = 'Green'
        incident_occurred = False
        
        # Strategic variables
        track_position_gained = 0
        undercut_window = False
        overcut_window = False
        tyre_cliff_reached = False
        energy_management = 100.0  # Battery percentage
        drs_train = False
        
        # Get strategy plan
        strategy = driver_strategies[driver['name']]
        planned_stops = strategy['config']['stops']
        compound_plan = strategy['config']['compounds']
        
        # Calculate optimal pit windows with variance
        base_pit_window = NUM_LAPS // (planned_stops + 1)
        for stop_num in range(planned_stops):
            optimal_lap = base_pit_window * (stop_num + 1) + random.randint(-3, 3)
            strategy['pit_windows'].append(optimal_lap)
        
        for lap in range(1, NUM_LAPS + 1):
            if row_id >= num_rows:
                break
            
            stint_lap_count += 1
            
            # Weather evolution with realistic patterns
            if random.random() < 0.04:
                weather_idx = WEATHER_CONDITIONS.index(current_weather)
                direction = 1 if random.random() > 0.5 else -1
                new_idx = max(0, min(3, weather_idx + direction))
                current_weather = WEATHER_CONDITIONS[new_idx]
            
            if 'Rain' in current_weather:
                rain_intensity = 2.5 + random.random() * 2.5 if current_weather == 'Heavy Rain' else 0.8 + random.random() * 1.2
            else:
                rain_intensity = 0.0
            
            # Temperature dynamics
            air_temp = 26 + random.random() * 7 + (2 if current_weather == 'Clear' else 0) - (3 if 'Rain' in current_weather else 0)
            track_temp = air_temp + 12 + random.random() * 6 - (5 if rain_intensity > 0 else 0)
            
            # Flag status
            if random.random() < 0.018 and not incident_occurred and lap > 5:
                flag_status = 'Safety Car' if random.random() > 0.6 else 'Yellow'
                incident_occurred = True
            elif incident_occurred and random.random() < 0.25:
                flag_status = 'Green'
                incident_occurred = False
            
            # Track evolution (rubber buildup improves grip)
            track_evolution_factor = min(1.0, lap * TRACK_EVOLUTION)
            
            # Tire temperature management (crucial for performance)
            if stint_lap_count <= COMPOUND_WARMUP[current_compound]:
                tyre_temp = min(90, 50 + stint_lap_count * 15)  # Warming up
            else:
                target_temp = 90 if current_compound in ['Soft', 'Medium'] else 85
                tyre_temp = target_temp + np.random.normal(0, 3) - (5 if rain_intensity > 0 else 0)
            
            tyre_temp = np.clip(tyre_temp, 40, 110)
            temp_optimal = 1.0 if 85 <= tyre_temp <= 95 else (0.97 if tyre_temp > 95 else 0.94)
            
            # Advanced tire wear model with cliff effect
            base_wear_rate = 1.0
            if strategy_mode == 'Aggressive':
                base_wear_rate = 1.35
            elif strategy_mode == 'Defensive':
                base_wear_rate = 0.75
            else:
                base_wear_rate = 1.0
            
            # Tire management skill affects wear
            tire_mgmt_factor = 1.0 - (driver['tire_mgmt'] - 0.85) * 0.5
            track_abrasion = (track_temp - 40) / 25
            fuel_weight_effect = (fuel_load - 50) / 100  # Heavier = more wear
            
            # Quadratic wear progression with cliff
            wear_progression = 0.65 + 0.18 * (stint_lap_count ** 1.5) * base_wear_rate * tire_mgmt_factor
            wear_progression *= (1 + track_abrasion + fuel_weight_effect + rain_intensity * 0.15)
            
            tyre_wear = min(100, tyre_wear + wear_progression)
            
            # Tire cliff effect (sudden performance drop)
            if tyre_wear > COMPOUND_CLIFF[current_compound] * 100:
                tyre_cliff_reached = True
                cliff_penalty = (tyre_wear - COMPOUND_CLIFF[current_compound] * 100) * 0.15
            else:
                tyre_cliff_reached = False
                cliff_penalty = 0
            
            expected_tyre_life = max(0, COMPOUND_LIFE[current_compound] - stint_lap_count - tyre_wear / 8)
            
            # Strategic pit stop decision logic
            pit_stop_flag = False
            strategic_reason = ''
            
            # Check if in pit window
            in_pit_window = any(abs(lap - window) <= 2 for window in strategy['pit_windows'])
            
            # Undercut opportunity (pit early to gain track position)
            if strategy['name'] == 'Undercut' and lap in strategy['pit_windows'][:1]:
                pit_stop_flag = True
                strategic_reason = 'Undercut attempt'
                undercut_window = True
            
            # Overcut opportunity (stay out longer on old tires)
            elif strategy['name'] == 'Overcut' and lap in strategy['pit_windows'] and stint_lap_count > 18:
                pit_stop_flag = True
                strategic_reason = 'Overcut strategy'
                overcut_window = True
            
            # Standard pit window
            elif in_pit_window and tyre_wear > 70 and pit_stop_count < planned_stops:
                pit_stop_flag = True
                strategic_reason = 'Planned pit window'
            
            # Emergency pit (tire failure risk)
            elif tyre_wear > 92 or tyre_cliff_reached:
                pit_stop_flag = True
                strategic_reason = 'Emergency stop - tire degradation'
            
            # Weather-forced pit stop
            elif rain_intensity > 1.8 and current_compound not in ['Intermediate', 'Wet']:
                pit_stop_flag = True
                strategic_reason = 'Weather change - wet tires'
            
            # Safety car pit opportunity
            elif flag_status == 'Safety Car' and stint_lap_count > 10 and pit_stop_count < planned_stops:
                if random.random() < 0.7:  # 70% take the opportunity
                    pit_stop_flag = True
                    strategic_reason = 'Safety car pit opportunity'
            
            # Execute pit stop
            if pit_stop_flag and pit_stop_count < planned_stops + 1:
                pit_stop_count += 1
                stint_number += 1
                stint_lap_count = 0
                tyre_wear = 0.0
                tyre_temp = 50.0
                tyre_cliff_reached = False
                
                # Compound selection based on strategy and conditions
                if rain_intensity > 2.5:
                    current_compound = 'Wet'
                elif rain_intensity > 1.0:
                    current_compound = 'Intermediate'
                else:
                    # Follow strategy plan or adapt
                    if stint_number < len(compound_plan):
                        current_compound = compound_plan[stint_number][0]
                    else:
                        # Emergency compound choice
                        remaining_laps = NUM_LAPS - lap
                        if remaining_laps < 20:
                            current_compound = 'Soft'
                        elif remaining_laps < 35:
                            current_compound = 'Medium'
                        else:
                            current_compound = 'Hard'
            
            # Fuel consumption with energy management
            fuel_consumption = 1.65 - (0.15 if strategy_mode == 'Defensive' else 0) + random.random() * 0.25
            fuel_load = max(8, fuel_load - fuel_consumption)
            
            # Energy management (ERS/Battery)
            if strategy_mode == 'Aggressive':
                energy_management = max(0, energy_management - random.uniform(3, 6))
            else:
                energy_management = min(100, energy_management + random.uniform(1, 3))
            
            # Engine power with strategic modes and energy deployment
            power_base = 93 + driver['skill'] * 7
            strategy_power_mod = 1.06 if strategy_mode == 'Aggressive' else (0.94 if strategy_mode == 'Defensive' else 1.0)
            flag_power_mod = 0.55 if flag_status == 'Safety Car' else (0.75 if flag_status == 'Yellow' else 1.0)
            energy_boost = (energy_management / 100) * 0.05
            
            engine_power = (power_base * strategy_power_mod * flag_power_mod * 
                           (1 - tyre_wear / 400) * (1 + energy_boost) + np.random.normal(0, 1.2))
            engine_power = np.clip(engine_power, 45, 100)
            
            # Throttle application
            throttle = engine_power + np.random.normal(0, 3.5)
            throttle = np.clip(throttle, 0, 100)
            
            # Lap time calculation with complex factors
            base_lap_time = 89 + (1 - driver['skill']) * 4.5
            
            # Fuel effect (lighter = faster, approximately 0.035s per kg)
            fuel_effect = (110 - fuel_load) * 0.035
            
            # Compound performance with warmup consideration
            compound_effect = (1 - COMPOUND_PACE[current_compound]) * 6
            if stint_lap_count <= COMPOUND_WARMUP[current_compound]:
                compound_effect += 1.5 * (COMPOUND_WARMUP[current_compound] - stint_lap_count + 1)
            
            # Tire degradation effect (gradual then cliff)
            wear_effect = tyre_wear * 0.055 + cliff_penalty
            
            # Temperature effect on grip
            temp_effect = (1 - temp_optimal) * 2.5
            
            # Track evolution bonus
            evolution_bonus = track_evolution_factor * 0.8
            
            # Weather impact
            weather_effect = rain_intensity * 5.5
            
            # Flag effects
            flag_effect = 28 if flag_status == 'Safety Car' else (12 if flag_status == 'Yellow' else 0)
            
            # Pit stop time loss
            pit_effect = PIT_LOSS if pit_stop_flag else 0
            
            # Strategy mode effect
            strategy_effect = -0.6 if strategy_mode == 'Aggressive' else (1.0 if strategy_mode == 'Defensive' else 0)
            
            # DRS benefit (0.3-0.4s per lap)
            drs_benefit = 0.35 if drs_train else 0
            
            # Tire management skill effect
            tire_skill_effect = (driver['tire_mgmt'] - 0.85) * 2.0
            
            lap_time = (base_lap_time - fuel_effect + compound_effect + wear_effect + temp_effect - 
                       evolution_bonus + weather_effect + flag_effect + pit_effect + strategy_effect - 
                       drs_benefit - tire_skill_effect + np.random.normal(0, 0.6))
            
            delta_lap_time = lap_time - previous_lap_time
            previous_lap_time = lap_time
            lap_times.append(lap_time)
            
            # Moving averages
            recent_laps = lap_times[-5:]
            avg_pace = np.mean(recent_laps)
            
            # Momentum (rate of pace change)
            momentum = (lap_times[-1] - lap_times[-6]) / 5 if len(lap_times) > 5 else 0
            
            # Speed calculation
            base_speed = 218 + driver['skill'] * 35
            speed = (base_speed * COMPOUND_PACE[current_compound] * temp_optimal * 
                    (1 - tyre_wear / 250) * (1 - rain_intensity / 12) * 
                    (0.48 if flag_status == 'Safety Car' else (0.68 if flag_status == 'Yellow' else 1.0)) +
                    np.random.normal(0, 6.5))
            
            # Position changes due to strategy
            if pit_stop_flag:
                track_position_gained -= random.randint(1, 3)  # Lose positions in pit
            elif undercut_window and stint_lap_count < 5:
                track_position_gained += 1  # Gain from undercut
            elif tyre_cliff_reached:
                track_position_gained -= 1  # Lose from tire deg
            
            current_position = max(1, min(len(DRIVERS), starting_position - track_position_gained))
            
            # Interval gap (distance to car ahead)
            if current_position == 1:
                interval_gap = 0.0
            else:
                base_gap = (current_position - 1) * 2.5
                tire_gap = (tyre_wear - 30) * 0.08 if tyre_wear > 30 else 0
                interval_gap = base_gap + tire_gap + random.uniform(-1.5, 1.5)
            
            interval_gap = max(0, interval_gap)
            
            # DRS status
            drs_status = 'Active' if (interval_gap < 1.0 and flag_status == 'Green' and lap > 2) else 'Inactive'
            drs_train = interval_gap < 1.0 and lap > 2
            
            # Incidents
            incident_risk = 0.006 + (0.004 if tyre_cliff_reached else 0) + (0.003 if rain_intensity > 1.5 else 0)
            has_incident = random.random() < incident_risk
            incident_categories = ['Collision', 'Mechanical', 'Track Debris', 'Off-track', 'Tire Puncture']
            incident_category = random.choice(incident_categories) if has_incident else 'None'
            incident_message = (f"{driver['name']} - {incident_category} at Turn {random.randint(1, 16)}" 
                              if has_incident else '')
            
            # Anomaly detection
            power_anomaly = abs(engine_power - 95) / 10
            if len(lap_times) > 4:
                recent_deltas = [abs(lap_times[i] - lap_times[i-1]) for i in range(-4, 0)]
                racecraft_anomaly = abs(delta_lap_time) / (np.mean(recent_deltas) + 0.15)
            else:
                racecraft_anomaly = 0.0
            
            # Strategic signals
            if delta_lap_time < -0.4 and tyre_wear < 65 and not tyre_cliff_reached:
                push_signal = 'PUSH'
            elif tyre_wear > 75 or tyre_cliff_reached or fuel_load < 20:
                push_signal = 'CONSERVE'
            else:
                push_signal = 'MAINTAIN'
            
            degradation_warning = (delta_lap_time > 1.8 and stint_lap_count > 12) or tyre_cliff_reached
            
            # Race pace composite score
            race_pace_score = (100 - (lap_time - 86) * 2.2 - tyre_wear * 0.35 - 
                             rain_intensity * 4.5 + energy_management * 0.1)
            
            # Win probability (Monte Carlo style)
            position_factor = (len(DRIVERS) - current_position + 1) / len(DRIVERS)
            tire_factor = 1 - (tyre_wear / 120)
            strategy_factor = 0.9 if strategy['name'] in ['Two-Stop', 'Undercut'] else 0.85
            win_prob = max(0, min(1, position_factor * tire_factor * strategy_factor * 
                                 driver['skill'] * (1 - rain_intensity / 15)))
            
            # Strategy mode recommendation based on situation
            if tyre_wear > 70 or tyre_cliff_reached:
                recommended_mode = 'Defensive'
            elif current_position <= 3 and interval_gap > 4 and tyre_wear < 50:
                recommended_mode = 'Aggressive'
            elif abs(lap - strategy['pit_windows'][pit_stop_count]) < 3 if pit_stop_count < len(strategy['pit_windows']) else False:
                recommended_mode = 'Neutral'
            else:
                recommended_mode = 'Neutral'
            
            # Humidity and wind
            humidity = 55 + rain_intensity * 10 + random.random() * 18
            wind_speed = 1.5 + random.random() * 7
            
            # Create row
            row = {
                'session_key': f'RACE_2025_COTA_{lap}',
                'lap_number': lap,
                'timestamp': (session_start + timedelta(milliseconds=(lap - 1) * 93000 + random.randint(0, 4000))).isoformat(),
                'driver': driver['name'],
                'team': driver['team'],
                'position': current_position,
                'interval_gap': round(interval_gap, 3),
                'strategy_mode': strategy_mode,
                'recommended_mode': recommended_mode,
                'race_strategy': strategy['name'],
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
                'tire_management_skill': driver['tire_mgmt']
            }
            
            data.append(row)
            row_id += 1
            
            # Dynamic strategy mode changes based on race situation
            if random.random() < 0.12:
                if tyre_wear > 65:
                    strategy_mode = 'Defensive'
                elif current_position <= 3 and not tyre_cliff_reached:
                    strategy_mode = 'Aggressive'
                else:
                    strategy_mode = recommended_mode
            
            # Reset strategic windows
            if stint_lap_count > 5:
                undercut_window = False
                overcut_window = False
        
        if row_id >= num_rows:
            break
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Post-processing: Add strategic insights
    print("\n" + "=" * 70)
    print("📈 Dataset Statistics:")
    print("=" * 70)
    print(f"Total Rows:          {len(df)}")
    print(f"Unique Drivers:      {df['driver'].nunique()}")
    print(f"Average Lap Time:    {df['lap_time'].mean():.3f}s")
    print(f"Std Dev Lap Time:    {df['lap_time'].std():.3f}s")
    print(f"Average Tyre Wear:   {df['tyre_wear_pct'].mean():.2f}%")
    print(f"Total Pit Stops:     {df['pit_stop_flag'].sum()}")
    print(f"Undercut Attempts:   {df['undercut_window'].sum()}")
    print(f"Overcut Attempts:    {df['overcut_window'].sum()}")
    print(f"Tire Cliff Events:   {df['tyre_cliff_reached'].sum()}")
    print(f"Total Incidents:     {(df['incident_category'] != 'None').sum()}")
    print(f"Rainy Laps:          {(df['rainfall_mm'] > 0.5).sum()}")
    print(f"Safety Car Laps:     {(df['flag_status'] == 'Safety Car').sum()}")
    
    print("\n🎯 Race Strategy Distribution:")
    print(df['race_strategy'].value_counts())
    
    print("\n📊 Strategy Mode Distribution:")
    print(df['strategy_mode'].value_counts())
    
    print("\n🛞 Tyre Compound Usage:")
    print(df['tyre_compound'].value_counts())
    
    print("\n⚡ Push Signal Distribution:")
    print(df['push_signal'].value_counts())
    
    # Strategic insights
    avg_stint_length = df.groupby(['driver', 'stint_number'])['stint_lap_count'].max().mean()
    print(f"\n📐 Average Stint Length: {avg_stint_length:.1f} laps")
    
    # Save to CSV
    df.to_csv(output_file, index=False)
    print("\n" + "=" * 70)
    print(f"✅ Dataset saved to: {output_file}")
    print(f"📦 File size: {len(df)} rows × {len(df.columns)} columns")
    print("=" * 70)
    
    return df

if __name__ == "__main__":
    df = generate_f1_dataset(num_rows=15000, output_file='f1_synthetic_dataset_5000.csv')
    
    print("\n🔍 Sample Data (First 5 Rows):")
    print(df.head()[['lap_number', 'driver', 'position', 'lap_time', 'tyre_compound', 'tyre_wear_pct', 'race_strategy', 'pit_stop_flag']].to_string())