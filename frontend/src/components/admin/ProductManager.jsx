import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import Loading from '../common/Loading';
import ErrorMessage from '../common/ErrorMessage';

const ProductManager = () => {
  const { isAuthenticated, isAdmin, tokens } = useAuth();
  
  // State management
  const [products, setProducts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Pagination and filtering
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  
  // Modal and form states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [formLoading, setFormLoading] = useState(false);
  
  // Form data
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    category_id: '',
    stock_quantity: '',
    weight_grams: '',
    preparation_time_hours: '',
    images: ['']
  });

  // Fetch products
  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        page: currentPage.toString(),
        limit: '10',
        available_only: 'false', // Show all products for admin
        sort_by: sortBy,
        sort_order: sortOrder
      });
      
      if (searchTerm) {
        // Use search endpoint if there's a search term
        params.set('q', searchTerm);
        const response = await api.get(`/products/search?${params}`);
        if (response.data.success) {
          setProducts(response.data.data.products);
          setTotalPages(response.data.data.pagination.total_pages);
        }
      } else {
        // Use regular listing endpoint
        if (categoryFilter) {
          params.set('category_id', categoryFilter);
        }
        const response = await api.get(`/products?${params}`);
        if (response.data.success) {
          setProducts(response.data.data.products);
          setTotalPages(response.data.data.pagination.total_pages);
        }
      }
    } catch (err) {
      console.error('Error fetching products:', err);
      setError('Eroare la încărcarea produselor. Încercați din nou.');
    } finally {
      setLoading(false);
    }
  }, [currentPage, searchTerm, categoryFilter, sortBy, sortOrder]);

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      const response = await api.get('/categories');
      if (response.data.success) {
        setCategories(response.data.data.categories);
      }
    } catch (err) {
      console.error('Error fetching categories:', err);
    }
  }, []);

  // Initialize data
  useEffect(() => {
    if (isAuthenticated && isAdmin()) {
      fetchProducts();
      fetchCategories();
    }
  }, [isAuthenticated, isAdmin, fetchProducts, fetchCategories]);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  // Handle image URL changes
  const handleImageChange = (index, value) => {
    setFormData(prev => ({
      ...prev,
      images: prev.images.map((img, i) => i === index ? value : img)
    }));
  };

  // Add new image field
  const addImageField = () => {
    if (formData.images.length < 10) {
      setFormData(prev => ({
        ...prev,
        images: [...prev.images, '']
      }));
    }
  };

  // Remove image field
  const removeImageField = (index) => {
    if (formData.images.length > 1) {
      setFormData(prev => ({
        ...prev,
        images: prev.images.filter((_, i) => i !== index)
      }));
    }
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      price: '',
      category_id: '',
      stock_quantity: '',
      weight_grams: '',
      preparation_time_hours: '',
      images: ['']
    });
  };

  // Handle create product
  const handleCreateProduct = async (e) => {
    e.preventDefault();
    try {
      setFormLoading(true);
      setError(null);
      
      // Filter out empty images
      const filteredImages = formData.images.filter(img => img.trim() !== '');
      
      const productData = {
        ...formData,
        images: filteredImages,
        price: parseFloat(formData.price),
        stock_quantity: parseInt(formData.stock_quantity) || 0,
        weight_grams: formData.weight_grams ? parseInt(formData.weight_grams) : null,
        preparation_time_hours: formData.preparation_time_hours ? parseInt(formData.preparation_time_hours) : null
      };

      const response = await api.post('/admin/products', productData, {
        headers: {
          'Authorization': `Bearer ${tokens?.access_token}`
        }
      });

      if (response.data.success) {
        setSuccess('Produsul a fost creat cu succes!');
        setShowCreateModal(false);
        resetForm();
        fetchProducts();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Error creating product:', err);
      const errorMessage = err.response?.data?.error?.message || 'Eroare la crearea produsului. Încercați din nou.';
      setError(errorMessage);
    } finally {
      setFormLoading(false);
    }
  };

  // Handle edit product
  const handleEditProduct = async (e) => {
    e.preventDefault();
    try {
      setFormLoading(true);
      setError(null);
      
      // Filter out empty images
      const filteredImages = formData.images.filter(img => img.trim() !== '');
      
      const productData = {
        ...formData,
        images: filteredImages,
        price: parseFloat(formData.price),
        stock_quantity: parseInt(formData.stock_quantity) || 0,
        weight_grams: formData.weight_grams ? parseInt(formData.weight_grams) : null,
        preparation_time_hours: formData.preparation_time_hours ? parseInt(formData.preparation_time_hours) : null
      };

      const response = await api.put(`/admin/products/${selectedProduct.id}`, productData, {
        headers: {
          'Authorization': `Bearer ${tokens?.access_token}`
        }
      });

      if (response.data.success) {
        setSuccess('Produsul a fost actualizat cu succes!');
        setShowEditModal(false);
        resetForm();
        setSelectedProduct(null);
        fetchProducts();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Error updating product:', err);
      const errorMessage = err.response?.data?.error?.message || 'Eroare la actualizarea produsului. Încercați din nou.';
      setError(errorMessage);
    } finally {
      setFormLoading(false);
    }
  };

  // Handle delete product
  const handleDeleteProduct = async () => {
    try {
      setFormLoading(true);
      setError(null);

      const response = await api.delete(`/admin/products/${selectedProduct.id}`, {
        headers: {
          'Authorization': `Bearer ${tokens?.access_token}`
        }
      });

      if (response.data.success) {
        setSuccess('Produsul a fost dezactivat cu succes!');
        setShowDeleteModal(false);
        setSelectedProduct(null);
        fetchProducts();
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Error deleting product:', err);
      const errorMessage = err.response?.data?.error?.message || 'Eroare la dezactivarea produsului. Încercați din nou.';
      setError(errorMessage);
    } finally {
      setFormLoading(false);
    }
  };

  // Open edit modal
  const openEditModal = (product) => {
    setSelectedProduct(product);
    setFormData({
      name: product.name || '',
      description: product.description || '',
      price: product.price?.toString() || '',
      category_id: product.category?.id || '',
      stock_quantity: product.stock_quantity?.toString() || '0',
      weight_grams: product.weight_grams?.toString() || '',
      preparation_time_hours: product.preparation_time_hours?.toString() || '',
      images: product.images?.length > 0 ? product.images : ['']
    });
    setShowEditModal(true);
  };

  // Open delete modal
  const openDeleteModal = (product) => {
    setSelectedProduct(product);
    setShowDeleteModal(true);
  };

  // Close modals
  const closeModals = () => {
    setShowCreateModal(false);
    setShowEditModal(false);
    setShowDeleteModal(false);
    setSelectedProduct(null);
    resetForm();
    setError(null);
  };

  // Handle search
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1);
    fetchProducts();
  };

  // Handle filter changes
  const handleFilterChange = (filterType, value) => {
    setCurrentPage(1);
    if (filterType === 'category') {
      setCategoryFilter(value);
    } else if (filterType === 'sort') {
      const [field, order] = value.split('_');
      setSortBy(field);
      setSortOrder(order);
    }
  };

  // Check admin access
  if (!isAuthenticated || !isAdmin()) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <ErrorMessage message="Acces neautorizat. Trebuie să fiți autentificat ca administrator." />
      </div>
    );
  }

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="flex justify-between items-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Gestionare Produse</h1>
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white font-medium py-2 px-4 rounded-lg transition-colors"
        >
          Adaugă Produs Nou
        </button>
      </div>

      {/* Success/Error Messages */}
      {success && (
        <div className="mb-6 p-4 bg-green-100 border border-green-400 text-green-700 rounded-lg">
          {success}
        </div>
      )}
      
      {error && (
        <div className="mb-6">
          <ErrorMessage message={error} />
        </div>
      )}

      {/* Filters and Search */}
      <div className="bg-white rounded-lg shadow-sm border p-6 mb-6">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Search */}
          <form onSubmit={handleSearch} className="md:col-span-2">
            <div className="flex">
              <input
                type="text"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                placeholder="Căutați produse..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-l-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
              />
              <button
                type="submit"
                className="px-4 py-2 bg-blue-600 text-white rounded-r-lg hover:bg-blue-700 transition-colors"
              >
                Căutare
              </button>
            </div>
          </form>

          {/* Category Filter */}
          <select
            value={categoryFilter}
            onChange={(e) => handleFilterChange('category', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="">Toate categoriile</option>
            {categories.map(category => (
              <option key={category.id} value={category.id}>
                {category.name}
              </option>
            ))}
          </select>

          {/* Sort */}
          <select
            value={`${sortBy}_${sortOrder}`}
            onChange={(e) => handleFilterChange('sort', e.target.value)}
            className="px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="name_asc">Nume (A-Z)</option>
            <option value="name_desc">Nume (Z-A)</option>
            <option value="price_asc">Preț (crescător)</option>
            <option value="price_desc">Preț (descrescător)</option>
            <option value="stock_quantity_asc">Stoc (crescător)</option>
            <option value="stock_quantity_desc">Stoc (descrescător)</option>
            <option value="created_at_desc">Cel mai recent</option>
            <option value="created_at_asc">Cel mai vechi</option>
          </select>
        </div>
      </div>

      {/* Products Table */}
      {loading ? (
        <div className="flex justify-center py-12">
          <Loading size="large" message="Se încarcă produsele..." />
        </div>
      ) : products.length === 0 ? (
        <div className="text-center py-12">
          <p className="text-gray-500 text-lg">Nu au fost găsite produse.</p>
        </div>
      ) : (
        <div className="bg-white rounded-lg shadow-sm border overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Produs
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Categorie
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Preț
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Stoc
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Status
                  </th>
                  <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Acțiuni
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {products.map((product) => (
                  <tr key={product.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        {product.images && product.images[0] && (
                          <div className="flex-shrink-0 h-10 w-10">
                            <img
                              className="h-10 w-10 rounded-lg object-cover"
                              src={product.images[0]}
                              alt={product.name}
                              onError={(e) => {
                                e.target.style.display = 'none';
                              }}
                            />
                          </div>
                        )}
                        <div className="ml-4">
                          <div className="text-sm font-medium text-gray-900">
                            {product.name}
                          </div>
                          <div className="text-sm text-gray-500 truncate max-w-xs">
                            {product.description}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm text-gray-900">
                        {product.category?.name || 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className="text-sm font-medium text-gray-900">
                        {product.price ? `${product.price.toFixed(2)} RON` : 'N/A'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`text-sm font-medium ${product.stock_quantity > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {product.stock_quantity || 0}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      <span className={`inline-flex px-2 py-1 text-xs font-semibold rounded-full ${
                        product.is_available && product.stock_quantity > 0
                          ? 'bg-green-100 text-green-800'
                          : 'bg-red-100 text-red-800'
                      }`}>
                        {product.is_available && product.stock_quantity > 0 ? 'Disponibil' : 'Indisponibil'}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                      <button
                        onClick={() => openEditModal(product)}
                        className="text-blue-600 hover:text-blue-900 mr-3 transition-colors"
                      >
                        Editează
                      </button>
                      <button
                        onClick={() => openDeleteModal(product)}
                        className={`transition-colors ${
                          product.is_available 
                            ? 'text-red-600 hover:text-red-900' 
                            : 'text-gray-400 cursor-not-allowed'
                        }`}
                        disabled={!product.is_available}
                      >
                        {product.is_available ? 'Dezactivează' : 'Dezactivat'}
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
              <div className="flex-1 flex justify-between sm:hidden">
                <button
                  onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                  disabled={currentPage === 1}
                  className="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Anterior
                </button>
                <button
                  onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                  disabled={currentPage === totalPages}
                  className="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Următor
                </button>
              </div>
              <div className="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
                <div>
                  <p className="text-sm text-gray-700">
                    Pagina <span className="font-medium">{currentPage}</span> din{' '}
                    <span className="font-medium">{totalPages}</span>
                  </p>
                </div>
                <div>
                  <nav className="relative z-0 inline-flex rounded-md shadow-sm -space-x-px">
                    <button
                      onClick={() => setCurrentPage(Math.max(1, currentPage - 1))}
                      disabled={currentPage === 1}
                      className="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Anterior
                    </button>
                    <button
                      onClick={() => setCurrentPage(Math.min(totalPages, currentPage + 1))}
                      disabled={currentPage === totalPages}
                      className="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                      Următor
                    </button>
                  </nav>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Create Product Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">Adaugă Produs Nou</h3>
              <button
                onClick={closeModals}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleCreateProduct} className="space-y-4">
              {/* Product Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nume Produs *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Introduceți numele produsului"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descriere *
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  required
                  rows="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Descrierea produsului (minim 10 caractere)"
                />
              </div>

              {/* Price and Category */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Preț (RON) *
                  </label>
                  <input
                    type="number"
                    name="price"
                    value={formData.price}
                    onChange={handleInputChange}
                    required
                    step="0.01"
                    min="0.01"
                    max="9999.99"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Categorie *
                  </label>
                  <select
                    name="category_id"
                    value={formData.category_id}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Selectați categoria</option>
                    {categories.filter(cat => cat.is_active).map(category => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Stock, Weight, Prep Time */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Stoc
                  </label>
                  <input
                    type="number"
                    name="stock_quantity"
                    value={formData.stock_quantity}
                    onChange={handleInputChange}
                    min="0"
                    max="10000"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Greutate (grame)
                  </label>
                  <input
                    type="number"
                    name="weight_grams"
                    value={formData.weight_grams}
                    onChange={handleInputChange}
                    min="1"
                    max="50000"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Timp preparare (ore)
                  </label>
                  <input
                    type="number"
                    name="preparation_time_hours"
                    value={formData.preparation_time_hours}
                    onChange={handleInputChange}
                    min="1"
                    max="168"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="24"
                  />
                </div>
              </div>

              {/* Images */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Imagini (URL-uri)
                </label>
                {formData.images.map((image, index) => (
                  <div key={index} className="flex mb-2">
                    <input
                      type="url"
                      value={image}
                      onChange={(e) => handleImageChange(index, e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="https://example.com/image.jpg"
                    />
                    {formData.images.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeImageField(index)}
                        className="ml-2 px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                      >
                        Șterge
                      </button>
                    )}
                  </div>
                ))}
                {formData.images.length < 10 && (
                  <button
                    type="button"
                    onClick={addImageField}
                    className="mt-2 px-3 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                  >
                    Adaugă imagine
                  </button>
                )}
              </div>

              {/* Form Actions */}
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={closeModals}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Anulează
                </button>
                <button
                  type="submit"
                  disabled={formLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {formLoading ? 'Se salvează...' : 'Salvează Produsul'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Edit Product Modal */}
      {showEditModal && selectedProduct && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-11/12 md:w-3/4 lg:w-1/2 shadow-lg rounded-md bg-white">
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-lg font-medium text-gray-900">
                Editează Produs: {selectedProduct.name}
              </h3>
              <button
                onClick={closeModals}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>

            <form onSubmit={handleEditProduct} className="space-y-4">
              {/* Same form fields as create modal */}
              {/* Product Name */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Nume Produs *
                </label>
                <input
                  type="text"
                  name="name"
                  value={formData.name}
                  onChange={handleInputChange}
                  required
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Introduceți numele produsului"
                />
              </div>

              {/* Description */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Descriere *
                </label>
                <textarea
                  name="description"
                  value={formData.description}
                  onChange={handleInputChange}
                  required
                  rows="3"
                  className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  placeholder="Descrierea produsului (minim 10 caractere)"
                />
              </div>

              {/* Price and Category */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Preț (RON) *
                  </label>
                  <input
                    type="number"
                    name="price"
                    value={formData.price}
                    onChange={handleInputChange}
                    required
                    step="0.01"
                    min="0.01"
                    max="9999.99"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0.00"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Categorie *
                  </label>
                  <select
                    name="category_id"
                    value={formData.category_id}
                    onChange={handleInputChange}
                    required
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                  >
                    <option value="">Selectați categoria</option>
                    {categories.filter(cat => cat.is_active).map(category => (
                      <option key={category.id} value={category.id}>
                        {category.name}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {/* Stock, Weight, Prep Time */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Stoc
                  </label>
                  <input
                    type="number"
                    name="stock_quantity"
                    value={formData.stock_quantity}
                    onChange={handleInputChange}
                    min="0"
                    max="10000"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="0"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Greutate (grame)
                  </label>
                  <input
                    type="number"
                    name="weight_grams"
                    value={formData.weight_grams}
                    onChange={handleInputChange}
                    min="1"
                    max="50000"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="500"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-1">
                    Timp preparare (ore)
                  </label>
                  <input
                    type="number"
                    name="preparation_time_hours"
                    value={formData.preparation_time_hours}
                    onChange={handleInputChange}
                    min="1"
                    max="168"
                    className="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="24"
                  />
                </div>
              </div>

              {/* Images */}
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Imagini (URL-uri)
                </label>
                {formData.images.map((image, index) => (
                  <div key={index} className="flex mb-2">
                    <input
                      type="url"
                      value={image}
                      onChange={(e) => handleImageChange(index, e.target.value)}
                      className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="https://example.com/image.jpg"
                    />
                    {formData.images.length > 1 && (
                      <button
                        type="button"
                        onClick={() => removeImageField(index)}
                        className="ml-2 px-3 py-2 bg-red-500 text-white rounded-lg hover:bg-red-600 transition-colors"
                      >
                        Șterge
                      </button>
                    )}
                  </div>
                ))}
                {formData.images.length < 10 && (
                  <button
                    type="button"
                    onClick={addImageField}
                    className="mt-2 px-3 py-2 bg-gray-500 text-white rounded-lg hover:bg-gray-600 transition-colors"
                  >
                    Adaugă imagine
                  </button>
                )}
              </div>

              {/* Form Actions */}
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={closeModals}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Anulează
                </button>
                <button
                  type="submit"
                  disabled={formLoading}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {formLoading ? 'Se actualizează...' : 'Actualizează Produsul'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && selectedProduct && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-96 shadow-lg rounded-md bg-white">
            <div className="mt-3 text-center">
              <div className="mx-auto flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.732 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
              </div>
              <h3 className="text-lg leading-6 font-medium text-gray-900 mt-4">
                Confirmă dezactivarea
              </h3>
              <div className="mt-2 px-7 py-3">
                <p className="text-sm text-gray-500">
                  Ești sigur că vrei să dezactivezi produsul <strong>"{selectedProduct.name}"</strong>?
                  Produsul va fi marcat ca indisponibil, dar datele vor fi păstrate.
                </p>
              </div>
              <div className="flex justify-center space-x-3 pt-4">
                <button
                  onClick={closeModals}
                  className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Anulează
                </button>
                <button
                  onClick={handleDeleteProduct}
                  disabled={formLoading}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
                >
                  {formLoading ? 'Se dezactivează...' : 'Dezactivează Produsul'}
                </button>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductManager;