import React, { useContext } from 'react';
import { motion } from 'framer-motion';
import { FiSun, FiMoon } from 'react-icons/fi';
import { ThemeContext } from '../context/ThemeContext';

const ThemeToggle = ({ className = '' }) => {
  const { darkMode, toggleDarkMode } = useContext(ThemeContext);

  // Variantes para la animación del icono
  const iconVariants = {
    initial: { opacity: 0, y: 10, scale: 0.8 },
    animate: { opacity: 1, y: 0, scale: 1 },
    exit: { opacity: 0, y: -10, scale: 0.8 }
  };

  // Variantes para la animación de la bolita
  const thumbVariants = {
    dark: { x: 24, backgroundColor: '#fff' },
    light: { x: 4, backgroundColor: '#fff' }
  };

  // Variantes para el fondo del toggle
  const toggleVariants = {
    dark: { backgroundColor: '#0284c7' },
    light: { backgroundColor: '#e5e5e5' }
  };

  return (
    <div className={`flex items-center ${className}`}>
      <motion.button
        type="button"
        initial={false}
        animate={darkMode ? 'dark' : 'light'}
        variants={toggleVariants}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        className="relative inline-flex h-6 w-11 items-center rounded-full focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2"
        onClick={toggleDarkMode}
        aria-label={darkMode ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
      >
        <span className="sr-only">
          {darkMode ? 'Cambiar a modo claro' : 'Cambiar a modo oscuro'}
        </span>
        <motion.span
          layout
          variants={thumbVariants}
          transition={{ type: 'spring', stiffness: 700, damping: 30 }}
          className="pointer-events-none absolute inline-block h-4 w-4 transform rounded-full shadow-lg"
        />
      </motion.button>
      
      <div className="relative ml-2 w-5 h-5">
        {darkMode ? (
          <motion.div
            key="moon-icon"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={iconVariants}
            transition={{ duration: 0.2 }}
          >
            <FiMoon className="text-primary-400" size={18} />
          </motion.div>
        ) : (
          <motion.div
            key="sun-icon"
            initial="initial"
            animate="animate"
            exit="exit"
            variants={iconVariants}
            transition={{ duration: 0.2 }}
          >
            <FiSun className="text-yellow-500" size={18} />
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default ThemeToggle; 