import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import ProductManager from '../ProductManager';
import * as AuthContext from '../../../context/AuthContext';
import api from '../../../services/api';

// Mock the API module
jest.mock('../../../services/api');

// Mock the AuthContext
const mockAuthContext = {
  isAuthenticated: true,
  isAdmin: jest.fn(() => true),
  tokens: {
    access_token: 'mock-access-token'
  },
  user: {
    id: 'admin-id',
    name: 'Test Admin',
    role: 'admin'
  }
};

// Mock test data
const mockProducts = [
  {
    id: '1',
    name: 'Brânză de capră',
    description: 'Brânză artizanală de capră',
    price: 25.99,
    category: {
      id: 'cat1',
      name: 'Produse lactate',
      slug: 'produse-lactate'
    },
    stock_quantity: 10,
    weight_grams: 500,
    preparation_time_hours: 24,
    is_available: true,
    images: ['https://example.com/image1.jpg']
  },
  {
    id: '2',
    name: 'Miere de salcâm',
    description: 'Miere naturală de salcâm',
    price: 15.50,
    category: {
      id: 'cat2',
      name: 'Miere și dulciuri',
      slug: 'miere-dulciuri'
    },
    stock_quantity: 0,
    is_available: false,
    images: []
  }
];

const mockCategories = [
  {
    id: 'cat1',
    name: 'Produse lactate',
    slug: 'produse-lactate',
    is_active: true
  },
  {
    id: 'cat2',
    name: 'Miere și dulciuri',
    slug: 'miere-dulciuri',
    is_active: true
  }
];

const mockProductsResponse = {
  data: {
    success: true,
    data: {
      products: mockProducts,
      pagination: {
        page: 1,
        limit: 10,
        total_items: 2,
        total_pages: 1,
        has_next: false,
        has_prev: false
      }
    }
  }
};

const mockCategoriesResponse = {
  data: {
    success: true,
    data: {
      categories: mockCategories
    }
  }
};

// Custom render with providers
const renderWithAuth = (component, authOverrides = {}) => {
  const authContextValue = { ...mockAuthContext, ...authOverrides };
  
  jest.spyOn(AuthContext, 'useAuth').mockReturnValue(authContextValue);
  
  return render(
    <BrowserRouter>
      {component}
    </BrowserRouter>
  );
};

describe('ProductManager Component', () => {
  const user = userEvent.setup();

  beforeEach(() => {
    jest.clearAllMocks();
    
    // Default API mocks
    api.get.mockImplementation((url) => {
      if (url.includes('/products')) {
        return Promise.resolve(mockProductsResponse);
      }
      if (url.includes('/categories')) {
        return Promise.resolve(mockCategoriesResponse);
      }
      return Promise.reject(new Error('Unknown endpoint'));
    });
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  describe('Authentication and Access Control', () => {
    test('renders error message for non-authenticated users', () => {
      renderWithAuth(<ProductManager />, { 
        isAuthenticated: false,
        isAdmin: jest.fn(() => false)
      });

      expect(screen.getByText(/acces neautorizat/i)).toBeInTheDocument();
      expect(screen.getByText(/trebuie să fiți autentificat ca administrator/i)).toBeInTheDocument();
    });

    test('renders error message for non-admin users', () => {
      renderWithAuth(<ProductManager />, { 
        isAuthenticated: true,
        isAdmin: jest.fn(() => false)
      });

      expect(screen.getByText(/acces neautorizat/i)).toBeInTheDocument();
    });

    test('renders component for authenticated admin users', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Gestionare Produse')).toBeInTheDocument();
      });
    });
  });

  describe('Component Rendering and Initial State', () => {
    test('shows loading state initially', () => {
      renderWithAuth(<ProductManager />);
      
      expect(screen.getByText(/se încarcă produsele/i)).toBeInTheDocument();
    });

    test('renders header with title and add button', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Gestionare Produse')).toBeInTheDocument();
        expect(screen.getByText('Adaugă Produs Nou')).toBeInTheDocument();
      });
    });

    test('fetches and displays products on mount', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Brânză de capră')).toBeInTheDocument();
        expect(screen.getByText('Miere de salcâm')).toBeInTheDocument();
      });

      expect(api.get).toHaveBeenCalledWith(expect.stringContaining('/products?'));
      expect(api.get).toHaveBeenCalledWith('/categories');
    });

    test('displays empty state when no products found', async () => {
      api.get.mockImplementation((url) => {
        if (url.includes('/products')) {
          return Promise.resolve({
            data: {
              success: true,
              data: {
                products: [],
                pagination: { page: 1, total_pages: 1 }
              }
            }
          });
        }
        if (url.includes('/categories')) {
          return Promise.resolve(mockCategoriesResponse);
        }
      });

      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText(/nu au fost găsite produse/i)).toBeInTheDocument();
      });
    });
  });

  describe('Product Listing and Display', () => {
    test('displays product information correctly', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        // Check product names
        expect(screen.getByText('Brânză de capră')).toBeInTheDocument();
        expect(screen.getByText('Miere de salcâm')).toBeInTheDocument();
        
        // Check categories
        expect(screen.getByText('Produse lactate')).toBeInTheDocument();
        expect(screen.getByText('Miere și dulciuri')).toBeInTheDocument();
        
        // Check prices
        expect(screen.getByText('25.99 RON')).toBeInTheDocument();
        expect(screen.getByText('15.50 RON')).toBeInTheDocument();
        
        // Check status
        expect(screen.getByText('Disponibil')).toBeInTheDocument();
        expect(screen.getByText('Indisponibil')).toBeInTheDocument();
      });
    });

    test('displays correct action buttons based on product status', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        const editButtons = screen.getAllByText('Editează');
        expect(editButtons).toHaveLength(2);

        const deleteButtons = screen.getAllByText(/dezactivează|dezactivat/i);
        expect(deleteButtons).toHaveLength(2);
      });
    });

    test('handles API error when fetching products', async () => {
      api.get.mockRejectedValueOnce(new Error('Network error'));

      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText(/eroare la încărcarea produselor/i)).toBeInTheDocument();
      });
    });
  });

  describe('Search and Filtering', () => {
    test('performs search when form is submitted', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Gestionare Produse')).toBeInTheDocument();
      });

      const searchInput = screen.getByPlaceholderText(/căutați produse/i);
      const searchButton = screen.getByRole('button', { name: /căutare/i });

      await user.type(searchInput, 'brânză');
      await user.click(searchButton);

      await waitFor(() => {
        expect(api.get).toHaveBeenCalledWith(expect.stringContaining('/products/search'));
      });
    });

    test('filters by category when category is selected', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Gestionare Produse')).toBeInTheDocument();
      });

      const categorySelect = screen.getByDisplayValue('Toate categoriile');
      
      await act(async () => {
        fireEvent.change(categorySelect, { target: { value: 'cat1' } });
      });

      await waitFor(() => {
        expect(api.get).toHaveBeenCalledWith(expect.stringContaining('category_id=cat1'));
      });
    });

    test('changes sort order when sort option is selected', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Gestionare Produse')).toBeInTheDocument();
      });

      const sortSelect = screen.getByDisplayValue('Nume (A-Z)');
      
      await act(async () => {
        fireEvent.change(sortSelect, { target: { value: 'price_desc' } });
      });

      await waitFor(() => {
        expect(api.get).toHaveBeenCalledWith(expect.stringContaining('sort_by=price&sort_order=desc'));
      });
    });
  });

  describe('Pagination', () => {
    test('displays pagination when multiple pages exist', async () => {
      api.get.mockImplementation((url) => {
        if (url.includes('/products')) {
          return Promise.resolve({
            data: {
              success: true,
              data: {
                products: mockProducts,
                pagination: {
                  page: 1,
                  total_pages: 3,
                  has_next: true,
                  has_prev: false
                }
              }
            }
          });
        }
        return Promise.resolve(mockCategoriesResponse);
      });

      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText(/pagina 1 din 3/i)).toBeInTheDocument();
        expect(screen.getByRole('button', { name: /următor/i })).toBeInTheDocument();
      });
    });

    test('navigates to next page when next button is clicked', async () => {
      api.get.mockImplementation((url) => {
        if (url.includes('/products')) {
          return Promise.resolve({
            data: {
              success: true,
              data: {
                products: mockProducts,
                pagination: {
                  page: 1,
                  total_pages: 3,
                  has_next: true,
                  has_prev: false
                }
              }
            }
          });
        }
        return Promise.resolve(mockCategoriesResponse);
      });

      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByRole('button', { name: /următor/i })).toBeInTheDocument();
      });

      const nextButton = screen.getByRole('button', { name: /următor/i });
      await user.click(nextButton);

      await waitFor(() => {
        expect(api.get).toHaveBeenCalledWith(expect.stringContaining('page=2'));
      });
    });
  });

  describe('Product Creation', () => {
    test('opens create modal when add button is clicked', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Adaugă Produs Nou')).toBeInTheDocument();
      });

      const addButton = screen.getByText('Adaugă Produs Nou');
      await user.click(addButton);

      expect(screen.getByText('Adaugă Produs Nou')).toBeInTheDocument();
      expect(screen.getByLabelText(/nume produs/i)).toBeInTheDocument();
    });

    test('submits create form with valid data', async () => {
      api.post.mockResolvedValueOnce({
        data: {
          success: true,
          message: 'Produsul a fost creat cu succes'
        }
      });

      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Adaugă Produs Nou')).toBeInTheDocument();
      });

      // Open modal
      const addButton = screen.getByText('Adaugă Produs Nou');
      await user.click(addButton);

      // Fill form
      await user.type(screen.getByLabelText(/nume produs/i), 'Test Product');
      await user.type(screen.getByLabelText(/descriere/i), 'Test description for product');
      await user.type(screen.getByLabelText(/preț/i), '19.99');
      
      const categorySelect = screen.getByLabelText(/categorie/i);
      await user.selectOptions(categorySelect, 'cat1');

      // Submit form
      const submitButton = screen.getByRole('button', { name: /salvează produsul/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(api.post).toHaveBeenCalledWith(
          '/admin/products',
          expect.objectContaining({
            name: 'Test Product',
            description: 'Test description for product',
            price: 19.99,
            category_id: 'cat1'
          }),
          expect.objectContaining({
            headers: {
              'Authorization': 'Bearer mock-access-token'
            }
          })
        );
      });
    });

    test('shows validation error for missing required fields', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Adaugă Produs Nou')).toBeInTheDocument();
      });

      // Open modal
      const addButton = screen.getByText('Adaugă Produs Nou');
      await user.click(addButton);

      // Try to submit without filling required fields
      const submitButton = screen.getByRole('button', { name: /salvează produsul/i });
      await user.click(submitButton);

      // Form should not submit due to HTML5 validation
      expect(api.post).not.toHaveBeenCalled();
    });

    test('handles API error during product creation', async () => {
      api.post.mockRejectedValueOnce({
        response: {
          data: {
            error: {
              message: 'Un produs cu numele specificat există deja'
            }
          }
        }
      });

      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Adaugă Produs Nou')).toBeInTheDocument();
      });

      // Open modal and fill form
      const addButton = screen.getByText('Adaugă Produs Nou');
      await user.click(addButton);

      await user.type(screen.getByLabelText(/nume produs/i), 'Duplicate Product');
      await user.type(screen.getByLabelText(/descriere/i), 'Test description');
      await user.type(screen.getByLabelText(/preț/i), '19.99');
      
      const categorySelect = screen.getByLabelText(/categorie/i);
      await user.selectOptions(categorySelect, 'cat1');

      const submitButton = screen.getByRole('button', { name: /salvează produsul/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/un produs cu numele specificat există deja/i)).toBeInTheDocument();
      });
    });

    test('closes modal when cancel button is clicked', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Adaugă Produs Nou')).toBeInTheDocument();
      });

      // Open modal
      const addButton = screen.getByText('Adaugă Produs Nou');
      await user.click(addButton);

      // Close modal
      const cancelButton = screen.getByRole('button', { name: /anulează/i });
      await user.click(cancelButton);

      // Modal should be closed
      expect(screen.queryByLabelText(/nume produs/i)).not.toBeInTheDocument();
    });
  });

  describe('Product Editing', () => {
    test('opens edit modal with pre-populated data', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Brânză de capră')).toBeInTheDocument();
      });

      const editButtons = screen.getAllByText('Editează');
      await user.click(editButtons[0]);

      await waitFor(() => {
        expect(screen.getByDisplayValue('Brânză de capră')).toBeInTheDocument();
        expect(screen.getByDisplayValue('25.99')).toBeInTheDocument();
      });
    });

    test('submits edit form with updated data', async () => {
      api.put.mockResolvedValueOnce({
        data: {
          success: true,
          message: 'Produsul a fost actualizat cu succes'
        }
      });

      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Brânză de capră')).toBeInTheDocument();
      });

      // Open edit modal
      const editButtons = screen.getAllByText('Editează');
      await user.click(editButtons[0]);

      // Update name
      const nameInput = screen.getByDisplayValue('Brânză de capră');
      await user.clear(nameInput);
      await user.type(nameInput, 'Brânză de capră actualizată');

      // Submit form
      const submitButton = screen.getByRole('button', { name: /actualizează produsul/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(api.put).toHaveBeenCalledWith(
          '/admin/products/1',
          expect.objectContaining({
            name: 'Brânză de capră actualizată'
          }),
          expect.objectContaining({
            headers: {
              'Authorization': 'Bearer mock-access-token'
            }
          })
        );
      });
    });
  });

  describe('Product Deletion', () => {
    test('opens delete confirmation modal', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Brânză de capră')).toBeInTheDocument();
      });

      const deleteButtons = screen.getAllByText('Dezactivează');
      await user.click(deleteButtons[0]);

      expect(screen.getByText('Confirmă dezactivarea')).toBeInTheDocument();
      expect(screen.getByText(/ești sigur că vrei să dezactivezi produsul/i)).toBeInTheDocument();
    });

    test('performs soft delete when confirmed', async () => {
      api.delete.mockResolvedValueOnce({
        data: {
          success: true,
          message: 'Produsul a fost dezactivat cu succes'
        }
      });

      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Brânză de capră')).toBeInTheDocument();
      });

      // Open delete modal
      const deleteButtons = screen.getAllByText('Dezactivează');
      await user.click(deleteButtons[0]);

      // Confirm deletion
      const confirmButton = screen.getByRole('button', { name: /dezactivează produsul/i });
      await user.click(confirmButton);

      await waitFor(() => {
        expect(api.delete).toHaveBeenCalledWith(
          '/admin/products/1',
          expect.objectContaining({
            headers: {
              'Authorization': 'Bearer mock-access-token'
            }
          })
        );
      });
    });

    test('cancels deletion when cancel is clicked', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Brânză de capră')).toBeInTheDocument();
      });

      // Open delete modal
      const deleteButtons = screen.getAllByText('Dezactivează');
      await user.click(deleteButtons[0]);

      // Cancel deletion
      const cancelButton = screen.getByRole('button', { name: /anulează/i });
      await user.click(cancelButton);

      // Modal should be closed
      expect(screen.queryByText('Confirmă dezactivarea')).not.toBeInTheDocument();
      expect(api.delete).not.toHaveBeenCalled();
    });
  });

  describe('Loading States', () => {
    test('shows loading state during form submission', async () => {
      // Mock a slow API response
      api.post.mockImplementation(() => 
        new Promise(resolve => setTimeout(() => resolve({
          data: { success: true }
        }), 100))
      );

      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Adaugă Produs Nou')).toBeInTheDocument();
      });

      // Open modal and fill form
      const addButton = screen.getByText('Adaugă Produs Nou');
      await user.click(addButton);

      await user.type(screen.getByLabelText(/nume produs/i), 'Test Product');
      await user.type(screen.getByLabelText(/descriere/i), 'Test description');
      await user.type(screen.getByLabelText(/preț/i), '19.99');
      
      const categorySelect = screen.getByLabelText(/categorie/i);
      await user.selectOptions(categorySelect, 'cat1');

      // Submit form
      const submitButton = screen.getByRole('button', { name: /salvează produsul/i });
      await user.click(submitButton);

      // Check loading state
      expect(screen.getByText(/se salvează/i)).toBeInTheDocument();
    });
  });

  describe('Romanian Localization', () => {
    test('displays all text in Romanian', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        // Check main interface text
        expect(screen.getByText('Gestionare Produse')).toBeInTheDocument();
        expect(screen.getByText('Adaugă Produs Nou')).toBeInTheDocument();
        expect(screen.getByPlaceholderText(/căutați produse/i)).toBeInTheDocument();
        expect(screen.getByText('Toate categoriile')).toBeInTheDocument();
        
        // Check table headers
        expect(screen.getByText('Produs')).toBeInTheDocument();
        expect(screen.getByText('Categorie')).toBeInTheDocument();
        expect(screen.getByText('Preț')).toBeInTheDocument();
        expect(screen.getByText('Stoc')).toBeInTheDocument();
        expect(screen.getByText('Status')).toBeInTheDocument();
        expect(screen.getByText('Acțiuni')).toBeInTheDocument();
        
        // Check action buttons
        expect(screen.getAllByText('Editează')).toHaveLength(2);
      });
    });

    test('shows Romanian error messages', async () => {
      api.get.mockRejectedValueOnce(new Error('Network error'));

      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText(/eroare la încărcarea produselor/i)).toBeInTheDocument();
      });
    });

    test('shows Romanian success messages', async () => {
      api.post.mockResolvedValueOnce({
        data: {
          success: true,
          message: 'Produsul a fost creat cu succes'
        }
      });

      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Adaugă Produs Nou')).toBeInTheDocument();
      });

      // Create a product to trigger success message
      const addButton = screen.getByText('Adaugă Produs Nou');
      await user.click(addButton);

      await user.type(screen.getByLabelText(/nume produs/i), 'Test Product');
      await user.type(screen.getByLabelText(/descriere/i), 'Test description');
      await user.type(screen.getByLabelText(/preț/i), '19.99');
      
      const categorySelect = screen.getByLabelText(/categorie/i);
      await user.selectOptions(categorySelect, 'cat1');

      const submitButton = screen.getByRole('button', { name: /salvează produsul/i });
      await user.click(submitButton);

      await waitFor(() => {
        expect(screen.getByText(/produsul a fost creat cu succes/i)).toBeInTheDocument();
      });
    });
  });

  describe('Dynamic Image Fields', () => {
    test('adds and removes image fields', async () => {
      renderWithAuth(<ProductManager />);

      await waitFor(() => {
        expect(screen.getByText('Adaugă Produs Nou')).toBeInTheDocument();
      });

      // Open modal
      const addButton = screen.getByText('Adaugă Produs Nou');
      await user.click(addButton);

      // Initially should have 1 image field
      expect(screen.getAllByPlaceholderText(/https:\/\/example\.com\/image\.jpg/i)).toHaveLength(1);

      // Add image field
      const addImageButton = screen.getByText('Adaugă imagine');
      await user.click(addImageButton);

      // Should now have 2 image fields
      expect(screen.getAllByPlaceholderText(/https:\/\/example\.com\/image\.jpg/i)).toHaveLength(2);

      // Remove image field
      const removeButtons = screen.getAllByText('Șterge');
      await user.click(removeButtons[0]);

      // Should be back to 1 image field
      expect(screen.getAllByPlaceholderText(/https:\/\/example\.com\/image\.jpg/i)).toHaveLength(1);
    });
  });
});