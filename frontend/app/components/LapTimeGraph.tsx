import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface LapData {
  lap: number;
  time: number;
}

interface LapTimeGraphProps {
  lapData: LapData[];
}

const LapTimeGraph: React.FC<LapTimeGraphProps> = ({ lapData }) => {
  return (
    <div className="bg-[#515151] rounded-lg p-6 h-full flex flex-col">
      <div className="text-[#D4D4D4] text-2xl mb-4">Lap Times</div>
      <ResponsiveContainer width="100%" height="100%">
        <LineChart
          data={lapData}
          margin={{
            top: 20,
            right: 30,
            left: 20,
            bottom: 20,
          }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="#444" />
          <XAxis 
            dataKey="lap" 
            stroke="#D4D4D4" 
            tick={{ fill: '#D4D4D4' }}
            fontSize={14}
          />
          <YAxis 
            stroke="#D4D4D4" 
            tick={{ fill: '#D4D4D4' }}
            fontSize={14}
          />
          <Tooltip 
            contentStyle={{ backgroundColor: '#333', borderColor: '#666' }}
            labelStyle={{ color: '#D4D4D4' }}
            itemStyle={{ color: '#D4D4D4' }}
          />
          <Line 
            type="monotone" 
            dataKey="time" 
            stroke="#00a2ff" 
            strokeWidth={3}
            activeDot={{ r: 8 }} 
            name="Lap Time (sec)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default LapTimeGraph;