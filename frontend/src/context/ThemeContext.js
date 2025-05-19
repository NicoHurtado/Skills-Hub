import React, { createContext, useState, useEffect } from 'react';

export const ThemeContext = createContext();

export const ThemeProvider = ({ children }) => {
  // Estado para el tema
  const [darkMode, setDarkMode] = useState(() => {
    // Verificar si hay un tema guardado en localStorage
    const savedTheme = localStorage.getItem('theme');
    // También verificar la preferencia del sistema
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches;
    
    // Si hay un tema guardado, usarlo; si no, usar la preferencia del sistema
    if (savedTheme) {
      return savedTheme === 'dark';
    } else {
      return prefersDark;
    }
  });

  // Cambiar entre tema oscuro y claro
  const toggleDarkMode = () => {
    setDarkMode(prevMode => !prevMode);
  };

  // Función para establecer el tema específicamente
  const setTheme = (isDark) => {
    setDarkMode(isDark);
  };

  // Observar cambios en la preferencia del sistema
  useEffect(() => {
    const mediaQuery = window.matchMedia('(prefers-color-scheme: dark)');
    const handleChange = () => {
      // Solo cambiar automáticamente si el usuario no ha establecido una preferencia
      if (!localStorage.getItem('theme')) {
        setDarkMode(mediaQuery.matches);
      }
    };
    
    mediaQuery.addEventListener('change', handleChange);
    return () => mediaQuery.removeEventListener('change', handleChange);
  }, []);

  // Aplicar el tema cuando cambie
  useEffect(() => {
    const theme = darkMode ? 'dark' : 'light';
    localStorage.setItem('theme', theme);
    
    // Aplicar la clase al elemento html para que los estilos se apliquen globalmente
    if (darkMode) {
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
    }
  }, [darkMode]);

  return (
    <ThemeContext.Provider value={{ darkMode, toggleDarkMode, setTheme }}>
      {children}
    </ThemeContext.Provider>
  );
}; 