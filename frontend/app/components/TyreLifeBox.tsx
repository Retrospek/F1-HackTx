import React from 'react';

interface TyreLifeProps {
  expectedLifeTime?: string;
}

const TyreLifeBox: React.FC<TyreLifeProps> = ({ 
  expectedLifeTime = 'N/A' 
}) => {
  return (
    <div className="bg-gradient-to-br from-gray-700/50 to-gray-900/70 rounded-2xl p-6 h-full flex flex-col justify-center 
      border border-gray-600/30 shadow-2xl backdrop-blur-sm transform transition-all hover:scale-[1.02]">
      <div className="text-gray-300 text-xl mb-4 font-semibold tracking-wider uppercase">
        Tyre Expected Life Time
      </div>
      <div className="text-white text-6xl font-bold text-center bg-clip-text text-transparent 
        bg-gradient-to-r from-green-400 to-green-600">
        {expectedLifeTime}
      </div>
    </div>
  );
};

export default TyreLifeBox;