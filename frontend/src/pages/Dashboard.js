import React, { useState, useEffect, useContext } from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiPlus, FiCalendar, FiClock, FiChevronRight, FiTrash2 } from 'react-icons/fi';
import Layout from '../components/Layout';
import { courseService } from '../services/api';
import { ThemeContext } from '../context/ThemeContext';

const CourseCard = ({ course, onDelete }) => {
  const [isDeleting, setIsDeleting] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const { darkMode } = useContext(ThemeContext);
  
  const handleDelete = async () => {
    if (isDeleting) return;
    
    try {
      setIsDeleting(true);
      await courseService.deleteCourse(course.id);
      onDelete(course.id);
    } catch (error) {
      console.error('Error deleting course:', error);
    } finally {
      setIsDeleting(false);
      setShowConfirm(false);
    }
  };
  
  return (
    <motion.div 
      whileHover={{ y: -5 }}
      transition={{ duration: 0.2 }}
      className="card card-hover relative"
    >
      {showConfirm ? (
        <div className="p-4 flex flex-col items-center justify-center h-full">
          <p className={`mb-4 text-center ${darkMode ? 'text-white' : 'text-neutral-900'}`}>
            ¿Estás seguro de que deseas eliminar este curso?
          </p>
          <div className="flex space-x-3">
            <button
              onClick={() => setShowConfirm(false)}
              className="btn btn-secondary"
              disabled={isDeleting}
            >
              Cancelar
            </button>
            <button
              onClick={handleDelete}
              className="btn bg-red-600 text-white hover:bg-red-700"
              disabled={isDeleting}
            >
              {isDeleting ? (
                <div className="flex items-center">
                  <div className="animate-spin rounded-full h-4 w-4 border-t-2 border-b-2 border-white mr-2"></div>
                  <span>Eliminando...</span>
                </div>
              ) : (
                'Eliminar'
              )}
            </button>
          </div>
        </div>
      ) : (
        <>
          <button
            onClick={() => setShowConfirm(true)}
            className={`absolute top-4 right-4 p-2 text-neutral-400 hover:text-red-500 rounded-full ${
              darkMode ? 'hover:bg-red-900/30' : 'hover:bg-red-50'
            } transition-colors duration-200`}
            aria-label="Delete course"
          >
            <FiTrash2 />
          </button>
          
          <Link to={`/courses/${course.id}`} className="block">
            <h3 className={`text-lg font-medium ${darkMode ? 'text-white' : 'text-neutral-900'} line-clamp-2 mb-4 pr-8`}>
              {course.title}
            </h3>
            
            <div className={`flex items-center text-sm ${darkMode ? 'text-neutral-300' : 'text-neutral-600'} mb-2`}>
              <FiClock className="mr-2" />
              <span>{course.available_time}</span>
            </div>
            
            <div className={`flex items-center text-sm ${darkMode ? 'text-neutral-300' : 'text-neutral-600'} mb-4`}>
              <FiCalendar className="mr-2" />
              <span>{new Date(course.created_at).toLocaleDateString()}</span>
            </div>
            
            <div className={`flex items-center justify-between mt-4 pt-4 border-t ${
              darkMode ? 'border-neutral-700/50' : 'border-neutral-100'
            }`}>
              <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                darkMode 
                  ? 'bg-primary-900/30 text-primary-400' 
                  : 'bg-primary-100 text-primary-800'
              }`}>
                {course.experience_level}
              </span>
              
              <FiChevronRight className="text-primary-500" />
            </div>
          </Link>
        </>
      )}
    </motion.div>
  );
};

const Dashboard = () => {
  const [courses, setCourses] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { darkMode } = useContext(ThemeContext);
  
  const fetchCourses = async () => {
    try {
      setLoading(true);
      const data = await courseService.getCourses();
      setCourses(data);
    } catch (error) {
      console.error('Error fetching courses:', error);
      setError('No se pudieron cargar los cursos. Por favor, intenta de nuevo más tarde.');
    } finally {
      setLoading(false);
    }
  };
  
  useEffect(() => {
    fetchCourses();
  }, []);
  
  const handleDelete = (courseId) => {
    setCourses(courses.filter(course => course.id !== courseId));
  };
  
  return (
    <Layout>
      <div className="mb-6 sm:flex sm:items-center sm:justify-between">
        <div>
          <h1 className={`text-2xl font-bold ${darkMode ? 'text-white' : 'text-neutral-900'}`}>Mis Cursos</h1>
          <p className={`mt-1 text-sm ${darkMode ? 'text-neutral-300' : 'text-neutral-600'}`}>
            Accede a tus cursos guardados o crea uno nuevo.
          </p>
        </div>
        <div className="mt-4 sm:mt-0">
          <Link
            to="/generate"
            className="btn btn-primary"
          >
            <FiPlus className="mr-2" />
            Nuevo curso
          </Link>
        </div>
      </div>
      
      {loading ? (
        <div className="flex justify-center items-center h-64">
          <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-primary-600"></div>
        </div>
      ) : error ? (
        <div className={`${
          darkMode 
            ? 'bg-red-900/20 border-red-800/30 text-red-400' 
            : 'bg-red-50 border-red-200 text-red-700'
        } border px-4 py-3 rounded-lg`} role="alert">
          <span>{error}</span>
        </div>
      ) : courses.length === 0 ? (
        <div className={`${
          darkMode 
            ? 'bg-neutral-800/50' 
            : 'bg-neutral-50'
        } rounded-2xl p-12 text-center`}>
          <div className={`mx-auto h-24 w-24 ${
            darkMode 
              ? 'text-neutral-500 bg-neutral-800' 
              : 'text-neutral-400 bg-white'
          } flex items-center justify-center rounded-full mb-4`}>
            <FiPlus className="h-12 w-12" />
          </div>
          <h3 className={`text-lg font-medium ${darkMode ? 'text-white' : 'text-neutral-900'} mb-2`}>No tienes cursos guardados</h3>
          <p className={`${darkMode ? 'text-neutral-300' : 'text-neutral-600'} mb-6`}>
            Crea tu primer curso personalizado y guárdalo para acceder luego.
          </p>
          <Link
            to="/generate"
            className="btn btn-primary"
          >
            Crear mi primer curso
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
          {courses.map((course) => (
            <CourseCard 
              key={course.id} 
              course={course} 
              onDelete={handleDelete}
            />
          ))}
        </div>
      )}
    </Layout>
  );
};

export default Dashboard; 