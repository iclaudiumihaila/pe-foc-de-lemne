import React, { useState, useEffect } from 'react';
import ErrorMessage from '../common/ErrorMessage';

const CustomerForm = ({ 
  onSubmit, 
  initialData = {}, 
  loading = false,
  className = ''
}) => {
  const [formData, setFormData] = useState({
    firstName: '',
    lastName: '',
    phone: '',
    email: '',
    address: '',
    city: '',
    county: '',
    postalCode: '',
    notes: '',
    ...initialData
  });

  const [errors, setErrors] = useState({});
  const [touched, setTouched] = useState({});

  // Romanian counties (județe)
  const romanianCounties = [
    'Alba', 'Arad', 'Argeș', 'Bacău', 'Bihor', 'Bistrița-Năsăud', 'Botoșani',
    'Brașov', 'Brăila', 'București', 'Buzău', 'Caraș-Severin', 'Călărași',
    'Cluj', 'Constanța', 'Covasna', 'Dâmbovița', 'Dolj', 'Galați', 'Giurgiu',
    'Gorj', 'Harghita', 'Hunedoara', 'Ialomița', 'Iași', 'Ilfov', 'Maramureș',
    'Mehedinți', 'Mureș', 'Neamț', 'Olt', 'Prahova', 'Satu Mare', 'Sălaj',
    'Sibiu', 'Suceava', 'Teleorman', 'Timiș', 'Tulcea', 'Vaslui', 'Vâlcea', 'Vrancea'
  ];

  // Validation patterns
  const patterns = {
    phone: /^07[0-9]{8}$/,
    email: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    postalCode: /^[0-9]{6}$/
  };

  // Validation rules
  const validateField = (name, value) => {
    const errors = {};

    switch (name) {
      case 'firstName':
        if (!value.trim()) {
          errors.firstName = 'Numele este obligatoriu';
        } else if (value.trim().length < 2) {
          errors.firstName = 'Numele trebuie să aibă cel puțin 2 caractere';
        }
        break;

      case 'lastName':
        if (!value.trim()) {
          errors.lastName = 'Prenumele este obligatoriu';
        } else if (value.trim().length < 2) {
          errors.lastName = 'Prenumele trebuie să aibă cel puțin 2 caractere';
        }
        break;

      case 'phone':
        if (!value.trim()) {
          errors.phone = 'Numărul de telefon este obligatoriu';
        } else if (!patterns.phone.test(value.replace(/\s/g, ''))) {
          errors.phone = 'Introduceți un număr de telefon valid (ex: 0712 345 678)';
        }
        break;

      case 'email':
        if (!value.trim()) {
          errors.email = 'Adresa de email este obligatorie';
        } else if (!patterns.email.test(value)) {
          errors.email = 'Introduceți o adresă de email validă';
        }
        break;

      case 'address':
        if (!value.trim()) {
          errors.address = 'Adresa este obligatorie';
        } else if (value.trim().length < 10) {
          errors.address = 'Adresa trebuie să fie mai detaliată (minim 10 caractere)';
        }
        break;

      case 'city':
        if (!value.trim()) {
          errors.city = 'Orașul este obligatoriu';
        } else if (value.trim().length < 2) {
          errors.city = 'Numele orașului trebuie să aibă cel puțin 2 caractere';
        }
        break;

      case 'county':
        if (!value.trim()) {
          errors.county = 'Județul este obligatoriu';
        }
        break;

      case 'postalCode':
        if (!value.trim()) {
          errors.postalCode = 'Codul poștal este obligatoriu';
        } else if (!patterns.postalCode.test(value.replace(/\s/g, ''))) {
          errors.postalCode = 'Introduceți un cod poștal valid (6 cifre)';
        }
        break;

      default:
        break;
    }

    return errors;
  };

  // Validate entire form
  const validateForm = () => {
    const newErrors = {};
    const requiredFields = ['firstName', 'lastName', 'phone', 'email', 'address', 'city', 'county', 'postalCode'];

    requiredFields.forEach(field => {
      const fieldErrors = validateField(field, formData[field]);
      Object.assign(newErrors, fieldErrors);
    });

    return newErrors;
  };

  // Handle input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    
    // Format phone number as user types
    let formattedValue = value;
    if (name === 'phone') {
      formattedValue = value.replace(/\D/g, '').substring(0, 10);
      if (formattedValue.length > 4) {
        formattedValue = formattedValue.replace(/(\d{4})(\d{3})(\d{3})/, '$1 $2 $3');
      }
    }

    // Format postal code
    if (name === 'postalCode') {
      formattedValue = value.replace(/\D/g, '').substring(0, 6);
    }

    setFormData(prev => ({
      ...prev,
      [name]: formattedValue
    }));

    // Real-time validation for touched fields
    if (touched[name]) {
      const fieldErrors = validateField(name, formattedValue);
      setErrors(prev => ({
        ...prev,
        ...fieldErrors,
        [name]: fieldErrors[name] // Clear error if validation passes
      }));
    }
  };

  // Handle field blur (mark as touched)
  const handleBlur = (e) => {
    const { name } = e.target;
    setTouched(prev => ({
      ...prev,
      [name]: true
    }));

    // Validate field on blur
    const fieldErrors = validateField(name, formData[name]);
    setErrors(prev => ({
      ...prev,
      ...fieldErrors
    }));
  };

  // Handle form submission
  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Mark all fields as touched
    const allFields = Object.keys(formData);
    const touchedFields = allFields.reduce((acc, field) => ({
      ...acc,
      [field]: true
    }), {});
    setTouched(touchedFields);

    // Validate entire form
    const formErrors = validateForm();
    setErrors(formErrors);

    // If no errors, submit form
    if (Object.keys(formErrors).length === 0) {
      // Clean phone number and postal code for submission
      const cleanedData = {
        ...formData,
        phone: formData.phone.replace(/\s/g, ''),
        postalCode: formData.postalCode.replace(/\s/g, '')
      };
      onSubmit(cleanedData);
    }
  };

  // Reset form when initialData changes
  useEffect(() => {
    if (Object.keys(initialData).length > 0) {
      setFormData(prev => ({
        ...prev,
        ...initialData
      }));
    }
  }, [initialData]);

  return (
    <div className={`bg-white rounded-lg shadow-sm p-6 ${className}`}>
      <h2 className="text-xl font-semibold text-gray-900 mb-6">
        Informații de livrare
      </h2>

      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Personal Information Section */}
        <div>
          <h3 className="text-lg font-medium text-gray-800 mb-4">
            Informații personale
          </h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {/* First Name */}
            <div>
              <label htmlFor="firstName" className="block text-sm font-medium text-gray-700 mb-2">
                Nume <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="firstName"
                name="firstName"
                value={formData.firstName}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="Introduceți numele"
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                  errors.firstName ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading}
              />
              {errors.firstName && (
                <ErrorMessage message={errors.firstName} className="mt-1" />
              )}
            </div>

            {/* Last Name */}
            <div>
              <label htmlFor="lastName" className="block text-sm font-medium text-gray-700 mb-2">
                Prenume <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="lastName"
                name="lastName"
                value={formData.lastName}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="Introduceți prenumele"
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                  errors.lastName ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading}
              />
              {errors.lastName && (
                <ErrorMessage message={errors.lastName} className="mt-1" />
              )}
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-4">
            {/* Phone */}
            <div>
              <label htmlFor="phone" className="block text-sm font-medium text-gray-700 mb-2">
                Telefon <span className="text-red-500">*</span>
              </label>
              <input
                type="tel"
                id="phone"
                name="phone"
                value={formData.phone}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="0712 345 678"
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                  errors.phone ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading}
              />
              {errors.phone && (
                <ErrorMessage message={errors.phone} className="mt-1" />
              )}
            </div>

            {/* Email */}
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-2">
                Email <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="nume@exemplu.ro"
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                  errors.email ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading}
              />
              {errors.email && (
                <ErrorMessage message={errors.email} className="mt-1" />
              )}
            </div>
          </div>
        </div>

        {/* Delivery Information Section */}
        <div>
          <h3 className="text-lg font-medium text-gray-800 mb-4">
            Adresa de livrare
          </h3>

          {/* Address */}
          <div className="mb-4">
            <label htmlFor="address" className="block text-sm font-medium text-gray-700 mb-2">
              Adresă <span className="text-red-500">*</span>
            </label>
            <input
              type="text"
              id="address"
              name="address"
              value={formData.address}
              onChange={handleChange}
              onBlur={handleBlur}
              placeholder="Strada, numărul, bloc, scara, apartament"
              className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                errors.address ? 'border-red-500' : 'border-gray-300'
              }`}
              disabled={loading}
            />
            {errors.address && (
              <ErrorMessage message={errors.address} className="mt-1" />
            )}
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* City */}
            <div>
              <label htmlFor="city" className="block text-sm font-medium text-gray-700 mb-2">
                Oraș <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="city"
                name="city"
                value={formData.city}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="Introduceți orașul"
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                  errors.city ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading}
              />
              {errors.city && (
                <ErrorMessage message={errors.city} className="mt-1" />
              )}
            </div>

            {/* County */}
            <div>
              <label htmlFor="county" className="block text-sm font-medium text-gray-700 mb-2">
                Județ <span className="text-red-500">*</span>
              </label>
              <select
                id="county"
                name="county"
                value={formData.county}
                onChange={handleChange}
                onBlur={handleBlur}
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                  errors.county ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading}
              >
                <option value="">Selectați județul</option>
                {romanianCounties.map(county => (
                  <option key={county} value={county}>
                    {county}
                  </option>
                ))}
              </select>
              {errors.county && (
                <ErrorMessage message={errors.county} className="mt-1" />
              )}
            </div>

            {/* Postal Code */}
            <div>
              <label htmlFor="postalCode" className="block text-sm font-medium text-gray-700 mb-2">
                Cod poștal <span className="text-red-500">*</span>
              </label>
              <input
                type="text"
                id="postalCode"
                name="postalCode"
                value={formData.postalCode}
                onChange={handleChange}
                onBlur={handleBlur}
                placeholder="123456"
                className={`w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent ${
                  errors.postalCode ? 'border-red-500' : 'border-gray-300'
                }`}
                disabled={loading}
              />
              {errors.postalCode && (
                <ErrorMessage message={errors.postalCode} className="mt-1" />
              )}
            </div>
          </div>

          {/* Special Instructions */}
          <div className="mt-4">
            <label htmlFor="notes" className="block text-sm font-medium text-gray-700 mb-2">
              Observații (opțional)
            </label>
            <textarea
              id="notes"
              name="notes"
              value={formData.notes}
              onChange={handleChange}
              onBlur={handleBlur}
              rows={3}
              placeholder="Instrucțiuni speciale pentru livrare..."
              className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-transparent"
              disabled={loading}
            />
          </div>
        </div>

        {/* Local Delivery Information */}
        <div className="bg-green-50 border border-green-200 rounded-lg p-4">
          <h4 className="text-sm font-medium text-green-800 mb-2">
            📍 Informații despre livrare
          </h4>
          <div className="text-sm text-green-700 space-y-1">
            <p>• Livrare gratuită în zona locală</p>
            <p>• Produsele sunt livrate în 1-2 zile lucrătoare</p>
            <p>• Veți fi contactați telefonic pentru confirmarea programării</p>
            <p>• Livrarea se face între orele 9:00 - 18:00</p>
          </div>
        </div>

        {/* Submit Button */}
        <div className="pt-4">
          <button
            type="submit"
            disabled={loading}
            className="w-full bg-green-600 text-white py-3 px-6 rounded-lg font-semibold hover:bg-green-700 disabled:bg-gray-400 disabled:cursor-not-allowed transition-colors duration-200"
          >
            {loading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                Se procesează...
              </span>
            ) : (
              'Continuă la verificarea telefonului'
            )}
          </button>
        </div>

        {/* Required Fields Note */}
        <div className="text-xs text-gray-500 text-center">
          Câmpurile marcate cu <span className="text-red-500">*</span> sunt obligatorii
        </div>
      </form>
    </div>
  );
};

export default CustomerForm;