import React, { useState, useEffect } from 'react';
import { FiCheck, FiStar } from 'react-icons/fi';
import Layout from '../components/Layout';
import axios from 'axios';
import { useAuth } from '../hooks/useAuth';

const PlansPage = () => {
  const { user } = useAuth();
  const [plans, setPlans] = useState([]);
  const [currentPlan, setCurrentPlan] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [subscriptionStatus, setSubscriptionStatus] = useState(null);

  useEffect(() => {
    const fetchPlans = async () => {
      try {
        setLoading(true);

        // Obtener los planes disponibles
        const plansResponse = await axios.get('http://localhost:8000/subscription-tiers', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        // Obtener el estado de suscripción actual
        const statusResponse = await axios.get('http://localhost:8000/subscription-status', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });

        // Organizar planes en el orden correcto
        const orderedPlans = [
          // Plan Free siempre primero
          plansResponse.data.find(p => p.name.toLowerCase() === 'free'),
          // Resto de planes ordenados por precio
          ...plansResponse.data
            .filter(p => p.name.toLowerCase() !== 'free')
            .sort((a, b) => a.price - b.price)
        ].filter(Boolean); // Filtrar cualquier posible undefined

        setPlans(orderedPlans);
        setSubscriptionStatus(statusResponse.data);
        setCurrentPlan(statusResponse.data.tier);
        setLoading(false);
      } catch (err) {
        console.error('Error fetching plan data:', err);
        setError('No se pudieron cargar los planes. Por favor, intenta de nuevo más tarde.');
        setLoading(false);
      }
    };

    fetchPlans();
  }, []);

  const handleSelectPlan = async (plan) => {
    try {
      if (plan.name.toLowerCase() === currentPlan.name.toLowerCase()) {
        return; // Ya tiene este plan
      }
      
      // Si es el plan gratuito, actualizamos directamente
      if (plan.name.toLowerCase() === 'free') {
        const response = await axios.post('http://localhost:8000/subscribe', 
          { tier_id: plan.id },
          { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
        );
        
        // Actualizar el estado
        setCurrentPlan(plan);
        alert(`¡Te has suscrito al plan ${plan.name}!`);
        
        // Recargar el estado de la suscripción
        const statusResponse = await axios.get('http://localhost:8000/subscription-status', {
          headers: {
            Authorization: `Bearer ${localStorage.getItem('token')}`
          }
        });
        setSubscriptionStatus(statusResponse.data);
      } else {
        // Para planes pagos, creamos un enlace de pago
        const response = await axios.post('http://localhost:8000/create-payment', 
          { tier_id: plan.id },
          { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
        );
        
        // Guardamos la referencia del pago para la verificación posterior
        localStorage.setItem('pending_payment_reference', response.data.reference);
        
        // Redirigimos al usuario a la página de pago
        window.location.href = response.data.payment_url;
      }
    } catch (err) {
      console.error('Error al procesar el plan:', err);
      setError('Error al procesar la solicitud. Por favor, intenta de nuevo.');
    }
  };

  if (loading) {
    return (
      <Layout>
        <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
          <h1 className="text-2xl font-bold text-neutral-900 mb-8">Planes de suscripción</h1>
          <div className="text-center py-12">Cargando planes...</div>
        </div>
      </Layout>
    );
  }

  return (
    <Layout>
      <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8">
        <h1 className="text-2xl font-bold text-neutral-900 mb-4">Planes de suscripción</h1>
        
        {subscriptionStatus && (
          <div className="mb-8 bg-white p-4 rounded-lg shadow-sm border border-neutral-200">
            <h2 className="text-lg font-medium text-neutral-700 mb-2">Tu suscripción actual</h2>
            <div className="flex flex-wrap gap-4">
              <div>
                <span className="text-sm font-medium text-neutral-500">Plan:</span>
                <span className="ml-2 text-neutral-900 font-medium">
                  {currentPlan?.name || 'Free'}
                </span>
              </div>
              <div>
                <span className="text-sm font-medium text-neutral-500">Cursos usados:</span>
                <span className="ml-2 text-neutral-900 font-medium">
                  {subscriptionStatus.course_count} de {currentPlan?.course_limit === -1 ? 'ilimitados' : currentPlan?.course_limit}
                </span>
              </div>
              <div>
                <span className="text-sm font-medium text-neutral-500">Estado:</span>
                <span className={`ml-2 font-medium ${subscriptionStatus.is_active ? 'text-green-600' : 'text-red-600'}`}>
                  {subscriptionStatus.is_active ? 'Activo' : 'Inactivo'}
                </span>
              </div>
              {subscriptionStatus.end_date && (
                <div>
                  <span className="text-sm font-medium text-neutral-500">Vence:</span>
                  <span className="ml-2 text-neutral-900 font-medium">
                    {new Date(subscriptionStatus.end_date).toLocaleDateString()}
                  </span>
                </div>
              )}
            </div>
          </div>
        )}
        
        {error && (
          <div className="mb-6 bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-lg" role="alert">
            <span>{error}</span>
          </div>
        )}

        <div className="grid md:grid-cols-3 gap-6 my-8">
          {plans.map((plan) => (
            <div 
              key={plan.id} 
              className={`border rounded-xl p-6 bg-white shadow-sm
                ${plan.name.toLowerCase() === 'pro' ? 'ring-2 ring-primary-500' : ''} 
                ${currentPlan && currentPlan.name.toLowerCase() === plan.name.toLowerCase() ? 'border-primary-500 bg-primary-50' : 'border-neutral-200'}`}
            >
              {plan.name.toLowerCase() === 'pro' && (
                <div className="flex items-center text-primary-700 mb-2">
                  <FiStar className="mr-1" />
                  <span className="text-sm font-medium">Más popular</span>
                </div>
              )}
              <div className="flex justify-between items-center mb-4">
                <h3 className="text-xl font-semibold text-neutral-900">{plan.name}</h3>
                {currentPlan && currentPlan.name.toLowerCase() === plan.name.toLowerCase() && (
                  <span className="px-2 py-1 bg-primary-100 text-primary-800 text-xs font-medium rounded-full">
                    Plan actual
                  </span>
                )}
              </div>
              <p className="text-3xl font-bold mb-4">
                ${plan.name.toLowerCase() === 'free' ? '0' : 
                  plan.name.toLowerCase() === 'pro' ? '19.900' : '24.900'}
                <span className="text-sm text-neutral-500 font-normal">/mes</span>
              </p>
              <ul className="space-y-4 mb-8">
                <li className="flex items-start">
                  <FiCheck className="text-green-500 mt-1 mr-2 flex-shrink-0" />
                  <span>{plan.course_limit === -1 ? 'Cursos ilimitados' : `${plan.course_limit} cursos`}</span>
                </li>
                <li className="flex items-start">
                  <FiCheck className="text-green-500 mt-1 mr-2 flex-shrink-0" />
                  <span>{plan.description}</span>
                </li>
                {plan.name.toLowerCase() === 'pro' && (
                  <li className="flex items-start">
                    <FiCheck className="text-green-500 mt-1 mr-2 flex-shrink-0" />
                    <span>Soporte prioritario</span>
                  </li>
                )}
                {plan.name.toLowerCase() === 'unlimited' && (
                  <>
                    <li className="flex items-start">
                      <FiCheck className="text-green-500 mt-1 mr-2 flex-shrink-0" />
                      <span>Soporte prioritario</span>
                    </li>
                    <li className="flex items-start">
                      <FiCheck className="text-green-500 mt-1 mr-2 flex-shrink-0" />
                      <span>Recursos adicionales</span>
                    </li>
                  </>
                )}
              </ul>
              <button 
                onClick={() => handleSelectPlan(plan)}
                className={`w-full py-3 px-4 rounded-lg transition-colors 
                  ${currentPlan && currentPlan.name.toLowerCase() === plan.name.toLowerCase()
                    ? 'border border-primary-500 text-primary-700 bg-primary-50 hover:bg-primary-100'
                    : plan.name.toLowerCase() === 'pro'
                      ? 'bg-primary-600 text-white hover:bg-primary-700' 
                      : plan.name.toLowerCase() === 'free'
                        ? 'border border-neutral-300 text-neutral-700 bg-white hover:bg-neutral-50'
                        : 'bg-primary-500 text-white hover:bg-primary-600'
                  }
                  disabled:opacity-50 disabled:cursor-not-allowed
                `}
                disabled={currentPlan && currentPlan.name.toLowerCase() === plan.name.toLowerCase()}
              >
                {currentPlan && currentPlan.name.toLowerCase() === plan.name.toLowerCase() 
                  ? 'Plan actual' 
                  : 'Seleccionar plan'}
              </button>
            </div>
          ))}
        </div>

        <div className="bg-white p-6 rounded-lg border border-neutral-200 mb-8">
          <h2 className="text-xl font-semibold text-neutral-900 mb-4">Preguntas frecuentes</h2>
          <div className="space-y-6">
            <div>
              <h3 className="text-lg font-medium text-neutral-900 mb-2">¿Cómo funciona la facturación?</h3>
              <p className="text-neutral-700">
                Los planes se facturan mensualmente. Puedes cancelar tu suscripción en cualquier momento.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-medium text-neutral-900 mb-2">¿Puedo cambiar de plan?</h3>
              <p className="text-neutral-700">
                Sí, puedes actualizar o degradar tu plan en cualquier momento. Los cambios se aplicarán inmediatamente.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-medium text-neutral-900 mb-2">¿Qué pasa con mis cursos si cancelo?</h3>
              <p className="text-neutral-700">
                Tus cursos existentes permanecerán en tu cuenta, pero no podrás crear nuevos cursos si excedes el límite de tu plan.
              </p>
            </div>
          </div>
        </div>
      </div>
    </Layout>
  );
};

export default PlansPage; 