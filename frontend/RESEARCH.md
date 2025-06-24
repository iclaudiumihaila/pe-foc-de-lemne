# Image Container Filling Issues - Research & Solutions

## Current Problem Analysis

After examining the SwipeableCard and ProductCardStack components, the issue is that images are not filling their containers properly. The current structure has:

1. **Parent container**: Uses `padding-bottom: 140%` for aspect ratio (creating a 10:14 or 5:7 ratio)
2. **Image container**: Has `height: 70%` of the card
3. **Image element**: Missing proper CSS properties to fill the container

## Why Images Don't Fill Their Containers

### 1. Missing CSS Properties on Images
The current implementation doesn't set any CSS properties on the `<img>` elements. For `object-fit` to work, images need:
- `width: 100%`
- `height: 100%`
- `object-fit: cover` (or another appropriate value)

### 2. Percentage Height Issues
When using `height: 70%`, the container needs a defined height from its parent. With the padding-bottom trick, this can be tricky because:
- The parent uses `padding-bottom` for height, not an explicit height
- Percentage heights require explicit parent heights to calculate against

### 3. Nested Container Complexity
The structure has multiple nested containers:
```
ProductCardStack (padding-bottom: 140%)
  └── SwipeableCard (position: absolute, full size)
      └── Image container (height: 70%)
          └── <img> (no size properties)
```

## Object-Fit Values Explained

- **cover**: Image maintains aspect ratio and covers entire container (may crop)
- **contain**: Image maintains aspect ratio and fits entirely within container (may show gaps)
- **fill**: Image stretches to fill container (may distort)
- **scale-down**: Acts like either `none` or `contain`, whichever is smaller
- **none**: Image keeps original size

For product cards, **`cover`** is typically the best choice as it ensures the container is always filled.

## Best Practices & Solutions

### Solution 1: Add CSS to Images (Simplest)
```css
/* Add to SwipeableCard.jsx styles */
.product-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

### Solution 2: Use Inline Styles (Current Pattern)
```jsx
<img
  src={getImageUrl(product.images[0])}
  alt={product?.name || 'Produs'}
  style={{
    width: '100%',
    height: '100%',
    objectFit: 'cover'
  }}
  draggable={false}
  onError={(e) => {
    e.target.src = '/images/placeholder-product.jpg';
  }}
/>
```

### Solution 3: Modern Aspect Ratio Approach
Instead of the padding-bottom trick, use the CSS `aspect-ratio` property:
```css
.card-container {
  width: 100%;
  aspect-ratio: 5 / 7; /* or 10 / 14 */
}

.image-container {
  height: 70%;
  position: relative;
}

.image-container img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
```

### Solution 4: Absolute Positioning Within Image Container
For the current structure with percentage heights:
```jsx
<div style={{ height: '70%', position: 'relative', overflow: 'hidden' }}>
  <img
    src={getImageUrl(product.images[0])}
    alt={product?.name || 'Produs'}
    style={{
      position: 'absolute',
      top: 0,
      left: 0,
      width: '100%',
      height: '100%',
      objectFit: 'cover'
    }}
  />
</div>
```

## Common Pitfalls to Avoid

1. **Forgetting to set both width and height**: Object-fit requires explicit dimensions
2. **Not considering parent container dimensions**: Percentage heights need defined parent heights
3. **Mixing padding-bottom trick with percentage heights**: Can cause unexpected behavior
4. **Not setting overflow: hidden**: Important when using object-fit: cover to hide overflow
5. **Forgetting about loading states**: Images may appear broken while loading

## Recommended Implementation

For the current codebase, the simplest and most effective solution is to add inline styles to all image elements:

```jsx
// In SwipeableCard.jsx (lines 103-110)
<img
  src={getImageUrl(product.images[0])}
  alt={product?.name || 'Produs'}
  style={{
    width: '100%',
    height: '100%',
    objectFit: 'cover'
  }}
  draggable={false}
  onError={(e) => {
    e.target.src = '/images/placeholder-product.jpg';
  }}
/>
```

This should be applied to:
1. SwipeableCard.jsx - main product image (line 103)
2. SwipeableCard.jsx - expanded modal image (line 222)
3. ProductCardStack.jsx - background card images (line 164)

## Additional Considerations

### Responsive Images
For better performance on mobile:
```jsx
<img
  src={getImageUrl(product.images[0])}
  srcSet={`
    ${getImageUrl(product.images[0], 'small')} 300w,
    ${getImageUrl(product.images[0], 'medium')} 600w,
    ${getImageUrl(product.images[0], 'large')} 1200w
  `}
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw"
  loading="lazy"
  style={{
    width: '100%',
    height: '100%',
    objectFit: 'cover'
  }}
/>
```

### Loading States
Consider adding a loading state with skeleton or blur effect:
```css
.image-loading {
  filter: blur(5px);
  transition: filter 0.3s ease-out;
}

.image-loaded {
  filter: blur(0);
}
```

### Browser Compatibility
- `object-fit` is supported in all modern browsers
- For older browsers, consider a polyfill or fallback strategy
- The `aspect-ratio` property has good support but may need fallbacks for older browsers

## Testing Recommendations

1. Test with various image aspect ratios (portrait, landscape, square)
2. Test on different screen sizes and orientations
3. Test with slow network to ensure loading states work properly
4. Test with missing images to ensure placeholders work
5. Test touch interactions aren't affected by image styling changes