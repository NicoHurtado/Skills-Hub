import React from 'react';
import { Link } from 'react-router-dom';
import { FiArrowLeft } from 'react-icons/fi';

const NotFound = () => {
  return (
    <div className="min-h-screen bg-neutral-50 flex flex-col justify-center items-center">
      <div className="text-center max-w-md px-4">
        <h1 className="text-9xl font-bold text-primary-600">404</h1>
        <h2 className="mt-4 text-3xl font-bold text-neutral-900">Página no encontrada</h2>
        <p className="mt-4 text-neutral-600">
          La página que estás buscando no existe o ha sido movida.
        </p>
        <div className="mt-8">
          <Link
            to="/"
            className="btn btn-primary inline-flex items-center"
          >
            <FiArrowLeft className="mr-2" />
            Volver al inicio
          </Link>
        </div>
      </div>
    </div>
  );
};

export default NotFound; 