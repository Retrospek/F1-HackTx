import React from 'react';

interface EnginePowerProps {
  usage?: string;
}

const EnginePowerBox: React.FC<EnginePowerProps> = ({ 
  usage = 'N/A' 
}) => {
  return (
    <div className="bg-[#515151] rounded-lg p-6 h-full flex flex-col justify-center">
      <div className="text-[#D4D4D4] text-xl mb-4">Engine Power Usage</div>
      <div className="text-[#D4D4D4] text-6xl font-bold text-center">
        {usage}
      </div>
    </div>
  );
};

export default EnginePowerBox;