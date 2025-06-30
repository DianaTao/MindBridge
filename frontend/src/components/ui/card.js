import React from 'react';

export const Card = ({ children, className = "", ...props }) => (
  <div 
    className={`bg-white/90 backdrop-blur-xl border border-blue-200/50 rounded-3xl shadow-2xl shadow-blue-500/20 overflow-hidden ${className}`}
    {...props}
  >
    {children}
  </div>
);

export const CardContent = ({ children, className = "", ...props }) => (
  <div className={`p-6 relative ${className}`} {...props}>
    {children}
  </div>
);

export const CardHeader = ({ children, className = "", ...props }) => (
  <div className={`p-6 pb-0 ${className}`} {...props}>
    {children}
  </div>
);

export const CardTitle = ({ children, className = "", ...props }) => (
  <h3 className={`text-xl font-bold text-slate-800 font-['Courier_New'] ${className}`} {...props}>
    {children}
  </h3>
);

export const CardDescription = ({ children, className = "", ...props }) => (
  <p className={`text-slate-600 text-sm font-['Courier_New'] ${className}`} {...props}>
    {children}
  </p>
); 