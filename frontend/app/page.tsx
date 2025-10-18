"use client";

import React, { useState } from 'react';
import TrackTemperature from './components/TrackTemperature';
import Rainfall from './components/Rainfall';
import FlagComponent from './components/FlagComponent';

export default function Dashboard() {
  // State to manage race data
  const [raceData, setRaceData] = useState({
    temperature: {
      fahrenheit: 100,
      celsius: 37
    },
    rainfall: 0,
    flagType: 'none' as 'none' | 'red' | 'yellow'
  });

  // Function to update race data (could be called after each lap)
  const updateRaceData = (newData: typeof raceData) => {
    setRaceData(newData);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-black to-gray-900 text-white">
      <div className="bg-blue-300 pl-4 pr-4 pt-2 pb-2 mr-80 rounded-b-xl">
        <div className="flex items-center">
          <span className="text-[#515151] font-bold mr-2">Race:</span>
          <span className="text-[#515151] mr-4">COTA 2024 Grand Prix</span>
          <span className="text-[#515151] font-bold mr-2">Driver:</span>
          <span className="text-[#515151]">Lewis Hamilton</span>
        </div>
      </div>
      
      {/* Dashboard Content */}
      <div className="absolute top-20 left-4 flex flex-col space-y-4">
        <TrackTemperature temperature={raceData.temperature} />
        <Rainfall percentage={raceData.rainfall} />
        <FlagComponent flagType={raceData.flagType} />
      </div>
    </div>
  );
}