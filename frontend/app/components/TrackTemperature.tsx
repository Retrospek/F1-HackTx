import React from 'react';

interface TrackTemperatureProps {
  temperature: {
    fahrenheit: number;
    celsius: number;
  };
}

const TrackTemperature: React.FC<TrackTemperatureProps> = ({ temperature }) => {
  return (
    <div className="bg-[#515151] rounded-lg p-3 w-[200px]">
      <div className="text-[#D4D4D4] text-sm mb-2">Track Temperature</div>
      <div className="text-[#D4D4D4] text-2xl font-bold">
        {temperature.fahrenheit}°F / {temperature.celsius}°C
      </div>
    </div>
  );
};

export default TrackTemperature;