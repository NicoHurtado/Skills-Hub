import React from 'react';
import { motion } from 'framer-motion';

const BackgroundGrid = ({ 
  className = '', 
  dotSize = 1,
  dotSpacing = 20,
  dotColor = 'rgba(80, 80, 220, 0.15)',
  animated = true
}) => {
  // Calculate the number of dots needed based on spacing
  const calculateDots = () => {
    if (typeof window === 'undefined') return { rows: 30, cols: 50 };
    
    const width = window.innerWidth;
    const height = window.innerHeight;
    
    const cols = Math.ceil(width / dotSpacing) + 1;
    const rows = Math.ceil(height / dotSpacing) + 1;
    
    return { rows, cols };
  };
  
  const { rows, cols } = calculateDots();
  
  const renderDots = () => {
    const dots = [];
    
    for (let row = 0; row < rows; row++) {
      for (let col = 0; col < cols; col++) {
        const key = `${row}-${col}`;
        const x = col * dotSpacing;
        const y = row * dotSpacing;
        
        const delayFactor = (row + col) * 0.01;
        
        if (animated) {
          dots.push(
            <motion.circle
              key={key}
              cx={x}
              cy={y}
              r={dotSize}
              fill={dotColor}
              initial={{ opacity: 0, scale: 0 }}
              animate={{ 
                opacity: 1, 
                scale: [0, 1.5, 1],
              }}
              transition={{ 
                duration: 2, 
                delay: delayFactor,
                ease: "easeOut" 
              }}
            />
          );
        } else {
          dots.push(
            <circle
              key={key}
              cx={x}
              cy={y}
              r={dotSize}
              fill={dotColor}
            />
          );
        }
      }
    }
    
    return dots;
  };
  
  return (
    <div className={`absolute inset-0 overflow-hidden pointer-events-none ${className}`}>
      <svg 
        className="absolute w-full h-full"
        style={{ 
          minWidth: '100%', 
          minHeight: '100%',
        }}
      >
        {renderDots()}
      </svg>
    </div>
  );
};

export default BackgroundGrid; 