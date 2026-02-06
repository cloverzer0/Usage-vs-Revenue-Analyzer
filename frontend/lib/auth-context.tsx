'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import { useRouter } from 'next/navigation';

interface User {
  id: number;
  email: string;
  username: string;
  full_name?: string;
  is_active: boolean;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, username: string, password: string, fullName?: string) => Promise<void>;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    // Check for existing token on mount (client-side only)
    if (typeof window !== 'undefined') {
      const storedToken = localStorage.getItem('auth_token');
      if (storedToken) {
        verifyToken(storedToken);
      } else {
        setIsLoading(false);
      }
    } else {
      setIsLoading(false);
    }
  }, []);

  const verifyToken = async (storedToken: string) => {
    try {
      const response = await fetch('/api/auth/me', {
        headers: {
          'Authorization': `Bearer ${storedToken}`
        }
      });

      if (response.ok) {
        const userData = await response.json();
        setUser(userData);
        setToken(storedToken);
      } else {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
      }
    } catch (error) {
      console.error('Token verification failed:', error);
      if (typeof window !== 'undefined') {
        localStorage.removeItem('auth_token');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const login = async (email: string, password: string) => {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    const response = await fetch('/api/auth/login', {
      method: 'POST',
      body: formData
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data = await response.json();
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', data.access_token);
    }
    setToken(data.access_token);
    setUser(data.user);
    // Use setTimeout to ensure state updates complete before redirect
    setTimeout(() => router.push('/dashboard'), 100);
  };

  const register = async (email: string, username: string, password: string, fullName?: string) => {
    const response = await fetch('/api/auth/register', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        email,
        username,
        password,
        full_name: fullName
      })
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Registration failed');
    }

    const data = await response.json();
    if (typeof window !== 'undefined') {
      localStorage.setItem('auth_token', data.access_token);
    }
    setToken(data.access_token);
    setUser(data.user);
    // Use setTimeout to ensure state updates complete before redirect
    setTimeout(() => router.push('/dashboard'), 100);
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    if (typeof window !== 'undefined') {
      localStorage.removeItem('auth_token');
    }
    router.push('/login');
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
