import React, { createContext, useContext, useState, useEffect } from 'react';

interface User {
  username: string;
  role: string;
}

interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  login: (username: string) => void;
  logout: () => void;
  sessionToken: string;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [user, setUser] = useState<User | null>(null);
  const [sessionToken, setSessionToken] = useState('');

  useEffect(() => {
    // Khởi tạo Session ID ngẫu nhiên cho Demo Rate Limit
    let storedToken = localStorage.getItem('demo_session_token');
    if (!storedToken) {
      storedToken = 'sess_' + Math.random().toString(36).substring(2, 15);
      localStorage.setItem('demo_session_token', storedToken);
    }
    setSessionToken(storedToken);

    const storedAuth = localStorage.getItem('is_authenticated');
    if (storedAuth === 'true') {
      setIsAuthenticated(true);
      setUser({ username: 'Demo User', role: 'admin' });
    }
  }, []);

  const login = (username: string) => {
    setIsAuthenticated(true);
    setUser({ username, role: 'admin' });
    localStorage.setItem('is_authenticated', 'true');
  };

  const logout = () => {
    setIsAuthenticated(false);
    setUser(null);
    localStorage.removeItem('is_authenticated');
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, user, login, logout, sessionToken }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
