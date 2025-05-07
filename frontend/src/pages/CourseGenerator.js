import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiCpu, FiArrowRight, FiCheck, FiInfo } from 'react-icons/fi';
import Layout from '../components/Layout';
import { courseService } from '../services/api';

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
  
  const [topic, setTopic] = useState('');
  const [experienceLevel, setExperienceLevel] = useState('');
  const [availableTime, setAvailableTime] = useState('');
  const [isGenerating, setIsGenerating] = useState(false);
  const [error, setError] = useState('');
  
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
      setError('Error al generar el curso. Por favor, intenta de nuevo.');
      setIsGenerating(false);
    }
  };
  
  return (
    <Layout>
      <div className="max-w-3xl mx-auto">
        <h1 className="text-2xl font-bold text-neutral-900 mb-6">Generar curso</h1>
        
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg" role="alert">
            <span>{error}</span>
          </div>
        )}
        
        <form onSubmit={handleSubmit} className="space-y-8">
          {/* Topic section */}
          <div className="card">
            <h2 className="text-lg font-medium text-neutral-900 mb-4 flex items-center">
              <span className="flex items-center justify-center bg-primary-100 text-primary-700 w-8 h-8 rounded-full mr-3">1</span>
              ¿Qué quieres aprender?
            </h2>
            
            <div>
              <label htmlFor="topic" className="block text-sm font-medium text-neutral-700 mb-1">
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
              <p className="mt-2 text-sm text-neutral-500">
                <FiInfo className="inline mr-1" />
                Ejemplos: "Programación en Python para análisis de datos", "Marketing digital para pequeños negocios"
              </p>
            </div>
          </div>
          
          {/* Experience level section */}
          <div className="card">
            <h2 className="text-lg font-medium text-neutral-900 mb-4 flex items-center">
              <span className="flex items-center justify-center bg-primary-100 text-primary-700 w-8 h-8 rounded-full mr-3">2</span>
              ¿Cuál es tu nivel de experiencia?
            </h2>
            
            <div className="grid gap-4 sm:grid-cols-3">
              {experienceLevels.map((level) => (
                <div 
                  key={level.id}
                  className={`border rounded-xl p-4 cursor-pointer transition-all duration-200 ${
                    experienceLevel === level.id 
                      ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200' 
                      : 'border-neutral-200 hover:border-primary-300'
                  }`}
                  onClick={() => setExperienceLevel(level.id)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-neutral-900">{level.name}</h3>
                    {experienceLevel === level.id && (
                      <FiCheck className="text-primary-600" />
                    )}
                  </div>
                  <p className="text-sm text-neutral-600">{level.description}</p>
                </div>
              ))}
            </div>
          </div>
          
          {/* Time duration section */}
          <div className="card">
            <h2 className="text-lg font-medium text-neutral-900 mb-4 flex items-center">
              <span className="flex items-center justify-center bg-primary-100 text-primary-700 w-8 h-8 rounded-full mr-3">3</span>
              ¿Cuánto tiempo tienes disponible?
            </h2>
            
            <div className="grid gap-4 sm:grid-cols-2">
              {timeDurations.map((time) => (
                <div 
                  key={time.id}
                  className={`border rounded-xl p-4 cursor-pointer transition-all duration-200 ${
                    availableTime === time.id 
                      ? 'border-primary-500 bg-primary-50 ring-2 ring-primary-200' 
                      : 'border-neutral-200 hover:border-primary-300'
                  }`}
                  onClick={() => setAvailableTime(time.id)}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-medium text-neutral-900">{time.name}</h3>
                    {availableTime === time.id && (
                      <FiCheck className="text-primary-600" />
                    )}
                  </div>
                  <p className="text-sm text-neutral-600">{time.description}</p>
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
      </div>
    </Layout>
  );
};

export default CourseGenerator; 