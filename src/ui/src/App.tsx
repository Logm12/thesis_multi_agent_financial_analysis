import React, { useState, useRef } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import { 
  Plus, 
  MessageSquare, 
  Settings, 
  LogOut, 
  Send, 
  MoreVertical,
  ThumbsUp,
  ThumbsDown,
  RotateCcw,
  Menu,
  Sparkles,
  LayoutGrid,
  Mic,
  LogIn
} from 'lucide-react';
import { Toaster, toast } from 'react-hot-toast';
import axios from 'axios';
import { useChat } from './hooks/useChat';
import './styles/globals.css';

function App() {
  const { messages, sendMessage, isLoading, currentStep } = useChat();
  const [input, setInput] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isLoggedIn, setIsLoggedIn] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSend = () => {
    if (input.trim() && !isLoading) {
      sendMessage(input);
      setInput('');
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const formData = new FormData();
    formData.append('file', file);

    setIsUploading(true);
    const toastId = toast.loading(`Đang nạp dữ liệu: ${file.name}...`);

    try {
      await axios.post('http://localhost:8001/upload', formData);
      toast.success('Đã nạp dữ liệu thành công!', { id: toastId });
    } catch (error) {
      toast.error('Lỗi khi tải file.', { id: toastId });
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) fileInputRef.current.value = '';
    }
  };

  return (
    <div className="app-container" style={{ backgroundColor: '#ffffff' }}>
      <Toaster position="top-right" />
      
      {/* Sidebar - Gemini Style */}
      <aside className="sidebar">
        <div style={{ padding: '8px', marginBottom: '20px' }}>
          <Menu size={24} style={{ cursor: 'pointer', color: '#444746' }} />
        </div>
        
        <div className="nav-item active" onClick={() => window.location.reload()} style={{ backgroundColor: '#dde3ea', marginBottom: '24px' }}>
          <Plus size={20} />
          <span>Cuộc trò chuyện mới</span>
        </div>

        <div className="history-section">
          <div className="nav-item">
            <MessageSquare size={18} />
            <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>Báo cáo tài chính FPT 2023</span>
          </div>
          <div className="nav-item">
            <MessageSquare size={18} />
            <span>Phân tích nợ vay Vingroup</span>
          </div>
        </div>

        <div className="sidebar-footer" style={{ marginTop: 'auto', borderTop: 'none' }}>
          <div className="nav-item">
            <Settings size={20} />
            <span>Cài đặt và trợ giúp</span>
          </div>
          
          {isLoggedIn ? (
            <div className="nav-item" onClick={() => setIsLoggedIn(false)}>
              <div style={{ width: '24px', height: '24px', borderRadius: '50%', backgroundColor: '#ff4d4f', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '12px', fontWeight: 700 }}>L</div>
              <span>Đăng xuất (Long)</span>
              <LogOut size={16} style={{ marginLeft: 'auto' }} />
            </div>
          ) : (
            <div className="nav-item" onClick={() => { setIsLoggedIn(true); toast.success('Đã đăng nhập thành công!'); }}>
              <LogIn size={20} />
              <span>Đăng nhập</span>
            </div>
          )}
        </div>
      </aside>

      {/* Main Chat Area */}
      <main className="chat-area" style={{ backgroundColor: '#ffffff' }}>
        <header style={{ display: 'flex', justifyContent: 'space-between', padding: '16px 24px', alignItems: 'center' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <span style={{ fontSize: '18px', fontWeight: 500, color: '#444746' }}>Gemini</span>
            <MoreVertical size={16} color="#444746" />
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
            <button style={{ padding: '6px 12px', borderRadius: '8px', border: '1px solid #c4c7c5', background: 'none', fontSize: '14px', display: 'flex', alignItems: 'center', gap: '8px' }}>
              <Sparkles size={14} color="#5d5fef" />
              Dùng thử Gemini Advanced
            </button>
            <LayoutGrid size={20} color="#444746" />
            <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: '#5d5fef', color: 'white', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 700 }}>L</div>
          </div>
        </header>

        <div className="messages-list" style={{ padding: '20px 20%' }}>
          {messages.length === 0 && (
            <div style={{ marginTop: '10vh' }}>
              <h1 style={{ fontSize: '56px', fontWeight: 500, background: 'linear-gradient(90deg, #4285f4, #9b72cb, #d96570)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', marginBottom: '8px' }}>
                Xin chào Long!
              </h1>
              <h1 style={{ fontSize: '56px', fontWeight: 500, color: '#c4c7c5' }}>
                Hôm nay có gì mới?
              </h1>
            </div>
          )}

          {messages.map((msg, i) => (
            <div key={i} style={{ display: 'flex', gap: '16px', marginBottom: '32px' }}>
              <div style={{ width: '32px', height: '32px', borderRadius: '50%', backgroundColor: msg.role === 'user' ? '#5d5fef' : '#f0f4f9', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                {msg.role === 'user' ? <span style={{ color: 'white', fontSize: '14px', fontWeight: 700 }}>L</span> : <Sparkles size={18} color="#4285f4" />}
              </div>
              <div className="prose" style={{ flex: 1, color: '#1f1f1f', fontSize: '16px' }}>
                {msg.content ? (
                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                ) : (
                  <div style={{ fontStyle: 'italic', color: '#444746' }}>
                    {currentStep || "Đang xử lý..."}
                  </div>
                )}
                {msg.role === 'assistant' && msg.content && (
                  <div style={{ display: 'flex', gap: '16px', marginTop: '24px', color: '#444746' }}>
                    <ThumbsUp size={18} style={{ cursor: 'pointer' }} />
                    <ThumbsDown size={18} style={{ cursor: 'pointer' }} />
                    <Sparkles size={18} style={{ cursor: 'pointer' }} />
                    <RotateCcw size={18} style={{ cursor: 'pointer', marginLeft: 'auto' }} />
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>

        {/* Floating Input Box - Gemini Style */}
        <div className="input-container" style={{ padding: '0 20% 32px' }}>
          <div className="pill-input-wrapper">
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{ display: 'none' }} 
              accept=".pdf"
              onChange={handleFileUpload}
            />
            <textarea 
              style={{ flex: 1, border: 'none', background: 'none', outline: 'none', fontSize: '16px', color: '#1f1f1f', resize: 'none', padding: '0' }}
              placeholder="Nhập câu hỏi tại đây"
              rows={3}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  handleSend();
                }
              }}
            />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 'auto', width: '100%' }}>
              <div style={{ display: 'flex', gap: '8px' }}>
                <button className="action-btn" onClick={() => fileInputRef.current?.click()} disabled={isUploading}>
                  <Plus size={20} color="#444746" />
                </button>
                <button className="action-btn"><Sparkles size={20} color="#444746" /></button>
              </div>
              <div style={{ display: 'flex', gap: '8px', alignItems: 'center' }}>
                <span style={{ fontSize: '12px', color: '#444746', marginRight: '8px' }}>Tiếng Việt</span>
                <Mic size={20} color="#444746" style={{ cursor: 'pointer' }} />
                <button 
                  className={`action-btn ${input.trim() ? 'send-btn-active' : ''}`}
                  onClick={handleSend}
                  disabled={isLoading || !input.trim()}
                  style={{ backgroundColor: input.trim() ? '#dde3ea' : 'transparent', borderRadius: '8px' }}
                >
                  <Send size={20} color={input.trim() ? '#1f1f1f' : '#c4c7c5'} />
                </button>
              </div>
            </div>
          </div>
          <p style={{ textAlign: 'center', fontSize: '12px', color: '#444746', marginTop: '16px' }}>
            Gemini có thể đưa ra thông tin không chính xác, kể cả về con người, vì vậy hãy kiểm tra lại các phản hồi của Gemini. <a href="#" style={{ color: '#444746', textDecoration: 'underline' }}>Quyền riêng tư của bạn và các Ứng dụng Gemini</a>
          </p>
        </div>
      </main>
    </div>
  );
}

export default App;
