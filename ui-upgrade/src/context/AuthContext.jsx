import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [loading, setLoading] = useState(true);
  const [requireSetup, setRequireSetup] = useState(false);

  useEffect(() => {
    // Check if user is authenticated on app load
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    try {
      // Flask uses session-based auth, so we just check if we can access protected routes
      const response = await fetch('http://localhost:5000/api/status', {
        credentials: 'include', // Important for session cookies
      });
      
      if (response.ok) {
        const data = await response.json();
        setUser({ email: 'user@ghostoffice.local' }); // Placeholder user data
        setIsAuthenticated(true);
      } else {
        // Check if setup is required
        const setupResponse = await fetch('http://localhost:5000/setup', {
          credentials: 'include',
          redirect: 'manual'
        });
        if (setupResponse.ok && setupResponse.status === 200) {
          setRequireSetup(true);
        }
        setIsAuthenticated(false);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
      setIsAuthenticated(false);
    } finally {
      setLoading(false);
    }
  };

  const login = async (password, totpToken = null) => {
    try {
      const formData = new FormData();
      formData.append('password', password);
      if (totpToken) {
        formData.append('totp_token', totpToken);
      }

      const response = await fetch('http://localhost:5000/login', {
        method: 'POST',
        credentials: 'include',
        body: formData,
      });

      if (response.ok) {
        // Check if we were redirected to dashboard (successful login)
        setUser({ email: 'user@ghostoffice.local' });
        setIsAuthenticated(true);
        return { success: true };
      } else {
        // Parse error from response
        const text = await response.text();
        return { success: false, error: text || 'Login failed' };
      }
    } catch (error) {
      console.error('Login error:', error);
      return { success: false, error: 'Network error' };
    }
  };

  const logout = async () => {
    try {
      await fetch('http://localhost:5000/logout', {
        method: 'GET',
        credentials: 'include',
      });
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      setUser(null);
      setIsAuthenticated(false);
    }
  };

  const value = {
    user,
    isAuthenticated,
    loading,
    requireSetup,
    login,
    logout
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
};