import React, { useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useCartContext } from '../../contexts/CartContext';

function Header() {
  const location = useLocation();
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const { cartItemCount } = useCartContext();
  
  // Mobile menu toggle
  const toggleMobileMenu = () => {
    setIsMobileMenuOpen(!isMobileMenuOpen);
  };
  
  // Close mobile menu when route changes
  useEffect(() => {
    setIsMobileMenuOpen(false);
  }, [location.pathname]);
  
  // Active navigation helper
  const isActive = (path) => {
    return location.pathname === path;
  };
  
  return (
    <header className="bg-gradient-primary text-white sticky top-0 z-50 shadow-lg">
      <div className="max-w-7xl mx-auto px-4">
        <div className="flex justify-between items-center py-4">
          {/* Logo/Brand */}
          <Link 
            to="/" 
            className="text-xl font-bold hover:opacity-90 transition-opacity duration-200"
            aria-label="Local Producer - Home"
          >
            🌱 Local Producer
          </Link>
          
          {/* Desktop Navigation */}
          <nav className="hidden md:flex space-x-1" aria-label="Main navigation">
            <Link 
              to="/" 
              className={`nav-link ${isActive('/') ? 'nav-link-active' : ''}`}
              aria-current={isActive('/') ? 'page' : undefined}
            >
              Acasă
            </Link>
            <Link 
              to="/products" 
              className={`nav-link ${isActive('/products') ? 'nav-link-active' : ''}`}
              aria-current={isActive('/products') ? 'page' : undefined}
            >
              Produse
            </Link>
            <Link 
              to="/cart" 
              className={`nav-link ${isActive('/cart') ? 'nav-link-active' : ''}`}
              aria-current={isActive('/cart') ? 'page' : undefined}
            >
              Coș
            </Link>
          </nav>
          
          {/* Desktop Cart & Mobile Menu Button */}
          <div className="flex items-center space-x-4">
            {/* Desktop Cart Icon */}
            <Link 
              to="/cart" 
              className="hidden sm:flex nav-link items-center space-x-2 relative min-h-[44px] min-w-[44px] justify-center"
              aria-label={`Coș de cumpărături cu ${cartItemCount} produse`}
            >
              <div className="relative">
                <span className="text-xl">🛒</span>
                {cartItemCount > 0 && (
                  <span className="absolute -top-2 -right-2 bg-red-500 text-white text-xs rounded-full h-5 w-5 flex items-center justify-center font-bold">
                    {cartItemCount > 99 ? '99+' : cartItemCount}
                  </span>
                )}
              </div>
              <span className="hidden lg:inline">Coș</span>
            </Link>
            
            {/* Mobile Menu Button */}
            <button
              type="button"
              onClick={toggleMobileMenu}
              className="md:hidden nav-link p-2 min-h-[44px] min-w-[44px] flex items-center justify-center"
              aria-expanded={isMobileMenuOpen}
              aria-controls="mobile-menu"
              aria-label="Deschide meniul mobil"
            >
              <span className="sr-only">Deschide meniul principal</span>
              {isMobileMenuOpen ? (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              ) : (
                <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
                </svg>
              )}
            </button>
          </div>
        </div>
        
        {/* Mobile Navigation Menu */}
        <div 
          id="mobile-menu"
          className={`md:hidden transition-all duration-300 ease-in-out ${
            isMobileMenuOpen 
              ? 'max-h-64 opacity-100 border-t border-white border-opacity-20 pt-4 pb-2' 
              : 'max-h-0 opacity-0 overflow-hidden'
          }`}
        >
          <nav className="flex flex-col space-y-2" aria-label="Mobile navigation">
            <Link 
              to="/" 
              className={`nav-link text-center py-3 min-h-[44px] flex items-center justify-center ${isActive('/') ? 'nav-link-active' : ''}`}
              aria-current={isActive('/') ? 'page' : undefined}
            >
              🏠 Acasă
            </Link>
            <Link 
              to="/products" 
              className={`nav-link text-center py-3 min-h-[44px] flex items-center justify-center ${isActive('/products') ? 'nav-link-active' : ''}`}
              aria-current={isActive('/products') ? 'page' : undefined}
            >
              🛍️ Produse
            </Link>
            <Link 
              to="/cart" 
              className={`nav-link text-center py-3 relative min-h-[44px] flex items-center justify-center ${isActive('/cart') ? 'nav-link-active' : ''}`}
              aria-current={isActive('/cart') ? 'page' : undefined}
              aria-label={`Coș de cumpărături cu ${cartItemCount} produse`}
            >
              <div className="flex items-center justify-center space-x-2">
                <div className="relative">
                  <span>🛒</span>
                  {cartItemCount > 0 && (
                    <span className="absolute -top-1 -right-1 bg-red-500 text-white text-xs rounded-full h-4 w-4 flex items-center justify-center font-bold">
                      {cartItemCount > 99 ? '99+' : cartItemCount}
                    </span>
                  )}
                </div>
                <span>Coș</span>
              </div>
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}

export default Header;