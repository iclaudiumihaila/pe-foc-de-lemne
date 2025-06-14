import React, { useState, useEffect, useCallback } from 'react';
import { useAuth } from '../../context/AuthContext';
import api from '../../services/api';
import Loading from '../common/Loading';
import ErrorMessage from '../common/ErrorMessage';

const CategoryManager = () => {
  const { isAuthenticated, isAdmin, tokens } = useAuth();
  
  // State management
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [success, setSuccess] = useState(null);
  
  // Search and filtering
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sortBy, setSortBy] = useState('name');
  const [sortOrder, setSortOrder] = useState('asc');
  
  // Modal and form states
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [showEditModal, setShowEditModal] = useState(false);
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [formLoading, setFormLoading] = useState(false);
  
  // Form data
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    display_order: ''
  });

  // Form validation errors
  const [formErrors, setFormErrors] = useState({});

  // Fetch categories
  const fetchCategories = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        active_only: 'false', // Show all categories for admin
        include_counts: 'true'
      });
      
      const response = await api.get(`/categories?${params}`);
      
      if (response.data.success) {
        let categoryList = response.data.data.categories;
        
        // Apply client-side filtering and sorting
        if (searchTerm) {
          categoryList = categoryList.filter(category =>
            category.name.toLowerCase().includes(searchTerm.toLowerCase())
          );
        }
        
        if (statusFilter) {
          const isActive = statusFilter === 'active';
          categoryList = categoryList.filter(category => category.is_active === isActive);
        }
        
        // Sort categories
        categoryList.sort((a, b) => {
          let aValue = a[sortBy];
          let bValue = b[sortBy];
          
          if (sortBy === 'name') {
            aValue = aValue.toLowerCase();
            bValue = bValue.toLowerCase();
          }
          
          if (sortOrder === 'asc') {
            return aValue > bValue ? 1 : -1;
          } else {
            return aValue < bValue ? 1 : -1;
          }
        });
        
        setCategories(categoryList);
      }
    } catch (err) {
      console.error('Error fetching categories:', err);
      setError('Eroare la încărcarea categoriilor. Încercați din nou.');
    } finally {
      setLoading(false);
    }
  }, [searchTerm, statusFilter, sortBy, sortOrder]);

  // Initialize data
  useEffect(() => {
    if (isAuthenticated && isAdmin()) {
      fetchCategories();
    }
  }, [isAuthenticated, isAdmin, fetchCategories]);

  // Handle form input changes
  const handleInputChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    
    // Clear field-specific error when user starts typing
    if (formErrors[name]) {
      setFormErrors(prev => ({
        ...prev,
        [name]: null
      }));
    }
  };

  // Validate form data
  const validateForm = () => {
    const errors = {};
    
    if (!formData.name.trim()) {
      errors.name = 'Numele categoriei este obligatoriu';
    } else if (formData.name.trim().length < 2) {
      errors.name = 'Numele categoriei trebuie să aibă cel puțin 2 caractere';
    } else if (formData.name.trim().length > 50) {
      errors.name = 'Numele categoriei nu poate avea mai mult de 50 de caractere';
    }
    
    if (formData.description && formData.description.length > 500) {
      errors.description = 'Descrierea nu poate avea mai mult de 500 de caractere';
    }
    
    if (formData.display_order && (isNaN(formData.display_order) || parseInt(formData.display_order) < 0 || parseInt(formData.display_order) > 10000)) {
      errors.display_order = 'Ordinea de afișare trebuie să fie un număr între 0 și 10000';
    }
    
    setFormErrors(errors);
    return Object.keys(errors).length === 0;
  };

  // Reset form
  const resetForm = () => {
    setFormData({
      name: '',
      description: '',
      display_order: ''
    });
    setFormErrors({});
  };

  // Handle create category
  const handleCreateCategory = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      setFormLoading(true);
      setError(null);
      
      const submitData = {
        name: formData.name.trim(),
        description: formData.description?.trim() || null,
        display_order: formData.display_order ? parseInt(formData.display_order) : null
      };
      
      const response = await api.post('/admin/categories', submitData, {
        headers: {
          'Authorization': `Bearer ${tokens?.access_token}`
        }
      });
      
      if (response.data.success) {
        setSuccess(response.data.message);
        setShowCreateModal(false);
        resetForm();
        fetchCategories();
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Error creating category:', err);
      if (err.response?.data?.error?.message) {
        setError(err.response.data.error.message);
      } else {
        setError('Eroare la crearea categoriei. Încercați din nou.');
      }
    } finally {
      setFormLoading(false);
    }
  };

  // Handle edit category
  const handleEditCategory = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }
    
    try {
      setFormLoading(true);
      setError(null);
      
      const submitData = {};
      
      // Only include changed fields
      if (formData.name.trim() !== selectedCategory.name) {
        submitData.name = formData.name.trim();
      }
      
      if ((formData.description?.trim() || null) !== selectedCategory.description) {
        submitData.description = formData.description?.trim() || null;
      }
      
      const newDisplayOrder = formData.display_order ? parseInt(formData.display_order) : null;
      if (newDisplayOrder !== selectedCategory.display_order) {
        submitData.display_order = newDisplayOrder;
      }
      
      if (Object.keys(submitData).length === 0) {
        setError('Nu au fost detectate modificări.');
        return;
      }
      
      const response = await api.put(`/admin/categories/${selectedCategory.id}`, submitData, {
        headers: {
          'Authorization': `Bearer ${tokens?.access_token}`
        }
      });
      
      if (response.data.success) {
        setSuccess(response.data.message);
        setShowEditModal(false);
        resetForm();
        setSelectedCategory(null);
        fetchCategories();
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Error updating category:', err);
      if (err.response?.data?.error?.message) {
        setError(err.response.data.error.message);
      } else {
        setError('Eroare la actualizarea categoriei. Încercați din nou.');
      }
    } finally {
      setFormLoading(false);
    }
  };

  // Handle delete category
  const handleDeleteCategory = async () => {
    try {
      setFormLoading(true);
      setError(null);
      
      const response = await api.delete(`/admin/categories/${selectedCategory.id}`, {
        headers: {
          'Authorization': `Bearer ${tokens?.access_token}`
        }
      });
      
      if (response.data.success) {
        setSuccess(response.data.message);
        setShowDeleteModal(false);
        setSelectedCategory(null);
        fetchCategories();
        
        // Clear success message after 3 seconds
        setTimeout(() => setSuccess(null), 3000);
      }
    } catch (err) {
      console.error('Error deleting category:', err);
      if (err.response?.data?.error?.message) {
        setError(err.response.data.error.message);
      } else if (err.response?.status === 409) {
        setError(err.response.data.error.message || 'Nu se poate șterge categoria care conține produse.');
      } else {
        setError('Eroare la ștergerea categoriei. Încercați din nou.');
      }
    } finally {
      setFormLoading(false);
    }
  };

  // Open edit modal
  const openEditModal = (category) => {
    setSelectedCategory(category);
    setFormData({
      name: category.name,
      description: category.description || '',
      display_order: category.display_order?.toString() || ''
    });
    setFormErrors({});
    setShowEditModal(true);
  };

  // Open delete modal
  const openDeleteModal = (category) => {
    setSelectedCategory(category);
    setShowDeleteModal(true);
  };

  // Close modals
  const closeModals = () => {
    setShowCreateModal(false);
    setShowEditModal(false);
    setShowDeleteModal(false);
    setSelectedCategory(null);
    resetForm();
    setError(null);
  };

  // Format date for display
  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('ro-RO', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Check if user is not authenticated or not admin
  if (!isAuthenticated || !isAdmin()) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="text-center">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Acces Interzis</h2>
          <p className="text-gray-600">Nu aveți permisiunea să accesați această pagină.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900">Gestiunea Categoriilor</h1>
        <p className="mt-2 text-gray-600">Gestionați categoriile de produse din magazin</p>
      </div>

      {/* Success/Error Messages */}
      {success && (
        <div className="mb-6 bg-green-50 border border-green-200 text-green-700 px-4 py-3 rounded-md">
          {success}
        </div>
      )}
      
      {error && (
        <div className="mb-6">
          <ErrorMessage message={error} />
        </div>
      )}

      {/* Controls */}
      <div className="mb-6 flex flex-col sm:flex-row gap-4 justify-between">
        <div className="flex flex-col sm:flex-row gap-4">
          {/* Search */}
          <div className="relative">
            <input
              type="text"
              placeholder="Căutați categorii..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="w-full sm:w-64 pl-10 pr-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
            />
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <svg className="h-5 w-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            </div>
          </div>
          
          {/* Status Filter */}
          <select
            value={statusFilter}
            onChange={(e) => setStatusFilter(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="">Toate categoriile</option>
            <option value="active">Doar active</option>
            <option value="inactive">Doar inactive</option>
          </select>
          
          {/* Sort Options */}
          <select
            value={`${sortBy}-${sortOrder}`}
            onChange={(e) => {
              const [field, order] = e.target.value.split('-');
              setSortBy(field);
              setSortOrder(order);
            }}
            className="px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
          >
            <option value="name-asc">Nume (A-Z)</option>
            <option value="name-desc">Nume (Z-A)</option>
            <option value="display_order-asc">Ordinea afișării (crescător)</option>
            <option value="display_order-desc">Ordinea afișării (descrescător)</option>
            <option value="product_count-desc">Numărul de produse (descrescător)</option>
            <option value="product_count-asc">Numărul de produse (crescător)</option>
          </select>
        </div>
        
        {/* Add Category Button */}
        <button
          onClick={() => setShowCreateModal(true)}
          className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-md font-medium transition-colors"
        >
          Adaugă Categorie Nouă
        </button>
      </div>

      {/* Categories List */}
      {loading ? (
        <Loading />
      ) : (
        <div className="bg-white shadow overflow-hidden sm:rounded-md">
          {categories.length === 0 ? (
            <div className="text-center py-12">
              <svg className="mx-auto h-12 w-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              <h3 className="mt-2 text-sm font-medium text-gray-900">Nu există categorii</h3>
              <p className="mt-1 text-sm text-gray-500">Începeți prin a crea prima categorie.</p>
            </div>
          ) : (
            <ul className="divide-y divide-gray-200">
              {categories.map((category) => (
                <li key={category.id} className="px-6 py-4">
                  <div className="flex items-center justify-between">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center space-x-3">
                        <h3 className="text-lg font-medium text-gray-900 truncate">
                          {category.name}
                        </h3>
                        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          category.is_active 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {category.is_active ? 'Activ' : 'Inactiv'}
                        </span>
                        {category.product_count > 0 && (
                          <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                            {category.product_count} {category.product_count === 1 ? 'produs' : 'produse'}
                          </span>
                        )}
                      </div>
                      {category.description && (
                        <p className="mt-1 text-sm text-gray-500 truncate">
                          {category.description}
                        </p>
                      )}
                      <div className="mt-2 flex items-center text-sm text-gray-500 space-x-4">
                        <span>Ordinea: {category.display_order || 'Nespecificat'}</span>
                        <span>Creat: {formatDate(category.created_at)}</span>
                        {category.updated_at !== category.created_at && (
                          <span>Actualizat: {formatDate(category.updated_at)}</span>
                        )}
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-2">
                      <button
                        onClick={() => openEditModal(category)}
                        className="bg-yellow-100 hover:bg-yellow-200 text-yellow-800 px-3 py-1 rounded-md text-sm font-medium transition-colors"
                      >
                        Editează
                      </button>
                      <button
                        onClick={() => openDeleteModal(category)}
                        className="bg-red-100 hover:bg-red-200 text-red-800 px-3 py-1 rounded-md text-sm font-medium transition-colors"
                      >
                        Șterge
                      </button>
                    </div>
                  </div>
                </li>
              ))}
            </ul>
          )}
        </div>
      )}

      {/* Create Category Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Adaugă Categorie Nouă</h3>
              
              <form onSubmit={handleCreateCategory}>
                <div className="space-y-4">
                  {/* Name */}
                  <div>
                    <label htmlFor="name" className="block text-sm font-medium text-gray-700">
                      Nume Categorie *
                    </label>
                    <input
                      type="text"
                      id="name"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      className={`mt-1 block w-full border ${formErrors.name ? 'border-red-300' : 'border-gray-300'} rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                      placeholder="Introduceți numele categoriei"
                      autoFocus
                    />
                    {formErrors.name && (
                      <p className="mt-1 text-sm text-red-600">{formErrors.name}</p>
                    )}
                  </div>
                  
                  {/* Description */}
                  <div>
                    <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                      Descriere
                    </label>
                    <textarea
                      id="description"
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      rows={3}
                      className={`mt-1 block w-full border ${formErrors.description ? 'border-red-300' : 'border-gray-300'} rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                      placeholder="Descrierea categoriei (opțional)"
                    />
                    {formErrors.description && (
                      <p className="mt-1 text-sm text-red-600">{formErrors.description}</p>
                    )}
                  </div>
                  
                  {/* Display Order */}
                  <div>
                    <label htmlFor="display_order" className="block text-sm font-medium text-gray-700">
                      Ordinea de Afișare
                    </label>
                    <input
                      type="number"
                      id="display_order"
                      name="display_order"
                      value={formData.display_order}
                      onChange={handleInputChange}
                      min="0"
                      max="10000"
                      className={`mt-1 block w-full border ${formErrors.display_order ? 'border-red-300' : 'border-gray-300'} rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                      placeholder="0"
                    />
                    {formErrors.display_order && (
                      <p className="mt-1 text-sm text-red-600">{formErrors.display_order}</p>
                    )}
                    <p className="mt-1 text-sm text-gray-500">Număr întreg între 0 și 10000 (opțional)</p>
                  </div>
                </div>
                
                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    type="button"
                    onClick={closeModals}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors"
                    disabled={formLoading}
                  >
                    Anulează
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors disabled:opacity-50"
                    disabled={formLoading}
                  >
                    {formLoading ? 'Se salvează...' : 'Salvează'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Edit Category Modal */}
      {showEditModal && selectedCategory && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <h3 className="text-lg font-medium text-gray-900 mb-4">Editează Categoria</h3>
              
              <form onSubmit={handleEditCategory}>
                <div className="space-y-4">
                  {/* Name */}
                  <div>
                    <label htmlFor="edit-name" className="block text-sm font-medium text-gray-700">
                      Nume Categorie *
                    </label>
                    <input
                      type="text"
                      id="edit-name"
                      name="name"
                      value={formData.name}
                      onChange={handleInputChange}
                      className={`mt-1 block w-full border ${formErrors.name ? 'border-red-300' : 'border-gray-300'} rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                      placeholder="Introduceți numele categoriei"
                      autoFocus
                    />
                    {formErrors.name && (
                      <p className="mt-1 text-sm text-red-600">{formErrors.name}</p>
                    )}
                  </div>
                  
                  {/* Description */}
                  <div>
                    <label htmlFor="edit-description" className="block text-sm font-medium text-gray-700">
                      Descriere
                    </label>
                    <textarea
                      id="edit-description"
                      name="description"
                      value={formData.description}
                      onChange={handleInputChange}
                      rows={3}
                      className={`mt-1 block w-full border ${formErrors.description ? 'border-red-300' : 'border-gray-300'} rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                      placeholder="Descrierea categoriei (opțional)"
                    />
                    {formErrors.description && (
                      <p className="mt-1 text-sm text-red-600">{formErrors.description}</p>
                    )}
                  </div>
                  
                  {/* Display Order */}
                  <div>
                    <label htmlFor="edit-display_order" className="block text-sm font-medium text-gray-700">
                      Ordinea de Afișare
                    </label>
                    <input
                      type="number"
                      id="edit-display_order"
                      name="display_order"
                      value={formData.display_order}
                      onChange={handleInputChange}
                      min="0"
                      max="10000"
                      className={`mt-1 block w-full border ${formErrors.display_order ? 'border-red-300' : 'border-gray-300'} rounded-md px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500`}
                      placeholder="0"
                    />
                    {formErrors.display_order && (
                      <p className="mt-1 text-sm text-red-600">{formErrors.display_order}</p>
                    )}
                    <p className="mt-1 text-sm text-gray-500">Număr întreg între 0 și 10000 (opțional)</p>
                  </div>
                </div>
                
                <div className="flex justify-end space-x-3 mt-6">
                  <button
                    type="button"
                    onClick={closeModals}
                    className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors"
                    disabled={formLoading}
                  >
                    Anulează
                  </button>
                  <button
                    type="submit"
                    className="px-4 py-2 text-sm font-medium text-white bg-blue-600 hover:bg-blue-700 rounded-md transition-colors disabled:opacity-50"
                    disabled={formLoading}
                  >
                    {formLoading ? 'Se salvează...' : 'Salvează Modificările'}
                  </button>
                </div>
              </form>
            </div>
          </div>
        </div>
      )}

      {/* Delete Confirmation Modal */}
      {showDeleteModal && selectedCategory && (
        <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50">
          <div className="relative top-20 mx-auto p-5 border w-full max-w-md shadow-lg rounded-md bg-white">
            <div className="mt-3">
              <div className="flex items-center mb-4">
                <div className="mx-auto flex-shrink-0 flex items-center justify-center h-12 w-12 rounded-full bg-red-100">
                  <svg className="h-6 w-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.732-.833-2.502 0L3.232 16.5c-.77.833.192 2.5 1.732 2.5z" />
                  </svg>
                </div>
              </div>
              
              <h3 className="text-lg font-medium text-gray-900 text-center mb-4">
                Șterge Categoria
              </h3>
              
              <div className="text-center mb-6">
                <p className="text-sm text-gray-500 mb-2">
                  Sigur doriți să ștergeți categoria
                </p>
                <p className="text-lg font-medium text-gray-900 mb-2">
                  "{selectedCategory.name}"?
                </p>
                
                {selectedCategory.product_count > 0 && (
                  <div className="bg-yellow-50 border border-yellow-200 rounded-md p-3 mt-3">
                    <div className="flex items-center">
                      <svg className="h-5 w-5 text-yellow-400 mr-2" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                      <p className="text-sm text-yellow-800">
                        Categoria conține {selectedCategory.product_count} {selectedCategory.product_count === 1 ? 'produs' : 'produse'} și nu poate fi ștearsă.
                      </p>
                    </div>
                  </div>
                )}
                
                {selectedCategory.product_count === 0 && (
                  <p className="text-sm text-gray-500">
                    Această acțiune nu poate fi anulată.
                  </p>
                )}
              </div>
              
              <div className="flex justify-center space-x-3">
                <button
                  type="button"
                  onClick={closeModals}
                  className="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 hover:bg-gray-300 rounded-md transition-colors"
                  disabled={formLoading}
                >
                  Anulează
                </button>
                {selectedCategory.product_count === 0 && (
                  <button
                    type="button"
                    onClick={handleDeleteCategory}
                    className="px-4 py-2 text-sm font-medium text-white bg-red-600 hover:bg-red-700 rounded-md transition-colors disabled:opacity-50"
                    disabled={formLoading}
                  >
                    {formLoading ? 'Se șterge...' : 'Confirmă Ștergerea'}
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CategoryManager;