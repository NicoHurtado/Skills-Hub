import React from 'react';
import { Link } from 'react-router-dom';
import { motion } from 'framer-motion';
import { FiArrowRight, FiClock, FiBookOpen, FiSave } from 'react-icons/fi';

// Variantes de animación
const fadeIn = {
  hidden: { opacity: 0 },
  visible: { opacity: 1 }
};

const slideInFromLeft = {
  hidden: { x: -60, opacity: 0 },
  visible: { x: 0, opacity: 1 }
};

const slideInFromRight = {
  hidden: { x: 60, opacity: 0 },
  visible: { x: 0, opacity: 1 }
};

const fadeInUp = {
  hidden: { y: 40, opacity: 0 },
  visible: { y: 0, opacity: 1 }
};

const staggerContainer = {
  hidden: { opacity: 0 },
  visible: {
    opacity: 1,
    transition: {
      staggerChildren: 0.2
    }
  }
};

const Landing = () => {
  return (
    <motion.div 
      initial="hidden" 
      animate="visible" 
      className="min-h-screen bg-white"
    >
      {/* Header/Navigation */}
      <motion.header 
        variants={fadeIn}
        transition={{ duration: 0.5 }}
        className="bg-white shadow-sm sticky top-0 z-10"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <motion.div 
              variants={slideInFromLeft}
              transition={{ duration: 0.6 }}
              className="flex-shrink-0 flex items-center"
            >
              <h1 className="text-xl font-bold text-primary-600">Skills Hub</h1>
            </motion.div>
            <motion.div 
              variants={slideInFromRight}
              transition={{ duration: 0.6 }}
              className="flex items-center space-x-4"
            >
              <Link to="/login" className="btn btn-secondary">
                Iniciar sesión
              </Link>
              <Link to="/register" className="btn btn-primary">
                Registrarse
              </Link>
            </motion.div>
          </div>
        </div>
      </motion.header>

      {/* Hero Section */}
      <section className="relative">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-16 pb-24 md:pt-24 md:pb-32">
          <div className="lg:grid lg:grid-cols-12 lg:gap-8">
            <div className="sm:text-center md:max-w-2xl md:mx-auto lg:col-span-6 lg:text-left">
              <motion.h1 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.7 }}
                className="text-4xl tracking-tight font-bold text-neutral-900 sm:text-5xl md:text-6xl"
              >
                <motion.span 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  className="block"
                >
                  Aprende cualquier
                </motion.span>
                <motion.span 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.5 }}
                  className="block text-primary-600"
                >
                  tema a tu ritmo
                </motion.span>
              </motion.h1>
              <motion.p 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.7 }}
                className="mt-6 text-lg text-neutral-600"
              >
                Skills Hub te permite generar cursos personalizados para aprender cualquier tema, adaptados a tu nivel de experiencia y tiempo disponible.
              </motion.p>
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.9 }}
                className="mt-8 sm:flex sm:justify-center lg:justify-start"
              >
                <motion.div 
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="rounded-md shadow"
                >
                  <Link
                    to="/register"
                    className="btn btn-primary py-3 px-6 text-base"
                  >
                    Comenzar gratis
                    <FiArrowRight className="ml-2" />
                  </Link>
                </motion.div>
                <motion.div 
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="mt-3 sm:mt-0 sm:ml-3"
                >
                  <Link
                    to="/login"
                    className="btn btn-outline py-3 px-6 text-base"
                  >
                    Iniciar sesión
                  </Link>
                </motion.div>
              </motion.div>
            </div>
            <div className="mt-12 relative sm:max-w-lg sm:mx-auto lg:mt-0 lg:max-w-none lg:mx-0 lg:col-span-6 lg:flex lg:items-center">
              <motion.div
                initial={{ opacity: 0, scale: 0.8 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ 
                  duration: 0.8, 
                  delay: 0.3,
                  type: "spring",
                  stiffness: 100
                }}
                className="relative mx-auto w-full rounded-2xl shadow-apple-xl overflow-hidden"
              >
                <div className="relative">
                  {/* Image element (replacing video) */}
                  <motion.div
                    initial={{ y: 30, opacity: 0 }}
                    animate={{ y: 0, opacity: 1 }}
                    transition={{ duration: 0.8, delay: 0.5 }}
                    className="relative aspect-video w-full flex items-center justify-center"
                  >
                    <img
                      src="/image.png"
                      alt="Skills Hub AI Learning"
                      className="w-full h-full object-contain rounded-2xl"
                    />
                    
                    {/* Overlay with gradient */}
                    <div className="absolute inset-0 bg-gradient-to-r from-primary-700/10 to-primary-900/10 rounded-2xl">
                      {/* Removed play button since we now have an image */}
                    </div>
                  </motion.div>
                  
                  {/* Caption */}
                  <div className="absolute bottom-4 left-4 right-4 bg-white/70 backdrop-blur-sm p-3 rounded-lg">
                    <p className="text-sm text-neutral-800 font-medium">
                      Genera cursos personalizados con IA y aprende a tu propio ritmo
                    </p>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <motion.section 
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true, amount: 0.2 }}
        variants={fadeIn}
        transition={{ duration: 0.5 }}
        className="bg-neutral-50 py-16 sm:py-24"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <motion.div 
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            className="lg:text-center"
          >
            <motion.h2 
              variants={fadeInUp}
              className="text-base text-primary-600 font-semibold tracking-wide uppercase"
            >
              Características
            </motion.h2>
            <motion.p 
              variants={fadeInUp}
              className="mt-2 text-3xl leading-8 font-bold tracking-tight text-neutral-900 sm:text-4xl"
            >
              Todo lo que necesitas para aprender eficientemente
            </motion.p>
            <motion.p 
              variants={fadeInUp}
              className="mt-4 max-w-2xl text-xl text-neutral-600 lg:mx-auto"
            >
              Skills Hub simplifica el proceso de aprendizaje con herramientas intuitivas y recursos personalizados.
            </motion.p>
          </motion.div>

          <motion.div 
            variants={staggerContainer}
            transition={{ duration: 0.3, delayChildren: 0.3, staggerChildren: 0.2 }}
            className="mt-16"
          >
            <div className="grid grid-cols-1 gap-8 sm:grid-cols-2 lg:grid-cols-3">
              {/* Feature 1 */}
              <motion.div 
                variants={fadeInUp}
                whileHover={{ y: -10, transition: { duration: 0.2 } }}
                className="card"
              >
                <div>
                  <motion.div 
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: "spring", stiffness: 300 }}
                    className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white"
                  >
                    <FiBookOpen className="h-6 w-6" />
                  </motion.div>
                  <div className="mt-5">
                    <h3 className="text-xl font-medium text-neutral-900">Cursos personalizados</h3>
                    <p className="mt-2 text-base text-neutral-600">
                      Genera cursos adaptados a tus necesidades específicas, nivel de experiencia y objetivo de aprendizaje.
                    </p>
                  </div>
                </div>
              </motion.div>

              {/* Feature 2 */}
              <motion.div 
                variants={fadeInUp}
                whileHover={{ y: -10, transition: { duration: 0.2 } }}
                className="card"
              >
                <div>
                  <motion.div 
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: "spring", stiffness: 300 }}
                    className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white"
                  >
                    <FiClock className="h-6 w-6" />
                  </motion.div>
                  <div className="mt-5">
                    <h3 className="text-xl font-medium text-neutral-900">Ahorra tiempo</h3>
                    <p className="mt-2 text-base text-neutral-600">
                      Obtén rápidamente contenido estructurado sin tener que buscar en múltiples fuentes o diseñar tu propio plan de estudio.
                    </p>
                  </div>
                </div>
              </motion.div>

              {/* Feature 3 */}
              <motion.div 
                variants={fadeInUp}
                whileHover={{ y: -10, transition: { duration: 0.2 } }}
                className="card"
              >
                <div>
                  <motion.div 
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: "spring", stiffness: 300 }}
                    className="flex items-center justify-center h-12 w-12 rounded-md bg-primary-500 text-white"
                  >
                    <FiSave className="h-6 w-6" />
                  </motion.div>
                  <div className="mt-5">
                    <h3 className="text-xl font-medium text-neutral-900">Biblioteca personal</h3>
                    <p className="mt-2 text-base text-neutral-600">
                      Guarda tus cursos generados en tu biblioteca personal y accede a ellos cuando quieras, desde cualquier dispositivo.
                    </p>
                  </div>
                </div>
              </motion.div>
            </div>
          </motion.div>
        </div>
      </motion.section>

      {/* CTA Section */}
      <motion.section 
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        variants={fadeIn}
        className="bg-primary-600"
      >
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between">
          <motion.h2 
            variants={slideInFromLeft}
            transition={{ duration: 0.5 }}
            className="text-3xl font-extrabold tracking-tight text-white sm:text-4xl"
          >
            <span className="block">¿Listo para aprender?</span>
            <motion.span 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.3, duration: 0.5 }}
              className="block text-primary-200"
            >
              Comienza a usar Skills Hub hoy mismo.
            </motion.span>
          </motion.h2>
          <motion.div 
            variants={slideInFromRight}
            transition={{ duration: 0.5 }}
            className="mt-8 flex lg:mt-0 lg:flex-shrink-0"
          >
            <motion.div 
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="inline-flex rounded-md shadow"
            >
              <Link
                to="/register"
                className="btn bg-white text-primary-700 hover:bg-primary-50 py-3 px-6 text-base"
              >
                Comenzar gratis
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </motion.section>

      {/* Footer */}
      <motion.footer 
        variants={fadeIn}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="bg-white"
      >
        <div className="max-w-7xl mx-auto py-12 px-4 overflow-hidden sm:px-6 lg:px-8">
          <motion.p 
            variants={fadeInUp}
            className="mt-8 text-center text-base text-neutral-500"
          >
            &copy; {new Date().getFullYear()} Skills Hub. Todos los derechos reservados.
          </motion.p>
        </div>
      </motion.footer>
    </motion.div>
  );
};

export default Landing; 