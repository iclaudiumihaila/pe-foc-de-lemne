import React, { useState } from 'react';
import PhoneVerification from '../components/checkout/PhoneVerification';

const TestPhoneVerification = () => {
  const [verificationData, setVerificationData] = useState(null);

  const handleVerified = (data) => {
    console.log('Verification successful:', data);
    setVerificationData(data);
  };

  return (
    <div className="min-h-screen bg-gray-100 py-12">
      <div className="container mx-auto px-4">
        <h1 className="text-3xl font-bold text-center mb-8">
          Test Phone Verification
        </h1>

        {!verificationData ? (
          <PhoneVerification 
            onVerified={handleVerified}
            initialPhone=""
          />
        ) : (
          <div className="max-w-md mx-auto p-6 bg-white rounded-lg shadow-md">
            <h2 className="text-2xl font-bold mb-4 text-green-600">
              ✓ Verificare completă!
            </h2>
            
            <div className="space-y-3">
              <div>
                <span className="font-semibold">Telefon:</span>
                <span className="ml-2">{verificationData.customer.phone_masked}</span>
              </div>
              
              <div>
                <span className="font-semibold">Nume:</span>
                <span className="ml-2">
                  {verificationData.customer.name || 'Neconfigurat'}
                </span>
              </div>
              
              <div>
                <span className="font-semibold">Adrese salvate:</span>
                <span className="ml-2">{verificationData.customer.addresses.length}</span>
              </div>
              
              <div>
                <span className="font-semibold">Client anterior:</span>
                <span className="ml-2">
                  {verificationData.customer.has_ordered_before ? 'Da' : 'Nu'}
                </span>
              </div>
              
              <div className="mt-4 p-3 bg-gray-100 rounded">
                <span className="font-semibold text-sm">Token JWT (primele 50 caractere):</span>
                <p className="text-xs mt-1 font-mono break-all">
                  {verificationData.token.substring(0, 50)}...
                </p>
              </div>
            </div>

            <button
              onClick={() => {
                setVerificationData(null);
                localStorage.removeItem('checkout_token');
              }}
              className="mt-6 w-full bg-gray-600 text-white py-2 px-4 rounded-md hover:bg-gray-700 transition-colors"
            >
              Test din nou
            </button>
          </div>
        )}

        {/* Debug info */}
        <div className="mt-8 max-w-2xl mx-auto">
          <details className="bg-gray-800 text-white p-4 rounded-lg">
            <summary className="cursor-pointer font-semibold">
              Informații pentru testare
            </summary>
            <div className="mt-4 space-y-2 text-sm">
              <p>• Folosiți orice număr de telefon românesc valid (ex: 0722123456)</p>
              <p>• În modul development, codul va fi afișat în răspuns</p>
              <p>• Limită: 3 SMS-uri per telefon pe zi</p>
              <p>• Limită: 5 SMS-uri per IP pe oră</p>
              <p>• Codul expiră în 5 minute</p>
              <p>• Token-ul JWT este valid 24 ore</p>
            </div>
          </details>
        </div>
      </div>
    </div>
  );
};

export default TestPhoneVerification;