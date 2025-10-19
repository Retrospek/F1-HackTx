'use client';

import React, { useState, useEffect } from 'react';

// Mock function to simulate ML strategy recommendation
const getStrategyRecommendation = () => {
  const strategies = [
    { aggressive: 10, neutral: 80, defensive: 10 },
    { aggressive: 40, neutral: 40, defensive: 20 },
    { aggressive: 20, neutral: 60, defensive: 20 }
  ];
  return strategies[Math.floor(Math.random() * strategies.length)];
};

const StrategyRecommendation = () => {
  const [strategy, setStrategy] = useState({
    aggressive: 10,
    neutral: 80,
    defensive: 10
  });

  // Determine the strategy type(s) with the highest percentage
  const findHighestStrategies = (strategyObj) => {
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

  // Update strategy periodically (simulating ML analysis)
  useEffect(() => {
    const updateStrategy = () => {
      const newStrategy = getStrategyRecommendation();
      setStrategy(newStrategy);
    };

    // Update every 5 seconds (for demonstration)
    const intervalId = setInterval(updateStrategy, 5000);

    return () => clearInterval(intervalId);
  }, []);

  // Determine which strategies are at the max
  const highestStrategies = findHighestStrategies(strategy);

  return (
    <div className="bg-gray-800 p-8 rounded-lg w-full h-full flex flex-col justify-center">
      <div className="text-white text-2xl mb-8 font-bold">
        Recommended Strategy Type
      </div>
      <div className="space-y-6">
        {/* Aggressive Strategy */}
        <div className="flex items-center">
          <div className="w-32 text-white text-lg">Aggressive</div>
          <div className="flex-grow bg-gray-700 rounded-full h-4 mr-4">
            <div 
              className={`h-4 rounded-full transition-all duration-500 ease-in-out ${
                highestStrategies.aggressive ? 'bg-blue-300' : 'bg-gray-500'
              }`}
              style={{ width: `${strategy.aggressive}%` }}
            ></div>
          </div>
          <div className="text-white text-lg w-16 text-right">
            {strategy.aggressive}%
          </div>
        </div>

        {/* Neutral Strategy */}
        <div className="flex items-center">
          <div className="w-32 text-white text-lg">Neutral</div>
          <div className="flex-grow bg-gray-700 rounded-full h-4 mr-4">
            <div 
              className={`h-4 rounded-full transition-all duration-500 ease-in-out ${
                highestStrategies.neutral ? 'bg-blue-300' : 'bg-gray-500'
              }`}
              style={{ width: `${strategy.neutral}%` }}
            ></div>
          </div>
          <div className="text-white text-lg w-16 text-right">
            {strategy.neutral}%
          </div>
        </div>

        {/* Defensive Strategy */}
        <div className="flex items-center">
          <div className="w-32 text-white text-lg">Defensive</div>
          <div className="flex-grow bg-gray-700 rounded-full h-4 mr-4">
            <div 
              className={`h-4 rounded-full transition-all duration-500 ease-in-out ${
                highestStrategies.defensive ? 'bg-blue-300' : 'bg-gray-500'
              }`}
              style={{ width: `${strategy.defensive}%` }}
            ></div>
          </div>
          <div className="text-white text-lg w-16 text-right">
            {strategy.defensive}%
          </div>
        </div>
      </div>
    </div>
  );
};

export default StrategyRecommendation;