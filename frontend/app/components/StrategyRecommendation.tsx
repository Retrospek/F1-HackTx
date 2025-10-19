import React from 'react';

interface StrategyRecommendationProps {
  strategy: {
    aggressive: number;
    neutral: number;
    defensive: number;
    recommended: string;
  };
}

const StrategyRecommendation: React.FC<StrategyRecommendationProps> = ({ strategy }) => {
  return (
    <div className="bg-gradient-to-br from-gray-800 to-gray-900 rounded-xl p-6 h-full flex flex-col shadow-xl hover:shadow-2xl transition-shadow duration-300">
      {/* Header */}
      <div className="text-sm text-[#D4D4D4] uppercase tracking-wider font-medium mb-3">
        ML Recommended Strategy:
      </div>
      
      {/* Recommended Strategy */}
      <div className="text-3xl font-bold text-white uppercase mb-6">
        {strategy.recommended}
      </div>
      
      {/* Confidence Bars */}
      <div className="flex-grow space-y-4">
        {/* Aggressive */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm capitalize text-[#D4D4D4] font-medium">Aggressive</span>
            <span className="text-lg font-bold text-white">{strategy.aggressive.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${
                strategy.recommended === 'AGGRESSIVE' ? 'bg-teal-500' : 'bg-blue-500'
              }`}
              style={{ width: `${strategy.aggressive}%` }}
            ></div>
          </div>
        </div>

        {/* Neutral */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm capitalize text-[#D4D4D4] font-medium">Neutral</span>
            <span className="text-lg font-bold text-white">{strategy.neutral.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${
                strategy.recommended === 'NEUTRAL' ? 'bg-teal-500' : 'bg-blue-500'
              }`}
              style={{ width: `${strategy.neutral}%` }}
            ></div>
          </div>
        </div>

        {/* Defensive */}
        <div>
          <div className="flex justify-between items-center mb-2">
            <span className="text-sm capitalize text-[#D4D4D4] font-medium">Defensive</span>
            <span className="text-lg font-bold text-white">{strategy.defensive.toFixed(1)}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-3 overflow-hidden">
            <div
              className={`h-3 rounded-full transition-all duration-500 ${
                strategy.recommended === 'DEFENSIVE' ? 'bg-teal-500' : 'bg-blue-500'
              }`}
              style={{ width: `${strategy.defensive}%` }}
            ></div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StrategyRecommendation;