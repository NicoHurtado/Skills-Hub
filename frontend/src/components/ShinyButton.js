import React, { useState, useRef, useEffect } from 'react';
import { motion } from 'framer-motion';

const ShinyButton = ({ 
  children, 
  onClick,
  className = '',
  primary = true,
  disabled = false
}) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovered, setIsHovered] = useState(false);
  const buttonRef = useRef(null);
  
  const baseClass = `relative overflow-hidden inline-flex items-center justify-center px-4 py-2 
                     rounded-xl font-medium shadow-sm focus:outline-none focus:ring-2 focus:ring-offset-2 
                     transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed`;
  
  const primaryClass = `bg-primary-600 text-white hover:bg-primary-700 focus:ring-primary-500`;
  const secondaryClass = `bg-white text-neutral-700 border border-neutral-300 hover:bg-neutral-50 focus:ring-primary-500`;
  
  const colorClass = primary ? primaryClass : secondaryClass;
  
  const handleMouseMove = (e) => {
    if (!buttonRef.current || disabled) return;
    
    const rect = buttonRef.current.getBoundingClientRect();
    setMousePosition({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
  };
  
  useEffect(() => {
    if (!isHovered || !buttonRef.current) return;
    
    const rect = buttonRef.current.getBoundingClientRect();
    setMousePosition({
      x: rect.width / 2,
      y: rect.height / 2
    });
  }, [isHovered]);
  
  return (
    <motion.button
      ref={buttonRef}
      onClick={onClick}
      disabled={disabled}
      className={`${baseClass} ${colorClass} ${className}`}
      whileTap={{ scale: 0.98 }}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {children}
      
      {isHovered && !disabled && (
        <motion.div 
          className="absolute top-0 left-0 w-full h-full pointer-events-none"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <div 
            className="absolute bg-white/30 rounded-full mix-blend-overlay"
            style={{
              left: mousePosition.x,
              top: mousePosition.y,
              transform: 'translate(-50%, -50%)',
              width: '150%',
              height: '150%',
              filter: 'blur(40px)',
              opacity: 0.8,
            }}
          />
          <div 
            className="absolute bg-white rounded-full"
            style={{
              left: mousePosition.x,
              top: mousePosition.y,
              transform: 'translate(-50%, -50%)',
              width: '10%',
              height: '10%',
              filter: 'blur(10px)',
              opacity: 0.6,
            }}
          />
        </motion.div>
      )}
    </motion.button>
  );
};

export default ShinyButton; 