import React from 'react';

interface RainfallProps {
  percentage: number;
}

const Rainfall: React.FC<RainfallProps> = ({ percentage }) => {
  return (
    <div className="bg-[#1A2B4A] rounded-lg p-4 text-center h-full flex flex-col justify-center">
      <div className="text-[#D4D4D4] text-2xl mb-2 uppercase tracking-wider">
        Rainfall
      </div>
      <div className="text-white text-6xl font-bold">
        {percentage}%
      </div>
    </div>
  );
};

export default Rainfall;