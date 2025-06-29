import React from 'react';

export const Select = ({ 
  children, 
  className = "", 
  value = "",
  onChange,
  disabled = false,
  ...props 
}) => {
  const baseClasses = "w-full px-4 py-3 rounded-2xl border border-blue-200/50 bg-white/80 backdrop-blur-xl text-slate-800 font-['Courier_New'] focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all duration-300 appearance-none";
  const disabledClasses = disabled ? "opacity-50 cursor-not-allowed" : "hover:border-blue-300 cursor-pointer";
  
  return (
    <div className="relative">
      <select
        className={`${baseClasses} ${disabledClasses} ${className}`}
        value={value}
        onChange={onChange}
        disabled={disabled}
        {...props}
      >
        {children}
      </select>
      <div className="absolute inset-y-0 right-0 flex items-center pr-3 pointer-events-none">
        <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </div>
    </div>
  );
};

export const SelectTrigger = ({ children, className = "", ...props }) => (
  <div className={`w-full px-4 py-3 rounded-2xl border border-blue-200/50 bg-white/80 backdrop-blur-xl text-slate-800 font-['Courier_New'] focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all duration-300 cursor-pointer flex items-center justify-between ${className}`} {...props}>
    {children}
    <svg className="w-5 h-5 text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
    </svg>
  </div>
);

export const SelectContent = ({ children, className = "", ...props }) => (
  <div className={`absolute top-full left-0 right-0 mt-1 bg-white border border-blue-200/50 rounded-2xl shadow-xl z-50 max-h-60 overflow-y-auto ${className}`} {...props}>
    {children}
  </div>
);

export const SelectValue = ({ placeholder = "Select an option", ...props }) => (
  <span className="text-slate-800 font-['Courier_New']" {...props}>
    {placeholder}
  </span>
);

export const SelectItem = ({ children, value, className = "", ...props }) => (
  <div 
    className={`px-4 py-3 hover:bg-blue-50 cursor-pointer font-['Courier_New'] ${className}`} 
    data-value={value}
    {...props}
  >
    {children}
  </div>
); 