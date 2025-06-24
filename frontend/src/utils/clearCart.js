// Utility function to clear cart from all storage locations
export const clearAllCartData = () => {
  // Clear from localStorage
  localStorage.removeItem('cart');
  localStorage.removeItem('cartId');
  
  // Clear from sessionStorage
  sessionStorage.removeItem('cart');
  
  // Log for debugging
  console.log('Cart data cleared from all storage locations');
};