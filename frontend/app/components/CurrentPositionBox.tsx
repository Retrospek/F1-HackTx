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
    <div className="bg-gradient-to-br from-gray-700/50 to-gray-900/70 rounded-2xl p-6 h-full flex flex-col justify-center 
      border border-gray-600/30 shadow-2xl backdrop-blur-sm transform transition-all hover:scale-[1.02]">
      <div className="text-gray-300 text-xl mb-4 font-semibold tracking-wider uppercase">
        Current Position and Compound
      </div>
      <div className="flex items-center mb-2 space-x-4">
        <span className="text-gray-400 text-lg">Position:</span>
        <span className="text-white text-4xl font-bold bg-clip-text text-transparent 
          bg-gradient-to-r from-blue-400 to-blue-600">
          {position}
        </span>
      </div>
      <div className="flex items-center space-x-4">
        <span className="text-gray-400 text-lg">Compound:</span>
        <span className="text-white text-4xl font-bold bg-clip-text text-transparent 
          bg-gradient-to-r from-purple-400 to-purple-600">
          {compound}
        </span>
      </div>
    </div>
  );
};

export default CurrentPositionBox;