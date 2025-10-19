"use client";

import React, { useState } from 'react';
import TrackTemperature from './components/TrackTemperature';
import Rainfall from './components/Rainfall';
import FlagComponent from './components/FlagComponent';
import StrategyRecommendation from './components/StrategyRecommendation';
import LapTimeGraph from './components/LapTimeGraph';
import CurrentPositionBox from './components/CurrentPositionBox';
import TyreLifeBox from './components/TyreLifeBox';
import EnginePowerBox from './components/EnginePowerBox';

export default function Dashboard() {
  // State to manage race data
  const [raceData, setRaceData] = useState({
    temperature: {
      fahrenheit: 100,
      celsius: 37
    },
    rainfall: 0,
    flagType: 'none' as 'none' | 'red' | 'yellow',
    strategy: {
      aggressive: 10,
      neutral: 80,
      defensive: 10
    },
    lapData: [
      { lap: 1, time: 90.5 },
      { lap: 2, time: 89.2 },
      { lap: 3, time: 91.1 }
    ],
    currentPosition: {
      position: '5th',
      compound: 'Soft'
    },
    tyreLife: '3 Laps',
    enginePower: '85%'
  });

  return (
    <div className="fixed inset-0 bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white flex flex-col">
      {/* Race Header */}
      <div className="bg-blue-300 pl-4 pr-4 pt-3 pb-3 rounded-b-xl">
        <div className="flex items-center text-lg">
          <span className="text-[#515151] font-bold mr-2">Race:</span>
          <span className="text-[#515151] mr-4">COTA 2024 Grand Prix</span>
          <span className="text-[#515151] font-bold mr-2">Driver:</span>
          <span className="text-[#515151]">Lewis Hamilton</span>
        </div>
      </div>
      
      {/* Dashboard Content */}
      <div className="flex-grow grid grid-cols-12 gap-4 p-3">
        {/* Left Column */}
        <div className="col-span-3 grid grid-rows-3 gap-4">
          <div className="row-span-1">
            <TrackTemperature temperature={raceData.temperature} />
          </div>
          <div className="row-span-1">
            <Rainfall percentage={raceData.rainfall} />
          </div>
          <div className="row-span-1">
            <FlagComponent flagType={raceData.flagType} />
          </div>
        </div>

        {/* Middle Column */}
        <div className="col-span-6 grid grid-rows-2 gap-4">
          <div className="row-span-1">
            <StrategyRecommendation initialStrategy={raceData.strategy} />
          </div>
          <div className="row-span-1">
            <LapTimeGraph lapData={raceData.lapData} />
          </div>
        </div>

        {/* Right Column */}
        <div className="col-span-3 grid grid-rows-3 gap-4">
          <div className="row-span-1">
            <CurrentPositionBox 
              position={raceData.currentPosition.position}
              compound={raceData.currentPosition.compound}
            />
          </div>
          <div className="row-span-1">
            <TyreLifeBox expectedLifeTime={raceData.tyreLife} />
          </div>
          <div className="row-span-1">
            <EnginePowerBox usage={raceData.enginePower} />
          </div>
        </div>
      </div>
    </div>
  );
}