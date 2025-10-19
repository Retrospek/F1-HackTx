import React from 'react';

interface TrackTemperatureProps {
  temperature: {
    fahrenheit: number;
    celsius: number;
  };
}

const TrackTemperature: React.FC<TrackTemperatureProps> = ({ temperature }) => {
  return (
    <div className="bg-[#1F2937] rounded-xl p-4 text-center h-full flex flex-col justify-between shadow-xl hover:shadow-2xl transition-shadow duration-300">
      {/* Label - Consistent Typography */}
      <div className="text-[#D4D4D4] text-sm uppercase tracking-wider font-medium mb-2">
        Track Temperature
      </div>
      
      {/* Primary Value */}
      <div className="flex-grow flex flex-col items-center justify-center">
        <div className="text-white text-6xl font-bold">
          {temperature.fahrenheit}°F
        </div>
        {/* Secondary Value */}
        <div className="text-white text-4xl font-bold mt-2">
          {temperature.celsius}°C
        </div>
      </div>
    </div>
  );
};

export default TrackTemperature;