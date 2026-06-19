import { LayoutDashboard, MessageSquare, Database, Settings, HelpCircle, ChevronRight, Sparkles, LogOut } from 'lucide-react';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/authStore';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const Sidebar = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const { user, logout } = useAuthStore();

  const getInitials = (name: string) => {
    if (!name) return 'U';
    const parts = name.trim().split(/\s+/);
    if (parts.length === 1) return parts[0].substring(0, 2).toUpperCase();
    return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
  };

  const getNickname = (name: string) => {
    if (!name) return '';
    const parts = name.trim().split(/\s+/);
    return parts[parts.length - 1];
  };


  const navItems = [
    { name: 'Dashboard', icon: LayoutDashboard, path: '/dashboard' },
    { name: 'AI Chat', icon: MessageSquare, path: '/' },
    { name: 'Knowledge', icon: Database, path: '/knowledge' },
    { name: 'Settings', icon: Settings, path: '/settings' },
  ];

  return (
    <aside className="w-72 h-full bg-white border-r border-slate-200 flex flex-col shrink-0 z-20">
      <div className="p-8">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-9 h-9 bg-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-200">
            <Sparkles className="w-5 h-5 text-white" />
          </div>
          <h1 className="text-xl font-bold text-slate-900 tracking-tight">
            Lumo <span className="text-indigo-600">AI</span>
          </h1>
        </div>
        <p className="text-[11px] font-semibold text-slate-400 uppercase tracking-widest px-1">Financial Analyzer</p>
      </div>
      
      <nav className="flex-1 px-4 space-y-1.5">
        {navItems.map((item) => {
          const isActive = location.pathname === item.path;
          return (
            <button
              key={item.name}
              onClick={() => navigate(item.path)}
              className={cn(
                "w-full flex items-center justify-between px-4 py-3 text-sm font-medium rounded-xl transition-all duration-200 group",
                isActive 
                  ? "bg-indigo-50 text-indigo-700 shadow-sm shadow-indigo-100" 
                  : "text-slate-500 hover:bg-slate-50 hover:text-slate-900"
              )}
            >
              <div className="flex items-center gap-3">
                <item.icon className={cn("w-5 h-5 transition-colors", isActive ? "text-indigo-600" : "text-slate-400 group-hover:text-slate-600")} />
                {item.name}
              </div>
              {isActive && <ChevronRight className="w-4 h-4 text-indigo-400" />}
            </button>
          );
        })}
      </nav>

      <div className="p-6 space-y-4">
        <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
          <div className="flex items-center gap-2 mb-2">
            <HelpCircle className="w-4 h-4 text-slate-400" />
            <p className="text-xs font-semibold text-slate-700">Need help?</p>
          </div>
          <p className="text-[11px] text-slate-500 leading-relaxed mb-3">Check our documentation for advanced financial queries.</p>
          <button className="w-full py-2 text-xs font-bold text-indigo-600 bg-white border border-indigo-100 rounded-lg hover:bg-indigo-50 transition-colors">Documentation</button>
        </div>

        <div className="flex items-center gap-3 px-2">
          <div className="relative">
            <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-indigo-600 to-blue-500 flex items-center justify-center text-white font-bold text-sm shadow-md select-none">
              {user ? getInitials(user.full_name) : 'U'}
            </div>
            <div className="absolute -bottom-1 -right-1 w-4 h-4 bg-green-500 border-2 border-white rounded-full animate-pulse" />
          </div>
          <div className="flex-1 min-w-0" title={user?.full_name || ''}>
            <p className="text-sm font-bold text-slate-900 truncate">
              {user ? getNickname(user.full_name) : 'User'}
            </p>
            <p className="text-[10px] font-semibold text-slate-400 uppercase tracking-tighter truncate">
              {user?.role === 'ADMIN' ? 'Administrator' : 'Jury Member'}
            </p>
          </div>
          <button 
            onClick={async () => { await logout(); window.location.hash = '/login'; }}
            title="Log Out"
            className="p-2 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
          >
            <LogOut className="w-4 h-4" />
          </button>
        </div>
      </div>
    </aside>
  );
};

export default Sidebar;
