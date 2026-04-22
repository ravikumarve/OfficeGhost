import { useState, useEffect } from 'react';

const API_BASE = 'http://localhost:5000';

export const useApi = (endpoint, options = {}) => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true);
        
        const headers = {
          ...options.headers,
        };

        // For FormData, don't set Content-Type header (browser will set it with boundary)
        if (!(options.body instanceof FormData)) {
          headers['Content-Type'] = 'application/json';
        }

        const response = await fetch(`${API_BASE}${endpoint}`, {
          ...options,
          headers,
          credentials: 'include', // Important for Flask session cookies
        });

        if (!response.ok) {
          if (response.status === 401) {
            // Redirect to login if unauthorized
            window.location.href = '/login';
            return;
          }
          throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();
        setData(result);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [endpoint]);

  return { data, loading, error };
};

export const apiCall = async (endpoint, options = {}) => {
  const headers = {
    ...options.headers,
  };

  // For FormData, don't set Content-Type header
  if (!(options.body instanceof FormData)) {
    headers['Content-Type'] = 'application/json';
  }

  const response = await fetch(`${API_BASE}${endpoint}`, {
    ...options,
    headers,
    credentials: 'include', // Important for Flask session cookies
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Redirect to login if unauthorized
      window.location.href = '/login';
      return;
    }
    throw new Error(`HTTP error! status: ${response.status}`);
  }

  return response.json();
};