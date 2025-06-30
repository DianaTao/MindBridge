import React from 'react';

export const Button = ({ 
  children, 
  onClick, 
  className = "", 
  disabled = false, 
  variant = "default",
  size = "default",
  ...props 
}) => {
  const baseClasses = "inline-flex items-center justify-center rounded-2xl font-medium font-['Courier_New'] transition-all duration-300 focus:outline-none focus:ring-2 focus:ring-offset-2";
  
  const variants = {
    default: "bg-gradient-to-r from-blue-500 to-indigo-500 hover:from-blue-600 hover:to-indigo-600 text-white border-0 shadow-xl shadow-blue-500/25",
    success: "bg-gradient-to-r from-emerald-500 to-teal-500 hover:from-emerald-600 hover:to-teal-600 text-white border-0 shadow-xl shadow-emerald-500/25",
    warning: "bg-gradient-to-r from-yellow-400 to-orange-500 hover:from-yellow-500 hover:to-orange-600 text-black border-0 shadow-xl shadow-yellow-500/25",
    error: "bg-gradient-to-r from-red-500 to-pink-500 hover:from-red-600 hover:to-pink-600 text-white border-0 shadow-xl shadow-red-500/25",
    secondary: "bg-gradient-to-r from-gray-400 to-slate-500 hover:from-gray-500 hover:to-slate-600 text-white border-0 shadow-xl shadow-gray-500/25",
    outline: "bg-transparent border-2 border-blue-500 text-blue-500 hover:bg-blue-500 hover:text-white",
  };
  
  const sizes = {
    sm: "px-4 py-2 text-sm",
    default: "px-6 py-3 text-base",
    lg: "px-8 py-4 text-lg",
  };
  
  const variantClasses = variants[variant] || variants.default;
  const sizeClasses = sizes[size] || sizes.default;
  const disabledClasses = disabled ? "opacity-50 cursor-not-allowed" : "hover:scale-105 active:scale-95";
  
  return (
    <button 
      onClick={onClick} 
      className={`${baseClasses} ${variantClasses} ${sizeClasses} ${disabledClasses} ${className}`} 
      disabled={disabled} 
      {...props}
    >
      {children}
    </button>
  );
}; 