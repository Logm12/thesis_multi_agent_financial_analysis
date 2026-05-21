import { StrictMode, Suspense } from 'react'
import { createRoot } from 'react-dom/client'
import './i18n.ts' // Khởi tạo đa ngôn ngữ
import './index.css'
import { AuthProvider } from './lib/auth-context.tsx'
import App from './App.tsx'

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <Suspense fallback={<div className="min-h-screen flex items-center justify-center font-sans text-slate-500">Loading academic engine...</div>}>
      <AuthProvider>
        <App />
      </AuthProvider>
    </Suspense>
  </StrictMode>,
)
