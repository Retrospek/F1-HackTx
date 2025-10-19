import React from 'react';

interface LapSignalBoxProps {
  signal: string;
}

const LapSignalBox: React.FC<LapSignalBoxProps> = ({ signal }) => {
  // Determine styling based on signal message
  const getSignalStyles = () => {
    const upperSignal = signal.toUpperCase();
    
    if (upperSignal.includes('PUSH') || upperSignal.includes('IMPROVING')) {
      return {
        bgColor: 'bg-green-600',
        pulseClass: 'animate-pulse'
      };
    } else if (upperSignal.includes('WARNING') || upperSignal.includes('DEGRADATION')) {
      return {
        bgColor: 'bg-red-600',
        pulseClass: 'animate-pulse'
      };
    } else if (upperSignal.includes('MAINTAIN') || upperSignal.includes('STABLE')) {
      return {
        bgColor: 'bg-blue-600',
        pulseClass: ''
      };
    } else {
      return {
        bgColor: 'bg-gray-600',
        pulseClass: ''
      };
    }
  };

  const { bgColor, pulseClass } = getSignalStyles();

  return (
    <div className="bg-[#1F2937] rounded-xl p-4 h-full flex flex-col justify-between shadow-xl hover:shadow-2xl transition-shadow duration-300">
      {/* Label - Consistent Typography */}
      <div className="text-[#D4D4D4] text-sm uppercase tracking-wider text-center font-medium mb-2">
        Race Pace
      </div>
      
      <div className={`
        ${bgColor} 
        ${pulseClass}
        rounded-lg 
        p-4 
        flex-grow 
        flex 
        items-center 
        justify-center
        text-center
      `}>
        {/* Signal Message - Consistent Typography */}
        <div className="text-white text-2xl font-bold leading-tight break-words uppercase">
          {signal}
        </div>
      </div>
    </div>
  );
};

export default LapSignalBox;