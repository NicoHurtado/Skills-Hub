import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import axios from 'axios';
import Layout from '../components/Layout';
import { FiCreditCard, FiCheck, FiX } from 'react-icons/fi';

function SimulatedPaymentPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  
  // Obtener los parámetros de la URL
  const searchParams = new URLSearchParams(location.search);
  const reference = searchParams.get('reference');
  const amount = searchParams.get('amount');
  const plan = searchParams.get('plan');
  
  // Manejar la aprobación de pago simulado
  const handleApprovePayment = async () => {
    if (!reference) {
      setError('No se encontró referencia de pago');
      return;
    }
    
    setLoading(true);
    try {
      const token = localStorage.getItem('token');
      if (!token) {
        setError('No hay sesión activa');
        setLoading(false);
        return;
      }
      
      // Guardar la referencia para verificarla en la página de éxito
      localStorage.setItem('pending_payment_reference', reference);
      
      // Aprobar el pago simulado
      await axios.post(
        'http://localhost:8000/approve-simulated-payment',
        { reference },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      
      // Redirigir a la página de éxito
      navigate('/payment-success');
    } catch (err) {
      console.error('Error al aprobar el pago:', err);
      setError(err.response?.data?.detail || 'Error al procesar el pago');
      setLoading(false);
    }
  };
  
  // Manejar la cancelación del pago
  const handleCancelPayment = () => {
    navigate('/pricing');
  };
  
  // Verificar que tenemos todos los datos necesarios
  useEffect(() => {
    if (!reference || !amount || !plan) {
      setError('Información de pago incompleta');
    }
  }, [reference, amount, plan]);
  
  return (
    <Layout>
      <div className="max-w-2xl mx-auto mt-10 p-6 bg-white rounded-lg shadow-lg">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold mb-2">Simulación de Pago</h1>
          <p className="text-gray-600">
            Esta es una página de simulación para pruebas de pago
          </p>
        </div>
        
        {error ? (
          <div className="bg-red-100 border-l-4 border-red-500 text-red-700 p-4 mb-6">
            <p>{error}</p>
          </div>
        ) : (
          <>
            <div className="border rounded-lg p-4 mb-6">
              <h2 className="text-xl font-semibold mb-4">Resumen de la compra</h2>
              <div className="flex justify-between py-2 border-b">
                <span>Plan:</span>
                <span className="font-medium">{plan}</span>
              </div>
              <div className="flex justify-between py-2 border-b">
                <span>Monto:</span>
                <span className="font-medium">
                  ${Number(amount).toLocaleString('es-CO')}
                </span>
              </div>
              <div className="flex justify-between py-2">
                <span>Referencia:</span>
                <span className="font-mono text-sm">{reference}</span>
              </div>
            </div>
            
            <div className="bg-blue-50 p-4 rounded-lg mb-6">
              <div className="flex items-center text-blue-700 mb-2">
                <FiCreditCard className="mr-2" />
                <span className="font-medium">Modo de Simulación</span>
              </div>
              <p className="text-blue-600 text-sm">
                En un entorno de producción, aquí se mostraría un formulario real de 
                pago. Para esta simulación, simplemente aprueba o cancela la transacción.
              </p>
            </div>
            
            <div className="flex justify-between mt-8">
              <button
                onClick={handleCancelPayment}
                className="px-6 py-2 bg-gray-200 hover:bg-gray-300 rounded-lg flex items-center"
                disabled={loading}
              >
                <FiX className="mr-2" />
                Cancelar
              </button>
              
              <button
                onClick={handleApprovePayment}
                className="px-6 py-2 bg-green-600 hover:bg-green-700 text-white rounded-lg flex items-center"
                disabled={loading}
              >
                {loading ? (
                  <span>Procesando...</span>
                ) : (
                  <>
                    <FiCheck className="mr-2" />
                    Aprobar Pago
                  </>
                )}
              </button>
            </div>
          </>
        )}
      </div>
    </Layout>
  );
}

export default SimulatedPaymentPage; 