// Script to clear cart - run this in browser console
localStorage.removeItem('cart');
localStorage.removeItem('cartId');
sessionStorage.removeItem('cart');
console.log('Cart cleared successfully');
window.location.reload();