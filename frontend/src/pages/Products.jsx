import React, { useState, useEffect, useCallback } from 'react';
import { useCartContext } from '../contexts/CartContext';
import api from '../services/api';
import { SectionLoading } from '../components/common/Loading';
import { ProductGridSkeleton } from '../components/common/LoadingSkeleton';
import ErrorMessage from '../components/common/ErrorMessage';
import { useApiToast } from '../components/common/Toast';
import ProductFilter from '../components/product/ProductFilter';

const Products = () => {
  const { addToCart } = useCartContext();
  const toast = useApiToast();
  
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
      const response = await api.get('/categories');
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
        limit: '12',
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
      
      const response = await api.get(`/products?${params}`);
      
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
  }, [currentPage, debouncedSearchTerm, selectedCategory, sortBy, sortOrder, toast]);

  // Initialize data
  useEffect(() => {
    fetchCategories();
  }, [fetchCategories]);

  // Fetch products when filters change
  useEffect(() => {
    setCurrentPage(1); // Reset to first page when filters change
  }, [debouncedSearchTerm, selectedCategory, sortBy, sortOrder]);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

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
  const handleAddToCart = async (product) => {
    try {
      await addToCart(product, 1);
    } catch (err) {
      console.error('Error adding to cart:', err);
    }
  };

  // Format price for display
  const formatPrice = (price) => {
    return new Intl.NumberFormat('ro-RO', {
      style: 'currency',
      currency: 'RON'
    }).format(price);
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-6">
          <div className="text-center">
            <h1 className="text-3xl font-bold text-gray-900">Produse Locale</h1>
            <p className="mt-2 text-gray-600">
              Descoperiți produsele locale de calitate de la producătorii din România
            </p>
          </div>
        </div>
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Product Filter Component */}
        <div className="mb-8">
          <ProductFilter
            // Filter state
            searchTerm={debouncedSearchTerm}
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
                {/* Products Grid */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 mb-8">
                  {products.map((product) => (
                    <div key={product.id} className="bg-white rounded-lg shadow-md hover:shadow-lg transition-shadow">
                      <div className="aspect-w-1 aspect-h-1 w-full overflow-hidden rounded-t-lg bg-gray-200">
                        {product.images && product.images.length > 0 ? (
                          <img
                            src={product.images[0]}
                            alt={product.name}
                            className="h-48 w-full object-cover object-center"
                            onError={(e) => {
                              e.target.src = '/images/placeholder-product.jpg';
                            }}
                          />
                        ) : (
                          <div className="h-48 w-full bg-gray-200 flex items-center justify-center">
                            <svg className="h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                            </svg>
                          </div>
                        )}
                      </div>
                      
                      <div className="p-4">
                        <h3 className="text-lg font-medium text-gray-900 mb-1">{product.name}</h3>
                        <p className="text-sm text-gray-600 mb-2 line-clamp-2">{product.description}</p>
                        
                        {product.category && (
                          <span className="inline-block bg-green-100 text-green-800 text-xs font-medium px-2.5 py-0.5 rounded-full mb-2">
                            {product.category.name}
                          </span>
                        )}
                        
                        <div className="flex items-center justify-between">
                          <span className="text-xl font-bold text-green-600">
                            {formatPrice(product.price)}
                          </span>
                          
                          <button
                            onClick={() => handleAddToCart(product)}
                            className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-colors"
                          >
                            Adaugă în coș
                          </button>
                        </div>
                        
                        {product.stock_quantity < 10 && product.stock_quantity > 0 && (
                          <p className="text-sm text-orange-600 mt-2">
                            Doar {product.stock_quantity} în stoc
                          </p>
                        )}
                      </div>
                    </div>
                  ))}
                </div>

                {/* Pagination */}
                {totalPages > 1 && (
                  <div className="flex items-center justify-center space-x-2">
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
    </div>
  );
};

export default Products;