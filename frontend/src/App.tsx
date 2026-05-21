import { useEffect, useState } from 'react';
import { HashRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import Home from './components/Home';
import KnowledgeManagement from './components/KnowledgeManagement';
import Dashboard from './components/Dashboard';
import Settings from './components/Settings';
import { Auth } from './components/Auth';
import { LandingPage } from './components/LandingPage';
import { AdminDashboard } from './components/AdminDashboard';
import { useAuthStore } from './store/authStore';
import { useChatStore } from './store/useChatStore';
import apiClient from './api/client';
import { ShieldAlert, Loader } from 'lucide-react';

function App() {
  const { user, isAuthenticated, isLoading, checkAuth, logout } = useAuthStore();
  const [showLogoutModal, setShowLogoutModal] = useState(false);

  useEffect(() => {
    const checkConnectivity = async () => {
      try {
        const response = await apiClient.get('/health');
        console.log('[App] Backend Connected:', response.data);
      } catch {
        console.error('[App] Backend Connection Failed');
      }
    };
    checkConnectivity();
    checkAuth();
  }, [checkAuth]);

  // Multi-tab logout listener
  useEffect(() => {
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'logout-event') {
        const checkAndLogout = () => {
          const isProcessing = useChatStore.getState().isProcessing;
          if (isProcessing) {
            // Wait for processing to finish, then log out
            const unsubscribe = useChatStore.subscribe(
              (state) => {
                if (!state.isProcessing) {
                  unsubscribe();
                  setShowLogoutModal(true);
                }
              }
            );
          } else {
            setShowLogoutModal(true);
          }
        };
        checkAndLogout();
      }
    };
    window.addEventListener('storage', handleStorageChange);
    return () => window.removeEventListener('storage', handleStorageChange);
  }, []);

  const handleModalClose = () => {
    setShowLogoutModal(false);
    logout(); // Clear Zustand state locally
  };

  if (isLoading) {
    return (
      <div className="min-h-screen w-full flex flex-col items-center justify-center bg-slate-950 text-slate-100 select-none">
        <Loader className="w-8 h-8 animate-spin text-indigo-500 mb-4" />
        <p className="text-sm font-medium text-slate-400">Verifying session...</p>
      </div>
    );
  }

  // Not authenticated: show LandingPage as default, allow routing to /login
  if (!isAuthenticated) {
    return (
      <Router>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/login" element={<Auth />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </Router>
    );
  }

  return (
    <Router>
      <div data-testid="app-root" className="flex min-h-screen w-full bg-background overflow-hidden relative">
        <Sidebar />
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/knowledge" element={<KnowledgeManagement />} />
          <Route path="/dashboard" element={<Dashboard />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="/admin" element={user?.role === 'ADMIN' ? <AdminDashboard /> : <Navigate to="/" replace />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>

        {/* Multi-tab Logout Alert Modal */}
        {showLogoutModal && (
          <div className="fixed inset-0 z-50 flex items-center justify-center bg-slate-950/60 backdrop-blur-md transition-opacity duration-300">
            <div className="w-full max-w-sm bg-slate-900 border border-slate-800 rounded-3xl p-6 shadow-2xl scale-100 animate-in fade-in zoom-in-95 duration-200">
              <div className="flex items-center gap-3 text-amber-500 mb-4">
                <div className="w-10 h-10 rounded-xl bg-amber-500/10 flex items-center justify-center shadow-lg shadow-amber-500/5">
                  <ShieldAlert className="w-5 h-5" />
                </div>
                <h3 className="font-bold text-slate-100">Session Ended</h3>
              </div>
              <p className="text-sm text-slate-400 leading-relaxed mb-6">
                You have logged out in another browser tab. Please log in again to continue.
              </p>
              <button
                onClick={handleModalClose}
                className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-500 active:bg-indigo-750 text-white text-sm font-semibold rounded-xl transition-all duration-200 shadow-lg shadow-indigo-600/10"
              >
                Log In Again
              </button>
            </div>
          </div>
        )}
      </div>
    </Router>
  );
}

export default App;
