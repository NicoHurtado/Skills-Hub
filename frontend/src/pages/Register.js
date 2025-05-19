import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiArrowLeft, FiUser, FiLock, FiMail } from 'react-icons/fi';
import { useAuth } from '../hooks/useAuth';

const Register = () => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: ''
  });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);
  
  const { register, isAuthenticated, error: authError } = useAuth();
  const navigate = useNavigate();
  
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);
  
  useEffect(() => {
    if (authError) {
      setError(authError);
      setIsSubmitting(false);
    }
  }, [authError]);
  
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };
  
  const validateForm = () => {
    if (!formData.username.trim()) {
      setError('El nombre de usuario es obligatorio');
      return false;
    }
    
    if (!formData.email.trim()) {
      setError('El correo electrónico es obligatorio');
      return false;
    }
    
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(formData.email)) {
      setError('Por favor, ingresa un correo electrónico válido');
      return false;
    }
    
    if (!formData.password.trim()) {
      setError('La contraseña es obligatoria');
      return false;
    }
    
    if (formData.password.length < 6) {
      setError('La contraseña debe tener al menos 6 caracteres');
      return false;
    }
    
    if (formData.password !== formData.confirmPassword) {
      setError('Las contraseñas no coinciden');
      return false;
    }
    
    return true;
  };
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    setError('');
    setIsSubmitting(true);
    
    const success = await register(formData.username, formData.email, formData.password);
    
    if (success) {
      setSuccess(true);
      setTimeout(() => {
        navigate('/login');
      }, 2000);
    } else {
      setIsSubmitting(false);
    }
  };

  // Variantes para animaciones
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: { 
      opacity: 1,
      transition: { 
        duration: 0.6,
        when: "beforeChildren",
        staggerChildren: 0.15
      }
    }
  };
  
  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: { 
      y: 0, 
      opacity: 1,
      transition: { 
        type: "spring",
        stiffness: 300,
        damping: 24
      }
    }
  };

  // Variantes para el botón
  const buttonVariants = {
    rest: { scale: 1 },
    hover: { scale: 1.02, boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)" },
    tap: { scale: 0.98 }
  };
  
  return (
    <div className="min-h-screen bg-gradient-to-b from-blue-50 to-white flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <motion.div 
        initial="hidden"
        animate="visible"
        variants={containerVariants}
        className="sm:mx-auto sm:w-full sm:max-w-md"
      >
        <motion.div variants={itemVariants} className="flex justify-center">
          <Link to="/" className="flex items-center text-primary-600 hover:text-primary-700 transition-colors duration-300">
            <FiArrowLeft className="mr-2" />
            <span>Volver al inicio</span>
          </Link>
        </motion.div>
        <motion.h2 
          variants={itemVariants} 
          className="mt-6 text-center text-3xl font-bold text-neutral-900"
        >
          Crea tu cuenta
        </motion.h2>
        <motion.p 
          variants={itemVariants} 
          className="mt-2 text-center text-sm text-neutral-600"
        >
          ¿Ya tienes una cuenta?{' '}
          <Link to="/login" className="font-medium text-primary-600 hover:text-primary-500 transition-colors duration-300">
            Inicia sesión
          </Link>
        </motion.p>
      </motion.div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.5, delay: 0.2 }}
          className="bg-white py-8 px-8 rounded-3xl shadow-lg"
        >
          {error && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 bg-red-50 border-l-4 border-red-500 text-red-700 p-4 rounded-lg"
              role="alert"
            >
              <span>{error}</span>
            </motion.div>
          )}
          
          {success && (
            <motion.div 
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="mb-6 bg-green-50 border-l-4 border-green-500 text-green-700 p-4 rounded-lg"
              role="alert"
            >
              <span>Registro exitoso. Redirigiendo al inicio de sesión...</span>
            </motion.div>
          )}
          
          <form className="space-y-5" onSubmit={handleSubmit}>
            <motion.div variants={itemVariants}>
              <label htmlFor="username" className="block text-sm font-medium text-neutral-700 mb-1">
                Nombre de usuario
              </label>
              <div className="relative">
                <motion.div 
                  className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
                  whileHover={{ scale: 1.1 }}
                >
                  <FiUser className="h-5 w-5 text-neutral-400" />
                </motion.div>
                <motion.input
                  whileFocus={{ boxShadow: "0 0 0 2px rgba(14, 165, 233, 0.3)" }}
                  id="username"
                  name="username"
                  type="text"
                  autoComplete="username"
                  required
                  value={formData.username}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-3 text-neutral-900 placeholder-neutral-400 bg-neutral-50 rounded-xl focus:outline-none focus:ring-primary-500 transition-shadow duration-200"
                  placeholder="Elige un nombre de usuario"
                />
              </div>
            </motion.div>

            <motion.div variants={itemVariants}>
              <label htmlFor="email" className="block text-sm font-medium text-neutral-700 mb-1">
                Correo electrónico
              </label>
              <div className="relative">
                <motion.div 
                  className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
                  whileHover={{ scale: 1.1 }}
                >
                  <FiMail className="h-5 w-5 text-neutral-400" />
                </motion.div>
                <motion.input
                  whileFocus={{ boxShadow: "0 0 0 2px rgba(14, 165, 233, 0.3)" }}
                  id="email"
                  name="email"
                  type="email"
                  autoComplete="email"
                  required
                  value={formData.email}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-3 text-neutral-900 placeholder-neutral-400 bg-neutral-50 rounded-xl focus:outline-none focus:ring-primary-500 transition-shadow duration-200"
                  placeholder="ejemplo@correo.com"
                />
              </div>
            </motion.div>

            <motion.div variants={itemVariants}>
              <label htmlFor="password" className="block text-sm font-medium text-neutral-700 mb-1">
                Contraseña
              </label>
              <div className="relative">
                <motion.div 
                  className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
                  whileHover={{ scale: 1.1 }}
                >
                  <FiLock className="h-5 w-5 text-neutral-400" />
                </motion.div>
                <motion.input
                  whileFocus={{ boxShadow: "0 0 0 2px rgba(14, 165, 233, 0.3)" }}
                  id="password"
                  name="password"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={formData.password}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-3 text-neutral-900 placeholder-neutral-400 bg-neutral-50 rounded-xl focus:outline-none focus:ring-primary-500 transition-shadow duration-200"
                  placeholder="Mínimo 6 caracteres"
                />
              </div>
            </motion.div>

            <motion.div variants={itemVariants}>
              <label htmlFor="confirmPassword" className="block text-sm font-medium text-neutral-700 mb-1">
                Confirmar contraseña
              </label>
              <div className="relative">
                <motion.div 
                  className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none"
                  whileHover={{ scale: 1.1 }}
                >
                  <FiLock className="h-5 w-5 text-neutral-400" />
                </motion.div>
                <motion.input
                  whileFocus={{ boxShadow: "0 0 0 2px rgba(14, 165, 233, 0.3)" }}
                  id="confirmPassword"
                  name="confirmPassword"
                  type="password"
                  autoComplete="new-password"
                  required
                  value={formData.confirmPassword}
                  onChange={handleChange}
                  className="block w-full pl-10 pr-3 py-3 text-neutral-900 placeholder-neutral-400 bg-neutral-50 rounded-xl focus:outline-none focus:ring-primary-500 transition-shadow duration-200"
                  placeholder="Repite tu contraseña"
                />
              </div>
            </motion.div>

            <motion.div variants={itemVariants} className="pt-2">
              <motion.button
                variants={buttonVariants}
                initial="rest"
                whileHover="hover"
                whileTap="tap"
                type="submit"
                disabled={isSubmitting || success}
                className={`w-full flex justify-center py-3 px-4 border border-transparent rounded-xl text-white font-medium bg-gradient-to-r from-primary-500 to-primary-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition-all ${(isSubmitting || success) ? 'opacity-75 cursor-not-allowed' : ''}`}
              >
                {isSubmitting ? (
                  <div className="flex items-center justify-center">
                    <div className="animate-spin rounded-full h-5 w-5 border-t-2 border-b-2 border-white mr-2"></div>
                    <span>Creando cuenta...</span>
                  </div>
                ) : (
                  'Registrarse'
                )}
              </motion.button>
            </motion.div>
          </form>
        </motion.div>
      </div>
    </div>
  );
};

export default Register; 