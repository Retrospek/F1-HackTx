import React from 'react';

interface CurrentPositionBoxProps {
  position: string;
  compound: string;
}

const CurrentPositionBox: React.FC<CurrentPositionBoxProps> = ({ position, compound }) => {
  // Determine compound color
  const getCompoundColor = () => {
    switch (compound.toLowerCase()) {
      case 'soft':
        return 'bg-red-500';
      case 'medium':
        return 'bg-yellow-400';
      case 'hard':
        return 'bg-white';
      case 'intermediate':
        return 'bg-green-500';
      case 'wet':
        return 'bg-blue-500';
      default:
        return 'bg-gray-400';
    }
  };

  return (
    <div className="bg-[#1F2937] rounded-xl p-4 text-center h-full flex flex-col justify-between shadow-xl hover:shadow-2xl transition-shadow duration-300">
      {/* Label - Consistent Typography */}
      <div className="text-[#D4D4D4] text-sm uppercase tracking-wider font-medium mb-2">
        Position & Compound
      </div>
      
      {/* Content */}
      <div className="flex-grow flex flex-col items-center justify-center space-y-3">
        {/* Position - Primary Value */}
        <div className="text-white text-6xl font-bold">
          {position}
        </div>
        
        {/* Compound - Secondary Value with Color Badge */}
        <div className="flex items-center space-x-2">
          <div className={`w-6 h-6 rounded-full ${getCompoundColor()}`}></div>
          <div className="text-white text-2xl font-bold">
            {compound}
          </div>
        </div>
      </div>
    </div>
  );
};

export default CurrentPositionBox;