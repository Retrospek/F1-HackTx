import React from 'react';

interface TrackTemperatureProps {
  temperature: {
    fahrenheit: number;
    celsius: number;
  };
}

const TrackTemperature: React.FC<TrackTemperatureProps> = ({ temperature }) => {
  return (
    <div className="bg-[#2C2C2C] rounded-lg p-4 text-center h-full flex flex-col justify-center">
      <div className="text-[#D4D4D4] text-xl mb-2 uppercase tracking-wider">
        Track Temperature
      </div>
      <div className="text-white text-6xl font-bold">
        {temperature.fahrenheit}°F / {temperature.celsius}°C
      </div>
    </div>
  )
};

export default TrackTemperature;