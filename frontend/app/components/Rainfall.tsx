import React from 'react';

interface RainfallProps {
  percentage: number;
}

const Rainfall: React.FC<RainfallProps> = ({ percentage }) => {
  return (
    <div className="bg-blue-300 rounded-lg text-center py-20 -mt-15">
      <div className="text-[#515151] text-3xl mb-4">Rainfall</div>
      <div className="text-[#515151] text-8xl font-bold">{percentage}%</div>
    </div>
  );
};

export default Rainfall;