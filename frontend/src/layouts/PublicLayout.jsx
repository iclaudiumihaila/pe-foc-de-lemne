import React from 'react';
import { Outlet } from 'react-router-dom';
import Header from '../components/common/Header';

const PublicLayout = () => {
  return (
    <div className="page-container font-sans">
      <Header />
      <main className="main-content">
        <Outlet />
      </main>
      <footer className="bg-secondary-800 text-white py-8 mt-16">
        <div className="max-w-7xl mx-auto px-4 text-center">
          <p className="font-semibold">&copy; 2024 Pe Foc de Lemne - Produse Locale Românești</p>
          <p className="opacity-80 mt-2">Sprijinind producătorii locali și agricultura durabilă</p>
          <div className="mt-4 space-y-2">
            <div className="flex justify-center space-x-6 text-sm">
              <a href="/termeni" className="hover:text-primary-300 transition-colors">
                Termeni și condiții
              </a>
              <a href="/confidentialitate" className="hover:text-primary-300 transition-colors">
                Politica de confidențialitate
              </a>
              <a href="/contact" className="hover:text-primary-300 transition-colors">
                Contact
              </a>
            </div>
            <p className="text-xs opacity-60">
              Marketplace pentru produse locale românești de la producători verificați
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default PublicLayout;