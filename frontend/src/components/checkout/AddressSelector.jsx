import React, { useState, useEffect } from 'react';
import api from '../../services/api';

const AddressSelector = ({ onAddressSelected, allowNewAddress = true }) => {
  const [addresses, setAddresses] = useState([]);
  const [selectedAddressId, setSelectedAddressId] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [showNewAddressForm, setShowNewAddressForm] = useState(false);
  const [newAddress, setNewAddress] = useState({
    street: '',
    city: '',
    county: '',
    postal_code: '',
    notes: '',
    set_as_default: false
  });

  // Romanian counties for validation
  const counties = [
    'Alba', 'Arad', 'Argeș', 'Bacău', 'Bihor', 'Bistrița-Năsăud', 'Botoșani',
    'Brăila', 'Brașov', 'București', 'Buzău', 'Călărași', 'Caraș-Severin',
    'Cluj', 'Constanța', 'Covasna', 'Dâmbovița', 'Dolj', 'Galați', 'Giurgiu',
    'Gorj', 'Harghita', 'Hunedoara', 'Ialomița', 'Iași', 'Ilfov', 'Maramureș',
    'Mehedinți', 'Mureș', 'Neamț', 'Olt', 'Prahova', 'Sălaj', 'Satu Mare',
    'Sibiu', 'Suceava', 'Teleorman', 'Timiș', 'Tulcea', 'Vâlcea', 'Vaslui', 'Vrancea'
  ];

  useEffect(() => {
    fetchAddresses();
  }, []);

  const fetchAddresses = async () => {
    try {
      setLoading(true);
      const response = await api.get('/checkout/addresses');
      
      if (response.data.success) {
        setAddresses(response.data.addresses);
        
        // Auto-select default address
        const defaultAddress = response.data.addresses.find(addr => addr.is_default);
        if (defaultAddress) {
          setSelectedAddressId(defaultAddress.id);
        }
      }
    } catch (err) {
      setError('Eroare la încărcarea adreselor. Încercați din nou.');
      console.error('Error fetching addresses:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddressSelect = (addressId) => {
    setSelectedAddressId(addressId);
    setShowNewAddressForm(false);
    
    const address = addresses.find(addr => addr.id === addressId);
    if (address && onAddressSelected) {
      onAddressSelected({ type: 'existing', addressId, address });
    }
  };

  const handleNewAddressChange = (field, value) => {
    setNewAddress(prev => ({ ...prev, [field]: value }));
  };

  const validateNewAddress = () => {
    const errors = [];
    
    if (!newAddress.street || newAddress.street.length < 5) {
      errors.push('Strada trebuie să aibă minim 5 caractere');
    }
    
    if (!newAddress.city || newAddress.city.length < 2) {
      errors.push('Orașul este obligatoriu');
    }
    
    if (!newAddress.county || !counties.includes(newAddress.county)) {
      errors.push('Selectați un județ valid');
    }
    
    if (!newAddress.postal_code || !/^\d{6}$/.test(newAddress.postal_code)) {
      errors.push('Codul poștal trebuie să aibă 6 cifre');
    }
    
    return errors;
  };

  const handleSaveNewAddress = async () => {
    const errors = validateNewAddress();
    if (errors.length > 0) {
      setError(errors.join('. '));
      return;
    }

    setLoading(true);
    setError('');

    try {
      const response = await api.post('/checkout/addresses', newAddress);
      
      if (response.data.success) {
        // Add new address to list
        const savedAddress = response.data.address;
        setAddresses(prev => [...prev, savedAddress]);
        
        // Select the new address
        setSelectedAddressId(savedAddress.id);
        setShowNewAddressForm(false);
        
        // Clear form
        setNewAddress({
          street: '',
          city: '',
          county: '',
          postal_code: '',
          notes: '',
          set_as_default: false
        });
        
        // Notify parent
        if (onAddressSelected) {
          onAddressSelected({ type: 'new', addressId: savedAddress.id, address: savedAddress });
        }
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error?.message || 'Eroare la salvarea adresei';
      setError(errorMsg);
    } finally {
      setLoading(false);
    }
  };

  if (loading && addresses.length === 0) {
    return (
      <div className="text-center py-8">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-green-600 mx-auto"></div>
        <p className="mt-4 text-gray-600">Se încarcă adresele...</p>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto">
      <h3 className="text-xl font-semibold mb-4">Adresa de livrare</h3>

      {error && (
        <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-700 rounded-md">
          {error}
        </div>
      )}

      {/* Existing addresses */}
      {addresses.length > 0 && !showNewAddressForm && (
        <div className="space-y-3 mb-4">
          {addresses.map(address => (
            <div
              key={address.id}
              onClick={() => handleAddressSelect(address.id)}
              className={`
                p-4 border rounded-lg cursor-pointer transition-all
                ${selectedAddressId === address.id 
                  ? 'border-green-500 bg-green-50' 
                  : 'border-gray-300 hover:border-gray-400'
                }
              `}
            >
              <div className="flex items-start">
                <div className="flex-shrink-0 mt-1">
                  <div className={`
                    w-5 h-5 rounded-full border-2 
                    ${selectedAddressId === address.id 
                      ? 'border-green-500 bg-green-500' 
                      : 'border-gray-400'
                    }
                  `}>
                    {selectedAddressId === address.id && (
                      <svg className="w-3 h-3 text-white m-auto" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 111.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    )}
                  </div>
                </div>
                
                <div className="ml-3 flex-grow">
                  <div className="font-medium">{address.street}</div>
                  <div className="text-sm text-gray-600">
                    {address.city}, {address.county} {address.postal_code}
                  </div>
                  {address.notes && (
                    <div className="text-sm text-gray-500 mt-1">{address.notes}</div>
                  )}
                  {address.is_default && (
                    <span className="inline-block mt-1 px-2 py-1 text-xs bg-green-100 text-green-700 rounded">
                      Adresă implicită
                    </span>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Add new address button/form */}
      {allowNewAddress && (
        <>
          {!showNewAddressForm ? (
            <button
              onClick={() => setShowNewAddressForm(true)}
              className="w-full py-3 px-4 border-2 border-dashed border-gray-300 rounded-lg text-gray-600 hover:border-gray-400 hover:text-gray-700 transition-colors"
            >
              + Adaugă adresă nouă
            </button>
          ) : (
            <div className="border border-gray-300 rounded-lg p-4">
              <h4 className="font-medium mb-4">Adresă nouă</h4>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Stradă și număr *
                  </label>
                  <input
                    type="text"
                    value={newAddress.street}
                    onChange={(e) => handleNewAddressChange('street', e.target.value)}
                    className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    placeholder="ex: Strada Primăverii 25, Bl. A2, Ap. 10"
                  />
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Oraș *
                    </label>
                    <input
                      type="text"
                      value={newAddress.city}
                      onChange={(e) => handleNewAddressChange('city', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      placeholder="ex: București"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Județ *
                    </label>
                    <select
                      value={newAddress.county}
                      onChange={(e) => handleNewAddressChange('county', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                    >
                      <option value="">Selectați județul</option>
                      {counties.map(county => (
                        <option key={county} value={county}>{county}</option>
                      ))}
                    </select>
                  </div>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Cod poștal *
                    </label>
                    <input
                      type="text"
                      value={newAddress.postal_code}
                      onChange={(e) => handleNewAddressChange('postal_code', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      placeholder="ex: 010101"
                      maxLength="6"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Note (opțional)
                    </label>
                    <input
                      type="text"
                      value={newAddress.notes}
                      onChange={(e) => handleNewAddressChange('notes', e.target.value)}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500"
                      placeholder="ex: Etaj 3, interfon 12"
                    />
                  </div>
                </div>

                <div className="flex items-center">
                  <input
                    type="checkbox"
                    id="set_as_default"
                    checked={newAddress.set_as_default}
                    onChange={(e) => handleNewAddressChange('set_as_default', e.target.checked)}
                    className="h-4 w-4 text-green-600 focus:ring-green-500 border-gray-300 rounded"
                  />
                  <label htmlFor="set_as_default" className="ml-2 text-sm text-gray-700">
                    Setează ca adresă implicită
                  </label>
                </div>

                <div className="flex gap-3">
                  <button
                    onClick={handleSaveNewAddress}
                    disabled={loading}
                    className="flex-1 bg-green-600 text-white py-2 px-4 rounded-md hover:bg-green-700 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2 disabled:bg-gray-400"
                  >
                    {loading ? 'Se salvează...' : 'Salvează adresa'}
                  </button>
                  <button
                    onClick={() => {
                      setShowNewAddressForm(false);
                      setError('');
                    }}
                    className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                  >
                    Anulează
                  </button>
                </div>
              </div>
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default AddressSelector;