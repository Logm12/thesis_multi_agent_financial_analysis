import React from 'react';
import { LayoutDashboard, TrendingUp, Users, ArrowUpRight, BarChart3, Clock, CheckCircle } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'T2', queries: 24 },
  { name: 'T3', queries: 35 },
  { name: 'T4', queries: 18 },
  { name: 'T5', queries: 47 },
  { name: 'T6', queries: 52 },
  { name: 'T7', queries: 30 },
  { name: 'CN', queries: 12 },
];

const Dashboard: React.FC = () => {
  return (
    <div className="flex-1 min-h-screen bg-slate-50 flex flex-col p-8 overflow-y-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
          <LayoutDashboard className="w-6 h-6 text-indigo-600" />
          Dashboard Hệ Thống
        </h1>
        <p className="text-sm text-slate-500 mt-1">Giám sát hiệu năng và tổng quan số liệu phân tích tài chính.</p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between group hover:border-indigo-200 transition-all duration-200">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Tổng số tài liệu</p>
            <p className="text-2xl font-bold text-slate-900 mt-2">12</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-indigo-50 text-indigo-600 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
            <BarChart3 className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between group hover:border-emerald-200 transition-all duration-200">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Số lượt truy vấn</p>
            <p className="text-2xl font-bold text-slate-900 mt-2">218</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-emerald-50 text-emerald-600 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
            <TrendingUp className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between group hover:border-sky-200 transition-all duration-200">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Người dùng hoạt động</p>
            <p className="text-2xl font-bold text-slate-900 mt-2">4</p>
          </div>
          <div className="w-12 h-12 rounded-xl bg-sky-50 text-sky-600 flex items-center justify-center group-hover:scale-110 transition-transform duration-200">
            <Users className="w-6 h-6" />
          </div>
        </div>

        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm flex items-center justify-between group hover:border-indigo-200 transition-all duration-200">
          <div>
            <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Thời gian phản hồi</p>
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
            <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider">Lượt truy vấn tuần này</h2>
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
          <h2 className="text-sm font-bold text-slate-800 uppercase tracking-wider mb-6">Trạng thái hệ thống</h2>
          <div className="space-y-5 flex-1">
            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                <CheckCircle className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">Database Connection</p>
                <p className="text-xs text-slate-400 mt-0.5">Kết nối PostgreSQL ổn định</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                <CheckCircle className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">Redis Cache</p>
                <p className="text-xs text-slate-400 mt-0.5">Sẵn sàng lưu trữ bộ nhớ đệm</p>
              </div>
            </div>

            <div className="flex items-start gap-3">
              <div className="w-8 h-8 rounded-full bg-emerald-50 text-emerald-600 flex items-center justify-center shrink-0">
                <CheckCircle className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm font-semibold text-slate-800">Vector Index (Chroma)</p>
                <p className="text-xs text-slate-400 mt-0.5">100% tài liệu được lập chỉ mục</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
