import React, { useState, useEffect } from 'react';
import AdminForm from './common/AdminForm';
import adminProductService from '../../services/adminProductService';

const { Container, Field, Actions, Error, validate } = AdminForm;

const ProductForm = ({ product, onSubmit, onCancel }) => {
  const [formData, setFormData] = useState({
    name: '',
    description: '',
    price: '',
    category_id: '',
    stock_quantity: 0,
    weight_grams: '',
    preparation_time_hours: '',
    images: [],
    is_available: true
  });
  
  const [errors, setErrors] = useState({});
  const [categories, setCategories] = useState([]);
  const [loading, setLoading] = useState(false);
  const [fetchingCategories, setFetchingCategories] = useState(true);
  const [submitError, setSubmitError] = useState('');
  const [uploadingImage, setUploadingImage] = useState(false);
  
  // Sample product data for autofill
  const sampleProducts = [
    {
      name: 'Miere de Salcâm Naturală',
      description: 'Miere de salcâm pură, recoltată din stupii proprii. Produs 100% natural, fără adaosuri sau zahăr. Perfectă pentru ceai, desert sau consum direct. Ambalată în borcane de sticlă.',
      price: '35.00',
      stock_quantity: 25,
      weight_grams: 500,
      preparation_time_hours: 24,
      images: []
    },
    {
      name: 'Brânză de Capră Proaspătă',
      description: 'Brânză de capră artizanală, preparată după rețete tradiționale. Gustoasă și cremoasă, perfectă pentru salate sau tartine. Bogată în proteine și calciu.',
      price: '28.50',
      stock_quantity: 15,
      weight_grams: 300,
      preparation_time_hours: 48,
      images: []
    },
    {
      name: 'Dulceață de Caise',
      description: 'Dulceață de caise preparată în casă cu fructe proaspete din grădina proprie. Fără conservanți sau coloranți artificiali. Ideală pentru mic dejun sau desert.',
      price: '18.00',
      stock_quantity: 30,
      weight_grams: 370,
      preparation_time_hours: 12,
      images: []
    },
    {
      name: 'Țuică de Prune',
      description: 'Țuică tradițională de prune, distilată în cazane de aramă. Grad alcoolic 40%. Îmbătrânită în butoaie de stejar pentru o aromă desăvârșită.',
      price: '45.00',
      stock_quantity: 20,
      weight_grams: 750,
      preparation_time_hours: 720,
      images: []
    },
    {
      name: 'Zacuscă de Casă',
      description: 'Zacuscă preparată după rețeta bunicii, cu vinete, ardei și roșii din grădină proprie. Fără conservanți, sterilizată termic. Perfectă pentru iarnă.',
      price: '15.00',
      stock_quantity: 40,
      weight_grams: 300,
      preparation_time_hours: 6,
      images: []
    },
    {
      name: 'Salam de Casă Afumat',
      description: 'Salam tradițional românesc, preparat din carne de porc crescut în gospodărie. Afumat natural cu lemn de fag. Condimentat cu usturoi și piper.',
      price: '38.00',
      stock_quantity: 10,
      weight_grams: 400,
      preparation_time_hours: 168,
      images: []
    },
    {
      name: 'Lapte de Capră Proaspăt',
      description: 'Lapte de capră proaspăt, bogat în nutrienți. Recomandat pentru persoanele cu intoleranță la lactoza din laptele de vacă. Livrat în sticle de sticlă.',
      price: '12.00',
      stock_quantity: 50,
      weight_grams: 1000,
      preparation_time_hours: 2,
      images: []
    },
    {
      name: 'Ouă de Găină de Țară',
      description: 'Ouă proaspete de la găini crescute în aer liber, hrănite natural. Gălbenuș portocaliu intens, bogat în omega 3. Ambalate în cutii de carton.',
      price: '2.50',
      stock_quantity: 100,
      weight_grams: 70,
      preparation_time_hours: 1,
      images: []
    }
  ];

  // Load categories on mount
  useEffect(() => {
    loadCategories();
  }, []);

  // Load product data if editing
  useEffect(() => {
    if (product) {
      console.log('Product data received:', product);
      console.log('Category ID:', product.category_id);
      console.log('Categories loaded:', categories);
      setFormData({
        name: product.name || '',
        description: product.description || '',
        price: product.price || '',
        category_id: product.category_id || '',
        stock_quantity: product.stock_quantity || 0,
        weight_grams: product.weight_grams || '',
        preparation_time_hours: product.preparation_time_hours || '',
        images: product.images || [],
        is_available: product.is_available !== undefined ? product.is_available : true
      });
    }
  }, [product, categories]);

  const loadCategories = async () => {
    try {
      setFetchingCategories(true);
      const data = await adminProductService.getCategories();
      console.log('Categories from API:', data);
      const mappedCategories = data.map(cat => ({
        value: cat.id,
        label: cat.name
      }));
      console.log('Mapped categories:', mappedCategories);
      setCategories(mappedCategories);
    } catch (error) {
      console.error('Error loading categories:', error);
      setSubmitError('Eroare la încărcarea categoriilor');
    } finally {
      setFetchingCategories(false);
    }
  };

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
    
    // Clear error for this field
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: null }));
    }
  };


  const handleRemoveImage = (index) => {
    setFormData(prev => ({
      ...prev,
      images: prev.images.filter((_, i) => i !== index)
    }));
  };

  const handleSetDefaultImage = (index) => {
    if (index === 0) return; // Already default
    
    setFormData(prev => {
      const newImages = [...prev.images];
      // Move selected image to the beginning
      const [selectedImage] = newImages.splice(index, 1);
      newImages.unshift(selectedImage);
      
      return {
        ...prev,
        images: newImages
      };
    });
  };
  
  const handleAutofill = () => {
    // Select a random sample product
    const randomProduct = sampleProducts[Math.floor(Math.random() * sampleProducts.length)];
    
    // Select the first available category
    const firstCategory = categories.length > 0 ? categories[0].value : '';
    
    // Update form with sample data
    setFormData(prev => ({
      ...prev,
      ...randomProduct,
      category_id: firstCategory,
      is_available: true
    }));
    
    // Clear any existing errors
    setErrors({});
    setSubmitError('');
  };

  const handleImageUpload = async (e) => {
    const file = e.target.files[0];
    if (!file) return;

    // Validate file type
    const allowedTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
    if (!allowedTypes.includes(file.type)) {
      setSubmitError('Tipul de fișier nu este permis. Folosiți JPG, PNG sau WebP.');
      return;
    }

    // Validate file size (10MB)
    if (file.size > 10 * 1024 * 1024) {
      setSubmitError('Fișierul este prea mare. Dimensiunea maximă este 10MB.');
      return;
    }

    setUploadingImage(true);
    setSubmitError('');

    try {
      const formData = new FormData();
      formData.append('image', file);

      const response = await fetch('/api/admin/products/upload-image', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('auth_access_token')}`
        },
        body: formData
      });

      if (!response.ok) {
        const error = await response.json();
        throw new Error(error.error || 'Eroare la încărcarea imaginii');
      }

      const result = await response.json();
      
      // Add the uploaded image URL to the images array
      setFormData(prev => ({
        ...prev,
        images: [...prev.images, result.data.url]
      }));

      // Reset file input
      e.target.value = '';
    } catch (error) {
      console.error('Upload error:', error);
      setSubmitError(error.message || 'Eroare la încărcarea imaginii');
    } finally {
      setUploadingImage(false);
    }
  };

  const validateForm = () => {
    const newErrors = {};

    // Validate required fields
    const nameError = validate.required(formData.name, 'Numele');
    if (nameError) newErrors.name = nameError;

    const descError = validate.required(formData.description, 'Descrierea');
    if (descError) {
      newErrors.description = descError;
    } else if (formData.description.trim().length < 5) {
      newErrors.description = 'Descrierea trebuie să aibă cel puțin 5 caractere';
    }

    const priceError = validate.required(formData.price, 'Prețul');
    if (priceError) {
      newErrors.price = priceError;
    } else {
      const numError = validate.number(formData.price, 'Prețul', 0.01, 9999.99);
      if (numError) newErrors.price = numError;
    }

    const categoryError = validate.required(formData.category_id, 'Categoria');
    if (categoryError) newErrors.category_id = categoryError;

    // Validate optional numeric fields
    if (formData.stock_quantity !== '') {
      const stockError = validate.number(formData.stock_quantity, 'Cantitatea în stoc', 0, 10000);
      if (stockError) newErrors.stock_quantity = stockError;
    }

    if (formData.weight_grams && formData.weight_grams !== '') {
      const weightError = validate.number(formData.weight_grams, 'Greutatea', 1, 50000);
      if (weightError) newErrors.weight_grams = weightError;
    }

    if (formData.preparation_time_hours && formData.preparation_time_hours !== '') {
      const prepError = validate.number(formData.preparation_time_hours, 'Timpul de preparare', 1, 168);
      if (prepError) newErrors.preparation_time_hours = prepError;
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!validateForm()) {
      return;
    }

    setLoading(true);
    setSubmitError('');

    try {
      // Prepare data for submission
      const submitData = {
        name: formData.name,
        description: formData.description,
        price: parseFloat(formData.price),
        category_id: formData.category_id,
        stock_quantity: parseInt(formData.stock_quantity) || 0,
        images: formData.images.filter(img => img.trim() !== ''),
        is_available: formData.is_available
      };

      // Add optional fields if they exist
      if (formData.weight_grams) {
        submitData.weight_grams = parseInt(formData.weight_grams);
      }

      if (formData.preparation_time_hours) {
        submitData.preparation_time_hours = parseInt(formData.preparation_time_hours);
      }

      console.log('Submitting product data:', submitData);
      await onSubmit(submitData);
    } catch (error) {
      setSubmitError(error.message || 'Eroare la salvarea produsului');
      setLoading(false);
    }
  };

  if (fetchingCategories) {
    return (
      <div className="flex justify-center items-center py-8">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
      </div>
    );
  }

  return (
    <Container onSubmit={handleSubmit}>
      <Error error={submitError} />
      
      {/* Autofill button for development/testing */}
      {!product && (
        <div className="mb-4 flex justify-end">
          <button
            type="button"
            onClick={handleAutofill}
            disabled={loading || fetchingCategories}
            className="px-3 py-1 text-sm font-medium text-gray-700 bg-gray-100 border border-gray-300 rounded-md hover:bg-gray-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            🎲 Completare automată (test)
          </button>
        </div>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Field
          label="Nume produs"
          name="name"
          value={formData.name}
          onChange={handleChange}
          error={errors.name}
          required
          placeholder="Ex: Miere de salcâm"
          disabled={loading}
        />
        
        <Field
          label="Categorie"
          name="category_id"
          type="select"
          value={formData.category_id}
          onChange={handleChange}
          error={errors.category_id}
          required
          options={categories}
          disabled={loading}
        />
      </div>
      
      <Field
        label="Descriere"
        name="description"
        type="textarea"
        value={formData.description}
        onChange={handleChange}
        error={errors.description}
        required
        placeholder="Descrieți produsul (minim 5 caractere)"
        rows={4}
        disabled={loading}
      />
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Field
          label="Preț (RON)"
          name="price"
          type="number"
          value={formData.price}
          onChange={handleChange}
          error={errors.price}
          required
          placeholder="0.00"
          disabled={loading}
        />
        
        <Field
          label="Cantitate în stoc"
          name="stock_quantity"
          type="number"
          value={formData.stock_quantity}
          onChange={handleChange}
          error={errors.stock_quantity}
          placeholder="0"
          disabled={loading}
        />
      </div>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Field
          label="Greutate (grame)"
          name="weight_grams"
          type="number"
          value={formData.weight_grams}
          onChange={handleChange}
          error={errors.weight_grams}
          placeholder="Optional"
          disabled={loading}
        />
        
        <Field
          label="Timp de preparare (ore)"
          name="preparation_time_hours"
          type="number"
          value={formData.preparation_time_hours}
          onChange={handleChange}
          error={errors.preparation_time_hours}
          placeholder="Optional"
          disabled={loading}
        />
      </div>
      
      {/* Images section */}
      <div className="space-y-3">
        <label className="block text-sm font-medium text-gray-700 dark:text-gray-300">
          Imagini produs
        </label>
        
        {/* File upload option */}
        <div className="space-y-2">
          <div className="flex items-center justify-center w-full">
            <label htmlFor="image-upload" className="flex flex-col items-center justify-center w-full h-32 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 dark:hover:bg-gray-800 dark:bg-gray-700 hover:bg-gray-100 dark:border-gray-600 dark:hover:border-gray-500">
              <div className="flex flex-col items-center justify-center pt-5 pb-6">
                {uploadingImage ? (
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-orange-600"></div>
                ) : (
                  <>
                    <svg className="w-8 h-8 mb-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                    </svg>
                    <p className="mb-2 text-sm text-gray-500 dark:text-gray-400">
                      <span className="font-semibold">Click pentru a încărca</span> sau trageți fișierul aici
                    </p>
                    <p className="text-xs text-gray-500 dark:text-gray-400">JPG, PNG sau WebP (MAX. 10MB)</p>
                  </>
                )}
              </div>
              <input 
                id="image-upload" 
                type="file" 
                className="hidden" 
                accept="image/jpeg,image/jpg,image/png,image/webp"
                onChange={handleImageUpload}
                disabled={loading || uploadingImage || formData.images.length >= 10}
              />
            </label>
          </div>
        </div>

        
        {formData.images.length > 0 && (
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3 mt-3">
            {formData.images.map((image, index) => (
              <div key={index} className="relative group">
                <img 
                  src={image} 
                  alt={`Produs ${index + 1}`} 
                  className="w-full h-32 object-cover rounded-lg"
                  onError={(e) => {
                    e.target.src = '/images/placeholder-product.jpg';
                  }}
                />
                {/* Delete button */}
                <button
                  type="button"
                  onClick={() => handleRemoveImage(index)}
                  disabled={loading}
                  className="absolute top-2 right-2 bg-red-600 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-red-700"
                  title="Șterge imaginea"
                >
                  <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
                
                {/* Set as default button */}
                {index !== 0 && (
                  <button
                    type="button"
                    onClick={() => handleSetDefaultImage(index)}
                    disabled={loading}
                    className="absolute top-2 left-2 bg-blue-600 text-white p-1 rounded-full opacity-0 group-hover:opacity-100 transition-opacity duration-200 hover:bg-blue-700"
                    title="Setează ca imagine principală"
                  >
                    <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                    </svg>
                  </button>
                )}
                
                {/* Primary badge */}
                {index === 0 && (
                  <span className="absolute bottom-2 left-2 bg-green-600 text-white text-xs px-2 py-1 rounded">
                    Principal
                  </span>
                )}
              </div>
            ))}
          </div>
        )}
        
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {formData.images.length}/10 imagini adăugate
        </p>
      </div>
      
      {/* Availability checkbox */}
      <div className="flex items-center">
        <input
          type="checkbox"
          id="is_available"
          name="is_available"
          checked={formData.is_available}
          onChange={handleChange}
          disabled={loading}
          className="h-4 w-4 text-orange-600 focus:ring-orange-500 border-gray-300 rounded"
        />
        <label htmlFor="is_available" className="ml-2 block text-sm text-gray-900 dark:text-gray-100">
          Produs disponibil pentru vânzare
        </label>
      </div>
      
      <Actions
        onCancel={onCancel}
        submitText={product ? 'Actualizează' : 'Creează'}
        isSubmitting={loading}
      />
    </Container>
  );
};

export default ProductForm;