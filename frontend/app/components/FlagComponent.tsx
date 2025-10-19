import React, { useState } from 'react';

export type FlagType = 'none' | 'red' | 'yellow';

interface FlagComponentProps {
  flagType?: FlagType;
  incidentMessage?: string;  // ADD THIS PROP
}

const FlagComponent: React.FC<FlagComponentProps> = ({ 
  flagType = 'none',
  incidentMessage = ''  // ADD THIS
}) => {
  const [isWarningFlashEnabled, setIsWarningFlashEnabled] = useState(true);

  // Determine background color and text based on flag type
  const getFlagStyles = () => {
    switch (flagType) {
      case 'red':
        return {
          bgColor: 'bg-red-600',
          text: 'RED FLAG',
          blinkClass: isWarningFlashEnabled ? 'animate-blink' : ''
        };
      case 'yellow':
        return {
          bgColor: 'bg-yellow-500',
          text: 'YELLOW FLAG',
          blinkClass: isWarningFlashEnabled ? 'animate-blink' : ''
        };
      default:
        return {
          bgColor: 'bg-[#2C2C2C]',
          text: 'GREEN',  // Changed from 'NONE'
          blinkClass: ''
        };
    }
  };

  const { bgColor, text, blinkClass } = getFlagStyles();

  return (
    <div className="bg-[#2C2C2C] rounded-xl p-4 text-center h-full flex flex-col justify-between shadow-xl hover:shadow-2xl transition-shadow duration-300">
      {/* Label - Consistent Typography */}
      <div className="text-[#D4D4D4] text-sm uppercase tracking-wider font-medium mb-2">
        Flag Status
      </div>
      
      <div className="flex-grow flex flex-col justify-center">
        {/* Flag Status - Primary Value */}
        <div className={`
          text-white 
          text-4xl 
          font-bold 
          py-4 
          rounded-lg 
          text-center 
          ${bgColor} 
          ${blinkClass}
        `}>
          {text}
        </div>
        
        {/* Incident Message - Secondary Info */}
        {incidentMessage && flagType !== 'none' && (
          <div className="mt-3 text-yellow-300 text-sm font-semibold bg-black/50 rounded px-2 py-2 break-words">
            {incidentMessage}
          </div>
        )}
      </div>
      
      {/* Toggle Control */}
      <div className="flex items-center justify-center mt-2">
        <span className="text-[#D4D4D4] text-xs mr-3 font-medium">Warning Flash</span>
        <label className="inline-flex items-center cursor-pointer">
          <input
            type="checkbox"
            checked={isWarningFlashEnabled}
            onChange={() => setIsWarningFlashEnabled(!isWarningFlashEnabled)}
            className="sr-only peer"
          />
          <div className="relative w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 dark:peer-focus:ring-blue-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full rtl:peer-checked:after:-translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:start-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-blue-600"></div>
        </label>
      </div>
    </div>
  );
};

export default FlagComponent;