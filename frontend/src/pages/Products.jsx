import React, { useState, useEffect, useCallback, useRef, useMemo } from 'react';
import { useCartContext } from '../contexts/CartContext';
import api from '../services/api';
import { SectionLoading } from '../components/common/Loading';
import { ProductGridSkeleton } from '../components/common/LoadingSkeleton';
import ErrorMessage from '../components/common/ErrorMessage';
import { useApiToast } from '../components/common/Toast';
import ProductFilter from '../components/product/ProductFilter';
import ProductCard from '../components/product/ProductCard';

const Products = () => {
  const { addToCart } = useCartContext();
  const toastApi = useApiToast();
  const toast = useMemo(() => toastApi, []);
  
  // State management
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchLoading, setSearchLoading] = useState(false);
  
  // Filter and search state
  const [searchTerm, setSearchTerm] = useState('');
  const [debouncedSearchTerm, setDebouncedSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  
  // Pagination state
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalItems, setTotalItems] = useState(0);
  
  // Search metadata
  const [searchActive, setSearchActive] = useState(false);
  const [searchResultCount, setSearchResultCount] = useState(0);
  
  // Mobile detection
  const [isMobile, setIsMobile] = useState(false);
  const [showMobileSearch, setShowMobileSearch] = useState(false);
  const [showMobileFilters, setShowMobileFilters] = useState(false);
  
  // Track initial mount
  const isInitialMount = useRef(true);
  
  useEffect(() => {
    const checkMobile = () => {
      const touchDevice = ('ontouchstart' in window) || 
        (navigator.maxTouchPoints > 0) ||
        (navigator.msMaxTouchPoints > 0);
      setIsMobile(touchDevice && window.innerWidth <= 768);
    };
    
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  // Transform API product data to ProductCard format
  const transformProduct = (apiProduct) => {
    return {
      id: apiProduct.id,
      name: apiProduct.name,
      price: apiProduct.price,
      image: apiProduct.images && apiProduct.images.length > 0 
        ? apiProduct.images[0] 
        : '/images/placeholder-product.jpg',
      description: apiProduct.description,
      category: apiProduct.category?.name || 'General',
      unit: apiProduct.unit || 'bucată',
      inStock: apiProduct.is_available !== false && apiProduct.stock_quantity > 0,
      stock_quantity: apiProduct.stock_quantity,
      quantity: 1
    };
  };

  // Debounce search term
  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSearchTerm(searchTerm);
    }, 300);
    
    return () => clearTimeout(timer);
  }, [searchTerm]);

  // Fetch categories with comprehensive error handling
  const fetchCategories = useCallback(async () => {
    try {
      const response = await api.get('/categories/');
      if (response.data.success) {
        setCategories(response.data.data.categories);
      }
    } catch (err) {
      console.error('Error fetching categories:', err);
      
      // Don't show toast for category errors as they're not critical
      // Categories will just show empty, which is acceptable
      if (err.isNetworkError) {
        console.warn('Network error loading categories');
      } else {
        console.warn('Server error loading categories');
      }
    }
  }, []);

  // Fetch products with comprehensive error handling
  const fetchProducts = useCallback(async () => {
    try {
      if (debouncedSearchTerm) {
        setSearchLoading(true);
      } else {
        setLoading(true);
      }
      setError(null);
      
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '20',
        available_only: 'true',
        sort_by: sortBy,
        sort_order: sortOrder
      });
      
      if (debouncedSearchTerm.trim()) {
        params.set('q', debouncedSearchTerm.trim());
      }
      
      if (selectedCategory) {
        params.set('category_id', selectedCategory);
      }
      
      const response = await api.get(`/products/?${params}`);
      
      if (response.data.success) {
        setProducts(response.data.data.products);
        setTotalPages(response.data.data.pagination.total_pages);
        setTotalItems(response.data.data.pagination.total_items);
        
        // Handle search metadata
        if (response.data.data.search) {
          setSearchActive(true);
          setSearchResultCount(response.data.data.search.total_results);
        } else {
          setSearchActive(false);
          setSearchResultCount(0);
        }
      }
    } catch (err) {
      console.error('Error fetching products:', err);
      
      // Set appropriate error message based on error type
      if (err.isNetworkError) {
        setError('Nu ne putem conecta la server. Verificați conexiunea la internet.');
      } else if (err.status >= 500) {
        setError('Eroare la server. Încercați din nou în câteva minute.');
      } else if (err.status === 404) {
        setError('Serviciul de produse nu este disponibil momentan.');
      } else {
        setError(err.message || 'Eroare la încărcarea produselor. Încercați din nou.');
      }
      
      // Show toast notification for critical errors
      if (err.isNetworkError) {
        toast.handleNetworkError();
      } else if (err.status >= 500) {
        toast.handleApiError(err, 'Problemă la server. Produsele nu pot fi încărcate.');
      }
    } finally {
      setLoading(false);
      setSearchLoading(false);
    }
  }, [currentPage, debouncedSearchTerm, selectedCategory, sortBy, sortOrder]);

  // Initialize categories once on mount
  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  // Fetch products when filters or page changes
  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  // Reset to first page when filters change (but not on initial mount)
  useEffect(() => {
    if (isInitialMount.current) {
      isInitialMount.current = false;
    } else {
      setCurrentPage(1);
    }
  }, [debouncedSearchTerm, selectedCategory, sortBy, sortOrder]);

  // Clear search
  const clearSearch = () => {
    setSearchTerm('');
    setDebouncedSearchTerm('');
  };

  // Handle category filter change
  const handleCategoryChange = (categoryId) => {
    setSelectedCategory(categoryId);
  };

  // Handle sort change
  const handleSortChange = (field, order) => {
    setSortBy(field);
    setSortOrder(order);
  };

  // Handle pagination
  const handlePageChange = (page) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  // Handle add to cart
  const handleAddToCart = async (product, quantity) => {
    try {
      console.log('Adding to cart:', product, 'Quantity:', quantity);
      await addToCart(product, quantity || product.quantity || 1);
      // No toast - visual feedback only
    } catch (err) {
      console.error('Error adding to cart:', err);
      // Silent error - button will show normal state
    }
  };


  return (
    <div className="min-h-screen bg-white">
      <div className="max-w-7xl mx-auto py-2">
        {/* Header */}
        <div className="mb-4 sm:mb-6">
          <div className="flex items-start justify-between">
            <div className="flex-1">
              <h1 className="text-xl sm:text-2xl font-semibold text-gray-900">Produse</h1>
              <p className="mt-1 text-sm text-gray-500">
                Produse locale de calitate de la producători verificați
              </p>
            </div>
            {/* Mobile action buttons */}
            {isMobile && (
              <div className="flex items-center gap-2 ml-4">
                {/* Search button */}
                <button
                  onClick={() => setShowMobileSearch(!showMobileSearch)}
                  className="p-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors"
                  aria-label="Căutare"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                  </svg>
                </button>
                {/* Filter button */}
                <button
                  onClick={() => setShowMobileFilters(!showMobileFilters)}
                  className="p-2 rounded-lg bg-gray-100 text-gray-700 hover:bg-gray-200 transition-colors relative"
                  aria-label="Filtre"
                >
                  <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
                  </svg>
                  {/* Active filters badge */}
                  {(selectedCategory || (searchTerm && searchTerm.trim())) && (
                    <span className="absolute -top-1 -right-1 w-3 h-3 bg-green-600 rounded-full"></span>
                  )}
                </button>
              </div>
            )}
          </div>
        </div>

        {/* Mobile Search Bar - Slides down when activated */}
        {isMobile && (
          <div className={`overflow-hidden transition-all duration-300 ease-in-out ${
            showMobileSearch ? 'max-h-20 mb-4' : 'max-h-0'
          }`}>
            <div className="relative">
              <input
                type="text"
                placeholder="Căutați produse..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-10 py-2.5 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 text-sm"
                autoFocus={showMobileSearch}
              />
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
                </svg>
              </div>
              {searchTerm && (
                <button
                  onClick={() => {
                    setSearchTerm('');
                    setDebouncedSearchTerm('');
                  }}
                  className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
                >
                  <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              )}
            </div>
          </div>
        )}

        {/* Product Filter Component - Hidden on mobile when using icon approach */}
        <div className={isMobile ? 'hidden' : 'mb-8'}>
          <ProductFilter
            // Filter state
            searchTerm={searchTerm}
            selectedCategory={selectedCategory}
            sortBy={sortBy}
            sortOrder={sortOrder}
            
            // Data
            categories={categories}
            
            // Callbacks
            onSearchChange={setSearchTerm}
            onCategoryChange={handleCategoryChange}
            onSortChange={handleSortChange}
            onClearSearch={clearSearch}
            
            // UI state
            loading={loading}
            searchLoading={searchLoading}
            totalResults={searchActive ? searchResultCount : totalItems}
            
            // Configuration
            showResultCount={true}
            collapsible={true}
          />
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6">
            <ErrorMessage message={error} />
          </div>
        )}

        {/* Loading State */}
        {loading ? (
          <div className="mb-8">
            <ProductGridSkeleton count={12} />
          </div>
        ) : searchLoading ? (
          <div className="mb-8">
            <SectionLoading message="Se caută produse..." height="h-64" />
          </div>
        ) : (
          <>
            {/* No Results */}
            {products.length === 0 ? (
              <div className="text-center py-12">
                <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2M4 13h2m13-8-4 4-4-4m-1 4l4 4 4-4" />
                </svg>
                <h3 className="mt-2 text-sm font-medium text-gray-900">
                  {searchActive 
                    ? `Nu am găsit produse pentru "${debouncedSearchTerm}"` 
                    : 'Nu există produse disponibile'
                  }
                </h3>
                <p className="mt-1 text-sm text-gray-500">
                  {searchActive 
                    ? 'Încercați cu alte cuvinte cheie sau navigați prin categorii.' 
                    : 'Reveniti în curând pentru produse noi.'
                  }
                </p>
                {searchActive && (
                  <div className="mt-4">
                    <button
                      onClick={clearSearch}
                      className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md transition-colors"
                    >
                      Vezi toate produsele
                    </button>
                  </div>
                )}
              </div>
            ) : (
              <>
                {/* Products Masonry Grid - Pinterest Style */}
                <div className="relative w-full">
                  <div className="masonry-grid">
                    {products.map((product) => {
                      const transformedProduct = transformProduct(product);
                      
                      return (
                        <ProductCard 
                          key={product.id}
                          product={transformedProduct}
                          onAddToCart={handleAddToCart}
                          className="masonry-item"
                        />
                      );
                    })}
                  </div>
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-center space-x-2 mt-8">
                    <button
                      onClick={() => handlePageChange(currentPage - 1)}
                      disabled={currentPage === 1}
                      className="px-3 py-2 rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Anterior
                    </button>
                    
                    {[...Array(totalPages)].map((_, index) => {
                      const page = index + 1;
                      return (
                        <button
                          key={page}
                          onClick={() => handlePageChange(page)}
                          className={`px-3 py-2 rounded-md text-sm font-medium ${
                            currentPage === page
                              ? 'bg-green-600 text-white'
                              : 'border border-gray-300 bg-white text-gray-500 hover:bg-gray-50'
                          }`}
                        >
                          {page}
                        </button>
                      );
                    })}
                    
                    <button
                      onClick={() => handlePageChange(currentPage + 1)}
                      disabled={currentPage === totalPages}
                      className="px-3 py-2 rounded-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Următorul
                    </button>
                  </div>
                )}
              </>
            )}
          </>
        )}
      </div>
      
      {/* Mobile Filters Modal */}
      {isMobile && showMobileFilters && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 z-50 flex items-end"
          onClick={() => setShowMobileFilters(false)}
        >
          <div 
            className="bg-white w-full rounded-t-2xl max-h-[80vh] overflow-hidden animate-slide-up"
            onClick={(e) => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between p-4 border-b">
              <h3 className="text-lg font-semibold">Filtre și Sortare</h3>
              <button
                onClick={() => setShowMobileFilters(false)}
                className="p-2 hover:bg-gray-100 rounded-lg"
              >
                <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
            
            {/* Modal Content */}
            <div className="p-4 space-y-6 overflow-y-auto max-h-[calc(80vh-80px)]">
              {/* Categories */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-3">Categorii</h4>
                <div className="space-y-2">
                  <button
                    onClick={() => {
                      setSelectedCategory('');
                      setShowMobileFilters(false);
                    }}
                    className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                      selectedCategory === '' 
                        ? 'bg-green-600 text-white' 
                        : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                    }`}
                  >
                    Toate produsele
                  </button>
                  {categories.map((category) => (
                    <button
                      key={category.id}
                      onClick={() => {
                        setSelectedCategory(category.id);
                        setShowMobileFilters(false);
                      }}
                      className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                        selectedCategory === category.id 
                          ? 'bg-green-600 text-white' 
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {category.name}
                    </button>
                  ))}
                </div>
              </div>
              
              {/* Sort Options */}
              <div>
                <h4 className="text-sm font-medium text-gray-700 mb-3">Sortare</h4>
                <div className="space-y-2">
                  {[
                    { value: 'name-asc', label: 'Nume (A-Z)' },
                    { value: 'name-desc', label: 'Nume (Z-A)' },
                    { value: 'price-asc', label: 'Preț crescător' },
                    { value: 'price-desc', label: 'Preț descrescător' },
                    { value: 'created_at-desc', label: 'Cele mai noi' }
                  ].map((option) => (
                    <button
                      key={option.value}
                      onClick={() => {
                        const [field, order] = option.value.split('-');
                        handleSortChange(field, order);
                        setShowMobileFilters(false);
                      }}
                      className={`w-full text-left px-4 py-2 rounded-lg transition-colors ${
                        `${sortBy}-${sortOrder}` === option.value
                          ? 'bg-green-600 text-white' 
                          : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
                      }`}
                    >
                      {option.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Products;