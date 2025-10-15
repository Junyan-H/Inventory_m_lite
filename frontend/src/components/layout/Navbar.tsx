import React from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useApp } from '@/context/AppContext';

export const Navbar: React.FC = () => {
  const location = useLocation();
  const { currentLocation, setCurrentLocation, currentUserLdap, setCurrentUserLdap } = useApp();

  const isActive = (path: string) => location.pathname === path;

  const navLinks = [
    { path: '/', label: 'Dashboard' },
    { path: '/inventory', label: 'Inventory' },
    { path: '/checkouts', label: 'Active Checkouts' },
    { path: '/overdue', label: 'Overdue' },
  ];

  return (
    <nav className="bg-white shadow-md">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex justify-between h-16">
          <div className="flex">
            <div className="flex-shrink-0 flex items-center">
              <Link to="/" className="text-xl font-bold text-primary-600">
                Inventory Management
              </Link>
            </div>
            <div className="hidden sm:ml-6 sm:flex sm:space-x-8">
              {navLinks.map((link) => (
                <Link
                  key={link.path}
                  to={link.path}
                  className={`inline-flex items-center px-1 pt-1 border-b-2 text-sm font-medium ${
                    isActive(link.path)
                      ? 'border-primary-500 text-gray-900'
                      : 'border-transparent text-gray-500 hover:border-gray-300 hover:text-gray-700'
                  }`}
                >
                  {link.label}
                </Link>
              ))}
            </div>
          </div>
          <div className="flex items-center space-x-4">
            <select
              value={currentLocation}
              onChange={(e) => setCurrentLocation(e.target.value)}
              className="input py-1 text-sm"
            >
              <option value="san_jose">San Jose</option>
              <option value="3k">3K</option>
              <option value="2u">2U</option>
            </select>
            {currentUserLdap && (
              <div className="flex items-center space-x-2">
                <span className="text-sm text-gray-700">{currentUserLdap}</span>
                <button
                  onClick={() => setCurrentUserLdap(null)}
                  className="text-sm text-gray-500 hover:text-gray-700"
                >
                  Logout
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </nav>
  );
};