import React, { useState, useEffect, useRef } from 'react';
import { Database, Search, Plus, Trash2, Edit2, FileText, RefreshCw } from 'lucide-react';
import apiClient from '../api/client';

interface Document {
  id: string;
  name: string;
  size: string;
  uploadedAt: string;
  status: 'indexed' | 'processing' | 'failed';
}

const KnowledgeManagement: React.FC = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [documents, setDocuments] = useState<Document[]>([]);
  const [toast, setToast] = useState<{ message: string; type: 'info' | 'success' | 'error' } | null>(null);
  const [processing, setProcessing] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const showToast = (message: string, type: 'info' | 'success' | 'error') => {
    setToast({ message, type });
    if (type === 'success' || type === 'error') {
      setTimeout(() => setToast(null), 4000);
    }
  };

  const fetchDocuments = async () => {
    try {
      const response = await apiClient.get('/documents');
      setDocuments(response.data);
    } catch (error) {
      console.error('Error fetching documents:', error);
      showToast('Lỗi khi tải danh sách tài liệu.', 'error');
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  const pollStatus = (taskId: string) => {
    if (!taskId || taskId === 'undefined') {
      showToast('Lỗi: Mã tiến trình không hợp lệ.', 'error');
      setProcessing(false);
      return;
    }

    let attempts = 0;
    const maxAttempts = 30; // 60 seconds total at 2000ms intervals

    const interval = setInterval(async () => {
      attempts++;
      if (attempts > maxAttempts) {
        clearInterval(interval);
        showToast('Hết thời gian chờ xử lý tài liệu.', 'error');
        setProcessing(false);
        fetchDocuments();
        return;
      }

      try {
        const response = await apiClient.get(`/status/${taskId}`);
        const { status, details } = response.data;

        if (status === 'completed') {
          clearInterval(interval);
          showToast('Tài liệu đã được phân tích và đánh chỉ mục thành công!', 'success');
          setProcessing(false);
          fetchDocuments(); // Refresh complete list
        } else if (status === 'failed') {
          clearInterval(interval);
          showToast(`Xử lý thất bại: ${details || 'Lỗi không xác định'}`, 'error');
          setProcessing(false);
          fetchDocuments(); // Refresh failed state
        }
      } catch (error) {
        console.error('Polling error:', error);
      }
    }, 2000);
  };

  const uploadFile = async (file: File) => {
    const isPdf = file.name.toLowerCase().endsWith('.pdf') && (file.type === 'application/pdf' || file.type === '');
    if (!isPdf) {
      showToast('File không hợp lệ. Vui lòng chỉ tải lên báo cáo định dạng PDF.', 'error');
      return;
    }

    const MAX_SIZE = 100 * 1024 * 1024; // 100MB
    if (file.size > MAX_SIZE) {
      showToast('Kích thước file quá lớn. Vui lòng tải lên file nhỏ hơn 100MB.', 'error');
      return;
    }

    const formData = new FormData();
    formData.append('file', file);

    setProcessing(true);
    showToast(`Đang tải lên tài liệu: ${file.name}...`, 'info');

    try {
      const response = await apiClient.post('/upload-pdf', formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      showToast('Đang phân tích và trích xuất tài liệu...', 'info');
      fetchDocuments(); // Fetch 'processing' status
      pollStatus(response.data.task_id);
    } catch (error) {
      showToast('Lỗi khi tải tài liệu lên. Vui lòng thử lại.', 'error');
      setProcessing(false);
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadFile(e.target.files[0]);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (window.confirm(`Bạn có chắc chắn muốn xóa tài liệu "${name}"? Thao tác này sẽ xóa vĩnh viễn dữ liệu tri thức tương ứng.`)) {
      try {
        showToast('Đang tiến hành xóa tài liệu...', 'info');
        await apiClient.delete(`/documents/${id}`);
        showToast('Đã xóa tài liệu và đồng bộ lại tri thức thành công!', 'success');
        fetchDocuments();
      } catch (error) {
        console.error('Delete error:', error);
        showToast('Không thể xóa tài liệu. Vui lòng thử lại.', 'error');
      }
    }
  };

  const handleRename = async (id: string, currentName: string) => {
    const newName = window.prompt('Nhập tên hiển thị mới cho tài liệu:', currentName);
    if (newName && newName.trim() !== '' && newName !== currentName) {
      try {
        showToast('Đang đổi tên tài liệu...', 'info');
        await apiClient.patch(`/documents/${id}`, { name: newName });
        showToast('Cập nhật tên tài liệu thành công!', 'success');
        fetchDocuments();
      } catch (error) {
        console.error('Rename error:', error);
        showToast('Lỗi khi đổi tên tài liệu.', 'error');
      }
    }
  };

  const filteredDocs = documents.filter(doc => 
    doc.name.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="flex-1 min-h-screen bg-slate-50 flex flex-col p-8 overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between mb-8">
        <div>
          <h1 className="text-2xl font-bold text-slate-900 tracking-tight flex items-center gap-2">
            <Database className="w-6 h-6 text-indigo-600" />
            Knowledge Base
          </h1>
          <p className="text-sm text-slate-500 mt-1">Quản lý tài liệu và dữ liệu tri thức của hệ thống phân tích báo cáo tài chính.</p>
        </div>
        <button 
          onClick={() => fileInputRef.current?.click()}
          disabled={processing}
          className="flex items-center gap-2 px-4 py-2 bg-indigo-600 hover:bg-indigo-700 disabled:opacity-50 text-white text-sm font-semibold rounded-xl shadow-lg shadow-indigo-100 transition-all duration-200"
        >
          <Plus className="w-4 h-4" />
          {processing ? 'Đang xử lý...' : 'Thêm tài liệu'}
        </button>
        <input 
          type="file"
          ref={fileInputRef}
          onChange={handleFileChange}
          className="hidden"
          accept=".pdf"
        />
      </div>

      {/* Stats row */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Tổng số tài liệu</p>
          <p className="text-2xl font-bold text-slate-900 mt-2">{documents.length}</p>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Trạng thái đồng bộ</p>
          <div className="flex items-center gap-2 mt-2">
            <span className="w-2 h-2 rounded-full bg-green-500 animate-pulse" />
            <p className="text-sm font-bold text-slate-900">
              {documents.filter(d => d.status === 'indexed').length} / {documents.length} Đã đánh chỉ mục
            </p>
          </div>
        </div>
        <div className="bg-white p-6 rounded-2xl border border-slate-200 shadow-sm">
          <p className="text-xs font-semibold text-slate-400 uppercase tracking-wider">Bộ nhớ sử dụng</p>
          <p className="text-2xl font-bold text-slate-900 mt-2">
            {(documents.reduce((acc, doc) => acc + (parseFloat(doc.size) || 0), 0)).toFixed(1)} MB
          </p>
        </div>
      </div>

      {/* Actions & Filters */}
      <div className="bg-white rounded-2xl border border-slate-200 shadow-sm overflow-hidden flex-1 flex flex-col">
        <div className="p-6 border-b border-slate-100 flex flex-col sm:flex-row items-center gap-4 justify-between">
          <div className="relative w-full sm:w-80">
            <Search className="w-4 h-4 text-slate-400 absolute left-3 top-1/2 -translate-y-1/2" />
            <input 
              type="text" 
              placeholder="Tìm kiếm tài liệu..."
              value={searchTerm}
              onChange={e => setSearchTerm(e.target.value)}
              className="w-full pl-9 pr-4 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:bg-white transition-all"
            />
          </div>
          <button 
            onClick={fetchDocuments}
            className="flex items-center gap-2 px-3 py-2 text-slate-500 hover:text-slate-800 text-sm font-medium hover:bg-slate-50 rounded-xl transition-all"
          >
            <RefreshCw className="w-4 h-4" />
            Làm mới danh sách
          </button>
        </div>

        {/* Table */}
        <div className="overflow-x-auto flex-1">
          <table className="w-full text-left border-collapse">
            <thead>
              <tr className="bg-slate-50 border-b border-slate-100 text-xs font-semibold text-slate-500 uppercase tracking-wider">
                <th className="px-6 py-4">Tên tài liệu</th>
                <th className="px-6 py-4">Dung lượng</th>
                <th className="px-6 py-4">Ngày tải lên</th>
                <th className="px-6 py-4">Trạng thái</th>
                <th className="px-6 py-4 text-right">Thao tác</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100 text-sm text-slate-600">
              {filteredDocs.map(doc => (
                <tr key={doc.id} className="hover:bg-slate-50/50 transition-colors">
                  <td className="px-6 py-4 font-medium text-slate-800 flex items-center gap-3">
                    <div className="w-8 h-8 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center">
                      <FileText className="w-4 h-4" />
                    </div>
                    {doc.name}
                  </td>
                  <td className="px-6 py-4">{doc.size}</td>
                  <td className="px-6 py-4 text-slate-400">{doc.uploadedAt}</td>
                  <td className="px-6 py-4">
                    {doc.status === 'indexed' ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-green-50 text-green-700">
                        <span className="w-1.5 h-1.5 rounded-full bg-green-500" />
                        Indexed
                      </span>
                    ) : doc.status === 'failed' ? (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-red-50 text-red-700">
                        <span className="w-1.5 h-1.5 rounded-full bg-red-500" />
                        Failed
                      </span>
                    ) : (
                      <span className="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-semibold bg-indigo-50 text-indigo-700">
                        <span className="w-1.5 h-1.5 rounded-full bg-indigo-500 animate-pulse" />
                        Processing
                      </span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <div className="flex items-center justify-end gap-2">
                      <button 
                        onClick={() => handleRename(doc.id, doc.name)}
                        className="p-1.5 text-slate-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-lg transition-all"
                        title="Sửa tên tài liệu"
                      >
                        <Edit2 className="w-4 h-4" />
                      </button>
                      <button 
                        onClick={() => handleDelete(doc.id, doc.name)}
                        className="p-1.5 text-slate-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-all"
                        title="Xóa tài liệu"
                      >
                        <Trash2 className="w-4 h-4" />
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
              {filteredDocs.length === 0 && (
                <tr>
                  <td colSpan={5} className="text-center py-12 text-slate-400 italic">
                    Không tìm thấy tài liệu phù hợp.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>

      {toast && (
        <div className={`fixed bottom-6 right-6 px-6 py-4 rounded-2xl shadow-xl border text-sm flex items-center gap-3 z-50 animate-fade-in ${
          toast.type === 'success' ? 'bg-emerald-50 border-emerald-100 text-emerald-800' :
          toast.type === 'error' ? 'bg-rose-50 border-rose-100 text-rose-800' :
          'bg-indigo-50 border-indigo-100 text-indigo-800'
        }`}>
          {toast.type === 'success' && <span className="w-2.5 h-2.5 rounded-full bg-emerald-500 animate-pulse" />}
          {toast.type === 'error' && <span className="w-2.5 h-2.5 rounded-full bg-rose-500 animate-pulse" />}
          {toast.type === 'info' && <span className="w-2.5 h-2.5 rounded-full bg-indigo-500 animate-pulse" />}
          <p className="font-semibold">{toast.message}</p>
        </div>
      )}
    </div>
  );
};

export default KnowledgeManagement;
