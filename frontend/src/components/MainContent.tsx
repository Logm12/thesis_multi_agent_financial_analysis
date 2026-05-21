import { useState, useRef, useEffect, useCallback } from 'react';
import { Sparkles, Upload, Send, Loader2, FileText } from 'lucide-react';
import { useDropzone } from 'react-dropzone';
import { useChatStore } from '../store/useChatStore';
import MessageBubble from './MessageBubble';
import apiClient from '../api/client';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const MainContent = () => {
  const { messages, addMessage, updateMessage, isProcessing, setProcessing, isLoading, setLoading } = useChatStore();
  const [inputValue, setInputValue] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [messages, isLoading, isProcessing]);

  const pollStatus = (taskId: string | undefined, messageId: string) => {
    if (!taskId || taskId === 'undefined') {
      console.error('[Polling] Aborting: Invalid taskId', taskId);
      updateMessage(messageId, {
        text: 'Lỗi: Không nhận được mã tiến trình hợp lệ từ máy chủ.',
        isSystem: false,
        isError: true
      });
      setProcessing(false);
      return;
    }

    let attempts = 0;
    const maxAttempts = 30; // 60 seconds (30 * 2000ms)

    const interval = setInterval(async () => {
      attempts++;
      if (attempts > maxAttempts) {
        clearInterval(interval);
        updateMessage(messageId, {
          text: 'Quá thời gian xử lý tài liệu. Vui lòng kiểm tra lại trạng thái ở Knowledge Base.',
          isSystem: false,
          isError: true
        });
        setProcessing(false);
        return;
      }

      try {
        const response = await apiClient.get(`/status/${taskId}`);
        const { status, details } = response.data || {};

        if (status === 'completed') {
          clearInterval(interval);
          updateMessage(messageId, {
            text: details || 'Tài liệu đã được xử lý và đánh chỉ mục thành công.',
            isSystem: false,
            hasChart: false
          });
          setProcessing(false);
        } else if (status === 'failed') {
          clearInterval(interval);
          updateMessage(messageId, {
            text: `Xin lỗi, quá trình xử lý tài liệu đã thất bại: ${details || 'Lỗi không xác định'}`,
            isSystem: false,
            isError: true
          });
          setProcessing(false);
        }
      } catch (error) {
        console.error('Polling error:', error);
        // Do not fail immediately on transient network error, wait for retries
      }
    }, 2000);
  };

  const uploadFile = async (file: File) => {
    // Validate file extension and MIME type
    const isPdf = file.name.toLowerCase().endsWith('.pdf') && (file.type === 'application/pdf' || file.type === '');
    if (!isPdf) {
      addMessage({
        text: 'File không hợp lệ. Vui lòng chỉ tải lên báo cáo định dạng PDF.',
        isUser: false,
        isSystem: true,
        isError: true
      });
      return;
    }

    // Validate file size (< 100MB)
    const MAX_SIZE = 100 * 1024 * 1024; // 100MB in bytes
    if (file.size > MAX_SIZE) {
      addMessage({
        text: 'Kích thước file quá lớn. Vui lòng tải lên file nhỏ hơn 100MB.',
        isUser: false,
        isSystem: true,
        isError: true
      });
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    const messageId = addMessage({
      text: `Đang phân tích tài liệu: ${file.name}...`,
      isUser: false,
      isSystem: true
    });

    setProcessing(true);

    try {
      const response = await apiClient.post('/upload-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      pollStatus(response.data.task_id, messageId);
    } catch (error) {
      updateMessage(messageId, {
        text: 'Lỗi khi tải tài liệu lên. Vui lòng thử lại.',
        isSystem: false,
        isError: true
      });
      setProcessing(false);
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      uploadFile(acceptedFiles[0]);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false,
    noClick: true // We want to use the specific upload button or dragging
  });

  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading) return;

    const userText = inputValue;
    setInputValue('');
    addMessage({ text: userText, isUser: true });

    setLoading(true);
    const aiMessageId = addMessage({ text: '', isUser: false, isSystem: true, steps: ['Khởi tạo luồng suy nghĩ...'] });

    const sseBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1').replace('/api/v1', '');
    const url = `${sseBaseUrl}/chat-stream?message=${encodeURIComponent(userText)}&thread_id=default`;

    const eventSource = new EventSource(url, { withCredentials: true });
    let steps: string[] = ['Khởi tạo luồng suy nghĩ...'];

    eventSource.addEventListener('step', (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.output) {
          // Prevent exact duplicate consecutive steps
          if (steps[steps.length - 1] !== data.output) {
            steps = [...steps, data.output];
          }
          updateMessage(aiMessageId, {
            text: '',
            isSystem: true,
            steps: steps
          });
        }
      } catch (e) {
        console.error('Error parsing step event:', e);
      }
    });

    eventSource.addEventListener('final_answer', (event) => {
      try {
        const data = JSON.parse(event.data);
        if (data.content) {
          updateMessage(aiMessageId, {
            text: data.content,
            isSystem: false,
            steps: steps,
            chartImageUrl: data.chart_url // Assign validated chart asset URL
          });
        }
      } catch (e) {
        console.error('Error parsing final_answer event:', e);
      }
    });

    eventSource.addEventListener('done', () => {
      eventSource.close();
      setLoading(false);
    });

    eventSource.addEventListener('error', (event) => {
      console.error('SSE Error:', event);
      eventSource.close();
      updateMessage(aiMessageId, {
        text: 'Xin lỗi, tôi gặp lỗi khi kết nối luồng với máy chủ.',
        isSystem: false,
        isError: true
      });
      setLoading(false);
    });
  };

  return (
    <main 
      {...getRootProps()}
      className={cn(
        "flex-1 h-screen flex flex-col bg-slate-50 transition-all duration-300 relative",
        isDragActive && "bg-indigo-50/50 ring-2 ring-indigo-500 ring-inset"
      )}
    >
      <input {...getInputProps()} />
      
      {/* Header */}
      <header className="h-16 border-b border-slate-200 bg-white/90 backdrop-blur-md flex items-center justify-between px-8 sticky top-0 z-10 shadow-sm">
        <div className="flex items-center gap-2.5">
          <div className="relative">
            <Sparkles className="w-5 h-5 text-indigo-600" />
            <span className="absolute -top-0.5 -right-0.5 w-2 h-2 bg-emerald-400 rounded-full border border-white" />
          </div>
          <div>
            <h2 className="font-bold text-slate-900 tracking-tight text-[15px] leading-none">Financial Intelligence Agent</h2>
            <p className="text-[10px] text-emerald-600 font-semibold uppercase tracking-widest mt-0.5">Multi-Agent Online</p>
          </div>
        </div>
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-1.5 text-[11px] font-semibold text-slate-400 bg-slate-50 border border-slate-200 rounded-full px-3 py-1.5">
            <span className="w-1.5 h-1.5 bg-emerald-400 rounded-full animate-pulse" />
            LangGraph Active
          </div>
          <button className="text-xs font-bold text-indigo-600 hover:text-indigo-700 bg-indigo-50 hover:bg-indigo-100 border border-indigo-100 px-3 py-1.5 rounded-full transition-all">Share</button>
        </div>
      </header>

      {/* Chat Area */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto p-8 pb-32 space-y-2"
      >
        {messages.length === 0 ? (
          <div className="h-full flex flex-col items-center justify-center text-center max-w-2xl mx-auto space-y-6">
            <div className="w-20 h-20 bg-indigo-100 rounded-3xl flex items-center justify-center mb-4 shadow-sm">
              <Sparkles className="w-10 h-10 text-indigo-600" />
            </div>
            <h1 className="text-4xl font-bold text-slate-900 tracking-tight">
              Phân tích báo cáo tài chính <span className="text-indigo-600">thế hệ mới</span>
            </h1>
            <p className="text-slate-500 text-lg leading-relaxed">
              Tải lên báo cáo tài chính (PDF) để bắt đầu phân tích dữ liệu chuyên sâu, 
              tự động trích xuất biểu đồ và nhận định từ AI.
            </p>
            
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 w-full mt-8">
              {/* Upload card */}
              <div className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:border-indigo-200 transition-all text-left group cursor-default">
                <div className="w-10 h-10 bg-indigo-50 rounded-xl flex items-center justify-center mb-4 group-hover:bg-indigo-100 transition-colors border border-indigo-100">
                  <FileText className="w-5 h-5 text-indigo-600" />
                </div>
                <h3 className="font-bold text-slate-800 mb-1.5 tracking-tight">Tải lên BCTC</h3>
                <p className="text-xs text-slate-500 leading-relaxed">Kéo thả hoặc nhấn biểu tượng upload để bắt đầu phân tích tài liệu PDF.</p>
              </div>
              {/* Chat card */}
              <div className="p-6 bg-white border border-slate-200 rounded-2xl shadow-sm hover:shadow-md hover:border-emerald-200 transition-all text-left group cursor-default">
                <div className="w-10 h-10 bg-emerald-50 rounded-xl flex items-center justify-center mb-4 group-hover:bg-emerald-100 transition-colors border border-emerald-100">
                  <Sparkles className="w-5 h-5 text-emerald-600" />
                </div>
                <h3 className="font-bold text-slate-800 mb-1.5 tracking-tight">Phân tích với AI</h3>
                <p className="text-xs text-slate-500 leading-relaxed">Đặt câu hỏi tài chính và nhận phân tích chuyên sâu với biểu đồ tự động.</p>
              </div>
            </div>
          </div>
        ) : (
          <div className="max-w-4xl mx-auto w-full">
            {messages.map((msg) => (
              <MessageBubble key={msg.id} message={msg} />
            ))}
            {isDragActive && (
              <div className="fixed inset-0 z-50 bg-indigo-600/10 backdrop-blur-[2px] flex items-center justify-center pointer-events-none">
                <div className="bg-white p-8 rounded-3xl shadow-2xl border-2 border-indigo-500 flex flex-col items-center space-y-4 animate-in zoom-in-95 duration-300">
                  <div className="w-16 h-16 bg-indigo-100 rounded-full flex items-center justify-center animate-bounce">
                    <Upload className="w-8 h-8 text-indigo-600" />
                  </div>
                  <p className="text-lg font-semibold text-slate-900">Thả tệp vào đây để tải lên</p>
                  <p className="text-sm text-slate-500">Hỗ trợ định dạng PDF</p>
                </div>
              </div>
            )}
          </div>
        )}
      </div>

      {/* Input Area - FIXED at bottom */}
      <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-slate-50 via-slate-50 to-transparent pt-12">
        <div className="max-w-4xl mx-auto">
          <div className="relative group">
            <div className="absolute inset-0 bg-indigo-500/5 rounded-2xl blur-xl group-focus-within:bg-indigo-500/10 transition-all" />
            <div className="relative flex items-center bg-white border border-slate-200 rounded-2xl shadow-sm focus-within:border-indigo-500 focus-within:ring-4 focus-within:ring-indigo-500/10 transition-all overflow-hidden">
              <button 
                onClick={() => document.getElementById('file-upload')?.click()}
                className="p-4 text-slate-400 hover:text-indigo-600 transition-colors border-r border-slate-100"
              >
                <Upload className="w-5 h-5" />
              </button>
              <input 
                id="file-upload" 
                type="file" 
                className="hidden" 
                accept=".pdf" 
                onChange={(e) => e.target.files?.[0] && uploadFile(e.target.files[0])}
              />
              <input
                type="text"
                placeholder="Hỏi AI về báo cáo tài chính của bạn..."
                className="flex-1 py-4 px-2 text-sm focus:outline-none text-slate-700 bg-transparent"
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
              />
              <button 
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading}
                className={cn(
                  "m-2 p-2.5 rounded-xl transition-all",
                  inputValue.trim() && !isLoading 
                    ? "bg-indigo-600 text-white shadow-md shadow-indigo-200 hover:bg-indigo-700" 
                    : "bg-slate-100 text-slate-400 cursor-not-allowed"
                )}
              >
                {isLoading ? <Loader2 className="w-5 h-5 animate-spin" /> : <Send className="w-5 h-5" />}
              </button>
            </div>
          </div>
          <p className="mt-3 text-center text-[11px] text-slate-400 font-medium">
            AI có thể đưa ra câu trả lời sai sót. Hãy kiểm tra lại các thông tin quan trọng.
          </p>
        </div>
      </div>
    </main>
  );
};

export default MainContent;
