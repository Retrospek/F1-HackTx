"use client";

import React, { useState, useEffect, useCallback } from 'react';
import TrackTemperature from './components/TrackTemperature';
import LapSignalBox from './components/LapSignalBox';
import FlagComponent, { FlagType } from './components/FlagComponent';
import StrategyRecommendation from './components/StrategyRecommendation';
import LapTimeGraph from './components/LapTimeGraph';
import CurrentPositionBox from './components/CurrentPositionBox';
import TyreLifeBox from './components/TyreLifeBox';
import EnginePowerBox from './components/EnginePowerBox';

// Define more robust interface for race data
interface RaceData {
  timestamp: string;
  current_lap: number;
  raw_lap_time: number;
  track_temp: number;
  rainfall_mm: number;
  throttle_percent: number;
  current_position: number;
  tyre_compound: string;
  stint_lap_count: number;  // ADD THIS
  tyre_wear_pct: number;     // ADD THIS
  flag_status: string;
  incident_message: string;  // ADD THIS
  delta_message: string;
  ML_Recommendation: string;
  ML_Confidence: {
    AGGRESSIVE: number;
    NEUTRAL: number;
    DEFENSIVE: number;
  };
  status: string;
}

interface RaceInfo {
  season: number;
  driver: string;
  total_laps: number;
  emulation_laps: number;
  circuit: string;
}

export default function Dashboard() {
  // Enhanced state management
  const [raceInfo, setRaceInfo] = useState<RaceInfo | null>(null);
  const [currentLap, setCurrentLap] = useState<RaceData | null>(null);
  const [lapTimeHistory, setLapTimeHistory] = useState<{lap: number, time: number}[]>([]);
  const [isRaceActive, setIsRaceActive] = useState(false);
  const [raceStatus, setRaceStatus] = useState('Ready');
  const [error, setError] = useState<string | null>(null);

  // Fetch race information on component mount
  useEffect(() => {
    const fetchRaceInfo = async () => {
      try {
        const response = await fetch('/api/race/info');
        
        if (!response.ok) {
          const errorText = await response.text();
          console.error('Detailed Race Info Error:', {
            status: response.status,
            statusText: response.statusText,
            body: errorText
          });
          throw new Error(`Race Info API Error: ${response.status}`);
        }
        
        const data: RaceInfo = await response.json();
        setRaceInfo(data);
      } catch (err) {
        console.error('Fetch Race Info Error:', err);
        setError(`Failed to load race metadata: ${err instanceof Error ? err.message : 'Unknown error'}`);
      }
    };

    fetchRaceInfo();
  }, []);

  // Fetch next lap data
  const fetchNextLap = useCallback(async () => {
    if (!raceInfo) return; 

    try {
      const response = await fetch('/api/feed');
      
      if (!response.ok) {
        const errorText = await response.text();
        console.error('Detailed Feed Error:', {
          status: response.status,
          statusText: response.statusText,
          body: errorText
        });
  
        if (response.status === 404) {
          console.error('API Endpoint Not Found. Check backend routing.');
          setError('API Endpoint Not Found. Ensure backend is running.');
        }
  
        if (response.status === 410) { 
          setIsRaceActive(false);
          setRaceStatus('Race Finished');
          return;
        }
  
        throw new Error(`API Error: ${response.status} - ${errorText}`);
      }
  
      const data: RaceData = await response.json();
      console.log('Received lap data:', data); // DEBUG: Check what data is received
      setCurrentLap(data);
      setRaceStatus(data.status);
      
      // Update lap time history
      if (data.raw_lap_time > 0) {
        setLapTimeHistory(prev => [
          ...prev,
          { lap: data.current_lap, time: data.raw_lap_time }
        ]);
      }

      setError(null);
    } catch (err) {
      console.error('Error fetching lap data:', err);
      setError(err instanceof Error ? err.message : 'Unknown network/API error');
      setIsRaceActive(false);
    }
  }, [raceInfo]);

  // Start race simulation
  const startRace = useCallback(async () => {
    try {
      const response = await fetch('/api/reset', { method: 'POST' });
      if (!response.ok) throw new Error("Failed to reset race");
    } catch (err) {
      console.error('Error resetting race:', err);
    }

    setIsRaceActive(true);
    setLapTimeHistory([]);
    setCurrentLap(null);
    setError(null);
    fetchNextLap();
  }, [fetchNextLap]);

  // Auto-advance laps when race is active
  useEffect(() => {
    if (!isRaceActive) return;

    const interval = setInterval(() => {
      fetchNextLap();
    }, 3000); // New lap every 3 seconds

    return () => clearInterval(interval);
  }, [isRaceActive, fetchNextLap]);

  // Temperature conversion utility
  const celsiusToFahrenheit = (celsius: number): number => {
    return Math.round((celsius * 9/5) + 32);
  };

  const toggleRace = useCallback(() => {
    setIsRaceActive(prev => !prev);
  }, []);

  // Mapped display data
  const displayData = {
    temperature: {
      fahrenheit: currentLap ? celsiusToFahrenheit(currentLap.track_temp) : 0,
      celsius: currentLap?.track_temp || 0
    },
    strategyConfidence: (() => {
      if (!currentLap) {
        return {
          aggressive: 10,
          neutral: 60,
          defensive: 30,
          recommended: 'N/A'
        };
      }
  
      const confidenceScores = currentLap.ML_Confidence || {
        AGGRESSIVE: 0.1,
        NEUTRAL: 0.6,
        DEFENSIVE: 0.3
      };
  
      return {
        aggressive: Math.round((confidenceScores.AGGRESSIVE || 0) * 100),
        neutral: Math.round((confidenceScores.NEUTRAL || 0) * 100),
        defensive: Math.round((confidenceScores.DEFENSIVE || 0) * 100),
        recommended: currentLap.ML_Recommendation || 'N/A'
      };
    })(),
    currentPosition: {
      position: currentLap ? `P${currentLap.current_position}` : 'N/A',
      compound: currentLap?.tyre_compound || 'N/A'
    },
    // FIX: Use stint_lap_count instead of current_lap
    tyreLife: currentLap ? `${currentLap.stint_lap_count} LAPS` : 'N/A',
    enginePower: currentLap ? `${Math.round(currentLap.throttle_percent)}%` : '0%',
    lapTimeSignal: currentLap?.delta_message || 'READY TO START',
    // FIX: Improved flag detection with incident message
    flagType: (() => {
      if (!currentLap) return 'none';
      
      const flagStatus = currentLap.flag_status;
      const incidentMsg = currentLap.incident_message;
      
      console.log('Flag Status:', flagStatus, 'Incident:', incidentMsg); // DEBUG
      
      // Check for Yellow flag or Safety Car
      if (flagStatus === 'Yellow' || flagStatus === 'Safety Car') {
        return 'yellow';
      }
      
      // Check for Red flag
      if (flagStatus === 'Red') {
        return 'red';
      }
      
      return 'none';
    })() as FlagType,
    // ADD: Include incident message
    incidentMessage: currentLap?.incident_message || '',
  };

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-teal-800 via-blue-900 to-blue-950 text-white flex flex-col">
      {/* Race Header */}
      <div className="bg-black text-white px-6 py-4 shadow-2xl border-b-2 border-blue-500/30">
        <div className="flex items-center justify-between">
          {/* Left: Race Info */}
          <div className="flex items-center space-x-6">
            <div className="flex items-center">
              <span className="text-[#D4D4D4] text-sm uppercase tracking-wider font-medium mr-2">Race:</span>
              <span className="text-white text-lg font-bold">{raceInfo?.circuit || 'Loading...'} {raceInfo?.season} GP</span>
            </div>
            <div className="h-6 w-px bg-gray-600"></div>
            <div className="flex items-center">
              <span className="text-[#D4D4D4] text-sm uppercase tracking-wider font-medium mr-2">Driver:</span>
              <span className="text-white text-lg font-bold">{raceInfo?.driver || 'Loading...'}</span>
            </div>
          </div>
          
          {/* Right: Race Controls */}
          <div className="flex items-center space-x-6">
            <div className="text-white text-lg font-bold">
              <span className="text-[#D4D4D4] text-sm uppercase tracking-wider font-medium">Lap: </span>
              {currentLap?.current_lap || 0} / {raceInfo?.total_laps || '?'}
            </div>
            <div className="h-6 w-px bg-gray-600"></div>
            <div className="flex items-center">
              <span className="text-[#D4D4D4] text-sm uppercase tracking-wider font-medium mr-2">Status:</span>
              <span className={`text-lg font-bold ${
                raceStatus === 'Active' ? 'text-green-400' : 
                raceStatus === 'Race Finished' ? 'text-red-400' : 
                'text-yellow-400'
              }`}>
                {raceStatus}
              </span>
            </div>
            <div className="h-6 w-px bg-gray-600"></div>
            {!isRaceActive && raceStatus !== 'Race Finished' && (
              <button
                onClick={startRace}
                className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-sm font-bold uppercase tracking-wider transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Start Race
              </button>
            )}
            {(currentLap !== null && raceStatus !== 'Race Finished' && isRaceActive) && (
              <button
                onClick={toggleRace}
                className="bg-yellow-500 hover:bg-yellow-600 text-white px-5 py-2.5 rounded-lg text-sm font-bold uppercase tracking-wider transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Pause
              </button>
            )}
             {(currentLap !== null && raceStatus !== 'Race Finished' && !isRaceActive && raceStatus !== 'Ready') && (
              <button
                onClick={toggleRace}
                className="bg-blue-600 hover:bg-blue-700 text-white px-5 py-2.5 rounded-lg text-sm font-bold uppercase tracking-wider transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Resume
              </button>
            )}
            {raceStatus === 'Race Finished' && (
              <button
                onClick={startRace}
                className="bg-red-500 hover:bg-red-600 text-white px-5 py-2.5 rounded-lg text-sm font-bold uppercase tracking-wider transition-all duration-200 shadow-lg hover:shadow-xl"
              >
                Restart
              </button>
            )}
          </div>
        </div>
        
        {/* Incident Message Banner */}
        {displayData.incidentMessage && (
          <div className="mt-3 pt-3 border-t border-gray-700">
            <div className="font-bold text-yellow-400 animate-pulse text-base uppercase tracking-wide">
              🚩 {displayData.incidentMessage}
            </div>
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
            <LapSignalBox signal={displayData.lapTimeSignal} />
          </div>
          <div className="row-span-1">
            <FlagComponent 
              flagType={displayData.flagType}
              incidentMessage={displayData.incidentMessage}  // PASS incident message
            />
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