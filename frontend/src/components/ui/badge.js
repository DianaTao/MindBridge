import React from 'react';

export const Badge = ({ children, className = '', variant = 'default', ...props }) => {
  const baseClasses =
    "inline-flex items-center px-3 py-1 rounded-full text-sm font-medium font-['Courier_New']";

  const variants = {
    default: 'bg-gradient-to-r from-blue-400 to-indigo-600 text-white shadow-lg shadow-blue-500/25',
    success:
      'bg-gradient-to-r from-green-400 to-emerald-600 text-white shadow-lg shadow-green-500/25',
    warning:
      'bg-gradient-to-r from-yellow-400 to-orange-500 text-black shadow-lg shadow-yellow-500/25',
    error: 'bg-gradient-to-r from-red-500 to-pink-600 text-white shadow-lg shadow-red-500/25',
    secondary:
      'bg-gradient-to-r from-gray-400 to-slate-500 text-white shadow-lg shadow-gray-500/25',
  };

  const variantClasses = variants[variant] || variants.default;

  return (
    <span className={`${baseClasses} ${variantClasses} ${className}`} {...props}>
      {children}
    </span>
  );
};
