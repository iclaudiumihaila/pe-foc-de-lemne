/**
 * Cookie Consent Component for Local Producer Web Application
 * 
 * GDPR-compliant cookie consent management with Romanian localization
 * and granular privacy controls.
 */

import React, { useState, useEffect } from 'react';
import { XMarkIcon, InformationCircleIcon, AdjustmentsHorizontalIcon } from '@heroicons/react/24/outline';
import { useAnalytics } from '../../hooks/useAnalytics';

const CookieConsent = () => {
  const { giveConsent, revokeConsent } = useAnalytics();
  const [showBanner, setShowBanner] = useState(false);
  const [showDetails, setShowDetails] = useState(false);
  const [showSettings, setShowSettings] = useState(false);
  const [cookieSettings, setCookieSettings] = useState({
    necessary: true, // Always required
    analytics: false,
    marketing: false,
    preferences: false
  });

  useEffect(() => {
    // Check if user has already made a decision
    const consentDecision = localStorage.getItem('cookie_consent_decision');
    const consentDate = localStorage.getItem('cookie_consent_date');
    
    // Show banner if no decision made or consent is older than 6 months
    if (!consentDecision || (consentDate && isConsentExpired(consentDate))) {
      setShowBanner(true);
    } else if (consentDecision === 'accepted') {
      // Load saved settings
      const savedSettings = localStorage.getItem('cookie_settings');
      if (savedSettings) {
        setCookieSettings(JSON.parse(savedSettings));
      }
    }
  }, []);

  const isConsentExpired = (consentDate) => {
    const sixMonthsAgo = new Date();
    sixMonthsAgo.setMonth(sixMonthsAgo.getMonth() - 6);
    return new Date(consentDate) < sixMonthsAgo;
  };

  const handleAcceptAll = () => {
    const allSettings = {
      necessary: true,
      analytics: true,
      marketing: false, // Keep false for privacy
      preferences: true
    };
    
    setCookieSettings(allSettings);
    saveConsentDecision('accepted', allSettings);
    giveConsent();
    setShowBanner(false);
  };

  const handleRejectAll = () => {
    const minimalSettings = {
      necessary: true,
      analytics: false,
      marketing: false,
      preferences: false
    };
    
    setCookieSettings(minimalSettings);
    saveConsentDecision('rejected', minimalSettings);
    revokeConsent();
    setShowBanner(false);
  };

  const handleSaveSettings = () => {
    saveConsentDecision('customized', cookieSettings);
    
    if (cookieSettings.analytics) {
      giveConsent();
    } else {
      revokeConsent();
    }
    
    setShowBanner(false);
    setShowSettings(false);
  };

  const saveConsentDecision = (decision, settings) => {
    localStorage.setItem('cookie_consent_decision', decision);
    localStorage.setItem('cookie_consent_date', new Date().toISOString());
    localStorage.setItem('cookie_settings', JSON.stringify(settings));
  };

  const handleSettingChange = (settingName) => {
    if (settingName === 'necessary') return; // Cannot be disabled
    
    setCookieSettings(prev => ({
      ...prev,
      [settingName]: !prev[settingName]
    }));
  };

  const reopenSettings = () => {
    setShowBanner(true);
    setShowSettings(true);
  };

  // Don't show banner if user has already consented recently
  if (!showBanner) {
    return (
      <div className="fixed bottom-4 left-4 z-40">
        <button
          onClick={reopenSettings}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm px-3 py-2 rounded-lg shadow-md transition-colors flex items-center space-x-2"
          title="Setări cookie-uri"
        >
          <AdjustmentsHorizontalIcon className="w-4 h-4" />
          <span>Cookie-uri</span>
        </button>
      </div>
    );
  }

  return (
    <div className="fixed inset-0 z-50 flex items-end justify-center p-4">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black bg-opacity-50" />
      
      {/* Cookie consent banner */}
      <div className="relative bg-white rounded-lg shadow-2xl max-w-2xl w-full border-t-4 border-primary-500">
        <div className="p-6">
          {/* Header */}
          <div className="flex items-start justify-between mb-4">
            <div className="flex items-center space-x-2">
              <InformationCircleIcon className="w-6 h-6 text-primary-500 flex-shrink-0 mt-0.5" />
              <h3 className="text-lg font-semibold text-gray-900">
                Respectăm confidențialitatea ta
              </h3>
            </div>
            <button
              onClick={() => setShowBanner(false)}
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              <XMarkIcon className="w-6 h-6" />
            </button>
          </div>

          {/* Main content */}
          {!showSettings ? (
            <div>
              <p className="text-gray-600 mb-4 leading-relaxed">
                Folosim cookie-uri pentru a îmbunătăți experiența ta pe site-ul nostru și pentru a 
                înțelege cum folosești produsele locale românești. Datele tale sunt procesate conform 
                legislației GDPR și a legilor românești de protecție a datelor.
              </p>

              {showDetails && (
                <div className="bg-gray-50 rounded-lg p-4 mb-4 text-sm">
                  <h4 className="font-medium text-gray-900 mb-2">Ce cookie-uri folosim:</h4>
                  <ul className="space-y-2 text-gray-600">
                    <li>
                      <strong>Cookie-uri necesare:</strong> Esențiale pentru funcționarea site-ului 
                      (coș de cumpărături, sesiune, securitate)
                    </li>
                    <li>
                      <strong>Cookie-uri de analiză:</strong> Ne ajută să înțelegem cum folosești 
                      site-ul pentru a-l îmbunătăți (Google Analytics 4)
                    </li>
                    <li>
                      <strong>Cookie-uri de preferințe:</strong> Memorează alegerile tale 
                      (limbă, valută, filtre produse)
                    </li>
                  </ul>
                  <p className="mt-3 text-xs text-gray-500">
                    Nu folosim cookie-uri de marketing sau publicitate. Toate datele sunt anonimizate 
                    și procesate în conformitate cu GDPR.
                  </p>
                </div>
              )}

              {/* Action buttons */}
              <div className="flex flex-col sm:flex-row gap-3">
                <button
                  onClick={handleAcceptAll}
                  className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors flex-1"
                >
                  Accept toate cookie-urile
                </button>
                
                <button
                  onClick={() => setShowSettings(true)}
                  className="border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors flex-1"
                >
                  Personalizează setările
                </button>
                
                <button
                  onClick={handleRejectAll}
                  className="text-gray-600 px-6 py-3 rounded-lg font-medium hover:bg-gray-100 transition-colors"
                >
                  Doar necesare
                </button>
              </div>

              {/* Toggle details */}
              <div className="mt-4 text-center">
                <button
                  onClick={() => setShowDetails(!showDetails)}
                  className="text-sm text-primary-600 hover:text-primary-700 transition-colors"
                >
                  {showDetails ? 'Ascunde detaliile' : 'Vezi detalii despre cookie-uri'}
                </button>
              </div>
            </div>
          ) : (
            /* Settings panel */
            <div>
              <h4 className="text-lg font-medium text-gray-900 mb-4">
                Setări cookie-uri personalizate
              </h4>
              
              <div className="space-y-4">
                {/* Necessary cookies */}
                <div className="flex items-start justify-between p-4 bg-gray-50 rounded-lg">
                  <div className="flex-1">
                    <h5 className="font-medium text-gray-900">Cookie-uri necesare</h5>
                    <p className="text-sm text-gray-600 mt-1">
                      Esențiale pentru funcționarea corectă a site-ului. Nu pot fi dezactivate.
                    </p>
                  </div>
                  <div className="ml-4">
                    <input
                      type="checkbox"
                      checked={cookieSettings.necessary}
                      disabled
                      className="w-4 h-4 text-primary-600 rounded border-gray-300 opacity-50"
                    />
                  </div>
                </div>

                {/* Analytics cookies */}
                <div className="flex items-start justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex-1">
                    <h5 className="font-medium text-gray-900">Cookie-uri de analiză</h5>
                    <p className="text-sm text-gray-600 mt-1">
                      Ne ajută să înțelegem cum folosești site-ul pentru a-l îmbunătăți. 
                      Datele sunt anonimizate conform GDPR.
                    </p>
                  </div>
                  <div className="ml-4">
                    <input
                      type="checkbox"
                      checked={cookieSettings.analytics}
                      onChange={() => handleSettingChange('analytics')}
                      className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
                    />
                  </div>
                </div>

                {/* Preferences cookies */}
                <div className="flex items-start justify-between p-4 border border-gray-200 rounded-lg">
                  <div className="flex-1">
                    <h5 className="font-medium text-gray-900">Cookie-uri de preferințe</h5>
                    <p className="text-sm text-gray-600 mt-1">
                      Memorează alegerile tale pentru o experiență personalizată 
                      (filtre produse, preferințe afișare).
                    </p>
                  </div>
                  <div className="ml-4">
                    <input
                      type="checkbox"
                      checked={cookieSettings.preferences}
                      onChange={() => handleSettingChange('preferences')}
                      className="w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500"
                    />
                  </div>
                </div>
              </div>

              {/* Privacy notice */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 mt-4">
                <p className="text-sm text-blue-800">
                  <strong>Protecția datelor:</strong> Toate datele sunt procesate conform GDPR și 
                  legislației românești. Poți modifica aceste setări oricând din footer-ul site-ului.
                </p>
              </div>

              {/* Action buttons */}
              <div className="flex flex-col sm:flex-row gap-3 mt-6">
                <button
                  onClick={handleSaveSettings}
                  className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 transition-colors flex-1"
                >
                  Salvează setările
                </button>
                
                <button
                  onClick={() => setShowSettings(false)}
                  className="border border-gray-300 text-gray-700 px-6 py-3 rounded-lg font-medium hover:bg-gray-50 transition-colors"
                >
                  Înapoi
                </button>
              </div>
            </div>
          )}

          {/* Footer links */}
          <div className="mt-6 pt-4 border-t border-gray-200 flex flex-wrap justify-center gap-4 text-sm">
            <a 
              href="/confidentialitate" 
              className="text-primary-600 hover:text-primary-700 transition-colors"
            >
              Politica de confidențialitate
            </a>
            <a 
              href="/termeni" 
              className="text-primary-600 hover:text-primary-700 transition-colors"
            >
              Termeni și condiții
            </a>
            <a 
              href="/gdpr" 
              className="text-primary-600 hover:text-primary-700 transition-colors"
            >
              Drepturile GDPR
            </a>
          </div>
        </div>
      </div>
    </div>
  );
};

/**
 * Cookie Settings Manager Component
 * Allows users to manage cookie preferences from settings page
 */
export const CookieSettingsManager = () => {
  const { consentGiven, giveConsent, revokeConsent } = useAnalytics();
  const [settings, setSettings] = useState({
    necessary: true,
    analytics: consentGiven,
    marketing: false,
    preferences: true
  });
  const [isLoading, setIsLoading] = useState(false);
  const [showSuccess, setShowSuccess] = useState(false);

  useEffect(() => {
    // Load current settings
    const savedSettings = localStorage.getItem('cookie_settings');
    if (savedSettings) {
      setSettings(JSON.parse(savedSettings));
    }
  }, []);

  const handleSaveSettings = async () => {
    setIsLoading(true);
    
    try {
      // Save settings
      localStorage.setItem('cookie_settings', JSON.stringify(settings));
      localStorage.setItem('cookie_consent_date', new Date().toISOString());
      
      // Update analytics consent
      if (settings.analytics) {
        giveConsent();
      } else {
        revokeConsent();
      }
      
      setShowSuccess(true);
      setTimeout(() => setShowSuccess(false), 3000);
    } catch (error) {
      console.error('Failed to save cookie settings:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSettingChange = (settingName) => {
    if (settingName === 'necessary') return;
    
    setSettings(prev => ({
      ...prev,
      [settingName]: !prev[settingName]
    }));
  };

  return (
    <div className="bg-white p-6 rounded-lg shadow-sm border">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Setări cookie-uri și confidențialitate
      </h3>
      
      <div className="space-y-4">
        {Object.entries({
          necessary: {
            title: 'Cookie-uri necesare',
            description: 'Esențiale pentru funcționarea site-ului. Nu pot fi dezactivate.',
            disabled: true
          },
          analytics: {
            title: 'Cookie-uri de analiză',
            description: 'Statistici anonimizate pentru îmbunătățirea site-ului.',
            disabled: false
          },
          preferences: {
            title: 'Cookie-uri de preferințe',
            description: 'Memorează setările tale pentru o experiență personalizată.',
            disabled: false
          }
        }).map(([key, config]) => (
          <div key={key} className="flex items-start justify-between p-4 border rounded-lg">
            <div className="flex-1">
              <h4 className="font-medium text-gray-900">{config.title}</h4>
              <p className="text-sm text-gray-600 mt-1">{config.description}</p>
            </div>
            <div className="ml-4">
              <input
                type="checkbox"
                checked={settings[key]}
                disabled={config.disabled}
                onChange={() => handleSettingChange(key)}
                className={`w-4 h-4 text-primary-600 rounded border-gray-300 focus:ring-primary-500 ${
                  config.disabled ? 'opacity-50' : ''
                }`}
              />
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 flex items-center justify-between">
        <button
          onClick={handleSaveSettings}
          disabled={isLoading}
          className="bg-primary-600 text-white px-6 py-2 rounded-lg font-medium hover:bg-primary-700 transition-colors disabled:opacity-50"
        >
          {isLoading ? 'Se salvează...' : 'Salvează setările'}
        </button>
        
        {showSuccess && (
          <span className="text-green-600 text-sm font-medium">
            ✓ Setările au fost salvate
          </span>
        )}
      </div>
      
      <p className="text-xs text-gray-500 mt-4">
        Ultima actualizare: {new Date().toLocaleDateString('ro-RO')}. 
        Conform GDPR și legislației românești de protecție a datelor.
      </p>
    </div>
  );
};

export default CookieConsent;