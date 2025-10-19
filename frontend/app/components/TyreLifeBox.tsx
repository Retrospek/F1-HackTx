import React from 'react';

interface TyreLifeBoxProps {
  expectedLifeTime: string;
}

const TyreLifeBox: React.FC<TyreLifeBoxProps> = ({ expectedLifeTime }) => {
  return (
    <div className="bg-[#1F2937] rounded-xl p-4 text-center h-full flex flex-col justify-center shadow-xl hover:shadow-2xl transition-shadow duration-300">
      <div className="text-[#D4D4D4] text-lg mb-2 uppercase tracking-wider">
        Tyre Life
      </div>
      <div className="text-white text-6xl font-bold">
        {expectedLifeTime}
      </div>
    </div>
  );
};

export default TyreLifeBox;