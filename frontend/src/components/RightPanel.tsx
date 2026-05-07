import { Info, Clock, FileText, ChevronRight, PieChart } from 'lucide-react';

const RightPanel = () => {
  const recentFiles = [
    { name: 'BaoCao_Q4_2023.pdf', date: '2 giờ trước', size: '2.4 MB' },
    { name: 'PhanTich_TaiChinh.pdf', date: 'Hôm qua', size: '1.8 MB' },
  ];

  return (
    <aside className="w-80 h-full bg-white border-l border-slate-200 flex flex-col shrink-0">
      <div className="p-8">
        <div className="flex items-center gap-2 mb-6">
          <Info className="w-5 h-5 text-slate-400" />
          <h2 className="font-bold text-slate-900 tracking-tight">Chi tiết phân tích</h2>
        </div>

        <div className="space-y-6">
          <section>
            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-4">Thống kê tài liệu</h3>
            <div className="grid grid-cols-2 gap-3">
              <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Số trang</p>
                <p className="text-xl font-bold text-slate-900">12</p>
              </div>
              <div className="p-4 bg-slate-50 rounded-2xl border border-slate-100">
                <p className="text-[10px] font-bold text-slate-400 uppercase mb-1">Thực thể</p>
                <p className="text-xl font-bold text-slate-900">45</p>
              </div>
            </div>
          </section>

          <section>
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest">Tài liệu gần đây</h3>
              <button className="text-[10px] font-bold text-indigo-600 hover:underline">Xem tất cả</button>
            </div>
            <div className="space-y-3">
              {recentFiles.map((file) => (
                <div key={file.name} className="flex items-center gap-3 p-3 bg-white border border-slate-100 rounded-xl hover:border-indigo-100 hover:shadow-sm transition-all group cursor-pointer">
                  <div className="w-9 h-9 bg-slate-50 rounded-lg flex items-center justify-center group-hover:bg-indigo-50 transition-colors">
                    <FileText className="w-5 h-5 text-slate-400 group-hover:text-indigo-600" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-xs font-bold text-slate-800 truncate">{file.name}</p>
                    <div className="flex items-center gap-2 mt-0.5">
                      <Clock className="w-3 h-3 text-slate-400" />
                      <p className="text-[10px] font-medium text-slate-400">{file.date}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </section>

          <section>
            <div className="p-6 bg-gradient-to-br from-indigo-600 to-blue-600 rounded-3xl text-white shadow-lg shadow-indigo-100 overflow-hidden relative group">
              <div className="absolute -right-4 -bottom-4 opacity-10 group-hover:scale-110 transition-transform duration-500">
                <PieChart className="w-32 h-32" />
              </div>
              <div className="relative">
                <h3 className="font-bold text-sm mb-1">Upgrade to Pro</h3>
                <p className="text-[11px] text-indigo-100 leading-relaxed mb-4">Get deeper financial insights and unlimited PDF analysis.</p>
                <button className="px-4 py-2 bg-white text-indigo-600 text-[11px] font-bold rounded-lg hover:bg-indigo-50 transition-colors shadow-sm flex items-center gap-2">
                  Learn more <ChevronRight className="w-3 h-3" />
                </button>
              </div>
            </div>
          </section>
        </div>
      </div>
      
      <div className="mt-auto p-8 border-t border-slate-100">
        <div className="flex items-center gap-2 text-slate-400">
          <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse" />
          <p className="text-[10px] font-bold uppercase tracking-wider">System Operational</p>
        </div>
      </div>
    </aside>
  );
};

export default RightPanel;
