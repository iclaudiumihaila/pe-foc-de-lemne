import React, { useState, useEffect, useCallback, useRef } from 'react';
import { Package, Plus, Edit2, Trash2, Search } from 'lucide-react';
import AdminTable from '../../components/admin/common/AdminTable';
import AdminModal from '../../components/admin/common/AdminModal';
import AdminPagination from '../../components/admin/common/AdminPagination';
import ProductForm from '../../components/admin/ProductForm';
import adminProductService from '../../services/adminProductService';
import { useToast } from '../../components/common/Toast';

const AdminProducts = () => {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [pagination, setPagination] = useState({
    page: 1,
    limit: 10,
    total_items: 0,
    total_pages: 0
  });
  const [searchQuery, setSearchQuery] = useState('');
  const [sortConfig, setSortConfig] = useState({
    sort_by: 'name',
    sort_order: 'asc'
  });
  const [selectedProduct, setSelectedProduct] = useState(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [productToDelete, setProductToDelete] = useState(null);
  const { showSuccess, showError } = useToast();

  // Fetch products
  const fetchProducts = useCallback(async () => {
    try {
      setLoading(true);
      const data = await adminProductService.getProducts({
        page: pagination.page,
        limit: pagination.limit,
        q: searchQuery,
        ...sortConfig,
        available_only: false // Show all products in admin
      });
      
      setProducts(data.products || []);
      setPagination(data.pagination || {
        page: 1,
        limit: 10,
        total_items: 0,
        total_pages: 0
      });
    } catch (error) {
      showError('Eroare la încărcarea produselor');
      console.error('Error fetching products:', error);
    } finally {
      setLoading(false);
    }
  }, [pagination.page, pagination.limit, searchQuery, sortConfig, showError]);

  // Simple debounce implementation
  const debounceRef = useRef(null);
  
  const debouncedSearch = useCallback((query) => {
    if (debounceRef.current) {
      clearTimeout(debounceRef.current);
    }
    
    debounceRef.current = setTimeout(() => {
      setPagination(prev => ({ ...prev, page: 1 }));
    }, 500);
  }, []);

  useEffect(() => {
    fetchProducts();
  }, [fetchProducts]);

  useEffect(() => {
    if (searchQuery) {
      debouncedSearch(searchQuery);
    }
  }, [searchQuery, debouncedSearch]);

  // Cleanup debounce on unmount
  useEffect(() => {
    return () => {
      if (debounceRef.current) {
        clearTimeout(debounceRef.current);
      }
    };
  }, []);

  // Table columns configuration
  const columns = [
    {
      key: 'name',
      label: 'Nume produs',
      sortable: true,
      render: (value, row) => (
        <div className="flex items-center">
          {row.images && row.images[0] ? (
            <img
              src={row.images[0]}
              alt={value}
              className="h-10 w-10 rounded-lg object-cover mr-3"
            />
          ) : (
            <div className="h-10 w-10 rounded-lg bg-gray-200 dark:bg-gray-700 mr-3 flex items-center justify-center">
              <Package className="h-5 w-5 text-gray-400" />
            </div>
          )}
          <div>
            <div className="text-sm font-medium text-gray-900 dark:text-white">
              {value}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              {row.category?.name || 'Fără categorie'}
            </div>
          </div>
        </div>
      )
    },
    {
      key: 'price',
      label: 'Preț',
      sortable: true,
      render: (value) => (
        <span className="text-sm font-medium text-gray-900 dark:text-white">
          {value.toFixed(2)} RON
        </span>
      )
    },
    {
      key: 'stock_quantity',
      label: 'Stoc',
      sortable: true,
      render: (value) => (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          value > 10 
            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
            : value > 0 
            ? 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900 dark:text-yellow-200'
            : 'bg-red-100 text-red-800 dark:bg-red-900 dark:text-red-200'
        }`}>
          {value} buc
        </span>
      )
    },
    {
      key: 'is_available',
      label: 'Status',
      render: (value) => (
        <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
          value 
            ? 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200'
            : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
        }`}>
          {value ? 'Disponibil' : 'Indisponibil'}
        </span>
      )
    },
    {
      key: 'actions',
      label: 'Acțiuni',
      render: (_, row) => (
        <div className="flex items-center space-x-2">
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleEdit(row);
            }}
            className="text-indigo-600 hover:text-indigo-900 dark:text-indigo-400 dark:hover:text-indigo-300"
            title="Editează"
          >
            <Edit2 className="h-4 w-4" />
          </button>
          <button
            onClick={(e) => {
              e.stopPropagation();
              handleDeleteClick(row);
            }}
            className="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300"
            title="Șterge"
          >
            <Trash2 className="h-4 w-4" />
          </button>
        </div>
      )
    }
  ];

  // Handle sort
  const handleSort = (field) => {
    setSortConfig(prev => ({
      sort_by: field,
      sort_order: prev.sort_by === field && prev.sort_order === 'asc' ? 'desc' : 'asc'
    }));
    setPagination(prev => ({ ...prev, page: 1 }));
  };

  // Handle create product
  const handleCreate = () => {
    setSelectedProduct(null);
    setIsModalOpen(true);
  };

  // Handle edit product
  const handleEdit = (product) => {
    console.log('EDIT CLICKED - Raw product from table:', product);
    console.log('EDIT CLICKED - category_id:', product.category_id);
    console.log('EDIT CLICKED - category_id type:', typeof product.category_id);
    
    // Fix the category_id if it's an object
    const productToEdit = { ...product };
    if (product.category_id && typeof product.category_id === 'object') {
      productToEdit.category_id = product.category_id.id || product.category;
    }
    
    console.log('EDIT CLICKED - Fixed product:', productToEdit);
    setSelectedProduct(productToEdit);
    setIsModalOpen(true);
  };

  // Handle delete click
  const handleDeleteClick = (product) => {
    setProductToDelete(product);
    setIsDeleteModalOpen(true);
  };

  // Handle delete confirm
  const handleDeleteConfirm = async () => {
    if (!productToDelete) return;

    try {
      await adminProductService.deleteProduct(productToDelete.id);
      showSuccess(`Produsul "${productToDelete.name}" a fost șters`);
      setIsDeleteModalOpen(false);
      setProductToDelete(null);
      fetchProducts();
    } catch (error) {
      showError('Eroare la ștergerea produsului');
      console.error('Error deleting product:', error);
    }
  };

  // Handle form submit
  const handleFormSubmit = async (formData) => {
    try {
      if (selectedProduct) {
        await adminProductService.updateProduct(selectedProduct.id, formData);
        showSuccess('Produs actualizat cu succes');
      } else {
        await adminProductService.createProduct(formData);
        showSuccess('Produs creat cu succes');
      }
      setIsModalOpen(false);
      setSelectedProduct(null);
      fetchProducts();
    } catch (error) {
      console.error('Error submitting product:', error);
      const errorMessage = error.response?.data?.error?.message || 
                          error.response?.data?.message || 
                          error.message || 
                          'Eroare la salvarea produsului';
      showError(errorMessage);
      throw error; // Re-throw to let ProductForm handle it
    }
  };

  // Handle page change
  const handlePageChange = (page) => {
    setPagination(prev => ({ ...prev, page }));
  };

  return (
    <div className="p-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <Package className="h-8 w-8 text-orange-600" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Administrare Produse
            </h1>
          </div>
          <button
            onClick={handleCreate}
            className="flex items-center px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Adaugă Produs
          </button>
        </div>

        {/* Search and filters */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-4">
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Search className="h-5 w-5 text-gray-400" />
            </div>
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Caută produse..."
              className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 text-gray-900 dark:text-white placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-orange-500 focus:border-orange-500 sm:text-sm"
            />
          </div>
        </div>

        {/* Products table */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <AdminTable
            columns={columns}
            data={products}
            onSort={handleSort}
            loading={loading}
            emptyMessage="Nu există produse"
          />
          
          {!loading && products.length > 0 && (
            <div className="px-6 py-4 border-t border-gray-200 dark:border-gray-700">
              <AdminPagination
                currentPage={pagination.page}
                totalPages={pagination.total_pages}
                onPageChange={handlePageChange}
                itemsPerPage={pagination.limit}
                totalItems={pagination.total_items}
              />
            </div>
          )}
        </div>
      </div>

      {/* Create/Edit Modal */}
      <AdminModal
        isOpen={isModalOpen}
        onClose={() => {
          setIsModalOpen(false);
          setSelectedProduct(null);
        }}
        title={selectedProduct ? 'Editează Produs' : 'Adaugă Produs'}
        size="lg"
      >
        <ProductForm
          product={selectedProduct}
          onSubmit={handleFormSubmit}
          onCancel={() => {
            setIsModalOpen(false);
            setSelectedProduct(null);
          }}
        />
      </AdminModal>

      {/* Delete Confirmation Modal */}
      <AdminModal
        isOpen={isDeleteModalOpen}
        onClose={() => {
          setIsDeleteModalOpen(false);
          setProductToDelete(null);
        }}
        title="Confirmare ștergere"
        size="sm"
        footer={
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => {
                setIsDeleteModalOpen(false);
                setProductToDelete(null);
              }}
              className="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 rounded-md hover:bg-gray-50 dark:hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500"
            >
              Anulează
            </button>
            <button
              onClick={handleDeleteConfirm}
              className="px-4 py-2 text-sm font-medium text-white bg-red-600 border border-transparent rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
            >
              Șterge
            </button>
          </div>
        }
      >
        <p className="text-sm text-gray-600 dark:text-gray-400">
          Sigur vrei să ștergi produsul <strong>{productToDelete?.name}</strong>? 
          Această acțiune va dezactiva produsul și nu poate fi anulată.
        </p>
      </AdminModal>
    </div>
  );
};

export default AdminProducts;