import React, { useState, useEffect } from 'react';
import { MessageSquare, Plus, Edit2, Trash2, RefreshCw, Shield, AlertCircle } from 'lucide-react';
import AdminTable from '../../components/admin/common/AdminTable';
import AdminModal from '../../components/admin/common/AdminModal';
import { useToast } from '../../components/common/Toast';

const AdminSMSProviders = () => {
  const [providers, setProviders] = useState([]);
  const [loading, setLoading] = useState(true);
  const [isDeleteModalOpen, setIsDeleteModalOpen] = useState(false);
  const [providerToDelete, setProviderToDelete] = useState(null);
  const { showToast } = useToast();

  useEffect(() => {
    // Mock data for now - will be replaced with API calls
    const mockProviders = [
    {
      id: 1,
      name: 'SMSO',
      type: 'smso',
      is_active: true,
      is_default: true,
      config: {
        api_url: 'https://app.smso.ro/api/v1/send',
        sender_id: 'PeFocLemne'
      },
      sent_count: 1245,
      success_rate: 98.5,
      last_used: '2024-01-15T10:30:00Z'
    },
    {
      id: 2,
      name: 'Twilio',
      type: 'twilio',
      is_active: false,
      is_default: false,
      config: {
        account_sid: 'AC...',
        from_number: '+40...'
      },
      sent_count: 0,
      success_rate: 0,
      last_used: null
    }
  ];

    // Simulate API call
    setTimeout(() => {
      setProviders(mockProviders);
      setLoading(false);
    }, 1000);
  }, []);

  // Table columns
  const columns = [
    {
      key: 'name',
      label: 'Nume Provider',
      render: (value, row) => (
        <div className="flex items-center">
          <div className={`h-8 w-8 rounded-lg ${row.is_active ? 'bg-green-100 dark:bg-green-900/20' : 'bg-gray-100 dark:bg-gray-800'} flex items-center justify-center mr-3`}>
            <MessageSquare className={`h-4 w-4 ${row.is_active ? 'text-green-600 dark:text-green-400' : 'text-gray-400'}`} />
          </div>
          <div>
            <div className="text-sm font-medium text-gray-900 dark:text-white">
              {value}
            </div>
            <div className="text-sm text-gray-500 dark:text-gray-400">
              Tip: {row.type}
            </div>
          </div>
        </div>
      )
    },
    {
      key: 'is_active',
      label: 'Status',
      render: (value, row) => (
        <div className="flex items-center space-x-2">
          <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
            value 
              ? 'bg-green-100 text-green-800 dark:bg-green-900/20 dark:text-green-200'
              : 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-200'
          }`}>
            {value ? 'Activ' : 'Inactiv'}
          </span>
          {row.is_default && (
            <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-blue-100 text-blue-800 dark:bg-blue-900/20 dark:text-blue-200">
              Principal
            </span>
          )}
        </div>
      )
    },
    {
      key: 'sent_count',
      label: 'SMS-uri Trimise',
      render: (value) => (
        <span className="text-sm text-gray-900 dark:text-white">
          {value.toLocaleString('ro-RO')}
        </span>
      )
    },
    {
      key: 'success_rate',
      label: 'Rată Succes',
      render: (value) => (
        <div className="flex items-center">
          <div className="w-16 bg-gray-200 dark:bg-gray-700 rounded-full h-2 mr-2">
            <div 
              className={`h-2 rounded-full ${
                value >= 95 ? 'bg-green-500' : 
                value >= 80 ? 'bg-yellow-500' : 
                'bg-red-500'
              }`}
              style={{ width: `${value}%` }}
            />
          </div>
          <span className="text-sm text-gray-900 dark:text-white">
            {value}%
          </span>
        </div>
      )
    },
    {
      key: 'last_used',
      label: 'Ultima Utilizare',
      render: (value) => (
        <span className="text-sm text-gray-500 dark:text-gray-400">
          {value ? new Date(value).toLocaleDateString('ro-RO') : 'Niciodată'}
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
            disabled={row.is_default}
          >
            <Trash2 className={`h-4 w-4 ${row.is_default ? 'opacity-50' : ''}`} />
          </button>
        </div>
      )
    }
  ];

  const handleCreate = () => {
    // TODO: Implement create functionality
  };

  const handleEdit = (provider) => {
    // TODO: Implement edit functionality
    console.log('Edit provider:', provider);
  };

  const handleDeleteClick = (provider) => {
    if (provider.is_default) {
      showToast('Nu puteți șterge providerul principal', 'error');
      return;
    }
    setProviderToDelete(provider);
    setIsDeleteModalOpen(true);
  };

  const handleDeleteConfirm = async () => {
    if (!providerToDelete) return;

    try {
      // API call would go here
      showToast(`Providerul "${providerToDelete.name}" a fost șters`, 'success');
      setIsDeleteModalOpen(false);
      setProviderToDelete(null);
      // Refresh providers
    } catch (error) {
      showToast('Eroare la ștergerea providerului', 'error');
    }
  };

  return (
    <div className="p-6">
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <MessageSquare className="h-8 w-8 text-orange-600" />
            <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
              Gestionare Provideri SMS
            </h1>
          </div>
          <button
            onClick={handleCreate}
            className="flex items-center px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-orange-500 transition-colors"
          >
            <Plus className="h-5 w-5 mr-2" />
            Adaugă Provider
          </button>
        </div>

        {/* Info Alert */}
        <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-4">
          <div className="flex">
            <AlertCircle className="h-5 w-5 text-blue-400 mt-0.5" />
            <div className="ml-3">
              <h3 className="text-sm font-medium text-blue-800 dark:text-blue-200">
                Configurare Provideri SMS
              </h3>
              <div className="mt-2 text-sm text-blue-700 dark:text-blue-300">
                <p>Configurați providerii SMS pentru verificarea numerelor de telefon la checkout.</p>
                <p className="mt-1">Providerul marcat ca principal va fi utilizat pentru toate SMS-urile.</p>
              </div>
            </div>
          </div>
        </div>

        {/* Providers Table */}
        <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
          <AdminTable
            columns={columns}
            data={providers}
            loading={loading}
            emptyMessage="Nu există provideri SMS configurați"
          />
        </div>

        {/* Stats Cards */}
        {!loading && providers.length > 0 && (
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="rounded-md bg-green-50 dark:bg-green-900/20 p-3">
                  <Shield className="h-6 w-6 text-green-600 dark:text-green-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Total SMS-uri Trimise
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {providers.reduce((sum, p) => sum + p.sent_count, 0).toLocaleString('ro-RO')}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="rounded-md bg-blue-50 dark:bg-blue-900/20 p-3">
                  <MessageSquare className="h-6 w-6 text-blue-600 dark:text-blue-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Provideri Activi
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {providers.filter(p => p.is_active).length}
                  </p>
                </div>
              </div>
            </div>

            <div className="bg-white dark:bg-gray-800 shadow rounded-lg p-6">
              <div className="flex items-center">
                <div className="rounded-md bg-orange-50 dark:bg-orange-900/20 p-3">
                  <RefreshCw className="h-6 w-6 text-orange-600 dark:text-orange-400" />
                </div>
                <div className="ml-4">
                  <p className="text-sm font-medium text-gray-500 dark:text-gray-400">
                    Rată Medie Succes
                  </p>
                  <p className="text-2xl font-semibold text-gray-900 dark:text-white">
                    {(providers.reduce((sum, p) => sum + p.success_rate, 0) / providers.length).toFixed(1)}%
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Delete Confirmation Modal */}
      <AdminModal
        isOpen={isDeleteModalOpen}
        onClose={() => {
          setIsDeleteModalOpen(false);
          setProviderToDelete(null);
        }}
        title="Confirmare ștergere"
        size="sm"
        footer={
          <div className="flex justify-end space-x-3">
            <button
              onClick={() => {
                setIsDeleteModalOpen(false);
                setProviderToDelete(null);
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
          Sigur vrei să ștergi providerul <strong>{providerToDelete?.name}</strong>? 
          Această acțiune nu poate fi anulată.
        </p>
      </AdminModal>
    </div>
  );
};

export default AdminSMSProviders;