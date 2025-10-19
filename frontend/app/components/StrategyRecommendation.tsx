// frontend/components/StrategyRecommendation.tsx

'use client';

import React from 'react';

// --- TYPE DEFINITION ---
interface StrategyConfidence {
  aggressive: number;
  neutral: number;
  defensive: number;
  recommended: string;
}

interface StrategyRecommendationProps {
  strategy: StrategyConfidence;
}

const StrategyRecommendation: React.FC<StrategyRecommendationProps> = ({ strategy }) => {

  // Determine the strategy type(s) with the highest percentage
  const findHighestStrategies = (strategyObj: StrategyConfidence) => {
    const max = Math.max(
      strategyObj.aggressive, 
      strategyObj.neutral, 
      strategyObj.defensive
    );
    return {
      aggressive: strategyObj.aggressive === max,
      neutral: strategyObj.neutral === max,
      defensive: strategyObj.defensive === max
    };
  };

  // Determine which strategies are at the max
  const highestStrategies = findHighestStrategies(strategy);

  // Helper to determine text color for the recommended strategy
  const getRecColor = (rec: string) => {
    if (rec.includes('Aggressive')) return 'text-red-500';
    if (rec.includes('Defense')) return 'text-yellow-500';
    return 'text-blue-500'; // FIX: Blue for Neutral/default
  };
  
  // Helper to format the bar color
  const getBarColor = (name: string, isHighest: boolean) => {
    if (!isHighest) return 'bg-gray-500';
    
    if (name === 'Aggressive') return 'bg-red-500';
    if (name === 'Defensive') return 'bg-yellow-500';
    return 'bg-blue-500'; // FIX: Blue for the highest bar (Neutral)
  }

  // --- Main Render ---
  return (
    <div className="bg-gray-800/80 p-6 rounded-xl w-full h-full flex flex-col justify-center border border-blue-600/50 shadow-lg">
      <div className="text-gray-300 text-lg font-bold uppercase tracking-wider mb-2">
        ML Recommended Strategy:
      </div>
      <div className={`text-white text-4xl font-extrabold mb-8 ${getRecColor(strategy.recommended)}`}>
        {strategy.recommended || 'AWAITING DATA'}
      </div>
      
      <div className="space-y-4">
        {/* Aggressive Strategy Bar */}
        <div className="flex items-center">
          <div className="w-24 text-white text-base">Aggressive</div>
          <div className="flex-grow bg-gray-700 rounded-full h-3 mr-3">
            <div 
              className={`h-3 rounded-full transition-all duration-500 ease-in-out ${
                getBarColor('Aggressive', highestStrategies.aggressive)
              }`}
              style={{ width: `${strategy.aggressive}%` }}
            ></div>
          </div>
          <div className="text-white text-base w-12 text-right">
            {strategy.aggressive.toFixed(1)}%
          </div>
        </div>

        {/* Neutral Strategy Bar */}
        <div className="flex items-center">
          <div className="w-24 text-white text-base">Neutral</div>
          <div className="flex-grow bg-gray-700 rounded-full h-3 mr-3">
            <div 
              className={`h-3 rounded-full transition-all duration-500 ease-in-out ${
                getBarColor('Neutral', highestStrategies.neutral)
              }`}
              style={{ width: `${strategy.neutral}%` }}
            ></div>
          </div>
          <div className="text-white text-base w-12 text-right">
            {strategy.neutral.toFixed(1)}%
          </div>
        </div>

        {/* Defensive Strategy Bar */}
        <div className="flex items-center">
          <div className="w-24 text-white text-base">Defensive</div>
          <div className="flex-grow bg-gray-700 rounded-full h-3 mr-3">
            <div 
              className={`h-3 rounded-full transition-all duration-500 ease-in-out ${
                getBarColor('Defensive', highestStrategies.defensive)
              }`}
              style={{ width: `${strategy.defensive}%` }}
            ></div>
          </div>
          <div className="text-white text-base w-12 text-right">
            {strategy.defensive.toFixed(1)}%
          </div>
        </div>
      </div>
    </div>
  );
};

export default StrategyRecommendation;