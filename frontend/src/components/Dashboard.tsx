import React from 'react';
import { LayoutDashboard, TrendingUp, Users, ArrowUpRight, BarChart3, Clock, CheckCircle, Brain, ChevronDown, ChevronUp } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { useChatStore } from '../store/useChatStore';

const data = [
  { name: 'Mon', queries: 24 },
  { name: 'Tue', queries: 35 },
  { name: 'Wed', queries: 18 },
  { name: 'Thu', queries: 47 },
  { name: 'Fri', queries: 52 },
  { name: 'Sat', queries: 30 },
  { name: 'Sun', queries: 12 },
];

const Dashboard: React.FC = () => {
  const activeSteps = useChatStore((state) => state.activeSteps);
  const [isAccordionOpen, setIsAccordionOpen] = React.useState(true);

  return (
    <div className="flex-1 min-h-screen bg-slate-50 flex flex-col p-8 overflow-y-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <LayoutDashboard className="w-6 h-6 text-indigo-600" />
          System Dashboard
        </h1>
        <p className="text-sm text-slate-500 mt-1">Monitor performance and overall financial analysis metrics.</p>
      </div>

      {/* Active Thought Tracing Accordion Panel */}
      {activeSteps.length > 0 && (
        <div className="mb-8 bg-indigo-950 text-slate-100 rounded-2xl border border-indigo-900 shadow-xl overflow-hidden animate-in slide-in-from-top duration-300">
          <button
            onClick={() => setIsAccordionOpen(!isAccordionOpen)}
            className="w-full px-6 py-4 flex items-center justify-between font-bold text-sm tracking-tight text-indigo-200 hover:text-white transition-colors"
          >
            <div className="flex items-center gap-2">
              <Brain className="w-5 h-5 text-indigo-400 animate-pulse" />
              <span>Real-Time Multi-Agent Thought Tracing Stream</span>
            </div>
            {isAccordionOpen ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
          </button>
          {isAccordionOpen && (
            <div className="px-6 pb-6 pt-2 space-y-2.5 font-mono text-xs text-indigo-300 max-h-60 overflow-y-auto border-t border-indigo-900/50">
              {activeSteps.map((step, index) => (
                <div key={index} className="flex items-start gap-2 animate-in fade-in duration-200">
                  <span className="text-indigo-500 font-bold shrink-0">{`[Step ${index + 1}]`}</span>
                  <span className="text-slate-200">{step}</span>
                </div>
              ))}
            </div>
          )}
        </div>
      )}

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between group hover:border-indigo-200 transition-all duration-200">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Documents</p>
            <p className="text-2xl font-bold text-slate-900 mt-2">12</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
            <BarChart3 className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between group hover:border-emerald-200 transition-all duration-200">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Total Queries</p>
            <p className="text-2xl font-bold text-slate-900 mt-2">218</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between group hover:border-sky-200 transition-all duration-200">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Active Users</p>
            <p className="text-2xl font-bold text-slate-900 mt-2">4</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
            <Users className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between group hover:border-indigo-200 transition-all duration-200">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Response Time</p>
            <p className="text-2xl font-bold text-slate-900 mt-2">1.2s</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
            <Clock className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8 flex-1">
        {/* Chart Column */}
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col min-h-[350px]">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Queries This Week</h2>
            <span className="flex items-center gap-1 text-xs text-emerald-600 font-semibold bg-emerald-50 px-2 py-1 rounded-lg">
              <ArrowUpRight className="w-3.5 h-3.5" /> +15.3%
            </span>
          </div>
          <div className="flex-1 w-full min-h-[250px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={data}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#94a3b8" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip cursor={{ fill: '#f8fafc' }} contentStyle={{ borderRadius: '12px', border: '1px solid #e2e8f0', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.05)' }} />
                <Bar dataKey="queries" fill="#4f46e5" radius={[4, 4, 0, 0]} barSize={36} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* System Activity Column */}
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex flex-col">
          <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-6">System Status</h2>
          <div className="space-y-5 flex-1">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                <CheckCircle className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">Database Connection</p>
                <p className="text-xs text-slate-400 mt-0.5">PostgreSQL connection stable</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                <CheckCircle className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">Redis Cache</p>
                <p className="text-xs text-slate-400 mt-0.5">Cache store initialized and ready</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                <CheckCircle className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">Vector Index (Chroma)</p>
                <p className="text-xs text-slate-400 mt-0.5">100% of document nodes indexed</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
