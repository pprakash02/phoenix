import { createContext, useContext } from 'react';

const AuthContext = createContext(null);

const ANONYMOUS_USER = { id: 'anonymous', email: '', name: 'User' };

export function AuthProvider({ children }) {
  return (
    <AuthContext.Provider
      value={{
        user: ANONYMOUS_USER,
        loading: false,
        isAuthenticated: true,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}

export default AuthContext;
