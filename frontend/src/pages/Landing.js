import React, { useEffect } from 'react';
import { Link } from 'react-router-dom';
import { motion, useAnimation } from 'framer-motion';
import { FiArrowRight, FiClock, FiBookOpen, FiSave, FiSearch } from 'react-icons/fi';

// Import our new components
import TextScramble from '../components/TextScramble';
import GlowingOrb from '../components/GlowingOrb';
import TextCycler from '../components/TextCycler';
import ShinyButton from '../components/ShinyButton';
import BackgroundGrid from '../components/BackgroundGrid';
import AnimatedSearch from '../components/AnimatedSearch';

// Animation variants
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
  const controls = useAnimation();
  
  useEffect(() => {
    controls.start("visible");
  }, [controls]);
  
  const learningTopics = [
    "Inteligencia Artificial",
    "Programación",
    "Marketing Digital",
    "Diseño UX/UI",
    "Machine Learning",
    "Desarrollo Web"
  ];
  
  const rhythmPhrases = [
    "a tu propio ritmo",
    "cuando tú quieras",
    "donde tú decidas",
    "como más te guste",
    "sin presiones",
    "a tu manera"
  ];

  return (
    <motion.div 
      initial="hidden" 
      animate="visible" 
      className="min-h-screen bg-neutral-900 text-white overflow-hidden relative"
    >
      {/* Background Grid */}
      <BackgroundGrid dotColor="rgba(80, 160, 255, 0.15)" dotSpacing={30} />
      
      {/* Header/Navigation */}
      <motion.header 
        variants={fadeIn}
        transition={{ duration: 0.5 }}
        className="bg-neutral-900/70 backdrop-blur-lg sticky top-0 z-10 border-b border-neutral-800"
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16 items-center">
            <motion.div 
              variants={slideInFromLeft}
              transition={{ duration: 0.6 }}
              className="flex-shrink-0 flex items-center"
            >
              <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-primary-400 to-primary-600">
                <TextScramble text="Prompt2Course" delay={300} duration={1500} />
              </h1>
            </motion.div>
            <motion.div 
              variants={slideInFromRight}
              transition={{ duration: 0.6 }}
              className="flex items-center space-x-4"
            >
              <Link to="/login">
                <motion.button 
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="px-4 py-2 rounded-xl bg-transparent border border-neutral-700 text-neutral-300 hover:bg-neutral-800 transition-all"
                >
                  Iniciar sesión
                </motion.button>
              </Link>
              <Link to="/register">
                <ShinyButton primary>
                  Registrarse
                </ShinyButton>
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
                className="text-4xl tracking-tight font-bold text-white sm:text-5xl md:text-6xl"
              >
                <motion.span 
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.2 }}
                  className="block"
                >
                  Aprende cualquier tema
                </motion.span>
                
                {/* Texto animado que cambia verticalmente */}
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ duration: 0.5, delay: 0.7 }}
                  className="block mt-2 h-16 overflow-hidden"
                >
                  <TextCycler 
                    texts={rhythmPhrases}
                    interval={3000}
                    textClassName="text-5xl md:text-6xl font-bold text-primary-400 animated-glow"
                  />
                </motion.div>
              </motion.h1>
              <motion.p 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 0.7 }}
                className="mt-6 text-lg text-neutral-300"
              >
                <TextScramble 
                  text="Prompt2Course te permite generar cursos personalizados para aprender cualquier tema, adaptados a tu nivel de experiencia, gustos, personalidad y tiempo disponible."
                  delay={1000}
                  duration={1500}
                />
              </motion.p>
              
              <motion.div 
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.5, delay: 1.5 }}
                className="mt-8 sm:flex sm:justify-center lg:justify-start"
              >
                <Link to="/register">
                  <ShinyButton className="py-3 px-6 text-base flex items-center space-x-2">
                    <span>Comenzar gratis</span>
                    <FiArrowRight className="ml-2" />
                  </ShinyButton>
                </Link>
                <motion.div 
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className="mt-3 sm:mt-0 sm:ml-3"
                >
                  <Link
                    to="/login"
                    className="inline-flex items-center px-6 py-3 border border-neutral-700 rounded-xl text-base font-medium text-neutral-300 bg-neutral-900 hover:bg-neutral-800 transition-all"
                  >
                    Iniciar sesión
                  </Link>
                </motion.div>
              </motion.div>
            </div>
            
            {/* Lado derecho - Animación de búsqueda */}
            <div className="mt-12 relative sm:max-w-lg sm:mx-auto lg:mt-0 lg:max-w-none lg:mx-0 lg:col-span-6 lg:flex lg:items-center justify-center">
              {/* Componente de búsqueda animada */}
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.8, delay: 0.6 }}
                className="relative z-10 w-full max-w-lg"
              >
                <AnimatedSearch />
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
        className="bg-neutral-900 relative py-16 sm:py-24 overflow-hidden"
      >
        {/* Subtle background effect */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute -top-40 -right-40 w-80 h-80 bg-primary-500/5 rounded-full blur-3xl" />
          <div className="absolute -bottom-40 -left-40 w-80 h-80 bg-primary-600/5 rounded-full blur-3xl" />
        </div>
        
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative z-10">
          <motion.div 
            variants={fadeInUp}
            transition={{ duration: 0.6 }}
            className="lg:text-center"
          >
            <motion.h2 
              variants={fadeInUp}
              className="text-base text-primary-400 font-semibold tracking-wide uppercase"
            >
              <TextScramble text="Características" delay={200} duration={1000} />
            </motion.h2>
            <motion.p 
              variants={fadeInUp}
              className="mt-2 text-3xl leading-8 font-bold tracking-tight text-white sm:text-4xl"
            >
              Todo lo que necesitas para aprender eficientemente
            </motion.p>
            <motion.p 
              variants={fadeInUp}
              className="mt-4 max-w-2xl text-xl text-neutral-300 lg:mx-auto"
            >
              Prompt2Course simplifica el proceso de aprendizaje con herramientas intuitivas y recursos personalizados.
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
                className="bg-neutral-800/50 backdrop-blur-sm rounded-2xl p-8 border border-neutral-700/50 shadow-xl"
              >
                <div>
                  <motion.div 
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: "spring", stiffness: 300 }}
                    className="flex items-center justify-center h-12 w-12 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 text-white"
                  >
                    <FiBookOpen className="h-6 w-6" />
                  </motion.div>
                  <div className="mt-5">
                    <h3 className="text-xl font-medium text-white">Cursos personalizados</h3>
                    <p className="mt-2 text-base text-neutral-300">
                      Genera cursos adaptados a tus necesidades específicas, nivel de experiencia y objetivo de aprendizaje.
                    </p>
                  </div>
                </div>
              </motion.div>

              {/* Feature 2 */}
              <motion.div 
                variants={fadeInUp}
                whileHover={{ y: -10, transition: { duration: 0.2 } }}
                className="bg-neutral-800/50 backdrop-blur-sm rounded-2xl p-8 border border-neutral-700/50 shadow-xl"
              >
                <div>
                  <motion.div 
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: "spring", stiffness: 300 }}
                    className="flex items-center justify-center h-12 w-12 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 text-white"
                  >
                    <FiClock className="h-6 w-6" />
                  </motion.div>
                  <div className="mt-5">
                    <h3 className="text-xl font-medium text-white">Ahorra tiempo</h3>
                    <p className="mt-2 text-base text-neutral-300">
                      Obtén rápidamente contenido estructurado sin tener que buscar en múltiples fuentes o diseñar tu propio plan de estudio.
                    </p>
                  </div>
                </div>
              </motion.div>

              {/* Feature 3 */}
              <motion.div 
                variants={fadeInUp}
                whileHover={{ y: -10, transition: { duration: 0.2 } }}
                className="bg-neutral-800/50 backdrop-blur-sm rounded-2xl p-8 border border-neutral-700/50 shadow-xl"
              >
                <div>
                  <motion.div 
                    whileHover={{ scale: 1.1, rotate: 5 }}
                    transition={{ type: "spring", stiffness: 300 }}
                    className="flex items-center justify-center h-12 w-12 rounded-full bg-gradient-to-br from-primary-400 to-primary-600 text-white"
                  >
                    <FiSave className="h-6 w-6" />
                  </motion.div>
                  <div className="mt-5">
                    <h3 className="text-xl font-medium text-white">Biblioteca personal</h3>
                    <p className="mt-2 text-base text-neutral-300">
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
        className="bg-gradient-to-r from-primary-600 to-primary-700 relative overflow-hidden"
      >
        {/* Background shine effect */}
        <motion.div 
          className="absolute inset-0 overflow-hidden"
          initial={{ opacity: 0.2 }}
          animate={{ opacity: 0.5 }}
          transition={{ duration: 8, repeat: Infinity, repeatType: 'reverse' }}
        >
          <div className="absolute top-1/4 -right-20 w-80 h-80 bg-white/20 rounded-full blur-3xl" />
          <div className="absolute bottom-1/4 -left-20 w-60 h-60 bg-white/10 rounded-full blur-3xl" />
        </motion.div>
        
        <div className="max-w-7xl mx-auto py-12 px-4 sm:px-6 lg:py-16 lg:px-8 lg:flex lg:items-center lg:justify-between relative z-10">
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
            </motion.span>
          </motion.h2>
          <motion.div 
            variants={slideInFromRight}
            transition={{ duration: 0.5 }}
            className="mt-8 flex lg:mt-0 lg:flex-shrink-0"
          >
            <Link to="/register">
              <ShinyButton primary={false} className="py-3 px-6 text-base bg-white text-primary-700 hover:bg-primary-50">
                Comenzar gratis
              </ShinyButton>
            </Link>
          </motion.div>
        </div>
      </motion.section>

      {/* Footer */}
      <motion.footer 
        variants={fadeIn}
        initial="hidden"
        whileInView="visible"
        viewport={{ once: true }}
        className="bg-neutral-900 border-t border-neutral-800"
      >
        <div className="max-w-7xl mx-auto py-12 px-4 overflow-hidden sm:px-6 lg:px-8">
          <motion.p 
            variants={fadeInUp}
            className="mt-8 text-center text-base text-neutral-400"
          >
            &copy; {new Date().getFullYear()} Prompt2Course. Todos los derechos reservados.
          </motion.p>
        </div>
      </motion.footer>
    </motion.div>
  );
};

export default Landing; 