import React from 'react';
import { motion } from 'framer-motion';
import { FiX, FiCheck, FiStar } from 'react-icons/fi';

const SubscriptionModal = ({ isOpen, onClose, plans, onSelectPlan, currentTier }) => {
  if (!isOpen) return null;

  // Crear estructura de planes personalizada
  // Solo mostramos el plan Pro (5 cursos) y Unlimited
  const customPlans = [
    {
      id: plans.find(p => p.course_limit === 5)?.id || 'tier_pro',
      name: 'Pro',
      price: 19.900,
      course_limit: 5,
      description: 'Ideal para usuarios regulares',
    },
    {
      id: plans.find(p => p.course_limit === -1)?.id || 'tier_unlimited',
      name: 'Unlimited',
      price: 24.900,
      course_limit: -1,
      description: 'Perfecto para uso intensivo',
    }
  ];

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center overflow-y-auto bg-black bg-opacity-50">
      <motion.div 
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        exit={{ opacity: 0, scale: 0.95 }}
        className="bg-white rounded-xl p-6 max-w-3xl w-full mx-4 shadow-2xl"
      >
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-2xl font-bold text-neutral-900">Actualiza tu plan</h2>
          <button 
            onClick={onClose}
            className="text-neutral-500 hover:text-neutral-700"
          >
            <FiX size={24} />
          </button>
        </div>

        <div className="mb-6">
          <p className="text-lg text-neutral-700">
            Has alcanzado el límite de cursos de tu plan actual. Actualiza para crear más cursos personalizados.
          </p>
        </div>

        <div className="grid md:grid-cols-3 gap-6 mb-8">
          {/* Plan Gratuito */}
          <div className={`border rounded-xl p-5 ${currentTier === 'free' ? 'border-primary-500 bg-primary-50' : 'border-neutral-200'}`}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium">Free</h3>
              {currentTier === 'free' && (
                <span className="px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded-full">
                  Tu plan actual
                </span>
              )}
            </div>
            <p className="text-3xl font-bold mb-4">$0<span className="text-sm text-neutral-500 font-normal">/mes</span></p>
            <ul className="space-y-3 mb-6">
              <li className="flex items-start">
                <FiCheck className="text-green-500 mt-1 mr-2 flex-shrink-0" />
                <span>1 curso</span>
              </li>
              <li className="flex items-start">
                <FiCheck className="text-green-500 mt-1 mr-2 flex-shrink-0" />
                <span>Acceso básico</span>
              </li>
            </ul>
            <button 
              className="w-full py-2 px-4 border border-neutral-300 rounded-lg text-neutral-700 bg-white hover:bg-neutral-50 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={currentTier === 'free'}
            >
              Plan actual
            </button>
          </div>

          {/* Planes disponibles */}
          {customPlans.map((plan) => (
            <div 
              key={plan.id} 
              className={`border rounded-xl p-5 ${plan.name.toLowerCase() === 'pro' ? 'ring-2 ring-primary-500' : ''} ${currentTier === plan.name.toLowerCase() ? 'border-primary-500 bg-primary-50' : 'border-neutral-200'}`}
            >
              {plan.name === 'Pro' && (
                <div className="flex items-center text-primary-700 mb-2">
                  <FiStar className="mr-1" />
                  <span className="text-sm font-medium">Más popular</span>
                </div>
              )}
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-lg font-medium">{plan.name}</h3>
                {currentTier === plan.name.toLowerCase() && (
                  <span className="px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded-full">
                    Tu plan actual
                  </span>
                )}
              </div>
              <p className="text-3xl font-bold mb-4">${plan.name === 'Pro' ? '19.900' : '24.900'}<span className="text-sm text-neutral-500 font-normal">/mes</span></p>
              <ul className="space-y-3 mb-6">
                <li className="flex items-start">
                  <FiCheck className="text-green-500 mt-1 mr-2 flex-shrink-0" />
                  <span>{plan.course_limit === -1 ? 'Cursos ilimitados' : `${plan.course_limit} cursos`}</span>
                </li>
                <li className="flex items-start">
                  <FiCheck className="text-green-500 mt-1 mr-2 flex-shrink-0" />
                  <span>{plan.description}</span>
                </li>
              </ul>
              <button 
                onClick={() => onSelectPlan(plan)}
                className={`w-full py-2 px-4 rounded-lg transition-colors 
                  ${currentTier === plan.name.toLowerCase() 
                    ? 'border border-primary-500 text-primary-700 bg-primary-50 hover:bg-primary-100'
                    : plan.name.toLowerCase() === 'pro'
                      ? 'bg-primary-600 text-white hover:bg-primary-700' 
                      : 'bg-primary-500 text-white hover:bg-primary-600'
                  }
                  ${currentTier === plan.name.toLowerCase() ? 'disabled:opacity-50 disabled:cursor-not-allowed' : ''}
                `}
                disabled={currentTier === plan.name.toLowerCase()}
              >
                {currentTier === plan.name.toLowerCase() ? 'Plan actual' : 'Seleccionar plan'}
              </button>
            </div>
          ))}
        </div>
      </motion.div>
    </div>
  );
};

export default SubscriptionModal; 