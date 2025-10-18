import React from 'react';

interface RainfallProps {
  percentage: number;
}

const Rainfall: React.FC<RainfallProps> = ({ percentage }) => {
  return (
    <div className="bg-blue-300 rounded-lg p-3 w-[200px] mt-4">
      <div className="text-[#515151] text-sm mb-2">Rainfall</div>
      <div className="text-[#515151] text-4xl font-bold">{percentage}%</div>
    </div>
  );
};

export default Rainfall;