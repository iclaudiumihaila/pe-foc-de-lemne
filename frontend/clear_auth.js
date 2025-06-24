// Clear all auth data
localStorage.removeItem('checkout_token');
localStorage.removeItem('auth_access_token');
localStorage.removeItem('adminToken');
localStorage.removeItem('authToken');
sessionStorage.clear();
console.log('All auth data cleared');
