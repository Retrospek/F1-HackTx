import React from 'react';

interface EnginePowerBoxProps {
  usage: string;
}

const EnginePowerBox: React.FC<EnginePowerBoxProps> = ({ usage }) => {
  return (
    <div className="bg-[#1F2937] rounded-xl p-4 text-center h-full flex flex-col justify-between shadow-xl hover:shadow-2xl transition-shadow duration-300">
      {/* Label - Consistent Typography */}
      <div className="text-[#D4D4D4] text-sm uppercase tracking-wider font-medium mb-2">
        Engine Power Usage
      </div>
      
      {/* Primary Value */}
      <div className="flex-grow flex items-center justify-center">
        <div className="text-white text-6xl font-bold">
          {usage}
        </div>
      </div>
    </div>
  );
};

export default EnginePowerBox;