import React, { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import ErrorMessage, { FormError } from '../components/common/ErrorMessage';
import Loading from '../components/common/Loading';

const AdminLogin = () => {
  const navigate = useNavigate();
  const { login, isAuthenticated, isLoading, error, clearError } = useAuth();

  // Form state
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });

  // Validation state
  const [validation, setValidation] = useState({
    username: '',
    password: ''
  });

  // Form submission state
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [showPassword, setShowPassword] = useState(false);

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/admin/dashboard', { replace: true });
    }
  }, [isAuthenticated, navigate]);

  // Clear auth error when component mounts
  useEffect(() => {
    clearError();
  }, [clearError]);

  // Romanian phone number validation
  const validatePhoneNumber = (phone) => {
    const phoneRegex = /^(\+40|0040|0)[0-9]{9}$/;
    const cleanPhone = phone.replace(/\s|-/g, '');
    return phoneRegex.test(cleanPhone);
  };

  // Form validation
  const validateField = (name, value) => {
    switch (name) {
      case 'username':
        if (!value.trim()) {
          return 'Numele de utilizator este obligatoriu';
        }
        if (value.trim().length < 10) {
          return 'Numele de utilizator trebuie să aibă cel puțin 10 caractere';
        }
        if (value.includes('@')) {
          // Email format validation could be added here
          return '';
        }
        if (!validatePhoneNumber(value)) {
          return 'Formatul numărului de telefon nu este valid (ex: +40722123456)';
        }
        return '';

      case 'password':
        if (!value) {
          return 'Parola este obligatorie';
        }
        if (value.length < 8) {
          return 'Parola trebuie să aibă cel puțin 8 caractere';
        }
        return '';

      default:
        return '';
    }
  };

  // Handle input change
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));

    // Clear previous validation error
    if (validation[name]) {
      setValidation(prev => ({
        ...prev,
        [name]: ''
      }));
    }

    // Clear auth error when user starts typing
    if (error) {
      clearError();
    }
  };

  // Handle input blur (for real-time validation)
  const handleInputBlur = (e) => {
    const { name, value } = e.target;
    const validationError = validateField(name, value);
    
    setValidation(prev => ({
      ...prev,
      [name]: validationError
    }));
  };

  // Validate entire form
  const validateForm = () => {
    const newValidation = {
      username: validateField('username', formData.username),
      password: validateField('password', formData.password)
    };

    setValidation(newValidation);

    // Return true if no validation errors
    return !Object.values(newValidation).some(error => error !== '');
  };

  // Handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    
    // Clear any existing errors
    clearError();
    
    // Validate form
    if (!validateForm()) {
      return;
    }

    setIsSubmitting(true);

    try {
      const result = await login({
        username: formData.username.trim(),
        password: formData.password
      });

      if (result.success) {
        // Login successful - AuthContext will handle redirect via useEffect
        navigate('/admin/dashboard', { replace: true });
      }
      // If login fails, error will be handled by AuthContext and displayed
    } catch (error) {
      console.error('Login error:', error);
      // Error handling is managed by AuthContext
    } finally {
      setIsSubmitting(false);
    }
  };

  // Handle password visibility toggle
  const togglePasswordVisibility = () => {
    setShowPassword(!showPassword);
  };

  // Form loading state
  const isFormLoading = isLoading || isSubmitting;

  return (
    <div className="min-h-screen bg-gradient-to-br from-green-50 to-orange-50 flex items-center justify-center py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-md w-full space-y-8">
        {/* Header */}
        <div className="text-center">
          <Link to="/" className="inline-block">
            <h1 className="text-3xl font-bold text-green-800 mb-2">
              Pe Foc de Lemne
            </h1>
          </Link>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">
            Autentificare Administrator
          </h2>
          <p className="text-sm text-gray-600">
            Introduceți datele de acces pentru a gestiona platforma
          </p>
        </div>

        {/* Error Display */}
        {error && (
          <ErrorMessage 
            message={error}
            type="error"
            dismissible={true}
            onDismiss={clearError}
          />
        )}

        {/* Login Form */}
        <form 
          onSubmit={handleSubmit} 
          className="bg-white shadow-lg rounded-lg px-8 pt-8 pb-8 space-y-6"
          noValidate
        >
          {/* Username Field */}
          <div>
            <label 
              htmlFor="username" 
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Nume utilizator / Număr telefon
            </label>
            <div className="relative">
              <input
                id="username"
                name="username"
                type="text"
                autoComplete="username"
                required
                value={formData.username}
                onChange={handleInputChange}
                onBlur={handleInputBlur}
                disabled={isFormLoading}
                placeholder="+40722123456 sau admin@example.com"
                className={`
                  appearance-none relative block w-full px-3 py-3 border
                  ${validation.username ? 'border-red-300' : 'border-gray-300'}
                  placeholder-gray-500 text-gray-900 rounded-md
                  focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10
                  disabled:bg-gray-100 disabled:cursor-not-allowed
                  sm:text-sm
                `.trim().replace(/\s+/g, ' ')}
                aria-invalid={validation.username ? 'true' : 'false'}
                aria-describedby={validation.username ? 'username-error' : undefined}
              />
              {validation.username && (
                <div className="absolute inset-y-0 right-0 pr-3 flex items-center pointer-events-none">
                  <span className="text-red-500 text-sm" aria-hidden="true">
                    ⚠️
                  </span>
                </div>
              )}
            </div>
            {validation.username && (
              <FormError 
                error={validation.username}
                id="username-error"
                className="mt-1"
              />
            )}
          </div>

          {/* Password Field */}
          <div>
            <label 
              htmlFor="password" 
              className="block text-sm font-medium text-gray-700 mb-2"
            >
              Parolă
            </label>
            <div className="relative">
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                autoComplete="current-password"
                required
                value={formData.password}
                onChange={handleInputChange}
                onBlur={handleInputBlur}
                disabled={isFormLoading}
                placeholder="Parola de administrator"
                className={`
                  appearance-none relative block w-full px-3 py-3 pr-10 border
                  ${validation.password ? 'border-red-300' : 'border-gray-300'}
                  placeholder-gray-500 text-gray-900 rounded-md
                  focus:outline-none focus:ring-green-500 focus:border-green-500 focus:z-10
                  disabled:bg-gray-100 disabled:cursor-not-allowed
                  sm:text-sm
                `.trim().replace(/\s+/g, ' ')}
                aria-invalid={validation.password ? 'true' : 'false'}
                aria-describedby={validation.password ? 'password-error' : undefined}
              />
              <button
                type="button"
                onClick={togglePasswordVisibility}
                disabled={isFormLoading}
                className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600 focus:outline-none focus:text-gray-600 disabled:cursor-not-allowed"
                aria-label={showPassword ? 'Ascunde parola' : 'Arată parola'}
              >
                <span className="text-sm">
                  {showPassword ? '🙈' : '👁️'}
                </span>
              </button>
            </div>
            {validation.password && (
              <FormError 
                error={validation.password}
                id="password-error"
                className="mt-1"
              />
            )}
          </div>

          {/* Submit Button */}
          <div>
            <button
              type="submit"
              disabled={isFormLoading}
              className={`
                group relative w-full flex justify-center py-3 px-4 border border-transparent
                text-sm font-medium rounded-md text-white
                ${isFormLoading 
                  ? 'bg-gray-400 cursor-not-allowed' 
                  : 'bg-green-600 hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-green-500'
                }
                transition-colors duration-200
              `.trim().replace(/\s+/g, ' ')}
              aria-disabled={isFormLoading}
            >
              {isFormLoading ? (
                <div className="flex items-center">
                  <Loading 
                    size="small" 
                    color="white" 
                    message="Se verifică datele..."
                    className="mr-2"
                  />
                  Se verifică datele...
                </div>
              ) : (
                'Autentificare'
              )}
            </button>
          </div>

          {/* Additional Information */}
          <div className="text-center">
            <p className="text-xs text-gray-500">
              Doar administratorii au acces la această secțiune
            </p>
          </div>
        </form>

        {/* Footer Links */}
        <div className="text-center space-y-2">
          <Link 
            to="/" 
            className="text-sm text-green-600 hover:text-green-500 focus:outline-none focus:underline"
          >
            ← Înapoi la magazin
          </Link>
        </div>
      </div>
    </div>
  );
};

export default AdminLogin;