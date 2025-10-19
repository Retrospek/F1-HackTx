import React from 'react';

interface CurrentPositionProps {
  position?: string;
  compound?: string;
}

const CurrentPositionBox: React.FC<CurrentPositionProps> = ({ 
  position = 'N/A', 
  compound = 'N/A' 
}) => {
  return (
    <div className="bg-[#515151] rounded-lg p-6 h-full flex flex-col justify-center">
      <div className="text-[#D4D4D4] text-xl mb-4">Current Position and Compound</div>
      <div className="flex items-center mb-2">
        <span className="text-[#D4D4D4] text-lg mr-4">Position:</span>
        <span className="text-[#D4D4D4] text-3xl font-bold">{position}</span>
      </div>
      <div className="flex items-center">
        <span className="text-[#D4D4D4] text-lg mr-4">Compound:</span>
        <span className="text-[#D4D4D4] text-3xl font-bold">{compound}</span>
      </div>
    </div>
  );
};

export default CurrentPositionBox;