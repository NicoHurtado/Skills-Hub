import React, { useState, useEffect, useContext } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { FiHome, FiPlus, FiLogOut, FiMenu, FiX, FiCreditCard } from 'react-icons/fi';
import axios from 'axios';
import ThemeToggle from './ThemeToggle';
import { ThemeContext } from '../context/ThemeContext';

const Layout = ({ children }) => {
  const { user, logout } = useAuth();
  const { darkMode } = useContext(ThemeContext);
  const navigate = useNavigate();
  const location = useLocation();
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [subscriptionPlan, setSubscriptionPlan] = useState('Free');
  const [planLoading, setPlanLoading] = useState(true);

  useEffect(() => {
    // Solo cargar si el usuario está autenticado
    if (user) {
      const fetchSubscriptionStatus = async () => {
        try {
          const response = await axios.get('http://localhost:8000/subscription-status', {
            headers: {
              Authorization: `Bearer ${localStorage.getItem('token')}`
            }
          });
          
          setSubscriptionPlan(response.data.tier.name);
          setPlanLoading(false);
        } catch (err) {
          console.error('Error fetching subscription:', err);
          setPlanLoading(false);
        }
      };
      
      fetchSubscriptionStatus();
    }
  }, [user]);

  const handleLogout = () => {
    logout();
    navigate('/login');
  };

  const navigation = [
    { name: 'Dashboard', href: '/dashboard', icon: FiHome },
    { name: 'Crear Curso', href: '/generate', icon: FiPlus },
    { name: 'Planes', href: '/plans', icon: FiCreditCard },
  ];

  // Simplificamos las clases para asegurar la visibilidad del texto
  const bgClass = darkMode ? 'bg-neutral-900' : 'bg-white';
  const sidebarClass = darkMode ? 'bg-neutral-800 border-neutral-700' : 'bg-white border-neutral-200';
  const headerClass = darkMode ? 'bg-neutral-800 border-neutral-700' : 'bg-white border-neutral-200';
  const textClass = darkMode ? 'text-white' : 'text-neutral-900';
  const textSecondaryClass = darkMode ? 'text-neutral-300' : 'text-neutral-600';
  const navItemActiveClass = darkMode 
    ? 'bg-primary-900/30 text-primary-400' 
    : 'bg-primary-50 text-primary-700';
  const navItemClass = darkMode
    ? 'text-white hover:bg-neutral-700/50'
    : 'text-neutral-900 hover:bg-neutral-100';

  return (
    <div className={`h-screen flex overflow-hidden ${bgClass} transition-colors duration-300`}>
      {/* Mobile sidebar overlay */}
      {sidebarOpen && (
        <div
          className="fixed inset-0 z-40 bg-neutral-900 bg-opacity-75 md:hidden"
          onClick={() => setSidebarOpen(false)}
        />
      )}

      {/* Mobile sidebar */}
      <div
        className={`fixed inset-y-0 left-0 flex flex-col z-50 w-64 shadow-xl transition-transform duration-300 ease-in-out transform ${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } md:hidden ${sidebarClass}`}
      >
        <div className={`flex items-center justify-between p-4 border-b ${headerClass}`}>
          <h2 className="text-xl font-semibold text-primary-600">Prompt2Course</h2>
          <button
            onClick={() => setSidebarOpen(false)}
            className={`p-2 rounded-md ${textSecondaryClass} hover:${textClass} hover:bg-neutral-100 dark:hover:bg-neutral-700`}
          >
            <FiX size={24} />
          </button>
        </div>

        <div className="flex-1 flex flex-col overflow-y-auto pt-5 pb-4">
          <nav className="flex-1 px-2 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-4 py-3 rounded-lg text-sm font-medium ${
                    isActive
                      ? navItemActiveClass
                      : navItemClass
                  }`}
                >
                  <item.icon
                    size={20}
                    className={`mr-3 ${
                      isActive ? 'text-primary-600 dark:text-primary-400' : textSecondaryClass
                    }`}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className={`p-4 border-t ${headerClass}`}>
          {/* Theme Toggle */}
          <div className="mb-4">
            <ThemeToggle />
          </div>
          
          {user && (
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center text-white font-medium text-lg">
                  {user.username.charAt(0).toUpperCase()}
                </div>
              </div>
              <div className="ml-3">
                <p className={`text-sm font-medium ${textClass}`}>{user.username}</p>
                <p className={`text-xs ${textSecondaryClass} truncate`}>{user.email}</p>
                {!planLoading && (
                  <div className="mt-1 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-800 dark:text-primary-400">
                    Plan {subscriptionPlan}
                  </div>
                )}
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className={`w-full flex items-center px-4 py-2 text-sm ${textClass} rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700/50`}
          >
            <FiLogOut className={`mr-3 ${textSecondaryClass}`} />
            Cerrar sesión
          </button>
        </div>
      </div>

      {/* Desktop sidebar */}
      <div className={`hidden md:flex md:flex-col md:w-64 md:fixed md:inset-y-0 border-r ${sidebarClass}`}>
        <div className={`flex items-center justify-between h-16 px-4 border-b ${headerClass}`}>
          <h2 className="text-xl font-semibold text-primary-600">Prompt2Course</h2>
        </div>

        <div className="flex-1 flex flex-col overflow-y-auto pt-5 pb-4">
          <nav className="flex-1 px-2 space-y-1">
            {navigation.map((item) => {
              const isActive = location.pathname === item.href;
              return (
                <Link
                  key={item.name}
                  to={item.href}
                  className={`flex items-center px-4 py-3 rounded-lg text-sm font-medium ${
                    isActive
                      ? navItemActiveClass
                      : navItemClass
                  }`}
                >
                  <item.icon
                    size={20}
                    className={`mr-3 ${
                      isActive ? 'text-primary-600 dark:text-primary-400' : textSecondaryClass
                    }`}
                  />
                  {item.name}
                </Link>
              );
            })}
          </nav>
        </div>

        <div className={`p-4 border-t ${headerClass}`}>
          {/* Theme Toggle */}
          <div className="mb-4">
            <ThemeToggle />
          </div>
          
          {user && (
            <div className="flex items-center mb-4">
              <div className="flex-shrink-0">
                <div className="w-10 h-10 rounded-full bg-primary-600 flex items-center justify-center text-white font-medium text-lg">
                  {user.username.charAt(0).toUpperCase()}
                </div>
              </div>
              <div className="ml-3">
                <p className={`text-sm font-medium ${textClass}`}>{user.username}</p>
                <p className={`text-xs ${textSecondaryClass} truncate`}>{user.email}</p>
                {!planLoading && (
                  <div className="mt-1 inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-primary-100 dark:bg-primary-900/30 text-primary-800 dark:text-primary-400">
                    Plan {subscriptionPlan}
                  </div>
                )}
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className={`w-full flex items-center px-4 py-2 text-sm ${textClass} rounded-lg hover:bg-neutral-100 dark:hover:bg-neutral-700/50`}
          >
            <FiLogOut className={`mr-3 ${textSecondaryClass}`} />
            Cerrar sesión
          </button>
        </div>
      </div>

      {/* Main content */}
      <div className="flex flex-col w-0 flex-1 md:ml-64">
        {/* Mobile header */}
        <div className={`flex items-center justify-between md:hidden h-16 px-4 border-b ${headerClass}`}>
          <h2 className="text-xl font-semibold text-primary-600">Prompt2Course</h2>
          
          <div className="flex items-center space-x-4">
            {/* Theme toggle en la barra superior móvil */}
            <ThemeToggle />
            
            <button
              onClick={() => setSidebarOpen(true)}
              className={`p-2 rounded-md ${textSecondaryClass} hover:${textClass} hover:bg-neutral-100 dark:hover:bg-neutral-700`}
            >
              <FiMenu size={24} />
            </button>
          </div>
        </div>
        
        {/* Page content */}
        <main className="flex-1 relative overflow-y-auto focus:outline-none">
          <div className="py-6 px-4 sm:px-6 lg:px-8">{children}</div>
        </main>
      </div>
    </div>
  );
};

export default Layout; 