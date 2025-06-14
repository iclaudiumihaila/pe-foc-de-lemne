# Task 68: Create admin authentication context

**ID**: 68_admin_auth_context_creation  
**Title**: Create admin authentication context  
**Description**: Implement admin auth state management in React context  
**Dependencies**: API service base setup (Task 44)  
**Estimate**: 20 minutes  
**Deliverable**: frontend/src/context/AuthContext.jsx

## Context

The backend admin authentication system is complete with endpoints, middleware, and comprehensive testing. Now we need to create the frontend React context to manage admin authentication state, handle login/logout operations, manage JWT tokens, and provide authentication utilities for admin components.

## Requirements

### Core Authentication Context
1. **Authentication State Management**: Track authentication status, current user, and loading states
2. **Login Operations**: Handle admin login with credentials validation and token storage
3. **Logout Operations**: Handle admin logout with token cleanup
4. **Token Management**: Store, retrieve, and manage JWT tokens in localStorage
5. **Automatic Token Refresh**: Handle token refresh before expiration
6. **Error Handling**: Provide Romanian localized error messages

### Authentication Flow Support
1. **Protected Route Helpers**: Utilities to check authentication status
2. **User Data Management**: Store and retrieve current admin user information
3. **Loading States**: Manage loading states during authentication operations
4. **Session Persistence**: Maintain authentication across browser sessions
5. **Token Validation**: Verify token validity and handle expired tokens

### Integration Requirements
1. **API Service Integration**: Use existing API service for authentication endpoints
2. **Romanian Localization**: Handle Romanian error messages from backend
3. **Context Provider**: Wrap application with authentication context
4. **Hook Interface**: Provide useAuth hook for components
5. **TypeScript Ready**: Structure for potential TypeScript adoption

## Technical Implementation

### AuthContext Structure
```javascript
const AuthContext = createContext({
  // Auth state
  isAuthenticated: false,
  user: null,
  isLoading: false,
  
  // Auth operations
  login: async (credentials) => {},
  logout: () => {},
  refreshToken: async () => {},
  
  // Utilities
  checkAuthStatus: () => {},
  getToken: () => {},
  setAuthData: (user, tokens) => {}
});
```

### Token Management
- Store access and refresh tokens in localStorage
- Implement automatic token refresh before expiration
- Clear tokens on logout and authentication errors
- Handle token validation and expiration

### Romanian Error Handling
- Map backend Romanian error messages to user-friendly display
- Provide consistent error handling across authentication operations
- Handle network errors and API failures gracefully

## Success Criteria

1. AuthContext provides complete authentication state management
2. Login operations integrate with backend admin authentication API
3. Token storage and refresh work automatically
4. Romanian error messages are handled and displayed properly
5. Authentication state persists across browser sessions
6. Context can be consumed by admin components via useAuth hook
7. Loading states are managed during authentication operations
8. Logout operations clean up all authentication data
9. Protected route utilities work correctly
10. Token validation and refresh handle edge cases properly

## Implementation Notes

- Use React Context API with useReducer for complex state management
- Implement automatic token refresh with timeout handling
- Store sensitive data (tokens) securely in localStorage
- Provide clear error handling for all authentication scenarios
- Ensure context works with React Router for protected routes
- Handle edge cases like network failures and malformed responses
- Test authentication context independently of UI components