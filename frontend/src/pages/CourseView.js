import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiArrowLeft, FiClock, FiBookOpen, FiCheckCircle, FiInfo, FiDownload, FiHelpCircle, FiAlertCircle } from 'react-icons/fi';
import Layout from '../components/Layout';
import { courseService } from '../services/api';

const CourseView = () => {
  const { courseId } = useParams();
  const navigate = useNavigate();
  
  const [course, setCourse] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [activeSection, setActiveSection] = useState('roadmap');
  
  useEffect(() => {
    const fetchCourse = async () => {
      try {
        setLoading(true);
        const data = await courseService.getCourse(courseId);
        setCourse(data);
      } catch (error) {
        console.error('Error fetching course:', error);
        setError('No se pudo cargar el curso. Por favor, intenta de nuevo más tarde.');
      } finally {
        setLoading(false);
      }
    };
    
    fetchCourse();
  }, [courseId]);
  
  if (loading) {
    return (
      <Layout>
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      </Layout>
    );
  }
  
  if (error) {
    return (
      <Layout>
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg" role="alert">
          <span>{error}</span>
        </div>
      </Layout>
    );
  }
  
  if (!course) {
    return (
      <Layout>
        <div className="bg-yellow-50 border border-yellow-200 text-yellow-700 px-4 py-3 rounded-lg" role="alert">
          <span>No se encontró el curso solicitado.</span>
        </div>
      </Layout>
    );
  }
  
  const courseContent = course.content;
  
  const tabs = [
    { id: 'roadmap', label: 'Mapa', icon: FiBookOpen },
    { id: 'modules', label: 'Módulos', icon: FiCheckCircle },
    { id: 'resources', label: 'Recursos', icon: FiDownload },
    { id: 'faqs', label: 'FAQs', icon: FiHelpCircle },
  ];
  
  return (
    <Layout>
      <div className="mb-6">
        <div className="flex mb-4">
          <button
            onClick={() => navigate('/dashboard')}
            className="flex items-center text-primary-600 hover:text-primary-700"
          >
            <FiArrowLeft className="mr-2" />
            <span>Volver a mis cursos</span>
          </button>
        </div>
        
        <div className="flex flex-col md:flex-row md:items-start justify-between">
          <div className="mb-4 md:mb-0">
            <h1 className="text-2xl font-bold text-neutral-900 mb-2">{courseContent.title}</h1>
            <div className="flex items-center text-neutral-600 mb-2">
              <FiClock className="mr-2" />
              <span>Tiempo: {course.available_time}</span>
              <span className="mx-2">•</span>
              <span>Nivel: {course.experience_level}</span>
            </div>
          </div>
        </div>
        
        <div className="bg-primary-50 border border-primary-200 text-primary-700 px-4 py-3 rounded-lg mt-4">
          <p className="text-sm font-medium">{courseContent.objective}</p>
        </div>
      </div>
      
      {/* Navigation tabs */}
      <div className="mb-6 border-b border-neutral-200">
        <nav className="flex overflow-x-auto hide-scrollbar space-x-8">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveSection(tab.id)}
              className={`flex items-center py-4 px-1 border-b-2 font-medium text-sm whitespace-nowrap ${
                activeSection === tab.id
                  ? 'border-primary-500 text-primary-600'
                  : 'border-transparent text-neutral-600 hover:text-neutral-700 hover:border-neutral-300'
              }`}
            >
              <tab.icon className={`mr-2 h-5 w-5 ${
                activeSection === tab.id ? 'text-primary-500' : 'text-neutral-500'
              }`} />
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
      
      {/* Content sections */}
      <div className="bg-white rounded-2xl shadow-apple p-6">
        {activeSection === 'roadmap' && (
          <div className="space-y-6">
            {/* Prerequisites section */}
            <div>
              <h2 className="text-lg font-medium text-neutral-900 mb-3">Conocimientos previos</h2>
              <ul className="space-y-2">
                {courseContent.prerequisites.length > 0 ? (
                  courseContent.prerequisites.map((item, index) => (
                    <li key={index} className="flex">
                      <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 text-primary-700 mr-3">
                        {index + 1}
                      </span>
                      <span className="text-neutral-700">{item}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-neutral-600">No se requieren conocimientos previos específicos.</li>
                )}
              </ul>
            </div>
            
            {/* Key definitions */}
            <div>
              <h2 className="text-lg font-medium text-neutral-900 mb-3">Definiciones clave</h2>
              <div className="bg-neutral-50 rounded-xl p-4">
                <ul className="space-y-3">
                  {courseContent.definitions.length > 0 ? (
                    courseContent.definitions.map((item, index) => (
                      <li key={index} className="flex">
                        <FiInfo className="text-primary-600 mr-3 flex-shrink-0 mt-1" />
                        <span className="text-neutral-700">{item}</span>
                      </li>
                    ))
                  ) : (
                    <li className="text-neutral-600">No hay definiciones clave para este curso.</li>
                  )}
                </ul>
              </div>
            </div>
            
            {/* Learning roadmap */}
            <div>
              <h2 className="text-lg font-medium text-neutral-900 mb-3">Ruta de aprendizaje</h2>
              <div className="space-y-3">
                {courseContent.roadmap.map((step, index) => (
                  <motion.div 
                    key={index}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.3, delay: index * 0.1 }}
                    className="bg-white rounded-xl border border-neutral-200 p-4 shadow-sm"
                  >
                    <div className="flex items-start">
                      <div className="flex-shrink-0 flex items-center justify-center w-8 h-8 rounded-full bg-primary-100 text-primary-700 mr-3">
                        {index + 1}
                      </div>
                      <div>
                        <p className="text-neutral-800">{step}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </div>
            </div>
          </div>
        )}
        
        {activeSection === 'modules' && (
          <div className="space-y-8">
            {courseContent.modules.map((module, moduleIndex) => (
              <div key={moduleIndex} className="border border-neutral-200 rounded-xl overflow-hidden">
                <div className="bg-primary-50 px-6 py-4 border-b border-neutral-200">
                  <h3 className="text-lg font-medium text-neutral-900">
                    <span className="inline-block bg-primary-100 text-primary-700 rounded-full w-8 h-8 text-center leading-8 mr-2">
                      {moduleIndex + 1}
                    </span>
                    {module.title}
                  </h3>
                </div>
                
                <div className="p-6">
                  <div className="space-y-4">
                    <h4 className="font-medium text-neutral-800">Pasos:</h4>
                    <ul className="space-y-3">
                      {module.steps.map((step, stepIndex) => (
                        <li key={stepIndex} className="flex">
                          <span className="flex-shrink-0 flex items-center justify-center w-6 h-6 rounded-full bg-primary-100 text-primary-700 mr-3">
                            {stepIndex + 1}
                          </span>
                          <span className="text-neutral-700">{step}</span>
                        </li>
                      ))}
                    </ul>
                    
                    {module.example && (
                      <div className="mt-4 bg-neutral-50 rounded-lg p-4">
                        <h4 className="font-medium text-neutral-800 mb-2">Ejemplo:</h4>
                        <p className="text-neutral-700">{module.example}</p>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
        
        {activeSection === 'resources' && (
          <div className="space-y-6">
            {/* Additional resources */}
            <div>
              <h2 className="text-lg font-medium text-neutral-900 mb-3">Recursos adicionales</h2>
              <ul className="space-y-3">
                {courseContent.resources.length > 0 ? (
                  courseContent.resources.map((resource, index) => (
                    <li key={index} className="flex">
                      <FiDownload className="text-primary-600 mr-3 flex-shrink-0 mt-1" />
                      <span className="text-neutral-700">{resource}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-neutral-600">No hay recursos adicionales para este curso.</li>
                )}
              </ul>
            </div>
            
            {/* Common errors */}
            <div>
              <h2 className="text-lg font-medium text-neutral-900 mb-3">Errores comunes</h2>
              <div className="bg-red-50 rounded-xl p-4">
                <ul className="space-y-3">
                  {courseContent.errors.length > 0 ? (
                    courseContent.errors.map((error, index) => (
                      <li key={index} className="flex">
                        <FiAlertCircle className="text-red-600 mr-3 flex-shrink-0 mt-1" />
                        <span className="text-red-800">{error}</span>
                      </li>
                    ))
                  ) : (
                    <li className="text-neutral-600">No hay errores comunes identificados para este curso.</li>
                  )}
                </ul>
              </div>
            </div>
            
            {/* Downloadable resources */}
            <div>
              <h2 className="text-lg font-medium text-neutral-900 mb-3">Recursos descargables</h2>
              <ul className="space-y-3">
                {courseContent.downloads.length > 0 ? (
                  courseContent.downloads.map((download, index) => (
                    <li key={index} className="flex">
                      <FiDownload className="text-primary-600 mr-3 flex-shrink-0 mt-1" />
                      <span className="text-neutral-700">{download}</span>
                    </li>
                  ))
                ) : (
                  <li className="text-neutral-600">No hay recursos descargables disponibles para este curso.</li>
                )}
              </ul>
            </div>
          </div>
        )}
        
        {activeSection === 'faqs' && (
          <div>
            <h2 className="text-lg font-medium text-neutral-900 mb-4">Preguntas frecuentes</h2>
            <div className="space-y-4">
              {courseContent.faqs.length > 0 ? (
                courseContent.faqs.map((faq, index) => (
                  <div key={index} className="border border-neutral-200 rounded-lg p-4">
                    <div className="flex">
                      <FiHelpCircle className="text-primary-600 mr-3 flex-shrink-0 mt-1" />
                      <span className="text-neutral-800 font-medium">{faq}</span>
                    </div>
                  </div>
                ))
              ) : (
                <div className="bg-neutral-50 rounded-lg p-4 text-neutral-600">
                  No hay preguntas frecuentes disponibles para este curso.
                </div>
              )}
            </div>
          </div>
        )}
        
        {/* Summary */}
        <div className="mt-8 pt-6 border-t border-neutral-200">
          <h2 className="text-lg font-medium text-neutral-900 mb-3">Resumen</h2>
          <div className="bg-neutral-50 rounded-xl p-4">
            <p className="text-neutral-700">{courseContent.summary}</p>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default CourseView; 