import React from 'react';

interface TrackTemperatureProps {
  temperature: {
    fahrenheit: number;
    celsius: number;
  };
}

const TrackTemperature: React.FC<TrackTemperatureProps> = ({ temperature }) => {
  return (
    <div className="bg-[#2C2C2C] rounded-lg p-6 text-center">
      <div className="text-[#D4D4D4] text-lg mb-2 uppercase tracking-wider">
        Track Temperature
      </div>
      <div className="text-white text-5xl font-bold">
        {temperature.fahrenheit}°F / {temperature.celsius}°C
      </div>
    </div>
  )
};

export default TrackTemperature;