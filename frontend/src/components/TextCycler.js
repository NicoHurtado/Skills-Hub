import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

const TextCycler = ({ 
  texts = [], 
  interval = 3000, 
  className = '',
  textClassName = '',
  activeIndex = 0
}) => {
  const [index, setIndex] = useState(activeIndex);
  
  useEffect(() => {
    if (texts.length <= 1) return;
    
    const timer = setInterval(() => {
      setIndex((prevIndex) => (prevIndex + 1) % texts.length);
    }, interval);
    
    return () => clearInterval(timer);
  }, [texts, interval]);
  
  if (!texts.length) return null;
  
  return (
    <div className={`relative ${className}`} style={{ minHeight: '1.5em' }}>
      <AnimatePresence mode="wait">
        <motion.div
          key={index}
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: -30 }}
          transition={{ 
            y: { type: 'spring', stiffness: 200, damping: 30 },
            opacity: { duration: 0.3 }
          }}
          style={{ 
            display: 'block', 
            width: '100%',
            textShadow: '0 0 10px rgba(56, 189, 248, 0.5)'
          }}
          className={`${textClassName}`}
        >
          {texts[index]}
        </motion.div>
      </AnimatePresence>
    </div>
  );
};

export default TextCycler; 