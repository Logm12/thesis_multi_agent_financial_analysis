import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useTranslation } from "react-i18next";
import { 
  Bot, User, Send, Loader2, AlertTriangle, 
  CheckCircle2, Terminal, BrainCircuit, Database, Search 
} from "lucide-react";
import { useAuth } from "../../lib/auth-context";

// Cấu hình backend URL linh hoạt
const API_BASE = "http://localhost:8001";

interface Message {
  role: "user" | "assistant" | "error";
  content: string;
  chartUrl?: string;
}

type NodeStatus = "idle" | "active" | "completed";

export function VisualizerSection() {
  const { t } = useTranslation();
  const { sessionToken } = useAuth();
  
  const [input, setInput] = useState("");
  const [messages, setMessages] = useState<Message[]>([
    { 
      role: "assistant", 
      content: "Xin chào! Đây là bản Demo của Lumo AI. Tôi đã nạp sẵn Báo cáo Tài chính FPT Online 2025. Bạn có thể hỏi tôi về các số liệu tài chính trong tài liệu này." 
    }
  ]);
  const [isThinking, setIsThinking] = useState(false);
  const [currentNode, setCurrentNode] = useState<string>("");
  const [errorMsg, setErrorMsg] = useState<string | null>(null);
  
  // Mapped node states for visualizer tracking
  const [nodeStates, setNodeStates] = useState({
    router: "idle" as NodeStatus,
    retriever: "idle" as NodeStatus,
    coder: "idle" as NodeStatus,
    synthesizer: "idle" as NodeStatus,
  });

  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, currentNode]);

  const resetNodes = () => {
    setNodeStates({
      router: "idle",
      retriever: "idle",
      coder: "idle",
      synthesizer: "idle"
    });
    setCurrentNode("");
    setErrorMsg(null);
  };

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isThinking) return;

    const userQuery = input;
    setInput("");
    setMessages(prev => [...prev, { role: "user", content: userQuery }]);
    setIsThinking(true);
    resetNodes();

    // Cấu hình SSE EventSource
    const url = `${API_BASE}/api/v1/demo?message=${encodeURIComponent(userQuery)}&session_id=${sessionToken}`;
    const eventSource = new EventSource(url);

    let assistantResponse = "";
    let currentChart: string | undefined = undefined;

    eventSource.addEventListener("step", (event) => {
      try {
        const data = JSON.parse(event.data);
        const node = data.node;
        setCurrentNode(data.output);
        
        // Cập nhật trạng thái graph trực quan
        setNodeStates(prev => {
          const next = { ...prev };
          if (node === "router") {
            next.router = "active";
          } else if (node === "retrieve_node") {
            next.router = "completed";
            next.retriever = "active";
          } else if (node.includes("coder") || node.includes("execute")) {
            next.router = "completed";
            next.retriever = "completed";
            next.coder = "active";
          } else if (node.includes("synthesizer")) {
            next.router = "completed";
            next.retriever = "completed";
            next.coder = "completed";
            next.synthesizer = "active";
          }
          return next;
        });
      } catch (err) {
        console.error("Parse step error:", err);
      }
    });

    eventSource.addEventListener("final_answer", (event) => {
      try {
        const data = JSON.parse(event.data);
        assistantResponse = data.content;
        if (data.chart_url) {
          currentChart = `${API_BASE}${data.chart_url}`;
        }
      } catch (err) {
        console.error("Parse answer error:", err);
      }
    });

    eventSource.addEventListener("error", (event: any) => {
      console.error("SSE Error event:", event);
      let message = "Đã xảy ra lỗi kết nối với Agent. Vui lòng thử lại.";
      try {
        if (event.data) {
          const data = JSON.parse(event.data);
          if (data.detail) message = data.detail;
        }
      } catch (e) {}
      
      setErrorMsg(message);
      setMessages(prev => [...prev, { role: "error", content: message }]);
      setIsThinking(false);
      eventSource.close();
    });

    eventSource.addEventListener("done", () => {
      setNodeStates({
        router: "completed",
        retriever: "completed",
        coder: "completed",
        synthesizer: "completed"
      });
      
      if (assistantResponse) {
        setMessages(prev => [...prev, { 
          role: "assistant", 
          content: assistantResponse,
          chartUrl: currentChart 
        }]);
      }
      setIsThinking(false);
      setCurrentNode("");
      eventSource.close();
    });

    // Xử lý khi connection tự ngắt không mong muốn
    eventSource.onerror = (e) => {
      if (eventSource.readyState === EventSource.CLOSED) return;
      setErrorMsg(t("demo.quota_limit"));
      setMessages(prev => [...prev, { role: "error", content: t("demo.quota_limit") }]);
      setIsThinking(false);
      eventSource.close();
    };
  };

  const renderNodeIndicator = (status: NodeStatus, label: string, desc: string, icon: React.ReactNode) => {
    const activeColor = status === "active" ? "border-indigo-500 bg-indigo-500/10 text-indigo-400 shadow-[0_0_15px_rgba(99,102,241,0.3)]" : 
                        status === "completed" ? "border-emerald-500 bg-emerald-500/10 text-emerald-400" : 
                        "border-border bg-accent/5 text-muted-foreground opacity-60";
    
    return (
      <div className={`flex gap-4 p-4 rounded-xl border-2 transition-all duration-300 items-start ${activeColor}`}>
        <div className="mt-0.5 flex items-center justify-center p-2 rounded-lg bg-background border border-current/20">
          {status === "active" ? <Loader2 className="w-5 h-5 animate-spin" /> : icon}
        </div>
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 justify-between">
            <h4 className="font-semibold tracking-wide text-sm uppercase text-foreground">{label}</h4>
            {status === "completed" && <CheckCircle2 className="w-4 h-4 text-emerald-400 flex-shrink-0" />}
          </div>
          <p className="text-xs mt-1 opacity-80 line-clamp-1">{desc}</p>
        </div>
      </div>
    );
  };

  return (
    <section id="visualizer" className="py-24 border-t border-border relative flex items-center justify-center flex-col px-6 bg-gradient-to-b from-accent/5 to-background">
      <div className="max-w-6xl w-full">
        
        {/* Header Section */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/30 text-indigo-500 text-xs font-bold uppercase tracking-wider mb-4">
            <BrainCircuit className="w-3.5 h-3.5" />
            <span>Live Demo Trace</span>
          </div>
          <h2 className="text-3xl md:text-4xl font-bold tracking-tight mb-4">
            {t("demo.chat_title")}
          </h2>
          <p className="text-muted-foreground max-w-2xl mx-auto text-lg">
            {t("demo.chat_subtitle")}
          </p>
        </motion.div>

        {/* Split Dashboard Demo View */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 w-full min-h-[600px]">
          
          {/* Cột 1: Interactive Chat Console (7 columns) */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="lg:col-span-7 bg-card rounded-2xl border border-border shadow-2xl flex flex-col overflow-hidden h-[600px] relative"
          >
            {/* Chat Head */}
            <div className="border-b border-border p-4 bg-accent/10 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <div className="w-3 h-3 rounded-full bg-red-500" />
                <div className="w-3 h-3 rounded-full bg-yellow-500" />
                <div className="w-3 h-3 rounded-full bg-emerald-500" />
                <span className="text-xs font-mono font-bold tracking-wider ml-2 text-muted-foreground uppercase">
                  demo_session_api_v1
                </span>
              </div>
              <div className="text-xs bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 font-semibold px-2.5 py-1 rounded-md">
                3 / 3 {t("demo.quota_left")}
              </div>
            </div>

            {/* Message Box History */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6 font-sans scrollbar-thin">
              <AnimatePresence initial={false}>
                {messages.map((msg, idx) => (
                  <motion.div
                    key={idx}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className={`flex gap-4 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    {msg.role !== 'user' && (
                      <div className={`w-9 h-9 rounded-full flex items-center justify-center border flex-shrink-0 shadow-md ${msg.role === 'error' ? 'bg-destructive/10 border-destructive/30 text-destructive' : 'bg-primary/10 border-primary/20 text-primary'}`}>
                        {msg.role === 'error' ? <AlertTriangle className="w-4 h-4" /> : <Bot className="w-5 h-5" />}
                      </div>
                    )}

                    <div className={`max-w-[80%] px-4 py-3 rounded-2xl text-sm leading-relaxed shadow-sm ${
                      msg.role === 'user' 
                        ? 'bg-primary text-primary-foreground rounded-tr-none' 
                        : msg.role === 'error'
                        ? 'bg-destructive/5 border border-destructive/20 text-destructive rounded-tl-none'
                        : 'bg-accent/20 border border-border text-foreground rounded-tl-none'
                    }`}>
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                      {msg.chartUrl && (
                        <div className="mt-4 rounded-lg overflow-hidden border-2 border-border bg-white p-1 shadow-inner">
                          <img src={msg.chartUrl} alt="Agent Calculated Chart" className="w-full h-auto object-contain" />
                        </div>
                      )}
                    </div>

                    {msg.role === 'user' && (
                      <div className="w-9 h-9 rounded-full bg-indigo-500 flex items-center justify-center border border-indigo-600 text-white flex-shrink-0 shadow-md">
                        <User className="w-5 h-5" />
                      </div>
                    )}
                  </motion.div>
                ))}
              </AnimatePresence>
              
              {/* Loader thinking mock indicator */}
              {isThinking && !currentNode && (
                <div className="flex gap-4 justify-start">
                  <div className="w-9 h-9 rounded-full bg-primary/10 flex items-center justify-center border border-primary/20 text-primary animate-pulse">
                    <Bot className="w-5 h-5" />
                  </div>
                  <div className="bg-accent/20 border border-border px-4 py-3 rounded-2xl rounded-tl-none flex items-center gap-3">
                    <Loader2 className="w-4 h-4 animate-spin text-primary" />
                    <span className="text-xs text-muted-foreground italic font-medium tracking-wide uppercase">
                      {t("demo.agent_thinking")}
                    </span>
                  </div>
                </div>
              )}

              <div ref={messagesEndRef} />
            </div>

            {/* Dynamic Status Overlay during streaming */}
            {currentNode && (
              <div className="px-6 py-2 bg-indigo-500/5 border-t border-indigo-500/10 flex items-center gap-3 text-indigo-400 font-mono text-xs">
                <Terminal className="w-4 h-4 animate-pulse flex-shrink-0" />
                <span className="font-bold uppercase tracking-wider">Trace:</span>
                <span className="truncate italic font-sans font-medium">{currentNode}</span>
              </div>
            )}

            {/* Input Controls */}
            <div className="border-t border-border p-4 bg-accent/5">
              <form onSubmit={handleSend} className="relative flex gap-3 items-center">
                <input 
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  disabled={isThinking}
                  placeholder={t("demo.placeholder")}
                  className="flex-1 h-12 rounded-xl bg-background border-2 border-border focus:border-primary focus:ring-0 px-4 pr-12 text-sm transition-all duration-300 focus:outline-none outline-none font-sans placeholder:text-muted-foreground disabled:opacity-70 disabled:cursor-not-allowed"
                />
                <button
                  type="submit"
                  disabled={isThinking || !input.trim()}
                  className="absolute right-2 top-1/2 -translate-y-1/2 w-9 h-9 rounded-lg flex items-center justify-center bg-primary text-primary-foreground hover:scale-105 hover:opacity-95 disabled:opacity-40 disabled:scale-100 disabled:cursor-not-allowed transition-all duration-300 shadow-md"
                >
                  {isThinking ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </button>
              </form>
            </div>
          </motion.div>

          {/* Cột 2: Multi-Agent Node Visualizer (5 columns) */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="lg:col-span-5 flex flex-col space-y-4 h-full justify-between"
          >
            <div className="bg-card rounded-2xl border border-border p-6 shadow-xl flex-1 flex flex-col gap-4 relative overflow-hidden">
              
              {/* Glowing node line indicator back-layer */}
              <div className="absolute left-[2.35rem] top-20 bottom-10 w-0.5 bg-gradient-to-b from-indigo-500/20 via-indigo-500 to-emerald-500/20 z-0 hidden sm:block" />
              
              <div className="z-10 relative">
                <h3 className="text-lg font-bold tracking-wide mb-2 flex items-center gap-2">
                  <BrainCircuit className="w-5 h-5 text-primary" />
                  {t("visualizer.title")}
                </h3>
                <p className="text-xs text-muted-foreground mb-6">
                  Theo dõi luồng thực thi và biến đổi các Agents theo thời gian thực.
                </p>
              </div>

              <div className="flex-1 flex flex-col gap-4 justify-center z-10 relative">
                {renderNodeIndicator(
                  nodeStates.router,
                  "1. Planner Router",
                  t("demo.step_routing"),
                  <BrainCircuit className="w-5 h-5" />
                )}

                {renderNodeIndicator(
                  nodeStates.retriever,
                  "2. Smart Retriever",
                  t("demo.step_retriever"),
                  <Search className="w-5 h-5" />
                )}

                {renderNodeIndicator(
                  nodeStates.coder,
                  "3. Python Coder",
                  t("demo.step_coder"),
                  <Terminal className="w-5 h-5" />
                )}

                {renderNodeIndicator(
                  nodeStates.synthesizer,
                  "4. Synthesizer",
                  t("demo.step_synthesizer"),
                  <Database className="w-5 h-5" />
                )}
              </div>
            </div>
          </motion.div>

        </div>
      </div>
    </section>
  );
}
