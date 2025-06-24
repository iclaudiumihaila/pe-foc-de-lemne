import React from 'react';
import { AlertCircle } from 'lucide-react';

// Form Field Component
export const FormField = ({ 
  label, 
  name, 
  type = 'text', 
  value, 
  onChange, 
  error, 
  required = false,
  placeholder,
  disabled = false,
  options = [], // for select fields
  rows = 3, // for textarea
  className = ''
}) => {
  const inputClasses = `mt-1 block w-full rounded-md border-gray-300 dark:border-gray-600 dark:bg-gray-700 dark:text-white shadow-sm focus:border-orange-500 focus:ring-orange-500 sm:text-sm ${
    error ? 'border-red-300 dark:border-red-600' : ''
  } ${disabled ? 'bg-gray-100 dark:bg-gray-800 cursor-not-allowed' : ''}`;

  const renderField = () => {
    switch (type) {
      case 'select':
        return (
          <select
            name={name}
            value={value}
            onChange={onChange}
            disabled={disabled}
            className={inputClasses}
            required={required}
          >
            <option value="">Select {label}</option>
            {options.map(option => (
              <option key={option.value} value={option.value}>
                {option.label}
              </option>
            ))}
          </select>
        );
      
      case 'textarea':
        return (
          <textarea
            name={name}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            disabled={disabled}
            rows={rows}
            className={inputClasses}
            required={required}
          />
        );
      
      case 'number':
        return (
          <input
            type="number"
            name={name}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            disabled={disabled}
            className={inputClasses}
            required={required}
            step="any"
          />
        );
      
      default:
        return (
          <input
            type={type}
            name={name}
            value={value}
            onChange={onChange}
            placeholder={placeholder}
            disabled={disabled}
            className={inputClasses}
            required={required}
          />
        );
    }
  };

  return (
    <div className={className}>
      <label htmlFor={name} className="block text-sm font-medium text-gray-700 dark:text-gray-300">
        {label} {required && <span className="text-red-500">*</span>}
      </label>
      {renderField()}
      {error && (
        <p className="mt-1 text-sm text-red-600 dark:text-red-400 flex items-center">
          <AlertCircle className="h-4 w-4 mr-1" />
          {error}
        </p>
      )}
    </div>
  );
};

// Form Actions Component
export const FormActions = ({ 
  onCancel, 
  onSubmit, 
  submitText = 'Save', 
  cancelText = 'Cancel',
  isSubmitting = false,
  className = '' 
}) => {
  return (
    <div className={`flex justify-end space-x-3 ${className}`}>
      <button
        type="button"
        onClick={onCancel}
        disabled={isSubmitting}
        className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {cancelText}
      </button>
      <button
        type="submit"
        onClick={onSubmit}
        disabled={isSubmitting}
        className="px-4 py-2 text-sm font-medium text-white bg-orange-600 border border-transparent rounded-md hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
      >
        {isSubmitting ? 'Saving...' : submitText}
      </button>
    </div>
  );
};

// Form Container Component
export const FormContainer = ({ children, onSubmit, className = '' }) => {
  const handleSubmit = (e) => {
    e.preventDefault();
    if (onSubmit) onSubmit(e);
  };

  return (
    <form onSubmit={handleSubmit} className={`space-y-6 ${className}`}>
      {children}
    </form>
  );
};

// Form Section Component
export const FormSection = ({ title, description, children, className = '' }) => {
  return (
    <div className={`${className}`}>
      {(title || description) && (
        <div className="mb-4">
          {title && (
            <h3 className="text-lg font-medium text-gray-900 dark:text-white">
              {title}
            </h3>
          )}
          {description && (
            <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
              {description}
            </p>
          )}
        </div>
      )}
      <div className="space-y-4">
        {children}
      </div>
    </div>
  );
};

// Form Error Alert Component
export const FormError = ({ error, className = '' }) => {
  if (!error) return null;

  return (
    <div className={`rounded-md bg-red-50 dark:bg-red-900/20 p-4 ${className}`}>
      <div className="flex">
        <div className="flex-shrink-0">
          <AlertCircle className="h-5 w-5 text-red-400" />
        </div>
        <div className="ml-3">
          <p className="text-sm font-medium text-red-800 dark:text-red-400">
            {error}
          </p>
        </div>
      </div>
    </div>
  );
};

// Validation utilities
export const validateRequired = (value, fieldName) => {
  if (!value || value.toString().trim() === '') {
    return `${fieldName} is required`;
  }
  return null;
};

export const validateEmail = (email) => {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!email) return 'Email is required';
  if (!emailRegex.test(email)) return 'Invalid email address';
  return null;
};

export const validatePhone = (phone) => {
  const phoneRegex = /^[0-9]{10}$/;
  if (!phone) return 'Phone number is required';
  if (!phoneRegex.test(phone.replace(/\D/g, ''))) return 'Invalid phone number';
  return null;
};

export const validateNumber = (value, fieldName, min, max) => {
  const num = parseFloat(value);
  if (isNaN(num)) return `${fieldName} must be a number`;
  if (min !== undefined && num < min) return `${fieldName} must be at least ${min}`;
  if (max !== undefined && num > max) return `${fieldName} must be at most ${max}`;
  return null;
};

// Export all components
const AdminForm = {
  Container: FormContainer,
  Field: FormField,
  Actions: FormActions,
  Section: FormSection,
  Error: FormError,
  validate: {
    required: validateRequired,
    email: validateEmail,
    phone: validatePhone,
    number: validateNumber
  }
};

export default AdminForm;