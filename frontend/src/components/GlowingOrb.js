import React from 'react';
import { motion } from 'framer-motion';

const GlowingOrb = ({ 
  size = 300,
  color = 'primary',
  intensity = 1,
  className
}) => {
  // Map color to appropriate tailwind class
  const colorMap = {
    primary: 'from-primary-400 to-primary-600',
    blue: 'from-blue-400 to-blue-600',
    purple: 'from-purple-400 to-purple-600',
    cyan: 'from-cyan-400 to-cyan-600',
    pink: 'from-pink-400 to-pink-600',
  };
  
  const colorClass = colorMap[color] || colorMap.primary;
  
  return (
    <div className={`relative ${className}`} style={{ width: size, height: size }}>
      {/* Base orb */}
      <motion.div
        initial={{ scale: 0.8, opacity: 0.5 }}
        animate={{ 
          scale: [0.8, 1.1, 0.9, 1],
          opacity: [0.5, 0.8, 0.7, 0.9]
        }}
        transition={{
          duration: 8,
          repeat: Infinity,
          repeatType: 'reverse',
          ease: 'easeInOut'
        }}
        className={`absolute rounded-full bg-gradient-to-br ${colorClass}`}
        style={{ 
          width: '100%', 
          height: '100%',
          filter: `blur(${10 * intensity}px)`
        }}
      />
      
      {/* Inner glow */}
      <motion.div
        initial={{ scale: 0.6, opacity: 0.7 }}
        animate={{ 
          scale: [0.6, 0.8, 0.7, 0.8],
          opacity: [0.7, 0.9, 0.8, 1]
        }}
        transition={{
          duration: 6,
          repeat: Infinity,
          repeatType: 'reverse',
          ease: 'easeInOut',
          delay: 0.5
        }}
        className="absolute rounded-full bg-white"
        style={{ 
          width: '40%', 
          height: '40%',
          left: '30%',
          top: '30%',
          filter: `blur(${5 * intensity}px)`
        }}
      />
      
      {/* Shine effect */}
      <motion.div
        initial={{ rotate: 0, scale: 0.9 }}
        animate={{ rotate: 360, scale: [0.9, 1.1, 0.9] }}
        transition={{
          duration: 15,
          repeat: Infinity,
          ease: 'linear'
        }}
        className="absolute w-full h-full"
      >
        <div
          className="absolute rounded-full bg-white"
          style={{ 
            width: '15%', 
            height: '15%',
            left: '10%',
            top: '20%',
            filter: 'blur(8px)',
            opacity: 0.7
          }}
        />
      </motion.div>
    </div>
  );
};

export default GlowingOrb; 