import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useCartContext } from '../contexts/CartContext';
import CustomerForm from '../components/checkout/CustomerForm';
import SMSVerification from '../components/checkout/SMSVerification';
import CartSummary from '../components/cart/CartSummary';
import { PageLoading } from '../components/common/Loading';
import ButtonLoading, { CheckoutButton } from '../components/common/ButtonLoading';
import ErrorMessage, { NetworkError, ServerError } from '../components/common/ErrorMessage';
import { SectionErrorBoundary } from '../components/common/ErrorBoundary';
import { useApiToast } from '../components/common/Toast';

const Checkout = () => {
  const navigate = useNavigate();
  const { 
    cartItems, 
    cartItemCount, 
    cartSubtotal, 
    cartTax, 
    cartTotal,
    formatPrice,
    clearCart 
  } = useCartContext();

  const [currentStep, setCurrentStep] = useState(1);
  const [customerData, setCustomerData] = useState(null);
  const [verificationData, setVerificationData] = useState(null);
  const [isProcessingOrder, setIsProcessingOrder] = useState(false);
  const [orderError, setOrderError] = useState('');
  const [stepError, setStepError] = useState('');
  
  const toast = useApiToast();

  // Redirect to cart if empty
  useEffect(() => {
    if (cartItemCount === 0) {
      navigate('/cart');
    }
  }, [cartItemCount, navigate]);

  // Checkout steps configuration
  const steps = [
    { id: 1, name: 'Informații de livrare', completed: false },
    { id: 2, name: 'Verificare telefon', completed: false },
    { id: 3, name: 'Finalizare comandă', completed: false }
  ];

  // Update step completion status
  const getStepStatus = (stepId) => {
    if (stepId < currentStep) return 'completed';
    if (stepId === currentStep) return 'current';
    return 'upcoming';
  };

  // Handle customer form submission with error handling
  const handleCustomerFormSubmit = async (data) => {
    try {
      setStepError('');
      setCustomerData(data);
      setCurrentStep(2);
      setOrderError('');
      
      toast.showSuccess('Informațiile de livrare au fost salvate.');
    } catch (err) {
      console.error('Error saving customer data:', err);
      setStepError('Eroare la salvarea informațiilor. Încercați din nou.');
      toast.handleApiError(err, 'Nu am putut salva informațiile de livrare.');
    }
  };

  // Handle SMS verification success with error handling
  const handleVerificationSuccess = async (data) => {
    try {
      setStepError('');
      setVerificationData(data);
      setCurrentStep(3);
      setOrderError('');
      
      toast.showSuccess('Telefonul a fost verificat cu succes.');
    } catch (err) {
      console.error('Error processing verification:', err);
      setStepError('Eroare la procesarea verificării. Încercați din nou.');
      toast.handleApiError(err, 'Nu am putut procesa verificarea telefonului.');
    }
  };

  // Handle back navigation
  const handleBackToCustomerForm = () => {
    setCurrentStep(1);
    setVerificationData(null);
    setOrderError('');
    setStepError('');
  };

  // Handle back to SMS verification
  const handleBackToVerification = () => {
    setCurrentStep(2);
    setOrderError('');
    setStepError('');
  };

  // Process final order with comprehensive error handling
  const handlePlaceOrder = async () => {
    setIsProcessingOrder(true);
    setOrderError('');
    setStepError('');

    try {
      // Validate required data before processing
      if (!customerData) {
        throw new Error('Informațiile de livrare lipsesc. Reveniți la primul pas.');
      }
      
      if (!verificationData) {
        throw new Error('Verificarea telefonului este necesară. Reveniți la pasul anterior.');
      }
      
      if (cartItems.length === 0) {
        throw new Error('Coșul este gol. Adăugați produse înainte de a plasa comanda.');
      }

      // Prepare order data
      const orderData = {
        customer: customerData,
        phone: {
          number: customerData.phone,
          verified: true,
          verificationData: verificationData
        },
        items: cartItems.map(item => ({
          productId: item.id,
          name: item.name,
          price: item.price,
          quantity: item.quantity,
          unit: item.unit,
          subtotal: item.price * item.quantity
        })),
        pricing: {
          subtotal: cartSubtotal,
          tax: cartTax,
          total: cartTotal,
          currency: 'RON'
        },
        delivery: {
          type: 'local_delivery',
          address: `${customerData.address}, ${customerData.city}, ${customerData.county} ${customerData.postalCode}`,
          notes: customerData.notes || ''
        },
        orderDate: new Date().toISOString(),
        orderNumber: `PFL-${Date.now()}`,
        status: 'pending'
      };

      // Simulate API call for order processing
      await new Promise(resolve => setTimeout(resolve, 2000));

      // In real implementation, this would be:
      // const response = await api.post('/orders', orderData);

      console.log('Order processed:', orderData);

      // Show success message
      toast.showSuccess('Comanda a fost plasată cu succes!');

      // Clear cart and navigate to confirmation
      await clearCart();
      navigate('/order-confirmation', { 
        state: { 
          orderData,
          orderNumber: orderData.orderNumber 
        } 
      });

    } catch (error) {
      console.error('Order processing error:', error);
      
      // Set appropriate error message based on error type
      if (error.isNetworkError) {
        setOrderError('Problemă de conexiune. Verificați internetul și încercați din nou.');
        toast.handleNetworkError();
      } else if (error.status >= 500) {
        setOrderError('Eroare la server. Încercați din nou în câteva minute.');
        toast.handleApiError(error, 'Problemă la server. Comanda nu a putut fi procesată.');
      } else if (error.message) {
        setOrderError(error.message);
        toast.handleApiError(error);
      } else {
        setOrderError('A apărut o eroare neașteptată la procesarea comenzii. Încercați din nou.');
        toast.showError('Eroare la procesarea comenzii. Încercați din nou.');
      }
    } finally {
      setIsProcessingOrder(false);
    }
  };

  // Render step content based on current step
  const renderStepContent = () => {
    switch (currentStep) {
      case 1:
        return (
          <SectionErrorBoundary>
            <CustomerForm
              onSubmit={handleCustomerFormSubmit}
              initialData={customerData}
              loading={false}
            />
          </SectionErrorBoundary>
        );
      
      case 2:
        return (
          <SectionErrorBoundary>
            <SMSVerification
              phoneNumber={customerData?.phone}
              onVerificationSuccess={handleVerificationSuccess}
              onBack={handleBackToCustomerForm}
              loading={false}
            />
          </SectionErrorBoundary>
        );
      
      case 3:
        return (
          <SectionErrorBoundary>
            <div className="bg-white rounded-lg shadow-sm p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-6">
              Confirmarea comenzii
            </h2>

            {/* Customer Information Summary */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-800 mb-3">
                Informații de livrare
              </h3>
              <div className="bg-gray-50 rounded-lg p-4 space-y-2 text-sm">
                <div><strong>Nume:</strong> {customerData?.firstName} {customerData?.lastName}</div>
                <div><strong>Telefon:</strong> {customerData?.phone} ✅ <span className="text-green-600">Verificat</span></div>
                <div><strong>Email:</strong> {customerData?.email}</div>
                <div><strong>Adresă:</strong> {customerData?.address}</div>
                <div><strong>Oraș:</strong> {customerData?.city}, {customerData?.county}</div>
                <div><strong>Cod poștal:</strong> {customerData?.postalCode}</div>
                {customerData?.notes && (
                  <div><strong>Observații:</strong> {customerData.notes}</div>
                )}
              </div>
            </div>

            {/* Order Items Summary */}
            <div className="mb-6">
              <h3 className="text-lg font-medium text-gray-800 mb-3">
                Produsele comandate ({cartItemCount})
              </h3>
              <div className="bg-gray-50 rounded-lg p-4 space-y-3">
                {cartItems.map((item) => (
                  <div key={item.id} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                    <div>
                      <span className="font-medium">{item.name}</span>
                      {item.isOrganic && (
                        <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">
                          BIO
                        </span>
                      )}
                      <div className="text-sm text-gray-600">
                        {formatPrice(item.price)} × {item.quantity} {item.unit}
                      </div>
                    </div>
                    <div className="font-medium">
                      {formatPrice(item.price * item.quantity)}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Pricing Summary */}
            <div className="mb-6">
              <div className="bg-green-50 border border-green-200 rounded-lg p-4 space-y-2">
                <div className="flex justify-between text-sm">
                  <span>Subtotal:</span>
                  <span>{formatPrice(cartSubtotal)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>TVA (19%):</span>
                  <span>{formatPrice(cartTax)}</span>
                </div>
                <div className="flex justify-between text-sm">
                  <span>Livrare locală:</span>
                  <span className="text-green-600">Gratuită</span>
                </div>
                <div className="border-t border-green-200 pt-2 flex justify-between font-bold text-lg">
                  <span>Total de plată:</span>
                  <span className="text-green-700">{formatPrice(cartTotal)}</span>
                </div>
              </div>
            </div>

            {/* Order Error */}
            {orderError && (
              <div className="mb-6">
                <ErrorMessage message={orderError} />
              </div>
            )}

            {/* Action Buttons */}
            <div className="space-y-3">
              <CheckoutButton
                onClick={handlePlaceOrder}
                loading={isProcessingOrder}
                loadingText="Se procesează comanda..."
                size="large"
              >
                Finalizează comanda ({formatPrice(cartTotal)})
              </CheckoutButton>

              <ButtonLoading
                onClick={handleBackToVerification}
                disabled={isProcessingOrder}
                variant="outline"
                size="medium"
                fullWidth={true}
                icon="←"
              >
                Înapoi la verificarea telefonului
              </ButtonLoading>
            </div>
          </div>
          </SectionErrorBoundary>
        );
      
      default:
        return null;
    }
  };

  // Show loading if cart is empty (will redirect)
  if (cartItemCount === 0) {
    return (
      <PageLoading message="Se redirecționează către coș..." />
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Breadcrumb Navigation */}
        <nav className="mb-6 text-sm text-gray-600">
          <Link to="/" className="hover:text-green-600 transition-colors">
            Acasă
          </Link>
          <span className="mx-2">›</span>
          <Link to="/cart" className="hover:text-green-600 transition-colors">
            Coș
          </Link>
          <span className="mx-2">›</span>
          <span className="text-gray-900">Finalizare comandă</span>
        </nav>

        {/* Page Header */}
        <div className="text-center mb-8">
          <h1 className="text-3xl md:text-4xl font-bold text-gray-900 mb-4">
            Finalizare comandă
          </h1>
          <p className="text-lg text-gray-600">
            Completați informațiile de livrare și confirmați comanda pentru produsele locale
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-between max-w-2xl mx-auto px-4">
            {steps.map((step, index) => {
              const status = getStepStatus(step.id);
              return (
                <div key={step.id} className="flex items-center flex-1">
                  <div className={`flex items-center justify-center w-10 h-10 sm:w-12 sm:h-12 rounded-full border-2 font-semibold text-sm ${
                    status === 'completed' 
                      ? 'bg-green-600 border-green-600 text-white' 
                      : status === 'current'
                      ? 'bg-white border-green-600 text-green-600'
                      : 'bg-gray-100 border-gray-300 text-gray-500'
                  }`}>
                    {status === 'completed' ? '✓' : step.id}
                  </div>
                  
                  <div className="ml-3 hidden sm:block">
                    <div className={`text-sm font-medium ${
                      status === 'current' ? 'text-green-600' : 'text-gray-500'
                    }`}>
                      {step.name}
                    </div>
                  </div>

                  {index < steps.length - 1 && (
                    <div className={`hidden sm:block w-12 h-0.5 ml-6 ${
                      status === 'completed' ? 'bg-green-600' : 'bg-gray-300'
                    }`} />
                  )}
                </div>
              );
            })}
          </div>
        </div>

        {/* Error Display */}
        {(orderError || stepError) && (
          <div className="mb-6">
            <SectionErrorBoundary>
              {orderError && orderError.includes('conexiune') ? (
                <NetworkError 
                  onRetry={() => {
                    setOrderError('');
                    if (currentStep === 3) {
                      handlePlaceOrder();
                    }
                  }}
                />
              ) : orderError && orderError.includes('server') ? (
                <ServerError 
                  onRetry={() => {
                    setOrderError('');
                    if (currentStep === 3) {
                      handlePlaceOrder();
                    }
                  }}
                />
              ) : (
                <ErrorMessage 
                  message={orderError || stepError}
                  showRetry={currentStep === 3}
                  onRetry={() => {
                    setOrderError('');
                    setStepError('');
                    if (currentStep === 3) {
                      handlePlaceOrder();
                    }
                  }}
                />
              )}
            </SectionErrorBoundary>
          </div>
        )}

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8">
          {/* Checkout Form */}
          <div className="lg:col-span-2">
            {renderStepContent()}
          </div>

          {/* Order Summary Sidebar */}
          <div className="lg:col-span-1">
            <div className="sticky top-4">
              <SectionErrorBoundary>
                <CartSummary 
                  showCheckoutButton={false}
                  showTitle={true}
                  className="mb-6"
                />
              </SectionErrorBoundary>

              {/* Security and Trust */}
              <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                <h4 className="text-sm font-medium text-blue-800 mb-2">
                  🔒 Comanda dvs. este securizată
                </h4>
                <div className="text-sm text-blue-700 space-y-1">
                  <p>• Informațiile sunt protejate prin criptare SSL</p>
                  <p>• Verificare prin SMS pentru siguranță</p>
                  <p>• Produse de la fermieri verificați</p>
                  <p>• Suport local 24/7</p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Footer Help */}
        <div className="mt-12 text-center">
          <div className="bg-white rounded-lg shadow-sm p-6 max-w-2xl mx-auto">
            <h3 className="text-lg font-semibold text-gray-900 mb-3">
              Aveți întrebări despre comandă?
            </h3>
            <p className="text-gray-600 mb-4">
              Echipa noastră vă poate ajuta cu orice întrebări despre produse, livrare sau plată.
            </p>
            <div className="flex flex-col sm:flex-row gap-3 justify-center text-sm">
              <div className="flex items-center justify-center gap-2 text-gray-600">
                <span>📧</span>
                <span>comenzi@pefocdelemne.ro</span>
              </div>
              <div className="flex items-center justify-center gap-2 text-gray-600">
                <span>📞</span>
                <span>0700 123 456</span>
              </div>
              <div className="flex items-center justify-center gap-2 text-gray-600">
                <span>⏰</span>
                <span>Luni - Duminică, 8:00 - 20:00</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Checkout;