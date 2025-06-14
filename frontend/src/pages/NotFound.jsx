import React from 'react';
import { Link } from 'react-router-dom';

function NotFound() {
  return (
    <div className="max-w-2xl mx-auto text-center space-y-8 py-16">
      <div>
        <h1 className="text-6xl font-bold text-secondary-800 mb-4">404</h1>
        <h2 className="text-2xl font-semibold text-secondary-700 mb-4">Page Not Found</h2>
        <p className="text-lg text-secondary-600">Sorry, the page you're looking for doesn't exist.</p>
      </div>
      
      <div className="card">
        <h3 className="text-xl font-semibold text-secondary-800 mb-6">What would you like to do?</h3>
        <div className="flex flex-col sm:flex-row gap-4 justify-center">
          <Link to="/" className="btn-primary">
            Return to Home
          </Link>
          <Link to="/products" className="btn-secondary">
            Browse Products
          </Link>
        </div>
      </div>
    </div>
  );
}

export default NotFound;