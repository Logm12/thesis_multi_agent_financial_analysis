import { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  Sparkles, ArrowRight, BrainCircuit, Search, Terminal, Database, 
  Bot, User, Send, Loader2, AlertTriangle, CheckCircle2, Shield, Cpu, Lock
} from 'lucide-react';

interface Message {
  role: 'user' | 'assistant' | 'error';
  content: string;
  chartUrl?: string;
}

type NodeStatus = 'idle' | 'active' | 'completed';

export function LandingPage() {
  const navigate = useNavigate();
  
  // State for Live Demo chat console
  const [input, setInput] = useState('');
  const [messages, setMessages] = useState<Message[]>([
    { 
      role: 'assistant', 
      content: 'Xin chào! Đây là bản Trải nghiệm nhanh của Lumo AI. Tôi đã nạp sẵn Báo cáo Tài chính FPT Online 2025. Bạn có thể đặt câu hỏi về các số liệu tài chính trong tài liệu này (Ví dụ: "Hãy vẽ biểu đồ so sánh Doanh thu và Lợi nhuận qua các năm" hoặc "Tóm tắt tình hình tài chính của FPT").' 
    }
  ]);
  const [isThinking, setIsThinking] = useState(false);
  const [currentNode, setCurrentNode] = useState<string>('');
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  // Track agent nodes visually
  const [nodeStates, setNodeStates] = useState({
    router: 'idle' as NodeStatus,
    retriever: 'idle' as NodeStatus,
    coder: 'idle' as NodeStatus,
    synthesizer: 'idle' as NodeStatus,
  });

  const [sessionToken] = useState(() => {
    let token = localStorage.getItem('demo_session_token');
    if (!token) {
      token = 'sess_' + Math.random().toString(36).substring(2, 15);
      localStorage.setItem('demo_session_token', token);
    }
    return token;
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, currentNode]);

  const resetNodes = () => {
    setNodeStates({
      router: 'idle',
      retriever: 'idle',
      coder: 'idle',
      synthesizer: 'idle'
    });
    setCurrentNode('');
    setErrorMsg(null);
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isThinking) return;

    const userQuery = input;
    setInput('');
    setMessages(prev => [...prev, { role: 'user', content: userQuery }]);
    setIsThinking(true);
    resetNodes();

    // Dynamically resolve backend url based on current frontend host
    const API_URL = import.meta.env.VITE_API_BASE_URL 
      ? import.meta.env.VITE_API_BASE_URL.replace('/api/v1', '') 
      : 'http://localhost:8001';
      
    const url = `${API_URL}/api/v1/demo?message=${encodeURIComponent(userQuery)}&session_id=${sessionToken}`;
    const eventSource = new EventSource(url);

    let assistantResponse = '';
    let currentChart: string | undefined = undefined;

    eventSource.addEventListener('step', (event) => {
      try {
        const data = JSON.parse(event.data);
        const node = data.node;
        setCurrentNode(data.output);
        
        setNodeStates(prev => {
          const next = { ...prev };
          if (node === 'router') {
            next.router = 'active';
          } else if (node === 'retrieve_node') {
            next.router = 'completed';
            next.retriever = 'active';
          } else if (node.includes('coder') || node.includes('execute')) {
            next.router = 'completed';
            next.retriever = 'completed';
            next.coder = 'active';
          } else if (node.includes('synthesizer')) {
            next.router = 'completed';
            next.retriever = 'completed';
            next.coder = 'completed';
            next.synthesizer = 'active';
          }
          return next;
        });
      } catch (err) {
        console.error('Parse step error:', err);
      }
    });

    eventSource.addEventListener('final_answer', (event) => {
      try {
        const data = JSON.parse(event.data);
        assistantResponse = data.content;
        if (data.chart_url) {
          currentChart = `${API_URL}${data.chart_url}`;
        }
      } catch (err) {
        console.error('Parse answer error:', err);
      }
    });

    eventSource.addEventListener('error', (event: any) => {
      let message = 'Vượt quá giới hạn 3 câu hỏi của bản demo! Vui lòng Đăng nhập / Đăng ký tài khoản để sử dụng hệ thống đầy đủ không giới hạn.';
      try {
        if (event.data) {
          const data = JSON.parse(event.data);
          if (data.detail) message = data.detail;
        }
      } catch (e) {}
      
      setErrorMsg(message);
      setMessages(prev => [...prev, { role: 'error', content: message }]);
      setIsThinking(false);
      eventSource.close();
    });

    eventSource.addEventListener('done', () => {
      setNodeStates({
        router: 'completed',
        retriever: 'completed',
        coder: 'completed',
        synthesizer: 'completed'
      });
      
      if (assistantResponse) {
        setMessages(prev => [...prev, { 
          role: 'assistant', 
          content: assistantResponse,
          chartUrl: currentChart 
        }]);
      }
      setIsThinking(false);
      setCurrentNode('');
      eventSource.close();
    });

    eventSource.onerror = () => {
      if (eventSource.readyState === EventSource.CLOSED) return;
      const quotaMsg = 'Bạn đã đạt giới hạn 3 câu hỏi cho phiên khách dùng thử. Vui lòng đăng ký/đăng nhập tài khoản chính thức để tiếp tục trải nghiệm toàn bộ tính năng!';
      setErrorMsg(quotaMsg);
      setMessages(prev => [...prev, { role: 'error', content: quotaMsg }]);
      setIsThinking(false);
      eventSource.close();
    };
  };

  const renderNodeIndicator = (status: NodeStatus, label: string, desc: string, icon: React.ReactNode) => {
    const activeColor = status === 'active' ? 'border-indigo-500 bg-indigo-500/10 text-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.2)]' : 
                        status === 'completed' ? 'border-emerald-500 bg-emerald-500/10 text-emerald-400' : 
                        'border-slate-800 bg-slate-900/40 text-slate-500 opacity-60';
    
    return (
      <div className={`flex gap-4 p-4 rounded-2xl border transition-all duration-300 items-start ${activeColor}`}>
        <div className="mt-0.5 flex items-center justify-center p-2 rounded-xl bg-slate-950 border border-current/20">
          {status === 'active' ? <Loader2 className="w-5 h-5 animate-spin text-indigo-400" /> : icon}
        </div>
        <div className="flex-1 min-w-0 text-left">
          <div className="flex items-center gap-2 justify-between">
            <h4 className="font-bold tracking-wider text-xs uppercase text-slate-100">{label}</h4>
            {status === 'completed' && <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />}
          </div>
          <p className="text-[11px] mt-1 text-slate-400 font-medium line-clamp-1">{desc}</p>
        </div>
      </div>
    );
  };

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100 font-sans antialiased flex flex-col w-full relative overflow-x-hidden selection:bg-indigo-600 selection:text-white">
      {/* Background Decorative Grids and Glowing Blobs */}
      <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_top,_var(--tw-gradient-stops))] from-indigo-950/30 via-slate-950 to-slate-950 -z-10" />
      <div className="absolute top-[-10%] left-[-10%] w-[50vw] h-[50vw] rounded-full bg-indigo-600/5 blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50vw] h-[50vw] rounded-full bg-blue-600/5 blur-[120px] pointer-events-none" />
      <div className="absolute inset-0 bg-[linear-gradient(to_right,#0f172a_1px,transparent_1px),linear-gradient(to_bottom,#0f172a_1px,transparent_1px)] bg-[size:4rem_4rem] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_0%,#000_70%,transparent_100%)] opacity-30 pointer-events-none" />

      {/* Header / Navbar */}
      <nav className="sticky top-0 z-50 w-full border-b border-slate-900 bg-slate-950/80 backdrop-blur-md">
        <div className="max-w-7xl mx-auto flex h-16 items-center justify-between px-6 md:px-8">
          <div className="flex items-center gap-3 font-bold tracking-tight text-white select-none">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-indigo-600 shadow-lg shadow-indigo-500/20">
              <Sparkles className="h-5 w-5 text-white" />
            </div>
            <span className="text-xl font-extrabold tracking-tight">Lumo <span className="text-indigo-500">AI</span></span>
          </div>

          <div className="flex items-center gap-6">
            <button 
              onClick={() => navigate('/login')}
              className="flex items-center gap-2 px-5 py-2 rounded-xl bg-indigo-600 hover:bg-indigo-500 text-white text-xs font-bold uppercase tracking-wider transition-all shadow-lg shadow-indigo-600/10 hover:shadow-indigo-600/20 active:scale-95"
            >
              Đăng nhập / Đăng ký
            </button>
          </div>
        </div>
      </nav>

      {/* Main Canvas */}
      <main className="flex-1 w-full max-w-7xl mx-auto px-6 md:px-8 flex flex-col items-center">
        
        {/* HERO SECTION */}
        <section className="pt-20 pb-16 md:pt-28 md:pb-20 text-center max-w-4xl flex flex-col items-center relative">
          <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full border border-indigo-500/30 bg-indigo-500/10 text-indigo-400 text-xs font-bold tracking-wider mb-6 backdrop-blur-md">
            <Sparkles className="w-4 h-4" />
            <span>HỘI ĐỒNG GS & CHUYÊN GIA ĐÁNH GIÁ CAO</span>
          </div>

          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold tracking-tight text-transparent bg-clip-text bg-gradient-to-b from-white via-slate-100 to-slate-400 mb-6 leading-[1.15]">
            Phân Tích Báo Cáo Tài Chính<br />
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-indigo-400 to-blue-400">Bằng Đa Tác Nhân Thông Minh</span>
          </h1>

          <p className="text-slate-400 text-base md:text-lg max-w-2xl mb-8 leading-relaxed font-medium">
            Hệ thống SaaS chuyên biệt phục vụ phân tích tự động, trích xuất thực thể tài chính bảo mật tuyệt đối thông qua mô hình LangGraph và hệ thống offline localized LLMs.
          </p>

          <div className="flex gap-4 flex-col sm:flex-row items-center justify-center">
            <button
              onClick={() => navigate('/login')}
              className="px-8 py-4 h-auto text-sm font-bold uppercase tracking-wider bg-indigo-600 hover:bg-indigo-500 text-white rounded-xl transition-all duration-300 shadow-[0_0_20px_rgba(79,70,229,0.3)] hover:shadow-[0_0_35px_rgba(79,70,229,0.5)] hover:scale-[1.03] active:scale-[0.98] group flex gap-2.5 items-center"
            >
              <span>Vào Trang Phân Tích</span>
              <ArrowRight className="w-4 h-4 group-hover:translate-x-1 transition-transform" />
            </button>
            
            <a
              href="#demo-live"
              className="px-6 py-4 rounded-xl border border-slate-800 hover:border-slate-700 bg-slate-900/40 hover:bg-slate-900/60 transition-all font-bold text-xs uppercase tracking-wider"
            >
              Xem Live Demo
            </a>
          </div>
        </section>

        {/* SECURITY & USP BENEFITS GRID */}
        <section className="py-20 w-full border-t border-slate-900">
          <div className="text-center mb-16">
            <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight mb-4">
              Nền Tảng Công Nghệ Đi Đầu
            </h2>
            <p className="text-slate-400 text-sm max-w-xl mx-auto">
              Được thiết kế để giải quyết những bài toán phức tạp nhất về bảo mật dữ liệu doanh nghiệp và độ chính xác tài chính.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            <div className="p-8 rounded-3xl border border-slate-900 bg-slate-950/40 hover:bg-slate-900/20 transition-all duration-300 hover:border-slate-800 flex flex-col gap-4 text-left">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 text-indigo-400">
                <Lock className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-100 mt-2">Bảo Mật Tenant Isolation</h3>
              <p className="text-slate-400 text-xs leading-relaxed font-medium">
                Sử dụng UUIDv4 và Row-Level Security (RLS) cứng ở tầng API giúp cách ly hoàn toàn dữ liệu tài chính giữa các tài khoản doanh nghiệp.
              </p>
            </div>

            <div className="p-8 rounded-3xl border border-slate-900 bg-slate-950/40 hover:bg-slate-900/20 transition-all duration-300 hover:border-slate-800 flex flex-col gap-4 text-left">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 text-indigo-400">
                <BrainCircuit className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-100 mt-2">Quy Trình Đa Tác Nhân (LangGraph)</h3>
              <p className="text-slate-400 text-xs leading-relaxed font-medium">
                Tự động hóa luồng nghiệp vụ qua mô hình lập kế hoạch, truy hồi thông minh (Retriever), tự sinh mã lập trình trực quan hóa (Coder) và tổng hợp đáp án.
              </p>
            </div>

            <div className="p-8 rounded-3xl border border-slate-900 bg-slate-950/40 hover:bg-slate-900/20 transition-all duration-300 hover:border-slate-800 flex flex-col gap-4 text-left">
              <div className="w-12 h-12 rounded-2xl bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 text-indigo-400">
                <Cpu className="w-6 h-6" />
              </div>
              <h3 className="text-lg font-bold text-slate-100 mt-2">Local LLM Offline Pipeline</h3>
              <p className="text-slate-400 text-xs leading-relaxed font-medium">
                Cho phép chạy độc lập ngoại tuyến trên server nội bộ, không phụ thuộc internet và triệt tiêu hoàn toàn khả năng rò rỉ thông tin mật.
              </p>
            </div>
          </div>
        </section>

        {/* LIVE DEMO TRACE SECTION */}
        <section id="demo-live" className="py-20 w-full border-t border-slate-900 text-center">
          <div className="mb-12">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-bold uppercase tracking-wider mb-4">
              <BrainCircuit className="w-3.5 h-3.5 animate-pulse" />
              <span>Theo Dõi Thực Thi Tác Nhân (Live Trace)</span>
            </div>
            <h2 className="text-2xl md:text-3xl font-extrabold tracking-tight mb-3">
              Trải Nghiệm Khách Sử Dụng Thử
            </h2>
            <p className="text-slate-400 text-sm max-w-xl mx-auto">
              Nhập câu hỏi tài chính và theo dõi cách hệ thống đa tác nhân lập kế hoạch, tìm kiếm dữ liệu, sinh code biểu đồ và xuất kết quả.
            </p>
          </div>

          {/* Console layout */}
          <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 w-full min-h-[550px] relative">
            
            {/* Interactive Chat Console (7 columns) */}
            <div className="lg:col-span-7 bg-slate-900/40 backdrop-blur-xl rounded-3xl border border-slate-800/80 shadow-2xl flex flex-col overflow-hidden h-[550px] relative">
              
              {/* Terminal Head */}
              <div className="border-b border-slate-800 p-4 bg-slate-950/60 flex items-center justify-between">
                <div className="flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-rose-500/80" />
                  <div className="w-3 h-3 rounded-full bg-amber-500/80" />
                  <div className="w-3 h-3 rounded-full bg-emerald-500/80" />
                  <span className="text-xs font-mono font-bold tracking-wider ml-2 text-slate-500 uppercase">
                    guest_api_v1_demo
                  </span>
                </div>
                <div className="text-[10px] bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-bold uppercase tracking-wider px-2.5 py-1 rounded-md">
                  Giới hạn: 3 câu hỏi
                </div>
              </div>

              {/* Chat Message Box */}
              <div className="flex-1 overflow-y-auto p-6 space-y-6 scrollbar-thin scrollbar-thumb-slate-800 scrollbar-track-transparent">
                {messages.map((msg, idx) => (
                  <div
                    key={idx}
                    className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {msg.role !== 'user' && (
                      <div className={`w-9 h-9 rounded-full flex items-center justify-center border flex-shrink-0 shadow-md ${msg.role === 'error' ? 'bg-rose-500/10 border-rose-500/20 text-rose-400' : 'bg-indigo-500/10 border-indigo-500/20 text-indigo-400'}`}>
                        {msg.role === 'error' ? <AlertTriangle className="w-4 h-4" /> : <Bot className="w-5 h-5" />}
                      </div>
                    )}

                    <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-xs leading-relaxed text-left shadow-sm ${
                      msg.role === 'user' 
                        ? 'bg-indigo-600 text-white rounded-tr-none' 
                        : msg.role === 'error'
                        ? 'bg-rose-950/20 border border-rose-800/40 text-rose-300 rounded-tl-none font-medium'
                        : 'bg-slate-900/60 border border-slate-800 text-slate-200 rounded-tl-none font-medium'
                    }`}>
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                      {msg.chartUrl && (
                        <div className="mt-4 rounded-xl overflow-hidden border border-slate-800 bg-slate-950 p-2 shadow-inner">
                          <img src={msg.chartUrl} alt="Chart generated by Python Coder Agent" className="w-full h-auto object-contain" />
                        </div>
                      )}
                    </div>

                    {msg.role === 'user' && (
                      <div className="w-9 h-9 rounded-full bg-indigo-600 flex items-center justify-center border border-indigo-500 text-white flex-shrink-0 shadow-md">
                        <User className="w-5 h-5" />
                      </div>
                    )}
                  </div>
                ))}
                
                {isThinking && !currentNode && (
                  <div className="flex gap-4 justify-start">
                    <div className="w-9 h-9 rounded-full bg-indigo-500/10 flex items-center justify-center border border-indigo-500/20 text-indigo-400 animate-pulse">
                      <Bot className="w-5 h-5" />
                    </div>
                    <div className="bg-slate-900/60 border border-slate-800 px-4 py-3 rounded-2xl rounded-tl-none flex items-center gap-3">
                      <Loader2 className="w-4 h-4 animate-spin text-indigo-400" />
                      <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">
                        Đang suy nghĩ...
                      </span>
                    </div>
                  </div>
                )}

                <div ref={messagesEndRef} />
              </div>

              {/* Trace Line */}
              {currentNode && (
                <div className="px-6 py-2.5 bg-indigo-950/20 border-t border-slate-800 flex items-center gap-3 text-indigo-400 font-mono text-[10px] text-left">
                  <Terminal className="w-4 h-4 animate-pulse flex-shrink-0" />
                  <span className="font-bold uppercase tracking-wider">Trace:</span>
                  <span className="truncate italic font-sans font-semibold text-slate-300">{currentNode}</span>
                </div>
              )}

              {/* Input form */}
              <div className="border-t border-slate-800 p-4 bg-slate-950/20">
                <form onSubmit={handleSend} className="relative flex gap-3 items-center">
                  <input 
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    disabled={isThinking}
                    placeholder="Đặt câu hỏi tài chính (ví dụ: So sánh doanh thu FPT qua các năm)..."
                    className="flex-1 h-12 rounded-xl bg-slate-950 border border-slate-800 focus:border-indigo-500 focus:ring-0 px-4 pr-12 text-xs transition-all duration-300 focus:outline-none outline-none font-medium placeholder:text-slate-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  />
                  <button
                    type="submit"
                    disabled={isThinking || !input.trim()}
                    className="absolute right-2 top-1/2 -translate-y-1/2 w-9 h-9 rounded-lg flex items-center justify-center bg-indigo-600 text-white hover:scale-105 hover:bg-indigo-500 disabled:opacity-40 disabled:scale-100 disabled:cursor-not-allowed transition-all duration-300 shadow-md"
                  >
                    {isThinking ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                  </button>
                </form>
              </div>
            </div>

            {/* Node Visualizer (5 columns) */}
            <div className="lg:col-span-5 flex flex-col space-y-4 justify-between h-full">
              <div className="bg-slate-900/40 backdrop-blur-xl rounded-3xl border border-slate-800/80 p-6 shadow-xl flex-1 flex flex-col gap-4 relative overflow-hidden text-left">
                
                {/* Visualizer Link Connector Line */}
                <div className="absolute left-[2.35rem] top-20 bottom-10 w-0.5 bg-gradient-to-b from-indigo-500/20 via-indigo-500 to-emerald-500/20 z-0 hidden sm:block pointer-events-none" />
                
                <div className="z-10 relative">
                  <h3 className="text-base font-bold tracking-wide mb-1 flex items-center gap-2 text-slate-100">
                    <BrainCircuit className="w-5 h-5 text-indigo-400" />
                    Agent Trace Monitor
                  </h3>
                  <p className="text-[10px] font-semibold text-slate-500 uppercase tracking-widest">
                    Theo dõi trực quan thời gian thực các trạm Agent
                  </p>
                </div>

                <div className="flex-1 flex flex-col gap-4 justify-center z-10 relative">
                  {renderNodeIndicator(
                    nodeStates.router,
                    "1. Planner Router",
                    "Định tuyến yêu cầu tài chính dựa trên mục tiêu truy vấn",
                    <BrainCircuit className="w-5 h-5" />
                  )}

                  {renderNodeIndicator(
                    nodeStates.retriever,
                    "2. Smart Retriever",
                    "Truy xuất ngữ cảnh chính xác từ Vector DB (ChromaDB)",
                    <Search className="w-5 h-5" />
                  )}

                  {renderNodeIndicator(
                    nodeStates.coder,
                    "3. Python Coder",
                    "Sinh code Python và thực thi bóc tách dữ liệu thành biểu đồ",
                    <Terminal className="w-5 h-5" />
                  )}

                  {renderNodeIndicator(
                    nodeStates.synthesizer,
                    "4. Synthesizer",
                    "Tổng hợp dữ liệu bóc tách và phản hồi đáp án tài chính",
                    <Database className="w-5 h-5" />
                  )}
                </div>
              </div>
            </div>

          </div>
        </section>

      </main>

      {/* Footer */}
      <footer className="border-t border-slate-900 bg-slate-950 py-8 text-center text-slate-500 text-xs font-semibold uppercase tracking-widest">
        <div>© 2026 Lumo AI Financial Analyzer. All Rights Reserved.</div>
      </footer>
    </div>
  );
}
