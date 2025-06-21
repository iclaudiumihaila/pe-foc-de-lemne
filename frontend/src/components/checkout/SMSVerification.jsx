import React, { useState, useEffect, useRef } from 'react';
import Loading from '../common/Loading';
import ErrorMessage from '../common/ErrorMessage';

const SMSVerification = ({ 
  phoneNumber, 
  onVerificationSuccess, 
  onBack,
  loading = false,
  className = ''
}) => {
  const [verificationCode, setVerificationCode] = useState(['', '', '', '', '', '']);
  const [isVerifying, setIsVerifying] = useState(false);
  const [error, setError] = useState('');
  const [resendCooldown, setResendCooldown] = useState(0);
  const [isResending, setIsResending] = useState(false);
  const inputRefs = useRef([]);

  // Initialize cooldown timer on component mount
  useEffect(() => {
    setResendCooldown(60); // 60 seconds initial cooldown
  }, []);

  // Countdown timer for resend button
  useEffect(() => {
    let timer;
    if (resendCooldown > 0) {
      timer = setTimeout(() => {
        setResendCooldown(resendCooldown - 1);
      }, 1000);
    }
    return () => clearTimeout(timer);
  }, [resendCooldown]);

  // Auto-submit when all 6 digits are entered
  useEffect(() => {
    const code = verificationCode.join('');
    if (code.length === 6 && !isVerifying) {
      handleVerifyCode(code);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [verificationCode, isVerifying]);

  // Format phone number for display (mask middle digits)
  const formatPhoneForDisplay = (phone) => {
    if (!phone) return '';
    // Format: 0712 345 678 -> 0712 *** 678
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 10) {
      return `${cleaned.slice(0, 4)} *** ${cleaned.slice(-3)}`;
    }
    return phone;
  };

  // Handle input change for verification code
  const handleCodeChange = (index, value) => {
    // Only allow digits
    if (!/^\d*$/.test(value)) return;

    const newCode = [...verificationCode];
    newCode[index] = value.slice(-1); // Take only the last digit
    setVerificationCode(newCode);

    // Clear error when user starts typing
    if (error) setError('');

    // Auto-focus next input
    if (value && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  // Handle backspace and navigation
  const handleKeyDown = (index, e) => {
    if (e.key === 'Backspace') {
      if (!verificationCode[index] && index > 0) {
        // If current field is empty, focus previous field
        inputRefs.current[index - 1]?.focus();
      } else {
        // Clear current field
        const newCode = [...verificationCode];
        newCode[index] = '';
        setVerificationCode(newCode);
      }
    } else if (e.key === 'ArrowLeft' && index > 0) {
      inputRefs.current[index - 1]?.focus();
    } else if (e.key === 'ArrowRight' && index < 5) {
      inputRefs.current[index + 1]?.focus();
    }
  };

  // Handle paste event
  const handlePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text').replace(/\D/g, '');
    
    if (pastedData.length === 6) {
      const newCode = pastedData.split('');
      setVerificationCode(newCode);
      // Focus last input
      inputRefs.current[5]?.focus();
    }
  };

  // Mock API call for code verification
  const handleVerifyCode = async (code) => {
    setIsVerifying(true);
    setError('');

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500));
      
      // Mock verification logic (in real app, this would be an API call)
      if (code === '123456') {
        // Success
        onVerificationSuccess({
          phoneNumber,
          verificationCode: code,
          verifiedAt: new Date().toISOString()
        });
      } else {
        // Failure
        setError('Codul introdus este incorect. Verificați și încercați din nou.');
        // Clear the code
        setVerificationCode(['', '', '', '', '', '']);
        inputRefs.current[0]?.focus();
      }
    } catch (err) {
      setError('A apărut o eroare la verificarea codului. Încercați din nou.');
      setVerificationCode(['', '', '', '', '', '']);
      inputRefs.current[0]?.focus();
    } finally {
      setIsVerifying(false);
    }
  };

  // Handle resend code
  const handleResendCode = async () => {
    setIsResending(true);
    setError('');

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      // Reset cooldown
      setResendCooldown(60);
      
      // Show success message
      setError(''); // Clear any existing errors
      
      // In real app, this would trigger SMS sending
      console.log('SMS code resent to:', phoneNumber);
      
    } catch (err) {
      setError('Nu am putut retrimite codul. Încercați din nou.');
    } finally {
      setIsResending(false);
    }
  };

  // Handle manual verification (when user clicks verify button)
  const handleManualVerify = () => {
    const code = verificationCode.join('');
    if (code.length === 6) {
      handleVerifyCode(code);
    } else {
      setError('Introduceți toate cele 6 cifre ale codului.');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loading />
      </div>
    );
  }

  return (
    <div className={`bg-white rounded-lg shadow-sm p-6 ${className}`}>
      <div className="text-center mb-8">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Verificare număr de telefon
        </h2>
        <div className="text-gray-600 space-y-2">
          <p>
            Am trimis un cod de verificare prin SMS la numărul:
          </p>
          <p className="font-medium text-lg text-gray-900">
            {formatPhoneForDisplay(phoneNumber)}
          </p>
          <p className="text-sm">
            Introduceți codul de 6 cifre primit prin SMS
          </p>
        </div>
      </div>

      {/* Verification Code Input */}
      <div className="mb-6">
        <div className="flex justify-center space-x-3 mb-4">
          {verificationCode.map((digit, index) => (
            <input
              key={index}
              ref={el => inputRefs.current[index] = el}
              type="text"
              inputMode="numeric"
              maxLength="1"
              value={digit}
              onChange={(e) => handleCodeChange(index, e.target.value)}
              onKeyDown={(e) => handleKeyDown(index, e)}
              onPaste={handlePaste}
              className={`w-12 h-12 text-center text-xl font-bold border-2 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                error ? 'border-red-500' : 'border-gray-300'
              } ${isVerifying ? 'bg-gray-100' : 'bg-white'}`}
              disabled={isVerifying}
              autoComplete="one-time-code"
            />
          ))}
        </div>

        {/* Error Message */}
        {error && (
          <ErrorMessage message={error} className="text-center" />
        )}
      </div>

      {/* Manual Verify Button (for cases where auto-verify fails) */}
      {verificationCode.join('').length === 6 && !isVerifying && (
        <div className="mb-6">
          <button
            onClick={handleManualVerify}
            className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 transition-colors"
          >
            Verifică codul
          </button>
        </div>
      )}

      {/* Loading State */}
      {isVerifying && (
        <div className="mb-6 text-center">
          <div className="inline-flex items-center text-gray-600">
            <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-green-600" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            Se verifică codul...
          </div>
        </div>
      )}

      {/* Resend Section */}
      <div className="border-t border-gray-200 pt-6">
        <div className="text-center space-y-4">
          <p className="text-sm text-gray-600">
            Nu ați primit codul?
          </p>
          
          {resendCooldown > 0 ? (
            <p className="text-sm text-gray-500">
              Puteți cere un nou cod în {resendCooldown} secunde
            </p>
          ) : (
            <button
              onClick={handleResendCode}
              disabled={isResending}
              className="text-green-600 hover:text-green-700 font-medium disabled:text-gray-400 disabled:cursor-not-allowed"
            >
              {isResending ? (
                <span className="inline-flex items-center">
                  <svg className="animate-spin -ml-1 mr-2 h-4 w-4" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                  Se retrimite...
                </span>
              ) : (
                'Retrimite codul'
              )}
            </button>
          )}
        </div>
      </div>

      {/* Back Button */}
      <div className="border-t border-gray-200 pt-6 mt-6">
        <button
          onClick={onBack}
          disabled={isVerifying || isResending}
          className="w-full text-gray-600 hover:text-gray-800 font-medium py-2 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
        >
          ← Înapoi la informații de livrare
        </button>
      </div>

      {/* Help Section */}
      <div className="mt-6 bg-blue-50 border border-blue-200 rounded-lg p-4">
        <h4 className="text-sm font-medium text-blue-800 mb-2">
          💡 Aveți probleme cu verificarea?
        </h4>
        <div className="text-sm text-blue-700 space-y-1">
          <p>• Verificați că ați introdus numărul de telefon corect</p>
          <p>• SMS-ul poate întârzia câteva minute</p>
          <p>• Verificați folderul de spam sau mesajele blocate</p>
          <p>• Pentru ajutor contactați: 0700 123 456</p>
        </div>
      </div>

      {/* Development Helper */}
      {process.env.NODE_ENV === 'development' && (
        <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
          <p className="text-xs text-yellow-800">
            <strong>Dezvoltare:</strong> Folosiți codul <code>123456</code> pentru testare
          </p>
        </div>
      )}
    </div>
  );
};

export default SMSVerification;