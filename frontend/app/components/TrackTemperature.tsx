import React from 'react';

interface TrackTemperatureProps {
  temperature: {
    fahrenheit: number;
    celsius: number;
  };
}

const TrackTemperature: React.FC<TrackTemperatureProps> = ({ temperature }) => {
  return (
    <div className="bg-[#515151] rounded-lg p-6 text-center ml-4 mt-4">
      <div className="text-[#D4D4D4] text-lg mb-2">Track Temperature</div>
      <div className="text-[#D4D4D4] text-5xl font-bold">
        {temperature.fahrenheit}°F / {temperature.celsius}°C
      </div>
    </div>
  )
};

export default TrackTemperature;