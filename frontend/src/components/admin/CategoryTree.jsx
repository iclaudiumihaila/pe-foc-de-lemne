import React, { useState } from 'react';
import { 
  Folder, 
  FolderOpen, 
  Edit, 
  Trash2, 
  ChevronRight, 
  ChevronDown,
  Package
} from 'lucide-react';

const CategoryTree = ({ categories, onEdit, onDelete, level = 0 }) => {
  const [expandedCategories, setExpandedCategories] = useState(new Set());

  const toggleExpand = (categoryId) => {
    const newExpanded = new Set(expandedCategories);
    if (newExpanded.has(categoryId)) {
      newExpanded.delete(categoryId);
    } else {
      newExpanded.add(categoryId);
    }
    setExpandedCategories(newExpanded);
  };

  const handleDelete = async (category) => {
    if (category.product_count > 0) {
      alert(`Nu puteți șterge categoria "${category.name}" deoarece conține ${category.product_count} produse.`);
      return;
    }

    if (category.children && category.children.length > 0) {
      alert(`Nu puteți șterge categoria "${category.name}" deoarece conține subcategorii.`);
      return;
    }

    if (window.confirm(`Sigur doriți să ștergeți categoria "${category.name}"?`)) {
      onDelete(category.id);
    }
  };

  if (!categories || categories.length === 0) {
    return level === 0 ? (
      <div className="text-center py-8 text-gray-500 dark:text-gray-400">
        Nu există categorii disponibile.
      </div>
    ) : null;
  }

  return (
    <div className={`${level > 0 ? 'ml-6' : ''}`}>
      {categories.map((category) => {
        const hasChildren = category.children && category.children.length > 0;
        const isExpanded = expandedCategories.has(category.id);

        return (
          <div key={category.id} className="mb-1">
            <div 
              className={`
                flex items-center justify-between p-3 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700
                transition-colors group ${level === 0 ? 'bg-white dark:bg-gray-800 shadow-sm' : ''}
              `}
            >
              <div className="flex items-center flex-1">
                {hasChildren && (
                  <button
                    onClick={() => toggleExpand(category.id)}
                    className="mr-2 p-1 hover:bg-gray-200 dark:hover:bg-gray-600 rounded transition-colors"
                  >
                    {isExpanded ? (
                      <ChevronDown className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                    ) : (
                      <ChevronRight className="w-4 h-4 text-gray-600 dark:text-gray-400" />
                    )}
                  </button>
                )}
                
                {!hasChildren && (
                  <div className="w-8" /> // Spacer pentru aliniere
                )}

                <div className="flex items-center">
                  {isExpanded ? (
                    <FolderOpen className="w-5 h-5 text-yellow-600 mr-3" />
                  ) : (
                    <Folder className="w-5 h-5 text-yellow-600 mr-3" />
                  )}
                  
                  <div>
                    <h3 className="font-medium text-gray-900 dark:text-white">
                      {category.name}
                    </h3>
                    {category.description && (
                      <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                        {category.description}
                      </p>
                    )}
                  </div>
                </div>
              </div>

              <div className="flex items-center gap-2 ml-4">
                {category.product_count > 0 && (
                  <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                    <Package className="w-4 h-4 mr-1" />
                    <span>{category.product_count}</span>
                  </div>
                )}

                <div className="opacity-0 group-hover:opacity-100 flex items-center gap-1 transition-opacity">
                  <button
                    onClick={() => onEdit(category)}
                    className="p-2 hover:bg-blue-100 dark:hover:bg-blue-900/20 rounded-lg transition-colors"
                    title="Editează categoria"
                  >
                    <Edit className="w-4 h-4 text-blue-600" />
                  </button>
                  
                  <button
                    onClick={() => handleDelete(category)}
                    className="p-2 hover:bg-red-100 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                    title="Șterge categoria"
                  >
                    <Trash2 className="w-4 h-4 text-red-600" />
                  </button>
                </div>
              </div>
            </div>

            {hasChildren && isExpanded && (
              <div className="mt-1">
                <CategoryTree 
                  categories={category.children} 
                  onEdit={onEdit} 
                  onDelete={onDelete}
                  level={level + 1}
                />
              </div>
            )}
          </div>
        );
      })}
    </div>
  );
};

export default CategoryTree;