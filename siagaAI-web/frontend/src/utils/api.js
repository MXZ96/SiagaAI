/**
 * API Utility - Enhanced fetch with retry logic and error handling
 */

const API_BASE_URL = import.meta.env.VITE_API_URL || '';

/**
 * Fetch with retry logic
 */
export async function fetchWithRetry(url, options = {}, maxRetries = 3, retryDelay = 1000) {
  const { retryOptions = {}, ...fetchOptions } = options;
  const { 
    retryStatusCodes = [408, 429, 500, 502, 503, 504],
    shouldRetry = () => true,
    onRetry = null
  } = retryOptions;

  let lastError;

  for (let attempt = 0; attempt <= maxRetries; attempt++) {
    try {
      const response = await fetch(url, {
        ...fetchOptions,
        // Add timeout
        signal: AbortSignal.timeout(10000) // 10 second timeout
      });

      // Check if should retry based on status
      if (attempt < maxRetries && retryStatusCodes.includes(response.status)) {
        lastError = new Error(`HTTP ${response.status}`);
        if (onRetry) onRetry(attempt + 1, maxRetries);
        await delay(retryDelay * (attempt + 1)); // Exponential backoff
        continue;
      }

      return response;
    } catch (error) {
      lastError = error;
      
      // Network errors - retry
      if (attempt < maxRetries && (error.name === 'TypeError' || error.name === 'AbortError')) {
        if (onRetry) onRetry(attempt + 1, maxRetries);
        await delay(retryDelay * (attempt + 1));
        continue;
      }
      
      throw error;
    }
  }

  throw lastError;
}

/**
 * Delay helper
 */
function delay(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

/**
 * API GET request with error handling
 */
export async function apiGet(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetchWithRetry(url, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API GET Error: ${endpoint}`, error);
    throw error;
  }
}

/**
 * API POST request with error handling
 */
export async function apiPost(endpoint, data, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetchWithRetry(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      body: JSON.stringify(data),
      ...options
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API POST Error: ${endpoint}`, error);
    throw error;
  }
}

/**
 * API PUT request
 */
export async function apiPut(endpoint, data, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetchWithRetry(url, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      body: JSON.stringify(data),
      ...options
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return await response.json();
  } catch (error) {
    console.error(`API PUT Error: ${endpoint}`, error);
    throw error;
  }
}

/**
 * API DELETE request
 */
export async function apiDelete(endpoint, options = {}) {
  const url = `${API_BASE_URL}${endpoint}`;
  
  try {
    const response = await fetchWithRetry(url, {
      method: 'DELETE',
      headers: {
        'Content-Type': 'application/json',
        ...options.headers
      },
      ...options
    });

    if (!response.ok) {
      const error = await response.json().catch(() => ({}));
      throw new Error(error.message || `HTTP ${response.status}`);
    }

    return response.status === 204 ? null : await response.json();
  } catch (error) {
    console.error(`API DELETE Error: ${endpoint}`, error);
    throw error;
  }
}

/**
 * Hook for API calls with loading and error states
 */
import { useState, useCallback } from 'react';

export function useApi(apiFunc, options = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const execute = useCallback(async (...args) => {
    setLoading(true);
    setError(null);
    
    try {
      const result = await apiFunc(...args);
      setData(result);
      return result;
    } catch (err) {
      setError(err.message || 'Terjadi kesalahan');
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiFunc]);

  const reset = useCallback(() => {
    setData(null);
    setError(null);
    setLoading(false);
  }, []);

  return {
    data,
    loading,
    error,
    execute,
    reset
  };
}
