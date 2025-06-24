import React, { useState, useEffect, useRef } from 'react';
import api from '../../services/api';

const PhoneVerification = ({ onVerified, initialPhone = '' }) => {
  const [phone, setPhone] = useState(initialPhone || '0775156791');
  const [name, setName] = useState('');
  const [code, setCode] = useState(['', '', '', '', '', '']);
  const [step, setStep] = useState('phone'); // 'phone' or 'code'
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState('');
  const [timeLeft, setTimeLeft] = useState(0);
  const [customerData, setCustomerData] = useState(null);
  
  const codeInputRefs = useRef([]);

  // Timer for resend cooldown
  useEffect(() => {
    if (timeLeft > 0) {
      const timer = setTimeout(() => setTimeLeft(timeLeft - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [timeLeft]);

  // Validate Romanian phone format
  const validatePhone = (phoneNumber) => {
    const cleaned = phoneNumber.replace(/\s/g, '');
    return /^(0|\+40)7[0-9]{8}$/.test(cleaned);
  };

  // Format phone for display
  const formatPhone = (phoneNumber) => {
    const cleaned = phoneNumber.replace(/\D/g, '');
    if (cleaned.length <= 4) return cleaned;
    if (cleaned.length <= 7) return `${cleaned.slice(0, 4)} ${cleaned.slice(4)}`;
    return `${cleaned.slice(0, 4)} ${cleaned.slice(4, 7)} ${cleaned.slice(7, 10)}`;
  };

  // Handle phone input change
  const handlePhoneChange = (e) => {
    const value = e.target.value;
    const cleaned = value.replace(/\D/g, '');
    
    // Limit to Romanian phone length
    if (cleaned.length <= 10) {
      setPhone(cleaned);
      setError('');
    }
  };

  // Send verification code
  const handleSendCode = async () => {
    if (!validatePhone(phone)) {
      setError('Format telefon invalid. Exemplu: 0722 123 456');
      return;
    }

    if (!name.trim() || name.trim().length < 3) {
      setError('Vă rugăm introduceți numele complet (minim 3 caractere)');
      return;
    }

    setLoading(true);
    setError('');

    console.log('=== SENDING VERIFICATION CODE ===');
    console.log('Phone:', phone);
    console.log('Name:', name);
    const payload = {
      phone: phone.startsWith('0') ? phone : '0' + phone,
      name: name.trim()
    };
    console.log('Payload:', payload);

    try {
      const response = await api.post('/checkout/phone/send-code', payload);
      console.log('Response:', response);

      if (response.data.success) {
        setSuccess('Cod trimis cu succes!');
        setStep('code');
        setTimeLeft(300); // 5 minutes
        codeInputRefs.current[0]?.focus();
      }
    } catch (err) {
      console.error('=== ERROR SENDING CODE ===');
      console.error('Error:', err);
      console.error('Response:', err.response);
      console.error('Response data:', err.response?.data);
      
      const errorData = err.response?.data?.error || {};
      
      if (errorData.code === 'SMS_LIMIT_EXCEEDED') {
        setError(errorData.message || 'Ați depășit limita de SMS-uri. Încercați mai târziu.');
      } else if (errorData.code === 'IP_LIMIT_EXCEEDED') {
        setError('Prea multe încercări. Vă rugăm așteptați o oră.');
      } else {
        setError('Eroare la trimiterea codului. Încercați din nou.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle code input change
  const handleCodeChange = (index, value) => {
    if (value.length <= 1 && /^\d*$/.test(value)) {
      const newCode = [...code];
      newCode[index] = value;
      setCode(newCode);
      setError('');

      // Auto-focus next input
      if (value && index < 5) {
        codeInputRefs.current[index + 1]?.focus();
      }

      // Auto-submit when all digits entered
      if (value && index === 5 && newCode.every(digit => digit)) {
        handleVerifyCode(newCode.join(''));
      }
    }
  };

  // Handle backspace in code input
  const handleCodeKeyDown = (index, e) => {
    if (e.key === 'Backspace' && !code[index] && index > 0) {
      codeInputRefs.current[index - 1]?.focus();
    }
  };

  // Handle paste in code input
  const handleCodePaste = (e) => {
    e.preventDefault();
    const pastedData = e.clipboardData.getData('text');
    const digits = pastedData.replace(/\D/g, '').slice(0, 6);
    
    if (digits.length === 6) {
      const newCode = digits.split('');
      setCode(newCode);
      codeInputRefs.current[5]?.focus();
      handleVerifyCode(digits);
    }
  };

  // Verify code
  const handleVerifyCode = async (verificationCode = null) => {
    const fullCode = verificationCode || code.join('');
    
    if (fullCode.length !== 6) {
      setError('Introduceți toate cele 6 cifre');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.post('/checkout/phone/verify-code', {
        phone: phone.startsWith('0') ? phone : '0' + phone,
        code: fullCode
      });

      if (response.data.success) {
        // Store JWT token
        localStorage.setItem('checkout_token', response.data.token);
        
        // Store customer data
        setCustomerData(response.data.customer);
        setSuccess('Telefon verificat cu succes!');
        
        // Call parent callback with verification data
        setTimeout(() => {
          onVerified({
            token: response.data.token,
            customer: response.data.customer,
            phone: phone
          });
        }, 1000);
      }
    } catch (err) {
      const errorData = err.response?.data?.error || {};
      
      if (errorData.code === 'INVALID_CODE') {
        setError('Cod invalid. Verificați și încercați din nou.');
      } else if (errorData.code === 'CODE_EXPIRED') {
        setError('Codul a expirat. Solicitați unul nou.');
      } else if (errorData.code === 'INVALID_VERIFICATION_CODE') {
        setError(errorData.message || 'Prea multe încercări. Solicitați un cod nou.');
      } else {
        setError('Eroare la verificare. Încercați din nou.');
      }
      
      // Clear code on error
      setCode(['', '', '', '', '', '']);
      codeInputRefs.current[0]?.focus();
    } finally {
      setLoading(false);
    }
  };

  // Resend code
  const handleResendCode = () => {
    setStep('phone');
    setCode(['', '', '', '', '', '']);
    setError('');
    setSuccess('');
  };

  // Format time left
  const formatTimeLeft = () => {
    const minutes = Math.floor(timeLeft / 60);
    const seconds = timeLeft % 60;
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  return (
    <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
      <h2 className="text-2xl font-bold mb-6 text-gray-800">
        Verificare telefon
      </h2>

      {step === 'phone' ? (
        <div>
          <p className="text-gray-600 mb-4">
            Introduceți numele și numărul de telefon pentru a continua comanda
          </p>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Nume complet
            </label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
              placeholder="Ion Popescu"
              disabled={loading}
            />
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Număr telefon
            </label>
            <div className="relative">
              <span className="absolute left-3 top-3 text-gray-500">
                {phone.startsWith('4') ? '+' : ''}
              </span>
              <input
                type="tel"
                value={formatPhone(phone)}
                onChange={handlePhoneChange}
                className="w-full pl-8 pr-3 py-3 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                placeholder="0722 123 456"
                disabled={loading}
              />
            </div>
          </div>

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-md">
              {success}
            </div>
          )}

          <button
            onClick={handleSendCode}
            disabled={loading || !phone}
            className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            {loading ? 'Se trimite...' : 'Trimite cod verificare'}
          </button>
        </div>
      ) : (
        <div>
          <p className="text-gray-600 mb-4">
            Cod trimis la {formatPhone(phone)}
          </p>

          <div className="mb-4">
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Cod verificare (6 cifre)
            </label>
            <div className="flex gap-2 justify-center">
              {code.map((digit, index) => (
                <input
                  key={index}
                  ref={el => codeInputRefs.current[index] = el}
                  type="text"
                  inputMode="numeric"
                  maxLength="1"
                  value={digit}
                  onChange={(e) => handleCodeChange(index, e.target.value)}
                  onKeyDown={(e) => handleCodeKeyDown(index, e)}
                  onPaste={index === 0 ? handleCodePaste : undefined}
                  className="w-12 h-12 text-center text-lg font-semibold border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500 focus:border-transparent"
                  disabled={loading}
                />
              ))}
            </div>
          </div>

          {timeLeft > 0 && (
            <p className="text-sm text-gray-500 text-center mb-4">
              Cod valid pentru: {formatTimeLeft()}
            </p>
          )}

          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md">
              {error}
            </div>
          )}

          {success && (
            <div className="mb-4 p-3 bg-green-50 border border-green-200 text-green-700 rounded-md">
              {success}
            </div>
          )}

          <button
            onClick={() => handleVerifyCode()}
            disabled={loading || code.some(d => !d)}
            className="w-full bg-green-600 text-white py-3 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors mb-3"
          >
            {loading ? 'Se verifică...' : 'Verifică cod'}
          </button>

          <button
            onClick={handleResendCode}
            disabled={loading}
            className="w-full text-green-600 py-2 px-4 hover:text-green-700 focus:outline-none focus:underline"
          >
            Trimite alt cod
          </button>
        </div>
      )}
    </div>
  );
};

export default PhoneVerification;