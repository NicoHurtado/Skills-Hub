import React, { useState, useContext } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiCpu, FiArrowRight, FiCheck, FiInfo } from 'react-icons/fi';
import Layout from '../components/Layout';
import SubscriptionModal from '../components/SubscriptionModal';
import { courseService } from '../services/api';
import axios from 'axios';
import { ThemeContext } from '../context/ThemeContext';

const experienceLevels = [
  { id: 'beginner', name: 'Principiante', description: 'Poco o ningún conocimiento previo.' },
  { id: 'intermediate', name: 'Intermedio', description: 'Conceptos básicos y algo de experiencia.' },
  { id: 'advanced', name: 'Avanzado', description: 'Amplio conocimiento y experiencia.' },
];

const timeDurations = [
  { id: '1hour', name: '1 hora', description: 'Curso rápido, conceptos clave.' },
  { id: '1day', name: '1 día', description: 'Curso de medio día, más detallado.' },
  { id: '1week', name: '1 semana', description: 'Curso completo con prácticas.' },
  { id: '1month', name: '1 mes', description: 'Curso exhaustivo y en profundidad.' },
];

const CourseGenerator = () => {
  const navigate = useNavigate();
  const { darkMode } = useContext(ThemeContext);
  
  const [topic, setTopic] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [availableTime, setAvailableTime] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  
  // Estados para el modal de suscripción
  const [showSubscriptionModal, setShowSubscriptionModal] = useState(false);
  const [availablePlans, setAvailablePlans] = useState([]);
  const [currentTier, setCurrentTier] = useState('free');
  
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!topic.trim()) {
      setError('Por favor, ingresa un tema para el curso');
      return;
    }
    
    if (!experienceLevel) {
      setError('Por favor, selecciona tu nivel de experiencia');
      return;
    }
    
    if (!availableTime) {
      setError('Por favor, selecciona el tiempo disponible');
      return;
    }
    
    setError('');
    setIsGenerating(true);
    
    try {
      // Get the name for the selected level and time
      const levelName = experienceLevels.find(level => level.id === experienceLevel)?.name || experienceLevel;
      const timeName = timeDurations.find(time => time.id === availableTime)?.name || availableTime;
      
      const result = await courseService.generateCourse(
        topic,
        levelName,
        timeName
      );
      
      // Save the course
      const courseData = {
        title: result.title,
        prompt: topic,
        content: result,
        experience_level: levelName,
        available_time: timeName
      };
      
      const savedCourse = await courseService.saveCourse(courseData);
      
      // Redirect to the course view page
      navigate(`/courses/${savedCourse.id}`);
    } catch (error) {
      console.error('Error generating course:', error);
      
      // Verificar si es un error de límite de suscripción
      if (error && error.isSubscriptionLimitError) {
        setAvailablePlans(error.available_plans || []);
        setCurrentTier(error.current_tier || 'free');
        setShowSubscriptionModal(true);
        setError('Has alcanzado el límite de cursos de tu plan actual.');
      } else {
        setError('Error al generar el curso. Por favor, intenta de nuevo.');
      }
      setIsGenerating(false);
    }
  };
  
  const handleSelectPlan = async (plan) => {
    try {
      // Aquí implementarías la lógica para suscribirse al plan
      const API_URL = 'http://localhost:8000';
      const token = localStorage.getItem('token');
      
      const response = await axios.post(`${API_URL}/subscribe`, 
        { tier_id: plan.id },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Cerrar el modal y mostrar un mensaje de éxito
      setShowSubscriptionModal(false);
      setError('');
      alert(`¡Te has suscrito al plan ${plan.name}! Ahora puedes crear hasta ${plan.course_limit === -1 ? 'ilimitados' : plan.course_limit} cursos.`);
      
      // Opcionalmente, intentar generar el curso nuevamente
      // handleSubmit(new Event('submit'));
    } catch (err) {
      console.error('Error al suscribirse:', err);
      setError('Error al procesar la suscripción. Por favor, intenta de nuevo.');
    }
  };

  // Clases dinámicas basadas en el tema
  const titleClass = darkMode ? 'text-white' : 'text-neutral-900';
  const subtitleClass = darkMode ? 'text-white' : 'text-neutral-900';
  const labelClass = darkMode ? 'text-white' : 'text-neutral-700';
  const hintTextClass = darkMode ? 'text-neutral-300' : 'text-neutral-500';
  
  // Clases para las tarjetas de selección
  const cardSelectedClass = darkMode 
    ? 'border-primary-500 bg-primary-900/30 ring-2 ring-primary-700'
    : 'border-primary-500 bg-primary-50 ring-2 ring-primary-200';
  
  const cardUnselectedClass = darkMode
    ? 'border-neutral-700 hover:border-primary-500'
    : 'border-neutral-200 hover:border-primary-300';
  
  // Clases para los textos en las tarjetas
  const cardTitleClass = darkMode ? 'text-white' : 'text-neutral-900';
  const cardDescriptionClass = darkMode ? 'text-neutral-300' : 'text-neutral-600';
  
  // Clase para los círculos numerados
  const circleClass = darkMode 
    ? 'flex items-center justify-center bg-primary-700 text-white w-8 h-8 rounded-full mr-3'
    : 'flex items-center justify-center bg-primary-100 text-primary-700 w-8 h-8 rounded-full mr-3';
  
  return (
    <Layout>
      <div className="max-w-3xl mx-auto">
        <h1 className={`text-2xl font-bold ${titleClass} mb-6`}>Generar curso</h1>
        
        {error && (
          <div className={`mb-6 ${darkMode 
            ? 'bg-red-900/20 border-red-800/30 text-red-400' 
            : 'bg-red-50 border-red-200 text-red-700'} 
            border px-4 py-3 rounded-lg`} role="alert">
            <span>{error}</span>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Topic section */}
          <div className="card">
            <h2 className={`text-lg font-medium ${subtitleClass} mb-4 flex items-center`}>
              <span className={circleClass}>1</span>
              ¿Qué quieres aprender?
            </h2>
            
            <div>
              <label htmlFor="topic" className={`block text-sm font-medium ${labelClass} mb-1`}>
                Tema o habilidad
              </label>
              <textarea
                id="topic"
                name="topic"
                rows={3}
                className="input"
                placeholder="Describe el tema que quieres aprender. Sé específico para obtener mejores resultados."
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
              />
              <p className={`mt-2 text-sm ${hintTextClass}`}>
                <FiInfo className="inline mr-1" />
                Ejemplos: "Programación en Python para análisis de datos", "Marketing digital para pequeños negocios"
              </p>
            </div>
          </div>
          
          {/* Experience level section */}
          <div className="card">
            <h2 className={`text-lg font-medium ${subtitleClass} mb-4 flex items-center`}>
              <span className={circleClass}>2</span>
              ¿Cuál es tu nivel de experiencia?
            </h2>
            
            <div className="grid gap-4 sm:grid-cols-3">
              {experienceLevels.map((level) => (
                <div 
                  key={level.id}
                  className={`border rounded-xl p-4 cursor-pointer transition-all duration-200 ${
                    experienceLevel === level.id 
                      ? cardSelectedClass
                      : cardUnselectedClass
                  }`}
                  onClick={() => setExperienceLevel(level.id)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className={`font-medium ${cardTitleClass}`}>{level.name}</h3>
                    {experienceLevel === level.id && (
                      <FiCheck className="text-primary-400" />
                    )}
                  </div>
                  <p className={`text-sm ${cardDescriptionClass}`}>{level.description}</p>
                </div>
              ))}
            </div>
          </div>
          
          {/* Time duration section */}
          <div className="card">
            <h2 className={`text-lg font-medium ${subtitleClass} mb-4 flex items-center`}>
              <span className={circleClass}>3</span>
              ¿Cuánto tiempo tienes disponible?
            </h2>
            
            <div className="grid gap-4 sm:grid-cols-2">
              {timeDurations.map((time) => (
                <div 
                  key={time.id}
                  className={`border rounded-xl p-4 cursor-pointer transition-all duration-200 ${
                    availableTime === time.id 
                      ? cardSelectedClass
                      : cardUnselectedClass
                  }`}
                  onClick={() => setAvailableTime(time.id)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className={`font-medium ${cardTitleClass}`}>{time.name}</h3>
                    {availableTime === time.id && (
                      <FiCheck className="text-primary-400" />
                    )}
                  </div>
                  <p className={`text-sm ${cardDescriptionClass}`}>{time.description}</p>
                </div>
              ))}
            </div>
          </div>
          
          {/* Submit button */}
          <div className="flex justify-end">
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              type="submit"
              disabled={isGenerating}
              className={`btn btn-primary py-3 px-6 ${isGenerating ? 'opacity-75 cursor-not-allowed' : ''}`}
            >
              {isGenerating ? (
                <div className="flex items-center">
                  <FiCpu className="animate-pulse mr-2" />
                  <span>Generando curso...</span>
                </div>
              ) : (
                <div className="flex items-center">
                  <span>Generar curso</span>
                  <FiArrowRight className="ml-2" />
                </div>
              )}
            </motion.button>
          </div>
        </form>
        
        {/* Modal de suscripción */}
        <SubscriptionModal 
          isOpen={showSubscriptionModal} 
          onClose={() => setShowSubscriptionModal(false)} 
          plans={availablePlans}
          onSelectPlan={handleSelectPlan}
          currentTier={currentTier}
        />
      </div>
    </Layout>
  );
};

export default CourseGenerator; 