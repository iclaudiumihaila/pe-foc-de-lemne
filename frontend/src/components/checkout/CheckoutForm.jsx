import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useCartContext } from '../../contexts/CartContext';
import PhoneVerification from './PhoneVerification';
import api from '../../services/api';
import { clearAllCartData } from '../../utils/clearCart';

const CheckoutForm = ({ isMobile = false }) => {
  const navigate = useNavigate();
  const { cartItems, cartSubtotal, clearCart, cartId, formatPrice } = useCartContext();
  
  const [verified, setVerified] = useState(false);
  const [customerData, setCustomerData] = useState(null);
  const [selectedAddress, setSelectedAddress] = useState(null);
  const [showAddressForm, setShowAddressForm] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState('');
  
  const [addressForm, setAddressForm] = useState({
    street: '',
    city: '',
    county: '',
    postal_code: '',
    notes: ''
  });

  const DELIVERY_FEE = 20;
  const total = cartSubtotal + DELIVERY_FEE;

  useEffect(() => {
    if (cartItems.length === 0) {
      navigate('/cart');
    }
  }, [cartItems, navigate]);

  useEffect(() => {
    const checkExistingSession = async () => {
      const token = localStorage.getItem('checkout_token');
      if (token) {
        try {
          const response = await api.get('/checkout/addresses');
          if (response.data.success) {
            setVerified(true);
            setCustomerData({
              phone_masked: response.data.customer?.phone_masked || 'Client verificat',
              name: response.data.customer?.name || '',
              addresses: response.data.addresses || []
            });
            if (response.data.addresses?.length > 0) {
              const lastUsed = response.data.addresses.find(addr => addr.is_default) || response.data.addresses[0];
              setSelectedAddress(lastUsed);
            } else {
              setShowAddressForm(true);
            }
          }
        } catch (err) {
          localStorage.removeItem('checkout_token');
        }
      }
    };
    
    checkExistingSession();
  }, []);

  const handlePhoneVerified = (data) => {
    setVerified(true);
    setCustomerData(data.customer);
    
    if (data.customer?.addresses?.length > 0) {
      const lastUsed = data.customer.addresses.find(addr => addr.is_default) || data.customer.addresses[0];
      setSelectedAddress(lastUsed);
    } else {
      setShowAddressForm(true);
    }
  };

  const handleAddressSubmit = async (e) => {
    e.preventDefault();
    setError('');
    
    try {
      const response = await api.post('/checkout/addresses', {
        ...addressForm,
        is_default: true
      });
      
      if (response.data.success) {
        setSelectedAddress(response.data.address);
        setShowAddressForm(false);
      }
    } catch (err) {
      setError(err.response?.data?.message || 'Eroare la salvarea adresei');
    }
  };

  const handleSubmitOrder = async () => {
    console.log('=== SUBMIT ORDER START ===');
    console.log('Selected address:', selectedAddress);
    console.log('Verified:', verified);
    console.log('Cart items:', cartItems);
    
    if (!selectedAddress) {
      setError('Vă rugăm să selectați o adresă de livrare');
      return;
    }

    setIsSubmitting(true);
    setError('');

    try {
      // Use the cart session ID from context (or fallback to localStorage)
      const existingCartId = cartId || localStorage.getItem('cartId');
      console.log('Using existing cart session ID:', existingCartId);
      
      // If cart wasn't synced to backend, sync now
      if (!existingCartId) {
        throw new Error('No cart session found');
      }
      
      // Ensure all items are synced to backend
      for (const item of cartItems) {
        try {
          await api.post('/cart/', {
            product_id: item.id || item._id,
            quantity: item.quantity,
            session_id: existingCartId
          });
        } catch (error) {
          // Ignore duplicate item errors, continue with order
          console.log('Cart sync error (may be duplicate):', error);
        }
      }
      
      console.log('Cart items:', cartItems);
      console.log('Checkout token:', localStorage.getItem('checkout_token'));
      
      // Create the order with the existing cart session ID
      const orderData = {
        cart_session_id: existingCartId,
        customer_info: {
          customer_name: customerData?.name || 'Client',
          special_instructions: ''
        }
      };
      
      // If authenticated (has valid checkout token), send address_id
      // Otherwise send full customer info for guest checkout
      if (verified && selectedAddress.id) {
        orderData.address_id = selectedAddress.id;
        console.log('Using address_id:', selectedAddress.id);
      } else {
        orderData.customer_info = {
          customer_name: customerData.name || 'Client',
          phone_number: '0775156791', // Your phone number
          delivery_address: {
            street: selectedAddress.street,
            city: selectedAddress.city,
            county: selectedAddress.county,
            postal_code: selectedAddress.postal_code,
            notes: selectedAddress.notes || ''
          },
          special_instructions: ''
        };
        console.log('Using customer_info:', orderData.customer_info);
      }

      console.log('Final order data:', JSON.stringify(orderData, null, 2));
      const response = await api.post('/orders', orderData);
      
      if (response.data.success) {
        // Clear cart from context and all storage
        clearCart();
        clearAllCartData();
        
        // Also clear the cart session ID if stored
        localStorage.removeItem('cartSessionId');
        sessionStorage.removeItem('cartSessionId');
        
        // Navigate to confirmation page
        navigate(`/confirmare-comanda/${response.data.order.order_number}`);
      }
    } catch (err) {
      console.error('Order creation error:', err);
      console.error('Error response:', err.response?.data);
      const errorMsg = err.response?.data?.message || err.response?.data?.error?.message || 'Eroare la plasarea comenzii';
      setError(errorMsg);
    } finally {
      setIsSubmitting(false);
    }
  };

  const counties = [
    'Alba', 'Arad', 'Argeș', 'Bacău', 'Bihor', 'Bistrița-Năsăud', 'Botoșani', 'Brașov',
    'Brăila', 'București', 'Buzău', 'Caraș-Severin', 'Călărași', 'Cluj', 'Constanța',
    'Covasna', 'Dâmbovița', 'Dolj', 'Galați', 'Giurgiu', 'Gorj', 'Harghita', 'Hunedoara',
    'Ialomița', 'Iași', 'Ilfov', 'Maramureș', 'Mehedinți', 'Mureș', 'Neamț', 'Olt',
    'Prahova', 'Satu Mare', 'Sălaj', 'Sibiu', 'Suceava', 'Teleorman', 'Timiș', 'Tulcea',
    'Vaslui', 'Vâlcea', 'Vrancea'
  ];

  if (isMobile) {
    return (
      <div className="flex flex-col min-h-[calc(100vh-64px)]">
        <div className="flex-1 overflow-y-auto">
          <div className="px-4 py-4">
            {error && (
              <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg">
                {error}
              </div>
            )}
            
            {!verified && (
              <div className="bg-gray-50 rounded-lg p-4">
                <h3 className="font-semibold text-lg mb-4">Verificare telefon</h3>
                <PhoneVerification onVerified={handlePhoneVerified} />
              </div>
            )}
            
            {verified && (
              <div className="space-y-4">
                {/* Customer Info */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <p className="text-sm text-gray-600">Client verificat</p>
                  <p className="font-medium">{customerData?.phone_masked}</p>
                </div>
                
                {/* Delivery Address */}
                <div className="bg-gray-50 rounded-lg p-4">
                  <h3 className="font-semibold text-lg mb-3">Adresă livrare</h3>
                  
                  {selectedAddress && !showAddressForm ? (
                    <div>
                      <p className="font-medium">{selectedAddress.street}</p>
                      <p className="text-gray-600">
                        {selectedAddress.city}, {selectedAddress.county} {selectedAddress.postal_code}
                      </p>
                      <button
                        onClick={() => setShowAddressForm(true)}
                        className="text-green-600 text-sm mt-2 underline"
                      >
                        Modifică adresa
                      </button>
                    </div>
                  ) : (
                    <form onSubmit={handleAddressSubmit} className="space-y-3">
                      <input
                        type="text"
                        required
                        value={addressForm.street}
                        onChange={(e) => setAddressForm({...addressForm, street: e.target.value})}
                        className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                        placeholder="Strada și număr"
                      />

                      <div className="grid grid-cols-2 gap-3">
                        <input
                          type="text"
                          required
                          value={addressForm.city}
                          onChange={(e) => setAddressForm({...addressForm, city: e.target.value})}
                          className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                          placeholder="Oraș"
                        />

                        <select
                          required
                          value={addressForm.county}
                          onChange={(e) => setAddressForm({...addressForm, county: e.target.value})}
                          className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                        >
                          <option value="">Județ</option>
                          {counties.map(county => (
                            <option key={county} value={county}>{county}</option>
                          ))}
                        </select>
                      </div>

                      <input
                        type="text"
                        required
                        pattern="[0-9]{6}"
                        value={addressForm.postal_code}
                        onChange={(e) => setAddressForm({...addressForm, postal_code: e.target.value})}
                        className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                        placeholder="Cod poștal (6 cifre)"
                      />
                      
                      <textarea
                        value={addressForm.notes}
                        onChange={(e) => setAddressForm({...addressForm, notes: e.target.value})}
                        className="w-full px-3 py-3 border border-gray-300 rounded-lg focus:outline-none focus:border-green-500"
                        placeholder="Notițe pentru livrare (opțional)"
                        rows="2"
                      />

                      <div className="flex gap-3">
                        <button
                          type="submit"
                          className="flex-1 bg-green-600 text-white px-4 py-3 rounded-lg hover:bg-green-700 font-medium"
                        >
                          Salvează adresa
                        </button>
                        {selectedAddress && (
                          <button
                            type="button"
                            onClick={() => setShowAddressForm(false)}
                            className="px-4 py-3 text-gray-600"
                          >
                            Anulează
                          </button>
                        )}
                      </div>
                    </form>
                  )}
                </div>
              </div>
            )}
          </div>
          
          {/* Add padding for fixed bottom */}
          <div className="h-32" />
        </div>
        
        {/* Fixed Bottom Summary - Mobile */}
        {verified && selectedAddress && (
          <div className="fixed bottom-0 left-0 right-0 bg-white shadow-[0_-4px_12px_rgba(0,0,0,0.08)] z-30">
            <div className="px-4 py-3">
              {/* Summary Row */}
              <div className="flex items-center justify-between mb-3">
                <div>
                  <p className="text-sm text-gray-600">Total comandă</p>
                  <p className="text-2xl font-bold text-gray-900">
                    {formatPrice(total)}
                  </p>
                </div>
                <div className="text-right">
                  <p className="text-xs text-gray-500">Livrare</p>
                  <p className="text-sm font-medium text-green-600">Gratuită</p>
                </div>
              </div>
              
              {/* Place Order Button */}
              <button
                onClick={handleSubmitOrder}
                disabled={isSubmitting || !selectedAddress}
                className="block w-full bg-green-600 text-white text-center py-3 rounded-lg font-medium text-base hover:bg-green-700 transition-colors shadow-sm disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                {isSubmitting ? 'Se procesează...' : 'Plasează comanda'}
              </button>
            </div>
          </div>
        )}
      </div>
    );
  }

  // Desktop version (existing code)
  return (
    <div className="container mx-auto px-4 py-8">
      <h1 className="text-2xl font-bold mb-6">Finalizare comandă</h1>
      
      <div className="grid lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2">
          {error && (
            <div className="mb-4 p-3 bg-red-50 text-red-600 rounded">
              {error}
            </div>
          )}
          
          {!verified && (
            <div>
              <PhoneVerification onVerified={handlePhoneVerified} />
            </div>
          )}
          
          {verified && (
            <div className="space-y-6">
              <div>
                <h3 className="font-medium mb-3">Adresă livrare</h3>
                
                {selectedAddress && !showAddressForm ? (
                  <div className="border border-gray-200 rounded p-4">
                    <p>{selectedAddress.street}</p>
                    <p className="text-gray-600">
                      {selectedAddress.city}, {selectedAddress.county} {selectedAddress.postal_code}
                    </p>
                    <button
                      onClick={() => setShowAddressForm(true)}
                      className="text-green-600 text-sm mt-2"
                    >
                      Modifică
                    </button>
                  </div>
                ) : (
                  <form onSubmit={handleAddressSubmit} className="space-y-3">
                    <input
                      type="text"
                      required
                      value={addressForm.street}
                      onChange={(e) => setAddressForm({...addressForm, street: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-green-500"
                      placeholder="Strada și număr"
                    />

                    <div className="grid grid-cols-2 gap-3">
                      <input
                        type="text"
                        required
                        value={addressForm.city}
                        onChange={(e) => setAddressForm({...addressForm, city: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-green-500"
                        placeholder="Oraș"
                      />

                      <select
                        required
                        value={addressForm.county}
                        onChange={(e) => setAddressForm({...addressForm, county: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-green-500"
                      >
                        <option value="">Județ</option>
                        {counties.map(county => (
                          <option key={county} value={county}>{county}</option>
                        ))}
                      </select>
                    </div>

                    <input
                      type="text"
                      required
                      pattern="[0-9]{6}"
                      value={addressForm.postal_code}
                      onChange={(e) => setAddressForm({...addressForm, postal_code: e.target.value})}
                      className="w-full px-3 py-2 border border-gray-300 rounded focus:outline-none focus:border-green-500"
                      placeholder="Cod poștal"
                    />

                    <div className="flex gap-3">
                      <button
                        type="submit"
                        className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                      >
                        Salvează
                      </button>
                      {selectedAddress && (
                        <button
                          type="button"
                          onClick={() => setShowAddressForm(false)}
                          className="text-gray-600 px-4 py-2"
                        >
                          Anulează
                        </button>
                      )}
                    </div>
                  </form>
                )}
              </div>

              {selectedAddress && !showAddressForm && (
                <button
                  onClick={handleSubmitOrder}
                  disabled={isSubmitting}
                  className="w-full bg-green-600 text-white py-3 rounded hover:bg-green-700 disabled:bg-gray-400"
                >
                  {isSubmitting ? 'Se procesează...' : 'Plasează comanda'}
                </button>
              )}
            </div>
          )}
        </div>

        <div className="lg:col-span-1">
          <div className="bg-gray-50 rounded p-4">
            <h3 className="font-medium mb-3">Comandă</h3>
            
            <div className="space-y-2 pb-3 border-b">
              {cartItems.map(item => (
                <div key={item._id || item.id} className="flex justify-between text-sm">
                  <span>{item.name} × {item.quantity}</span>
                  <span>{(item.price * item.quantity).toFixed(2)} RON</span>
                </div>
              ))}
            </div>
            
            <div className="pt-3 space-y-1">
              <div className="flex justify-between text-sm">
                <span>Subtotal</span>
                <span>{cartSubtotal.toFixed(2)} RON</span>
              </div>
              <div className="flex justify-between text-sm">
                <span>Transport</span>
                <span>{DELIVERY_FEE.toFixed(2)} RON</span>
              </div>
              <div className="flex justify-between font-medium pt-2 border-t">
                <span>Total</span>
                <span>{total.toFixed(2)} RON</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default CheckoutForm;