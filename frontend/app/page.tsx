// frontend/app/page.tsx

"use client";

import React, { useState, useEffect, useCallback } from 'react';
import TrackTemperature from './components/TrackTemperature';
import Rainfall from './components/Rainfall';
import FlagComponent from './components/FlagComponent';
import StrategyRecommendation from './components/StrategyRecommendation';
import LapTimeGraph from './components/LapTimeGraph';
import CurrentPositionBox from './components/CurrentPositionBox';
import TyreLifeBox from './components/TyreLifeBox';
import EnginePowerBox from './components/EnginePowerBox';

// API Configuration
const API_BASE_URL = ''; // Uses Next.js proxy

// --- TYPE DEFINITIONS MATCHING FASTAPI RESPONSE ---
interface RaceData {
  status: string;
  current_lap: number;
  raw_lap_time: number;
  
  // Strategy
  ML_Recommendation: string;
  ML_Confidence: number;
  
  // Dashboard Metrics
  throttle_percent: number;
  track_temp: number;
  rainfall_mm: number;
  current_position: number;
  tyre_compound: string;
  stint_lap_count: number;
  delta_message: string;
}

interface RaceInfo {
  season: number;
  driver: string;
  total_laps: number;
  emulation_laps: number;
  circuit: string;
}

interface LapTimeData {
  lap: number;
  time: number;
}

export default function Dashboard() {
  // State initialization
  const [raceInfo, setRaceInfo] = useState<RaceInfo | null>(null);
  const [currentLap, setCurrentLap] = useState<RaceData | null>(null);
  const [lapTimeHistory, setLapTimeHistory] = useState<LapTimeData[]>([]);
  const [isRaceActive, setIsRaceActive] = useState(false);
  const [raceStatus, setRaceStatus] = useState('Ready');
  const [error, setError] = useState<string | null>(null);
  
  // --- FETCH METADATA ON LOAD ---
  useEffect(() => {
    const fetchRaceInfo = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/race/info`);
        if (!response.ok) throw new Error(`Info API Error: ${response.status}`);
        
        const data: RaceInfo = await response.json();
        setRaceInfo(data);
      } catch (err) {
        console.error('Error fetching race info:', err);
        setError("Failed to load race metadata. Check FastAPI server.");
      }
    };
    fetchRaceInfo();
  }, []); // Run only once on mount

  // Fetch next lap from API
  const fetchNextLap = useCallback(async () => {
    if (!raceInfo) return; 

    try {
      const response = await fetch(`${API_BASE_URL}/api/feed`);
      
      if (!response.ok) {
        if (response.status === 410) { 
          setIsRaceActive(false);
          setRaceStatus('Race Finished');
          return;
        }
        throw new Error(`API Error: ${response.status}`);
      }

      const data: RaceData = await response.json();
      setCurrentLap(data);
      setRaceStatus(data.status);
      
      // Update lap time history only if lap time is valid
      if (data.raw_lap_time > 0) {
        setLapTimeHistory(prev => [
          ...prev,
          { lap: data.current_lap, time: data.raw_lap_time }
        ]);
      }

      setError(null);
    } catch (err) {
      console.error('Error fetching lap data:', err);
      if (err instanceof Error && err.message.includes("410")) {
        setIsRaceActive(false);
        setRaceStatus('Race Finished');
      } else {
        setError(err instanceof Error ? err.message : 'Unknown network/API error');
        setIsRaceActive(false);
      }
    }
  }, [raceInfo]);

  // Start race simulation and reset API counter
  const startRace = useCallback(async () => {
    // Reset API counter on the backend
    try {
      const response = await fetch(`${API_BASE_URL}/api/reset`, { method: 'POST' });
      if (!response.ok) throw new Error("Failed to reset race");
    } catch (err) {
      console.error('Error resetting race:', err);
    }

    setIsRaceActive(true);
    setLapTimeHistory([]);
    setCurrentLap(null); // Clear current lap data for clean start
    setError(null);
    fetchNextLap(); // Fetch the first lap
  }, [fetchNextLap]);

  // Pause/Resume race
  const toggleRace = () => {
    setIsRaceActive(!isRaceActive);
  };

  // Auto-advance laps when race is active
  useEffect(() => {
    if (!isRaceActive) return;

    const interval = setInterval(() => {
      fetchNextLap();
    }, 3000); // New lap every 3 seconds

    return () => clearInterval(interval);
  }, [isRaceActive, fetchNextLap]);

  // Helper functions for display
  const celsiusToFahrenheit = (celsius: number): number => {
    return (celsius * 9/5) + 32;
  };

  const getFlagType = (flagStatus: string): 'none' | 'red' | 'yellow' => {
    if (flagStatus.includes('YELLOW')) return 'yellow';
    if (flagStatus.includes('RED')) return 'red';
    // Use delta_message logic to trigger caution flags dynamically
    if (currentLap?.delta_message.includes('WARNING') && isRaceActive) return 'yellow'; 
    return 'none';
  };

  // --- MAPPED DATA FOR COMPONENTS ---
  // Ensure we check if currentLap is available before mapping
  const displayData = {
    // Strategy: Mock confidence scores based on the single recommendation
    strategyConfidence: {
      // NOTE: We distribute confidence across all three strategies for the bar chart visualization
      // Here, we hard-set the recommended strategy's confidence and distribute the rest
      aggressive: currentLap?.ML_Recommendation === 'Aggressive' ? currentLap.ML_Confidence : 10, 
      neutral: currentLap?.ML_Recommendation === 'Neutral' ? currentLap.ML_Confidence : 60,
      defensive: currentLap?.ML_Recommendation === 'Defense' ? currentLap.ML_Confidence : 30,
      recommended: currentLap?.ML_Recommendation || 'N/A'
    },
    // Weather
    temperature: {
      fahrenheit: currentLap ? celsiusToFahrenheit(currentLap.track_temp) : 0, 
      celsius: currentLap?.track_temp || 0
    },
    rainfall: currentLap?.rainfall_mm || 0,
    
    // Flag 
    flagType: getFlagType(currentLap?.delta_message || ''),
    
    // Position & Compound
    currentPosition: {
      position: currentLap ? `P${currentLap.current_position}` : 'N/A',
      compound: currentLap?.tyre_compound || 'N/A'
    },
    // Tyre Life & Engine
    tyreLife: currentLap ? `${currentLap.stint_lap_count} LAPS` : 'N/A', 
    enginePower: currentLap ? `${Math.round(currentLap.throttle_percent)}%` : '0%',
    // Messages
    lapTimeSignal: currentLap?.delta_message || (currentLap ? 'AWAITING NEXT LAP' : 'READY TO START')
  };

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-teal-800 via-blue-900 to-blue-950 text-white flex flex-col">
      {/* Race Header */}
      <div className="bg-black text-white pl-4 pr-4 pt-3 pb-3 rounded-b-xl shadow-lg">
        <div className="flex items-center justify-between">
          <div className="flex items-center text-lg">
            {/* FIX: Use raceInfo state for dynamic metadata */}
            <span className="text-white font-bold mr-2">Race:</span>
            <span className="text-white mr-4">{raceInfo?.circuit || 'Loading...'} {raceInfo?.season} GP</span>
            <span className="text-white font-bold mr-2">Driver:</span>
            <span className="text-white">{raceInfo?.driver || 'Loading...'}</span>
          </div>
          
          {/* Race Controls */}
          <div className="flex items-center space-x-4">
            <div className="text-white font-bold">
              Lap: {currentLap?.current_lap || 0} / {raceInfo?.total_laps || '?'}
            </div>
            <div className="text-white">
              Status: {raceStatus}
            </div>
            {/* Control Buttons (Logic remains the same) */}
            {!isRaceActive && raceStatus !== 'Race Finished' && (
              <button
                onClick={startRace}
                className="bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-bold transition-colors"
              >
                Start Race
              </button>
            )}
            {(currentLap !== null && raceStatus !== 'Race Finished' && isRaceActive) && (
              <button
                onClick={toggleRace}
                className={`bg-yellow-500 hover:bg-yellow-600 text-white px-4 py-2 rounded-lg font-bold transition-colors`}
              >
                Pause
              </button>
            )}
             {(currentLap !== null && raceStatus !== 'Race Finished' && !isRaceActive && raceStatus !== 'Ready') && (
              <button
                onClick={toggleRace}
                className={`bg-green-500 hover:bg-green-600 text-white px-4 py-2 rounded-lg font-bold transition-colors`}
              >
                Resume
              </button>
            )}
            {raceStatus === 'Race Finished' && (
              <button
                onClick={startRace}
                className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-bold transition-colors"
              >
                Restart
              </button>
            )}
          </div>
        </div>
        
        {/* Lap Time Signal */}
        {displayData.lapTimeSignal && (
          <div className={`mt-2 font-bold ${
            displayData.lapTimeSignal.includes('WARNING') ? 'text-red-500' :
            displayData.lapTimeSignal.includes('PUSH') ? 'text-green-500' :
            'text-blue-500'
          }`}>
            📊 {displayData.lapTimeSignal}
          </div>
        )}
      </div>
      
      {/* Dashboard Content */}
      <div className="flex-grow grid grid-cols-12 gap-4 p-3">
        {/* Left Column (Weather/Incidents) */}
        <div className="col-span-3 grid grid-rows-3 gap-4">
          <div className="row-span-1">
            <TrackTemperature temperature={displayData.temperature} />
          </div>
          <div className="row-span-1">
            <Rainfall percentage={displayData.rainfall} />
          </div>
          <div className="row-span-1">
            <FlagComponent flagType={displayData.flagType} />
          </div>
        </div>

        {/* Middle Column (Strategy/Graph) */}
        <div className="col-span-6 grid grid-rows-2 gap-4">
          <div className="row-span-1">
            <StrategyRecommendation 
              strategy={displayData.strategyConfidence}
            />
          </div>
          <div className="row-span-1">
            <LapTimeGraph lapData={lapTimeHistory} />
          </div>
        </div>

        {/* Right Column (Driver Metrics) */}
        <div className="col-span-3 grid grid-rows-3 gap-4">
          <div className="row-span-1">
            <CurrentPositionBox 
              position={displayData.currentPosition.position}
              compound={displayData.currentPosition.compound}
            />
          </div>
          <div className="row-span-1">
            <TyreLifeBox expectedLifeTime={displayData.tyreLife} />
          </div>
          <div className="row-span-1">
            <EnginePowerBox usage={displayData.enginePower} />
          </div>
        </div>
      </div>
    </div>
  );
}