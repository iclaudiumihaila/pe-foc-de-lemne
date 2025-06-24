import React, { useState, useEffect } from 'react';
import { FolderTree, Plus, RefreshCw, Search } from 'lucide-react';
import CategoryTree from '../../components/admin/CategoryTree';
import CategoryForm from '../../components/admin/CategoryForm';
import adminCategoryService from '../../services/adminCategoryService';

const AdminCategories = () => {
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [showForm, setShowForm] = useState(false);
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [successMessage, setSuccessMessage] = useState('');

  // Load categories on mount
  useEffect(() => {
    loadCategories();
  }, []);

  // Clear success message after 3 seconds
  useEffect(() => {
    if (successMessage) {
      const timer = setTimeout(() => setSuccessMessage(''), 3000);
      return () => clearTimeout(timer);
    }
  }, [successMessage]);

  const loadCategories = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await adminCategoryService.getCategoriesTree();
      setCategories(data);
    } catch (err) {
      setError('Eroare la încărcarea categoriilor');
      console.error('Error loading categories:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleAddCategory = () => {
    setSelectedCategory(null);
    setShowForm(true);
  };

  const handleEditCategory = (category) => {
    setSelectedCategory(category);
    setShowForm(true);
  };

  const handleDeleteCategory = async (categoryId) => {
    try {
      setSaving(true);
      await adminCategoryService.deleteCategory(categoryId);
      setSuccessMessage('Categorie ștearsă cu succes!');
      await loadCategories();
    } catch (err) {
      if (err.response?.status === 400) {
        alert(err.response.data.error || 'Nu se poate șterge categoria');
      } else {
        setError('Eroare la ștergerea categoriei');
      }
    } finally {
      setSaving(false);
    }
  };

  const handleSubmitCategory = async (formData) => {
    try {
      setSaving(true);
      setError(null);
      
      if (selectedCategory) {
        await adminCategoryService.updateCategory(selectedCategory.id, formData);
        setSuccessMessage('Categorie actualizată cu succes!');
      } else {
        await adminCategoryService.createCategory(formData);
        setSuccessMessage('Categorie adăugată cu succes!');
      }
      
      setShowForm(false);
      setSelectedCategory(null);
      await loadCategories();
    } catch (err) {
      if (err.response?.data?.error) {
        setError(err.response.data.error);
      } else {
        setError(selectedCategory ? 'Eroare la actualizarea categoriei' : 'Eroare la adăugarea categoriei');
      }
    } finally {
      setSaving(false);
    }
  };

  // Filter categories based on search term
  const filterCategories = (cats, term) => {
    if (!term) return cats;
    
    return cats.reduce((filtered, category) => {
      const matchesSearch = category.name.toLowerCase().includes(term.toLowerCase()) ||
                          (category.description && category.description.toLowerCase().includes(term.toLowerCase()));
      
      const filteredChildren = category.children ? filterCategories(category.children, term) : [];
      
      if (matchesSearch || filteredChildren.length > 0) {
        filtered.push({
          ...category,
          children: filteredChildren
        });
      }
      
      return filtered;
    }, []);
  };

  const filteredCategories = filterCategories(categories, searchTerm);

  return (
    <div className="p-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <FolderTree className="h-8 w-8 text-orange-600" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Gestionare Categorii
            </h1>
          </div>
          
          <button
            onClick={handleAddCategory}
            className="flex items-center gap-2 px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            Adaugă Categorie
          </button>
        </div>

        {/* Success Message */}
        {successMessage && (
          <div className="bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 text-green-700 dark:text-green-300 px-4 py-3 rounded-lg">
            {successMessage}
          </div>
        )}

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-700 dark:text-red-300 px-4 py-3 rounded-lg">
            {error}
          </div>
        )}

        {/* Search and Actions Bar */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
          <div className="flex items-center justify-between gap-4">
            <div className="flex-1 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-5 h-5" />
              <input
                type="text"
                placeholder="Caută categorii..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:outline-none dark:bg-gray-700 dark:text-white dark:placeholder-gray-400"
              />
            </div>
            
            <button
              onClick={loadCategories}
              className="flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors dark:text-gray-300"
              disabled={loading}
            >
              <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
              Reîncarcă
            </button>
          </div>
        </div>

        {/* Categories List */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
          {loading ? (
            <div className="flex justify-center py-12">
              <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-orange-600"></div>
            </div>
          ) : (
            <CategoryTree
              categories={filteredCategories}
              onEdit={handleEditCategory}
              onDelete={handleDeleteCategory}
            />
          )}
        </div>
      </div>

      {/* Category Form Modal */}
      <CategoryForm
        isOpen={showForm}
        onClose={() => {
          setShowForm(false);
          setSelectedCategory(null);
        }}
        onSubmit={handleSubmitCategory}
        category={selectedCategory}
        categories={categories}
        loading={saving}
      />
    </div>
  );
};

export default AdminCategories;