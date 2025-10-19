import React from 'react';

interface CurrentPositionProps {
  position?: string;
  compound?: string;
}

const CurrentPositionBox: React.FC<CurrentPositionProps> = ({ 
  position = 'N/A', 
  compound = 'N/A' 
}) => {
  // Get compound color
  const getCompoundColor = (comp: string) => {
    switch (comp.toLowerCase()) {
      case 'soft':
        return 'from-red-400 to-red-600';
      case 'medium':
        return 'from-yellow-400 to-yellow-600';
      case 'hard':
        return 'from-gray-300 to-gray-500';
      case 'intermediate':
        return 'from-green-400 to-green-600';
      case 'wet':
        return 'from-blue-400 to-blue-600';
      default:
        return 'from-purple-400 to-purple-600';
    }
  };

  // Get tire emoji
  const getTireEmoji = (comp: string) => {
    switch (comp.toLowerCase()) {
      case 'soft':
        return '🔴';
      case 'medium':
        return '🟡';
      case 'hard':
        return '⚪';
      case 'intermediate':
        return '🟢';
      case 'wet':
        return '🔵';
      default:
        return '🏎️';
    }
  };

  return (
    <div className="bg-gradient-to-br from-gray-700/50 to-gray-900/70 rounded-2xl p-6 h-full flex flex-col justify-center 
      border border-gray-600/30 shadow-2xl backdrop-blur-sm transform transition-all hover:scale-[1.02]">
      <div className="text-gray-300 text-xl mb-4 font-semibold tracking-wider uppercase">
        Position & Compound
      </div>
      <div className="flex items-center mb-4 space-x-4">
        <span className="text-gray-400 text-lg">Position:</span>
        <span className="text-white text-5xl font-bold bg-clip-text text-transparent 
          bg-gradient-to-r from-blue-400 to-blue-600 drop-shadow-lg">
          {position}
        </span>
      </div>
      <div className="flex items-center space-x-4">
        <span className="text-gray-400 text-lg">Compound:</span>
        <div className="flex items-center space-x-2">
          <span className="text-3xl">{getTireEmoji(compound)}</span>
          <span className={`text-white text-3xl font-bold bg-clip-text text-transparent 
            bg-gradient-to-r ${getCompoundColor(compound)} drop-shadow-lg`}>
            {compound}
          </span>
        </div>
      </div>
    </div>
  );
};

export default CurrentPositionBox;