import React, { useEffect, useState, useRef } from 'react';

const TextScramble = ({ text, delay = 0, duration = 2000, className }) => {
  const [output, setOutput] = useState('');
  const [isAnimating, setIsAnimating] = useState(false);
  const timeoutRef = useRef(null);
  
  const chars = '!<>-_\\/[]{}—=+*^?#_abcdefghijklmnopqrstuvwxyz';
  
  useEffect(() => {
    if (timeoutRef.current) clearTimeout(timeoutRef.current);
    
    timeoutRef.current = setTimeout(() => {
      scramble();
    }, delay);
    
    return () => {
      if (timeoutRef.current) clearTimeout(timeoutRef.current);
    };
  }, [text, delay]);
  
  const scramble = () => {
    setIsAnimating(true);
    
    let iteration = 0;
    const finalText = text;
    const maxIterations = 30;
    const frameRate = Math.floor(duration / maxIterations);
    
    const updateText = () => {
      if (iteration >= maxIterations) {
        setOutput(finalText);
        setIsAnimating(false);
        return;
      }
      
      const progress = iteration / maxIterations;
      const completeLength = Math.floor(finalText.length * progress);
      
      let outputText = '';
      for (let i = 0; i < finalText.length; i++) {
        if (i < completeLength) {
          outputText += finalText[i];
        } else if (finalText[i] === ' ') {
          outputText += ' ';
        } else {
          outputText += chars[Math.floor(Math.random() * chars.length)];
        }
      }
      
      setOutput(outputText);
      iteration++;
      
      setTimeout(updateText, frameRate);
    };
    
    updateText();
  };
  
  return (
    <span className={className}>
      {output || text}
    </span>
  );
};

export default TextScramble; 