import React, { useState } from 'react';
import { Settings as SettingsIcon, Save, Key, Cpu, Shield, HelpCircle, Eye, EyeOff } from 'lucide-react';

const Settings: React.FC = () => {
  const [provider, setProvider] = useState<'openai' | 'ollama'>('openai');
  const [apiKey, setApiKey] = useState('');
  const [showKey, setShowKey] = useState(false);
  const [saved, setSaved] = useState(false);

  const handleSave = (e: React.FormEvent) => {
    e.preventDefault();
    setSaved(true);
    setTimeout(() => setSaved(false), 3000);
  };

  return (
    <div className="flex-1 min-h-screen bg-slate-50 flex flex-col p-8 overflow-y-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <SettingsIcon className="w-6 h-6 text-indigo-600" />
          Cấu hình Hệ thống
        </h1>
        <p className="text-sm text-slate-500 mt-1">Quản lý API Key, thiết lập LLM Provider và tùy chọn hệ thống.</p>
      </div>

      <form onSubmit={handleSave} className="max-w-3xl bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden">
        <div className="p-8 space-y-8">
          {/* Section 1: Provider selection */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-800">
              <Cpu className="w-5 h-5 text-indigo-600" />
              <h2 className="text-base font-bold">LLM Provider</h2>
            </div>
            <p className="text-xs text-slate-400">Chọn mô hình ngôn ngữ lớn làm động cơ phân tích báo cáo tài chính.</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <label className={`p-4 rounded-xl border flex flex-col gap-2 cursor-pointer transition-all ${
                provider === 'openai' 
                  ? 'border-indigo-600 bg-indigo-50/30 ring-2 ring-indigo-600/10' 
                  : 'border-slate-200 hover:border-slate-300'
              }`}>
                <input 
                  type="radio" 
                  name="provider" 
                  value="openai" 
                  checked={provider === 'openai'} 
                  onChange={() => setProvider('openai')}
                  className="sr-only" 
                />
                <span className="text-sm font-bold text-slate-800">OpenAI (GPT-4o)</span>
                <span className="text-xs text-slate-500">Mô hình điện toán đám mây cao cấp, chính xác, độ bảo mật cao.</span>
              </label>

              <label className={`p-4 rounded-xl border flex flex-col gap-2 cursor-pointer transition-all ${
                provider === 'ollama' 
                  ? 'border-indigo-600 bg-indigo-50/30 ring-2 ring-indigo-600/10' 
                  : 'border-slate-200 hover:border-slate-300'
              }`}>
                <input 
                  type="radio" 
                  name="provider" 
                  value="ollama" 
                  checked={provider === 'ollama'} 
                  onChange={() => setProvider('ollama')}
                  className="sr-only" 
                />
                <span className="text-sm font-bold text-slate-800">Local (Ollama)</span>
                <span className="text-xs text-slate-500">Chạy offline hoàn toàn trên máy cục bộ, bảo mật dữ liệu tuyệt đối.</span>
              </label>
            </div>
          </div>

          <hr className="border-slate-100" />

          {/* Section 2: API Keys */}
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-slate-800">
              <Key className="w-5 h-5 text-indigo-600" />
              <h2 className="text-base font-bold">API Configuration</h2>
            </div>
            <div className="space-y-2">
              <label className="text-xs font-bold text-slate-500 uppercase tracking-wider block">OpenAI API Key</label>
              <div className="relative">
                <input 
                  type={showKey ? 'text' : 'password'} 
                  placeholder="sk-proj-........................"
                  value={apiKey}
                  onChange={e => setApiKey(e.target.value)}
                  disabled={provider !== 'openai'}
                  className="w-full pl-4 pr-10 py-2.5 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 disabled:opacity-50 disabled:bg-slate-100 transition-all"
                />
                <button 
                  type="button"
                  onClick={() => setShowKey(!showKey)}
                  disabled={provider !== 'openai'}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600 disabled:opacity-30"
                >
                  {showKey ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>
          </div>

          <hr className="border-slate-100" />

          {/* Section 3: Security Policy */}
          <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100 flex gap-3 items-start">
            <Shield className="w-5 h-5 text-indigo-600 shrink-0 mt-0.5" />
            <div>
              <p className="text-xs font-bold text-slate-700">Chính sách Bảo mật Dữ liệu</p>
              <p className="text-[11px] text-slate-500 leading-relaxed mt-1">Hệ thống Lumo AI lưu trữ mã khóa bảo mật của bạn an toàn trong môi trường lưu trữ cục bộ, không bao giờ gửi khóa lên bất kỳ máy chủ trung gian nào.</p>
            </div>
          </div>
        </div>

        {/* Form Footer */}
        <div className="px-8 py-4 bg-slate-50 border-t border-slate-100 flex items-center justify-between">
          <span className="text-xs text-slate-500 flex items-center gap-1">
            <HelpCircle className="w-3.5 h-3.5" /> Cần giúp đỡ trong việc lấy API Key?
          </span>
          <button 
            type="submit"
            className="flex items-center gap-2 px-5 py-2 bg-indigo-600 hover:bg-indigo-700 text-white text-sm font-semibold rounded-xl shadow-lg shadow-indigo-100 transition-all duration-200"
          >
            <Save className="w-4 h-4" />
            {saved ? 'Đã lưu cấu hình!' : 'Lưu cài đặt'}
          </button>
        </div>
      </form>
    </div>
  );
};

export default Settings;
