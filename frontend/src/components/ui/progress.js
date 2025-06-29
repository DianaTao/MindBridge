import React from 'react';

export const Progress = ({ 
  value = 0, 
  className = "", 
  max = 100,
  showLabel = false,
  ...props 
}) => {
  const percentage = Math.min(Math.max((value / max) * 100, 0), 100);
  
  return (
    <div className={`w-full ${className}`} {...props}>
      <div className="w-full bg-blue-100 rounded-full h-2 overflow-hidden">
        <div 
          className="h-full bg-gradient-to-r from-cyan-400 to-blue-500 rounded-full transition-all duration-300 ease-out"
          style={{ width: `${percentage}%` }}
        />
      </div>
      {showLabel && (
        <div className="flex justify-between items-center mt-2">
          <span className="text-slate-600 text-sm font-['Courier_New']">Progress</span>
          <span className="text-slate-800 font-bold text-sm font-['Courier_New']">
            {Math.round(percentage)}%
          </span>
        </div>
      )}
    </div>
  );
}; 