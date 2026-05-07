import { useEffect } from 'react';
import Sidebar from './components/Sidebar';
import MainContent from './components/MainContent';
import RightPanel from './components/RightPanel';
import apiClient from './api/client';

function App() {
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
  }, []);

  return (
    <div data-testid="app-root" className="flex min-h-screen w-full bg-background overflow-hidden">
      <Sidebar />
      <MainContent />
      <RightPanel />
    </div>
  );
}

export default App;
