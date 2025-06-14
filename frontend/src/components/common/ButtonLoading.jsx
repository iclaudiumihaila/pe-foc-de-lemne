import React from 'react';
import { DotsLoading } from './Loading';

// Loading button component for form submissions and async actions
const ButtonLoading = ({
  children,
  loading = false,
  disabled = false,
  loadingText = 'Se procesează...',
  variant = 'primary',
  size = 'medium',
  type = 'button',
  onClick,
  className = '',
  icon = null,
  loadingIcon = 'spinner',
  fullWidth = false,
  ...props
}) => {
  // Variant styles
  const variantStyles = {
    primary: 'bg-green-600 hover:bg-green-700 text-white border-green-600 focus:ring-green-500',
    secondary: 'bg-gray-600 hover:bg-gray-700 text-white border-gray-600 focus:ring-gray-500',
    outline: 'bg-transparent hover:bg-green-50 text-green-600 border-green-600 focus:ring-green-500',
    danger: 'bg-red-600 hover:bg-red-700 text-white border-red-600 focus:ring-red-500',
    success: 'bg-green-600 hover:bg-green-700 text-white border-green-600 focus:ring-green-500',
    warning: 'bg-yellow-600 hover:bg-yellow-700 text-white border-yellow-600 focus:ring-yellow-500'
  };

  // Size styles
  const sizeStyles = {
    small: 'px-3 py-1.5 text-sm min-h-[32px]',
    medium: 'px-4 py-2 text-sm min-h-[40px]',
    large: 'px-6 py-3 text-base min-h-[48px]'
  };

  // Disabled styles when loading or disabled
  const disabledStyles = 'opacity-50 cursor-not-allowed';

  const isDisabled = loading || disabled;

  const buttonClasses = `
    inline-flex
    items-center
    justify-center
    border
    rounded-md
    font-medium
    transition-all
    duration-200
    focus:outline-none
    focus:ring-2
    focus:ring-offset-2
    ${sizeStyles[size]}
    ${variantStyles[variant]}
    ${isDisabled ? disabledStyles : ''}
    ${fullWidth ? 'w-full' : ''}
    ${className}
  `.trim().replace(/\s+/g, ' ');

  const renderLoadingIcon = () => {
    switch (loadingIcon) {
      case 'dots':
        return <DotsLoading className="mr-2" color="white" />;
      case 'spinner':
      default:
        return (
          <svg 
            className="animate-spin -ml-1 mr-2 h-4 w-4 text-current" 
            xmlns="http://www.w3.org/2000/svg" 
            fill="none" 
            viewBox="0 0 24 24"
          >
            <circle 
              className="opacity-25" 
              cx="12" 
              cy="12" 
              r="10" 
              stroke="currentColor" 
              strokeWidth="4"
            />
            <path 
              className="opacity-75" 
              fill="currentColor" 
              d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
            />
          </svg>
        );
    }
  };

  const renderContent = () => {
    if (loading) {
      return (
        <>
          {renderLoadingIcon()}
          <span>{loadingText}</span>
        </>
      );
    }

    return (
      <>
        {icon && <span className="mr-2">{icon}</span>}
        {children}
      </>
    );
  };

  return (
    <button
      type={type}
      onClick={isDisabled ? undefined : onClick}
      disabled={isDisabled}
      className={buttonClasses}
      aria-label={loading ? loadingText : undefined}
      role="button"
      {...props}
    >
      {renderContent()}
    </button>
  );
};

// Specialized button variants
export const SubmitButton = ({ 
  children = 'Trimite', 
  loadingText = 'Se trimite...', 
  ...props 
}) => (
  <ButtonLoading
    type="submit"
    variant="primary"
    loadingText={loadingText}
    {...props}
  >
    {children}
  </ButtonLoading>
);

export const SaveButton = ({ 
  children = 'Salvează', 
  loadingText = 'Se salvează...', 
  ...props 
}) => (
  <ButtonLoading
    type="submit"
    variant="success"
    loadingText={loadingText}
    icon="💾"
    {...props}
  >
    {children}
  </ButtonLoading>
);

export const DeleteButton = ({ 
  children = 'Șterge', 
  loadingText = 'Se șterge...', 
  ...props 
}) => (
  <ButtonLoading
    variant="danger"
    loadingText={loadingText}
    icon="🗑️"
    {...props}
  >
    {children}
  </ButtonLoading>
);

export const CancelButton = ({ 
  children = 'Anulează', 
  ...props 
}) => (
  <ButtonLoading
    variant="outline"
    {...props}
  >
    {children}
  </ButtonLoading>
);

export const LoadMoreButton = ({ 
  children = 'Încarcă mai mult', 
  loadingText = 'Se încarcă...', 
  ...props 
}) => (
  <ButtonLoading
    variant="outline"
    loadingText={loadingText}
    icon="⬇️"
    {...props}
  >
    {children}
  </ButtonLoading>
);

export const RefreshButton = ({ 
  children = 'Actualizează', 
  loadingText = 'Se actualizează...', 
  ...props 
}) => (
  <ButtonLoading
    variant="outline"
    loadingText={loadingText}
    icon="🔄"
    {...props}
  >
    {children}
  </ButtonLoading>
);

export const AddToCartButton = ({ 
  children = 'Adaugă în coș', 
  loadingText = 'Se adaugă...', 
  ...props 
}) => (
  <ButtonLoading
    variant="primary"
    loadingText={loadingText}
    icon="🛒"
    {...props}
  >
    {children}
  </ButtonLoading>
);

export const CheckoutButton = ({ 
  children = 'Finalizează comanda', 
  loadingText = 'Se procesează...', 
  ...props 
}) => (
  <ButtonLoading
    variant="primary"
    size="large"
    fullWidth={true}
    loadingText={loadingText}
    icon="✅"
    {...props}
  >
    {children}
  </ButtonLoading>
);

export const LoginButton = ({ 
  children = 'Conectează-te', 
  loadingText = 'Se conectează...', 
  ...props 
}) => (
  <ButtonLoading
    type="submit"
    variant="primary"
    fullWidth={true}
    loadingText={loadingText}
    icon="🔐"
    {...props}
  >
    {children}
  </ButtonLoading>
);

export const VerifyButton = ({ 
  children = 'Verifică', 
  loadingText = 'Se verifică...', 
  ...props 
}) => (
  <ButtonLoading
    type="submit"
    variant="primary"
    loadingText={loadingText}
    icon="✅"
    {...props}
  >
    {children}
  </ButtonLoading>
);

export default ButtonLoading;