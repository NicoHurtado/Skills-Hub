import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { FiCheck, FiX, FiLoader } from 'react-icons/fi';
import Layout from '../components/Layout';
import axios from 'axios';

const PaymentSuccessPage = () => {
  const navigate = useNavigate();
  const [status, setStatus] = useState('loading'); // loading, success, error
  const [message, setMessage] = useState('');
  const [plan, setPlan] = useState(null);

  useEffect(() => {
    const checkPayment = async () => {
      // Obtener la referencia del pago pendiente
      const reference = localStorage.getItem('pending_payment_reference');
      
      if (!reference) {
        setStatus('error');
        setMessage('No se encontró información del pago');
        return;
      }
      
      try {
        // Verificar el estado del pago en el servidor
        const response = await axios.post(
          'http://localhost:8000/verify-payment',
          { reference },
          { headers: { Authorization: `Bearer ${localStorage.getItem('token')}` } }
        );
        
        if (response.data.success) {
          setStatus('success');
          setMessage(response.data.message);
          setPlan(response.data.plan);
          
          // Limpiar la referencia del pago
          localStorage.removeItem('pending_payment_reference');
        } else {
          setStatus('error');
          setMessage(response.data.message);
        }
      } catch (err) {
        console.error('Error al verificar el pago:', err);
        setStatus('error');
        setMessage('Error al verificar el estado del pago');
      }
    };
    
    checkPayment();
  }, []);

  return (
    <Layout>
      <div className="max-w-3xl mx-auto px-4 py-8">
        <div className="bg-white shadow-sm rounded-lg p-8 text-center">
          {status === 'loading' && (
            <div className="py-8">
              <FiLoader className="mx-auto h-12 w-12 text-primary-500 animate-spin" />
              <h2 className="mt-4 text-xl font-semibold text-neutral-900">Verificando tu pago</h2>
              <p className="mt-2 text-neutral-600">Estamos confirmando el estado de tu transacción...</p>
            </div>
          )}
          
          {status === 'success' && (
            <div className="py-8">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-green-100">
                <FiCheck className="h-8 w-8 text-green-600" />
              </div>
              <h2 className="mt-4 text-xl font-semibold text-neutral-900">¡Pago exitoso!</h2>
              <p className="mt-2 text-neutral-600">{message}</p>
              <div className="mt-6 bg-primary-50 rounded-lg p-4 inline-block">
                <p className="text-primary-700 font-medium">
                  Tu plan <span className="font-bold">{plan}</span> ya está activo
                </p>
              </div>
              <div className="mt-8">
                <button
                  onClick={() => navigate('/dashboard')}
                  className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700"
                >
                  Ir al dashboard
                </button>
              </div>
            </div>
          )}
          
          {status === 'error' && (
            <div className="py-8">
              <div className="mx-auto flex items-center justify-center h-16 w-16 rounded-full bg-red-100">
                <FiX className="h-8 w-8 text-red-600" />
              </div>
              <h2 className="mt-4 text-xl font-semibold text-neutral-900">Hubo un problema con el pago</h2>
              <p className="mt-2 text-neutral-600">{message}</p>
              <div className="mt-8">
                <button
                  onClick={() => navigate('/plans')}
                  className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-primary-600 hover:bg-primary-700"
                >
                  Volver a planes
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </Layout>
  );
};

export default PaymentSuccessPage; 