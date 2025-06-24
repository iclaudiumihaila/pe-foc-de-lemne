import React, { useState, useEffect } from 'react';
import { X } from 'lucide-react';

const CategoryForm = ({ 
  isOpen, 
  onClose, 
  onSubmit, 
  category = null, 
  categories = [], 
  loading = false 
}) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    parent: null,
    slug: '',
    active: true
  });

  const [errors, setErrors] = useState({});

  useEffect(() => {
    if (category) {
      setFormData({
        name: category.name || '',
        description: category.description || '',
        parent: category.parent || null,
        slug: category.slug || '',
        active: category.active !== undefined ? category.active : true
      });
    } else {
      setFormData({
        name: '',
        description: '',
        parent: null,
        slug: '',
        active: true
      });
    }
    setErrors({});
  }, [category, isOpen]);

  // Generate slug from name
  const generateSlug = (name) => {
    return name
      .toLowerCase()
      .normalize('NFD')
      .replace(/[\u0300-\u036f]/g, '') // Remove diacritics
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '');
  };

  const handleNameChange = (e) => {
    const name = e.target.value;
    setFormData({
      ...formData,
      name,
      slug: generateSlug(name)
    });
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    // Validation
    const newErrors = {};
    if (!formData.name.trim()) {
      newErrors.name = 'Numele este obligatoriu';
    }
    if (!formData.slug.trim()) {
      newErrors.slug = 'Slug-ul este obligatoriu';
    }

    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    // Check for circular parent reference
    if (category && formData.parent === category.id) {
      setErrors({ parent: 'O categorie nu poate fi propriul părinte' });
      return;
    }

    onSubmit(formData);
  };

  // Get available parent categories (exclude current category and its children)
  const getAvailableParents = () => {
    if (!category) return categories;

    const excludeIds = new Set([category.id]);
    
    // Recursively add all descendant IDs
    const addDescendants = (cats) => {
      cats.forEach(cat => {
        if (cat.parent && excludeIds.has(cat.parent)) {
          excludeIds.add(cat.id);
          if (cat.children) {
            addDescendants(cat.children);
          }
        }
      });
    };

    // Flatten categories for easier processing
    const flatCategories = [];
    const flatten = (cats, level = 0) => {
      cats.forEach(cat => {
        flatCategories.push({ ...cat, level });
        if (cat.children) {
          flatten(cat.children, level + 1);
        }
      });
    };
    flatten(categories);

    addDescendants(flatCategories);

    return flatCategories.filter(cat => !excludeIds.has(cat.id));
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white dark:bg-gray-800 rounded-lg p-6 w-full max-w-md">
        <div className="flex justify-between items-center mb-6">
          <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
            {category ? 'Editare Categorie' : 'Adăugare Categorie'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Nume *
            </label>
            <input
              type="text"
              value={formData.name}
              onChange={handleNameChange}
              className={`w-full p-2 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:outline-none dark:bg-gray-700 dark:text-white ${
                errors.name ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
              placeholder="Ex: Lemn de foc"
            />
            {errors.name && (
              <p className="text-red-500 dark:text-red-400 text-sm mt-1">{errors.name}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Slug
            </label>
            <input
              type="text"
              value={formData.slug}
              onChange={(e) => setFormData({ ...formData, slug: e.target.value })}
              className={`w-full p-2 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:outline-none dark:bg-gray-700 dark:text-white ${
                errors.slug ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
              placeholder="lemn-de-foc"
            />
            {errors.slug && (
              <p className="text-red-500 dark:text-red-400 text-sm mt-1">{errors.slug}</p>
            )}
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Descriere
            </label>
            <textarea
              value={formData.description}
              onChange={(e) => setFormData({ ...formData, description: e.target.value })}
              className="w-full p-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-orange-500 focus:outline-none dark:bg-gray-700 dark:text-white"
              rows="3"
              placeholder="Descrierea categoriei..."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
              Categorie părinte
            </label>
            <select
              value={formData.parent || ''}
              onChange={(e) => setFormData({ 
                ...formData, 
                parent: e.target.value || null 
              })}
              className={`w-full p-2 border rounded-lg focus:ring-2 focus:ring-orange-500 focus:outline-none dark:bg-gray-700 dark:text-white ${
                errors.parent ? 'border-red-500' : 'border-gray-300 dark:border-gray-600'
              }`}
            >
              <option value="">Fără părinte (categorie principală)</option>
              {getAvailableParents().map((cat) => (
                <option key={cat.id} value={cat.id}>
                  {'  '.repeat(cat.level || 0)}{cat.name}
                </option>
              ))}
            </select>
            {errors.parent && (
              <p className="text-red-500 dark:text-red-400 text-sm mt-1">{errors.parent}</p>
            )}
          </div>

          <div>
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={formData.active}
                onChange={(e) => setFormData({ ...formData, active: e.target.checked })}
                className="mr-2"
              />
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">
                Categorie activă
              </span>
            </label>
          </div>

          <div className="flex justify-end gap-3 pt-4">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 dark:text-gray-300"
              disabled={loading}
            >
              Anulare
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-orange-600 text-white rounded-lg hover:bg-orange-700 disabled:opacity-50"
              disabled={loading}
            >
              {loading ? 'Se salvează...' : (category ? 'Actualizare' : 'Adăugare')}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CategoryForm;