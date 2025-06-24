import React from 'react';
import { X, RotateCcw, Heart } from 'lucide-react';

const SwipeActions = ({ 
  onSkip, 
  onUndo, 
  onLike, 
  canUndo = false,
  disabled = false 
}) => {
  return (
    <div className="flex items-center justify-center gap-6 mt-8">
      {/* Skip Button */}
      <button
        onClick={onSkip}
        disabled={disabled}
        className="action-button group relative bg-white border-2 border-gray-200 rounded-full p-4 shadow-lg hover:shadow-xl hover:scale-110 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200"
        aria-label="Treci peste produs"
      >
        <div className="absolute inset-0 bg-red-500 rounded-full opacity-0 group-hover:opacity-10 transition-opacity" />
        <X className="w-8 h-8 text-red-500" strokeWidth={3} />
      </button>

      {/* Undo Button */}
      <button
        onClick={onUndo}
        disabled={!canUndo || disabled}
        className="action-button group relative bg-white border-2 border-gray-200 rounded-full p-3 shadow-md hover:shadow-lg hover:scale-110 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200"
        aria-label="Anulează ultima acțiune"
      >
        <div className="absolute inset-0 bg-yellow-500 rounded-full opacity-0 group-hover:opacity-10 transition-opacity" />
        <RotateCcw className="w-6 h-6 text-yellow-600" strokeWidth={2.5} />
      </button>

      {/* Like/Add to Cart Button */}
      <button
        onClick={onLike}
        disabled={disabled}
        className="action-button group relative bg-white border-2 border-gray-200 rounded-full p-4 shadow-lg hover:shadow-xl hover:scale-110 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:scale-100 transition-all duration-200"
        aria-label="Adaugă în coș"
      >
        <div className="absolute inset-0 bg-green-500 rounded-full opacity-0 group-hover:opacity-10 transition-opacity" />
        <Heart className="w-8 h-8 text-green-500" strokeWidth={3} fill="none" />
      </button>
    </div>
  );
};

export default SwipeActions;