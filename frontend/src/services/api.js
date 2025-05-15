import axios from 'axios';

const API_URL = 'http://localhost:8000';

// Create an axios instance with default configuration
const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add request interceptor to include auth token in all authenticated requests
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Course API Services
export const courseService = {
  // Generate a course
  generateCourse: async (topic, experienceLevel, availableTime) => {
    try {
      const response = await api.post('/generate-course', {
        topic,
        experience_level: experienceLevel,
        available_time: availableTime,
      });
      return response.data;
    } catch (error) {
      // Para 403 con need_upgrade, queremos pasar todos los detalles del error
      if (error.response?.status === 403 && error.response?.data?.detail?.need_upgrade) {
        throw { ...error.response.data.detail, isSubscriptionLimitError: true };
      }
      throw new Error(error.response?.data?.detail?.message || error.response?.data?.detail || 'Failed to generate course');
    }
  },
  
  // Save a course
  saveCourse: async (courseData) => {
    try {
      const response = await api.post('/save-course', courseData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to save course');
    }
  },
  
  // Get all courses for current user
  getCourses: async () => {
    try {
      const response = await api.get('/courses');
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch courses');
    }
  },
  
  // Get a specific course by ID
  getCourse: async (courseId) => {
    try {
      const response = await api.get(`/courses/${courseId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch course');
    }
  },
  
  // Delete a course
  deleteCourse: async (courseId) => {
    try {
      const response = await api.delete(`/courses/${courseId}`);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to delete course');
    }
  },
  
  // Solicitar un reemplazo para un tema que ya conoces
  requestTopicReplacement: async (requestData) => {
    try {
      const response = await api.post('/replace-topic', requestData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get topic replacement');
    }
  },
  
  // Solicitar un reemplazo para un módulo que ya conoces
  requestModuleReplacement: async (requestData) => {
    try {
      const response = await api.post('/replace-module', requestData);
      return response.data;
    } catch (error) {
      throw new Error(error.response?.data?.detail || 'Failed to get module replacement');
    }
  },
};

export default api; 