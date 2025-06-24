import React from 'react';

// Base skeleton component
const Skeleton = ({ 
  className = '', 
  height = 'h-4', 
  width = 'w-full',
  rounded = 'rounded',
  animated = true 
}) => (
  <div 
    className={`
      ${height} 
      ${width} 
      ${rounded} 
      bg-gray-200 
      ${animated ? 'animate-pulse' : ''} 
      ${className}
    `}
    aria-label="Se încarcă conținutul"
    role="status"
  />
);

// Product card skeleton - Minimalist Pinterest style
export const ProductCardSkeleton = ({ className = '' }) => (
  <div className={`bg-white ${className}`}>
    {/* Image skeleton - variable height */}
    <Skeleton height="h-64" className="mb-0" rounded="" />
    
    <div className="p-3 space-y-2">
      {/* Title skeleton */}
      <Skeleton height="h-4" width="w-3/4" />
      
      {/* Price skeleton */}
      <Skeleton height="h-5" width="w-1/2" />
      
      {/* Button skeleton */}
      <Skeleton height="h-10" width="w-full" />
    </div>
  </div>
);

// Product grid skeleton - Masonry Pinterest style
export const ProductGridSkeleton = ({ count = 8, className = '' }) => (
  <div className={`masonry-grid ${className}`}>
    {Array.from({ length: count }).map((_, index) => (
      <div key={index} className="masonry-item">
        <ProductCardSkeleton />
      </div>
    ))}
  </div>
);

// Cart item skeleton
export const CartItemSkeleton = ({ className = '' }) => (
  <div className={`bg-white rounded-lg border border-gray-200 p-4 ${className}`}>
    <div className="flex items-center space-x-4">
      {/* Image skeleton */}
      <Skeleton height="h-16" width="w-16" rounded="rounded-lg" />
      
      <div className="flex-1 space-y-2">
        {/* Product name */}
        <Skeleton height="h-5" width="w-2/3" />
        
        {/* Price and quantity */}
        <div className="flex items-center justify-between">
          <Skeleton height="h-4" width="w-1/4" />
          <Skeleton height="h-8" width="w-20" rounded="rounded-md" />
        </div>
      </div>
      
      {/* Remove button */}
      <Skeleton height="h-8" width="w-8" rounded="rounded-full" />
    </div>
  </div>
);

// Cart summary skeleton
export const CartSummarySkeleton = ({ className = '' }) => (
  <div className={`bg-white rounded-lg shadow-sm border border-gray-200 p-6 ${className}`}>
    {/* Title */}
    <Skeleton height="h-6" width="w-1/2" className="mb-4" />
    
    {/* Summary lines */}
    <div className="space-y-3 mb-4">
      <div className="flex justify-between">
        <Skeleton height="h-4" width="w-1/3" />
        <Skeleton height="h-4" width="w-1/4" />
      </div>
      <div className="flex justify-between">
        <Skeleton height="h-4" width="w-1/4" />
        <Skeleton height="h-4" width="w-1/4" />
      </div>
      <div className="border-t pt-3">
        <div className="flex justify-between">
          <Skeleton height="h-5" width="w-1/3" />
          <Skeleton height="h-5" width="w-1/3" />
        </div>
      </div>
    </div>
    
    {/* Checkout button */}
    <Skeleton height="h-12" width="w-full" rounded="rounded-md" />
  </div>
);

// Form skeleton
export const FormSkeleton = ({ className = '' }) => (
  <div className={`bg-white rounded-lg shadow-sm p-6 ${className}`}>
    {/* Form title */}
    <Skeleton height="h-6" width="w-1/2" className="mb-6" />
    
    {/* Form fields */}
    <div className="space-y-4">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <Skeleton height="h-4" width="w-1/3" className="mb-2" />
          <Skeleton height="h-10" width="w-full" rounded="rounded-md" />
        </div>
        <div>
          <Skeleton height="h-4" width="w-1/2" className="mb-2" />
          <Skeleton height="h-10" width="w-full" rounded="rounded-md" />
        </div>
      </div>
      
      <div>
        <Skeleton height="h-4" width="w-1/4" className="mb-2" />
        <Skeleton height="h-10" width="w-full" rounded="rounded-md" />
      </div>
      
      <div>
        <Skeleton height="h-4" width="w-1/3" className="mb-2" />
        <Skeleton height="h-24" width="w-full" rounded="rounded-md" />
      </div>
    </div>
    
    {/* Submit button */}
    <Skeleton height="h-12" width="w-1/3" className="mt-6" rounded="rounded-md" />
  </div>
);

// Table skeleton
export const TableSkeleton = ({ 
  rows = 5, 
  columns = 4, 
  className = '' 
}) => (
  <div className={`bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden ${className}`}>
    {/* Table header */}
    <div className="bg-gray-50 p-4 border-b border-gray-200">
      <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
        {Array.from({ length: columns }).map((_, index) => (
          <Skeleton key={index} height="h-4" width="w-2/3" />
        ))}
      </div>
    </div>
    
    {/* Table rows */}
    <div className="divide-y divide-gray-200">
      {Array.from({ length: rows }).map((_, rowIndex) => (
        <div key={rowIndex} className="p-4">
          <div className="grid gap-4" style={{ gridTemplateColumns: `repeat(${columns}, 1fr)` }}>
            {Array.from({ length: columns }).map((_, colIndex) => (
              <Skeleton key={colIndex} height="h-4" width={colIndex === 0 ? 'w-3/4' : 'w-1/2'} />
            ))}
          </div>
        </div>
      ))}
    </div>
  </div>
);

// Dashboard stats skeleton
export const StatsSkeleton = ({ className = '' }) => (
  <div className={`grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 ${className}`}>
    {Array.from({ length: 4 }).map((_, index) => (
      <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <div className="flex items-center justify-between">
          <div className="space-y-2">
            <Skeleton height="h-4" width="w-20" />
            <Skeleton height="h-8" width="w-16" />
          </div>
          <Skeleton height="h-12" width="w-12" rounded="rounded-lg" />
        </div>
      </div>
    ))}
  </div>
);

// Text content skeleton
export const TextSkeleton = ({ 
  lines = 3, 
  className = '' 
}) => (
  <div className={`space-y-3 ${className}`}>
    {Array.from({ length: lines }).map((_, index) => (
      <Skeleton 
        key={index} 
        height="h-4" 
        width={index === lines - 1 ? 'w-2/3' : 'w-full'} 
      />
    ))}
  </div>
);

// List skeleton
export const ListSkeleton = ({ 
  items = 5, 
  className = '' 
}) => (
  <div className={`space-y-4 ${className}`}>
    {Array.from({ length: items }).map((_, index) => (
      <div key={index} className="flex items-center space-x-3">
        <Skeleton height="h-10" width="w-10" rounded="rounded-full" />
        <div className="flex-1 space-y-2">
          <Skeleton height="h-4" width="w-3/4" />
          <Skeleton height="h-3" width="w-1/2" />
        </div>
      </div>
    ))}
  </div>
);

// Page content skeleton for initial loading
export const PageSkeleton = ({ className = '' }) => (
  <div className={`min-h-screen bg-gray-50 py-8 px-4 ${className}`}>
    <div className="max-w-7xl mx-auto">
      {/* Page header skeleton */}
      <div className="text-center mb-8">
        <Skeleton height="h-8" width="w-1/3" className="mx-auto mb-4" />
        <Skeleton height="h-4" width="w-1/2" className="mx-auto" />
      </div>
      
      {/* Content skeleton */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <div className="lg:col-span-2 space-y-6">
          <FormSkeleton />
        </div>
        <div className="lg:col-span-1">
          <CartSummarySkeleton />
        </div>
      </div>
    </div>
  </div>
);

export default Skeleton;