import React, { useState, useEffect, useCallback } from 'react';

const ProductFilter = ({
  // Filter state
  searchTerm,
  selectedCategory,
  sortBy,
  sortOrder,
  
  // Data
  categories = [],
  
  // Callbacks
  onSearchChange,
  onCategoryChange,
  onSortChange,
  onClearSearch,
  
  // UI state
  loading = false,
  searchLoading = false,
  totalResults = 0,
  
  // Configuration
  showResultCount = true,
  collapsible = true,
  className = ''
}) => {
  // Local UI state
  const [filtersExpanded, setFiltersExpanded] = useState(false);
  const [localSearchTerm, setLocalSearchTerm] = useState(searchTerm || '');

  // Update local search term when prop changes
  useEffect(() => {
    setLocalSearchTerm(searchTerm || '');
  }, [searchTerm]);

  // Debounced search handler
  useEffect(() => {
    const timer = setTimeout(() => {
      if (localSearchTerm !== searchTerm) {
        onSearchChange(localSearchTerm);
      }
    }, 300);
    
    return () => clearTimeout(timer);
  }, [localSearchTerm, searchTerm, onSearchChange]);

  // Handle local search input change
  const handleSearchInputChange = (e) => {
    setLocalSearchTerm(e.target.value);
  };

  // Handle clear search
  const handleClearSearch = useCallback(() => {
    setLocalSearchTerm('');
    if (onClearSearch) {
      onClearSearch();
    } else {
      onSearchChange('');
    }
  }, [onClearSearch, onSearchChange]);

  // Handle sort change
  const handleSortChange = (e) => {
    const [field, order] = e.target.value.split('-');
    onSortChange(field, order);
  };

  // Get active filters count for mobile
  const getActiveFiltersCount = () => {
    let count = 0;
    if (searchTerm && searchTerm.trim()) count++;
    if (selectedCategory) count++;
    return count;
  };

  // Search Input Component
  const SearchInput = () => (
    <div className="relative">
      <input
        type="text"
        placeholder="Căutați produse..."
        value={localSearchTerm}
        onChange={handleSearchInputChange}
        className="w-full pl-10 pr-10 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-green-500 focus:border-green-500 text-sm"
      />
      <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
        <svg className="h-4 w-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
        </svg>
      </div>
      {localSearchTerm && (
        <button
          onClick={handleClearSearch}
          className="absolute inset-y-0 right-0 pr-3 flex items-center text-gray-400 hover:text-gray-600"
        >
          <svg className="h-4 w-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      )}
      {searchLoading && (
        <div className="absolute inset-y-0 right-0 pr-3 flex items-center">
          <div className="animate-spin h-4 w-4 border-2 border-green-500 border-t-transparent rounded-full"></div>
        </div>
      )}
    </div>
  );

  // Category Filters Component
  const CategoryFilters = () => (
    <div className="space-y-3">
      <h4 className="text-sm font-medium text-gray-700">Categorii</h4>
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => onCategoryChange('')}
          className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
            selectedCategory === '' 
              ? 'bg-green-600 text-white' 
              : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
          }`}
        >
          Toate produsele
        </button>
        {categories.map((category) => (
          <button
            key={category.id}
            onClick={() => onCategoryChange(category.id)}
            className={`px-3 py-1.5 rounded-full text-sm font-medium transition-colors ${
              selectedCategory === category.id 
                ? 'bg-green-600 text-white' 
                : 'bg-white text-gray-700 border border-gray-300 hover:bg-gray-50'
            }`}
          >
            {category.name}
          </button>
        ))}
      </div>
    </div>
  );

  // Sort Dropdown Component
  const SortDropdown = () => (
    <div className="flex items-center gap-2">
      <label htmlFor="sort-select" className="text-sm text-gray-600 whitespace-nowrap">
        Sortează:
      </label>
      <select
        id="sort-select"
        value={`${sortBy}-${sortOrder}`}
        onChange={handleSortChange}
        className="border border-gray-300 rounded-md px-3 py-1.5 text-sm focus:ring-2 focus:ring-green-500 focus:border-green-500 bg-white"
      >
        <option value="name-asc">Nume (A-Z)</option>
        <option value="name-desc">Nume (Z-A)</option>
        <option value="price-asc">Preț crescător</option>
        <option value="price-desc">Preț descrescător</option>
        <option value="created_at-desc">Cele mai noi</option>
      </select>
    </div>
  );

  // Filter Summary Component
  const FilterSummary = () => {
    const hasActiveSearch = searchTerm && searchTerm.trim();
    const hasActiveCategory = selectedCategory;
    const hasActiveFilters = hasActiveSearch || hasActiveCategory;

    if (!hasActiveFilters && !showResultCount) return null;

    return (
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 pt-3 border-t border-gray-200">
        {showResultCount && (
          <div className="text-sm text-gray-600">
            {hasActiveSearch ? (
              <span>
                <strong>{totalResults}</strong> rezultate pentru <strong>"{searchTerm}"</strong>
              </span>
            ) : (
              <span>
                <strong>{totalResults}</strong> produse {hasActiveCategory && 'în categoria selectată'}
              </span>
            )}
          </div>
        )}
        
        {hasActiveFilters && (
          <div className="flex items-center gap-2">
            <span className="text-sm text-gray-500">Filtre active:</span>
            <div className="flex gap-1">
              {hasActiveSearch && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-blue-100 text-blue-800">
                  Căutare: "{searchTerm}"
                  <button
                    onClick={handleClearSearch}
                    className="ml-1 hover:text-blue-900"
                  >
                    <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </span>
              )}
              {hasActiveCategory && (
                <span className="inline-flex items-center px-2 py-1 rounded-full text-xs bg-green-100 text-green-800">
                  {categories.find(cat => cat.id === selectedCategory)?.name || 'Categorie'}
                  <button
                    onClick={() => onCategoryChange('')}
                    className="ml-1 hover:text-green-900"
                  >
                    <svg className="h-3 w-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </span>
              )}
            </div>
          </div>
        )}
      </div>
    );
  };

  // Mobile Filter Toggle
  const MobileFilterToggle = () => {
    const activeCount = getActiveFiltersCount();
    
    return (
      <button
        onClick={() => setFiltersExpanded(!filtersExpanded)}
        className="md:hidden flex items-center justify-between w-full px-4 py-3 bg-white border border-gray-300 rounded-lg text-sm font-medium text-gray-700 hover:bg-gray-50"
      >
        <span className="flex items-center">
          <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707v4.172a1 1 0 01-.629.928l-2 .618a1 1 0 01-1.371-.928v-4.79a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          Filtre
          {activeCount > 0 && (
            <span className="ml-2 inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-800">
              {activeCount}
            </span>
          )}
        </span>
        <svg 
          className={`h-4 w-4 transform transition-transform ${filtersExpanded ? 'rotate-180' : ''}`}
          fill="none" 
          stroke="currentColor" 
          viewBox="0 0 24 24"
        >
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
        </svg>
      </button>
    );
  };

  return (
    <div className={`product-filter bg-white rounded-lg border border-gray-200 ${className}`}>
      {/* Desktop Layout */}
      <div className="hidden md:block p-6">
        {/* Search and Sort Row */}
        <div className="flex flex-col lg:flex-row gap-4 items-start lg:items-center justify-between mb-6">
          <div className="flex-1 max-w-md">
            <SearchInput />
          </div>
          <SortDropdown />
        </div>
        
        {/* Category Filters */}
        <div className="mb-4">
          <CategoryFilters />
        </div>
        
        {/* Filter Summary */}
        <FilterSummary />
      </div>

      {/* Mobile Layout */}
      <div className="md:hidden">
        {/* Search Input - Always Visible */}
        <div className="p-4 border-b border-gray-200">
          <SearchInput />
        </div>
        
        {/* Mobile Filter Toggle */}
        <div className="p-4 border-b border-gray-200">
          <MobileFilterToggle />
        </div>
        
        {/* Collapsible Filter Content */}
        {filtersExpanded && (
          <div className="p-4 space-y-4 border-b border-gray-200">
            <CategoryFilters />
            <div className="pt-2">
              <SortDropdown />
            </div>
          </div>
        )}
        
        {/* Filter Summary - Always Visible if Active */}
        <div className="p-4">
          <FilterSummary />
        </div>
      </div>
      
      {/* Loading Overlay */}
      {loading && (
        <div className="absolute inset-0 bg-white bg-opacity-75 flex items-center justify-center rounded-lg">
          <div className="flex items-center space-x-2 text-gray-600">
            <div className="animate-spin h-5 w-5 border-2 border-green-500 border-t-transparent rounded-full"></div>
            <span className="text-sm">Se încarcă filtrele...</span>
          </div>
        </div>
      )}
    </div>
  );
};

export default ProductFilter;