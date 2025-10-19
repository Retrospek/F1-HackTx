import React from 'react';

interface TyreLifeProps {
  expectedLifeTime?: string;
}

const TyreLifeBox: React.FC<TyreLifeProps> = ({ 
  expectedLifeTime = 'N/A' 
}) => {
  return (
    <div className="bg-[#515151] rounded-lg p-6 h-full flex flex-col justify-center">
      <div className="text-[#D4D4D4] text-xl mb-4">Tyre Expected Life Time</div>
      <div className="text-[#D4D4D4] text-6xl font-bold text-center">
        {expectedLifeTime}
      </div>
    </div>
  );
};

export default TyreLifeBox;