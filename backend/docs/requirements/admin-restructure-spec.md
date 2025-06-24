# Admin Area Restructuring Requirements Specification

## 1. Business Requirements

### 1.1 Current State
- Admin area currently uses the same layout as the public site
- Main site header (green banner with cart) appears on all admin pages
- Admin dashboard has its own navigation system that conflicts with main header

### 1.2 Desired State
- Dedicated admin layout without public site header
- Clean, professional admin interface
- Consistent navigation across all admin pages
- Clear separation between public and admin areas

## 2. Functional Requirements

### 2.1 Layout Requirements
- **Admin Layout**:
  - No public site header (green banner)
  - No public site footer
  - Admin-specific navigation bar with user info and logout
  - Persistent sidebar navigation
  - Clean, focused workspace

- **Public Layout**:
  - Keep existing header and footer
  - Maintain current design for all non-admin routes

### 2.2 Routing Requirements
- All `/admin/*` routes use admin layout
- All other routes use public layout
- Smooth transitions between layouts
- Maintain authentication state across layouts

### 2.3 Navigation Requirements
- Admin sidebar with links to:
  - Dashboard
  - Products Management
  - Orders Management
  - Categories Management
- Quick actions accessible from dashboard
- User info and logout in admin nav bar
- "Back to store" link for returning to public site

## 3. Technical Requirements

### 3.1 Component Architecture
- Create layout wrapper components
- Implement route-based layout switching
- Maintain existing component functionality
- Ensure proper component isolation

### 3.2 State Management
- Preserve authentication state
- Maintain cart state (for when returning to public site)
- Handle layout transitions cleanly

### 3.3 Performance Requirements
- Lazy load admin components
- Minimize bundle size for public users
- Fast layout switching

## 4. Design Requirements

### 4.1 Admin UI Guidelines
- Professional, clean interface
- Consistent spacing and typography
- Clear visual hierarchy
- Responsive design for admin area

### 4.2 Color Scheme
- Maintain brand colors but in admin context
- Clear distinction from public site
- Professional appearance

## 5. Security Requirements
- Admin routes protected by authentication
- Proper authorization checks
- Secure session management
- Clear logout functionality