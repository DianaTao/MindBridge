import React from 'react';

export const Input = ({
  className = '',
  type = 'text',
  placeholder = '',
  value = '',
  onChange,
  disabled = false,
  ...props
}) => {
  const baseClasses =
    "w-full px-4 py-3 rounded-2xl border border-blue-200/50 bg-white/80 backdrop-blur-xl text-slate-800 font-['Courier_New'] placeholder-slate-500 focus:outline-none focus:ring-2 focus:ring-blue-500/50 focus:border-blue-500 transition-all duration-300";
  const disabledClasses = disabled ? 'opacity-50 cursor-not-allowed' : 'hover:border-blue-300';

  return (
    <input
      type={type}
      className={`${baseClasses} ${disabledClasses} ${className}`}
      placeholder={placeholder}
      value={value}
      onChange={onChange}
      disabled={disabled}
      {...props}
    />
  );
};
