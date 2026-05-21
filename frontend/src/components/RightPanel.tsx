import React, { useState, useEffect, useRef } from 'react';
import { ChevronLeft, ChevronRight, ZoomIn, ZoomOut, FileText, Loader2 } from 'lucide-react';
import { useChatStore } from '../store/useChatStore';
import apiClient from '../api/client';

interface Document {
  id: string;
  name: string;
  size: string;
  uploadedAt: string;
  status: 'indexed' | 'processing' | 'failed';
}

interface PageInfo {
  page: number;
  width: number;
  height: number;
}

interface DocInfo {
  id: string;
  name: string;
  totalPages: number;
  pages: PageInfo[];
}

const RightPanel: React.FC = () => {
  const { 
    activePdfId, 
    activePage, 
    highlightedBbox, 
    setActivePdf, 
    setActivePage, 
    setHighlightedBbox 
  } = useChatStore();

  const [documents, setDocuments] = useState<Document[]>([]);
  const [docInfo, setDocInfo] = useState<DocInfo | null>(null);
  const [loading, setLoading] = useState(false);
  const [zoom, setZoom] = useState<number>(1); // Zoom multiplier
  const [imgLoaded, setImgLoaded] = useState(false);

  const containerRef = useRef<HTMLDivElement>(null);
  const imgRef = useRef<HTMLImageElement>(null);
  const [bboxStyle, setBboxStyle] = useState<React.CSSProperties>({ display: 'none' });

  // 1. Fetch available documents in the system
  const fetchDocuments = async () => {
    try {
      const response = await apiClient.get('/documents');
      setDocuments(response.data);
      
      // If there's an indexed document and no active PDF is set, automatically select the first one
      if (response.data.length > 0 && !activePdfId) {
        const indexedDoc = response.data.find((d: Document) => d.status === 'indexed');
        if (indexedDoc) {
          setActivePdf(indexedDoc.id);
        } else {
          setActivePdf(response.data[0].id);
        }
      }
    } catch (err) {
      console.error('Error fetching documents in right panel:', err);
    }
  };

  useEffect(() => {
    fetchDocuments();
  }, []);

  // 2. Fetch active PDF structural information
  useEffect(() => {
    if (!activePdfId) {
      setDocInfo(null);
      return;
    }

    const fetchDocInfo = async () => {
      setLoading(true);
      setImgLoaded(false);
      try {
        const response = await apiClient.get(`/documents/${activePdfId}/info`);
        setDocInfo(response.data);
      } catch (err) {
        console.error('Error fetching document info:', err);
        setDocInfo(null);
      } finally {
        setLoading(false);
      }
    };

    fetchDocInfo();
  }, [activePdfId]);

  // 3. Compute Bounding Box absolute coordinates dynamically
  const updateBboxPosition = () => {
    if (!highlightedBbox || !imgRef.current || !docInfo) {
      setBboxStyle({ display: 'none' });
      return;
    }

    try {
      const parsed = JSON.parse(highlightedBbox);
      if (parsed.page !== activePage) {
        setBboxStyle({ display: 'none' });
        return;
      }

      const bbox = parsed.bbox; // [x0, y0, x1, y1]
      const pageMeta = docInfo.pages.find(p => p.page === activePage);
      if (!pageMeta) return;

      const img = imgRef.current;
      const rect = img.getBoundingClientRect();

      // Calculate ratios
      const scaleX = rect.width / pageMeta.width;
      const scaleY = rect.height / pageMeta.height;

      const left = bbox[0] * scaleX;
      const top = bbox[1] * scaleY;
      const width = (bbox[2] - bbox[0]) * scaleX;
      const height = (bbox[3] - bbox[1]) * scaleY;

      setBboxStyle({
        display: 'block',
        position: 'absolute',
        left: `${left}px`,
        top: `${top}px`,
        width: `${width}px`,
        height: `${height}px`,
        mixBlendMode: 'multiply',
      });
    } catch (e) {
      console.error('Error parsing/drawing highlighted bounding box:', e);
      setBboxStyle({ display: 'none' });
    }
  };

  // Recalculate on image load, zoom change, page change, or window resize
  useEffect(() => {
    updateBboxPosition();
  }, [highlightedBbox, activePage, zoom, imgLoaded, docInfo]);

  useEffect(() => {
    window.addEventListener('resize', updateBboxPosition);
    return () => window.removeEventListener('resize', updateBboxPosition);
  }, [highlightedBbox, activePage, zoom, docInfo]);

  // Page handlers
  const handlePrevPage = () => {
    if (activePage > 1) {
      setActivePage(activePage - 1);
      setHighlightedBbox(null);
    }
  };

  const handleNextPage = () => {
    if (docInfo && activePage < docInfo.totalPages) {
      setActivePage(activePage + 1);
      setHighlightedBbox(null);
    }
  };

  const handleZoomIn = () => setZoom(prev => Math.min(prev + 0.15, 2.5));
  const handleZoomOut = () => setZoom(prev => Math.max(prev - 0.15, 0.6));
  const handleResetZoom = () => setZoom(1);

  const apiBaseUrl = (import.meta.env.VITE_API_BASE_URL || 'http://localhost:8001/api/v1');

  return (
    <aside data-testid="right-panel" className="w-full h-full bg-slate-900 border-l border-slate-800 flex flex-col shrink-0 relative overflow-hidden text-slate-100 shadow-2xl">
      {/* Header bar */}
      <div className="h-16 border-b border-slate-800 flex items-center justify-between px-6 shrink-0 bg-slate-950/60 backdrop-blur-md z-10">
        <div className="flex items-center gap-2">
          <FileText className="w-5 h-5 text-indigo-400" />
          <h2 className="font-bold text-sm text-slate-200 truncate max-w-[200px]">
            {docInfo ? docInfo.name : 'Bộ đọc BCTC'}
          </h2>
        </div>

        {docInfo && (
          <div className="flex items-center gap-2">
            <button 
              onClick={handlePrevPage} 
              disabled={activePage <= 1}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-30 disabled:pointer-events-none text-slate-300 transition-colors"
            >
              <ChevronLeft className="w-4 h-4" />
            </button>
            <span className="text-xs font-semibold text-slate-400 bg-slate-800/50 px-2 py-1 rounded">
              Trang {activePage} / {docInfo.totalPages}
            </span>
            <button 
              onClick={handleNextPage} 
              disabled={activePage >= docInfo.totalPages}
              className="p-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 disabled:opacity-30 disabled:pointer-events-none text-slate-300 transition-colors"
            >
              <ChevronRight className="w-4 h-4" />
            </button>
          </div>
        )}
      </div>

      {/* Toolbar Controls */}
      {docInfo && (
        <div className="h-12 border-b border-slate-800 flex items-center justify-between px-6 shrink-0 bg-slate-900/50 z-10">
          <div className="flex items-center gap-1.5">
            <button 
              onClick={handleZoomOut} 
              className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
              title="Thu nhỏ"
            >
              <ZoomOut className="w-4 h-4" />
            </button>
            <span 
              onClick={handleResetZoom}
              className="text-xs font-bold text-slate-400 cursor-pointer hover:text-indigo-400 bg-slate-800/40 px-2 py-1 rounded transition-colors"
              title="Reset Zoom"
            >
              {Math.round(zoom * 100)}%
            </span>
            <button 
              onClick={handleZoomIn} 
              className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-slate-200 transition-colors"
              title="Phóng to"
            >
              <ZoomIn className="w-4 h-4" />
            </button>
          </div>

          <div className="flex items-center gap-3">
            {highlightedBbox && (
              <button 
                onClick={() => setHighlightedBbox(null)}
                className="text-[10px] font-bold text-red-400 hover:text-red-300 bg-red-500/10 px-2 py-1 rounded-full border border-red-500/20 hover:bg-red-500/20 transition-all"
              >
                Xóa Highlight
              </button>
            )}
            <select
              value={activePdfId || ''}
              onChange={(e) => setActivePdf(e.target.value)}
              className="bg-slate-800 border border-slate-700 text-slate-300 text-xs rounded-lg px-2 py-1 max-w-[150px] truncate focus:outline-none focus:border-indigo-500"
            >
              {documents.map((doc) => (
                <option key={doc.id} value={doc.id}>
                  {doc.name}
                </option>
              ))}
            </select>
          </div>
        </div>
      )}

      {/* Primary Display Area — dark background makes white PDF page pop */}
      <div 
        ref={containerRef}
        className="flex-1 overflow-auto bg-[#0d1117] p-6 flex items-start justify-center relative select-none"
      >
        {loading ? (
          <div className="absolute inset-0 flex flex-col items-center justify-center gap-3 bg-slate-950/80">
            <Loader2 className="w-8 h-8 text-indigo-500 animate-spin" />
            <p className="text-xs font-semibold text-slate-400">Đang phân tích cấu trúc PDF...</p>
          </div>
        ) : !activePdfId ? (
          <div className="flex flex-col items-center justify-center text-center p-8 m-auto max-w-sm">
            <div className="w-16 h-16 bg-slate-900 border border-slate-800 rounded-3xl flex items-center justify-center mb-6 shadow-xl animate-pulse">
              <FileText className="w-8 h-8 text-slate-500" />
            </div>
            <h3 className="font-bold text-slate-300 text-base mb-2">Chưa chọn báo cáo</h3>
            <p className="text-xs text-slate-500 leading-relaxed mb-6">
              Vui lòng chọn một báo cáo tài chính đã được tải lên từ kho tri thức để bắt đầu phân tích tương tác trực quan.
            </p>
            <div className="w-full max-h-48 overflow-y-auto space-y-2 border border-slate-800 rounded-xl p-2 bg-slate-900/30">
              {documents.map((doc) => (
                <div 
                  key={doc.id}
                  onClick={() => setActivePdf(doc.id)}
                  className="flex items-center justify-between p-2.5 rounded-lg bg-slate-900/60 border border-slate-800 hover:border-indigo-500/50 hover:bg-slate-900/100 cursor-pointer transition-all"
                >
                  <span className="text-xs font-bold text-slate-300 truncate max-w-[180px]">{doc.name}</span>
                  <span className="text-[9px] font-semibold bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 px-1.5 py-0.5 rounded-full">Sẵn sàng</span>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div 
            className="relative bg-white shadow-2xl rounded-lg overflow-hidden transition-transform duration-200 origin-top"
            style={{ transform: `scale(${zoom})` }}
          >
            {/* PDF Image View */}
            <img 
              ref={imgRef}
              src={`${apiBaseUrl}/documents/${activePdfId}/page/${activePage}/image`}
              alt={`BCTC Page ${activePage}`}
              onLoad={() => setImgLoaded(true)}
              className="max-w-full h-auto object-contain pointer-events-none"
              style={{ minWidth: '400px', maxHeight: '85vh' }}
            />

            {/* Bounding Box Highlights — fade-in + mix-blend-mode per REQ-UI-01 */}
            {bboxStyle.display !== 'none' && (
              <div 
                key={highlightedBbox /* key forces re-mount → restart animation */}
                style={{
                  ...bboxStyle,
                  background: 'rgba(244, 63, 94, 0.15)',
                  border: '2px solid #f43f5e',
                  boxShadow: '0 0 0 1px rgba(244,63,94,0.3), 0 4px 24px rgba(244,63,94,0.15)',
                }}
                className="bbox-highlight rounded pointer-events-none"
              />
            )}
          </div>
        )}
      </div>

      {/* Footer metadata */}
      <div className="h-10 border-t border-slate-800 bg-slate-950 px-6 flex items-center justify-between text-[10px] text-slate-500 shrink-0">
        <div className="flex items-center gap-1.5">
          <div className="w-1.5 h-1.5 bg-emerald-500 rounded-full animate-pulse" />
          <span className="font-bold uppercase tracking-wider">Visual Grounding Engine Active</span>
        </div>
        {docInfo && (
          <span>Kích thước trang: {docInfo.pages[activePage - 1]?.width || 0} x {docInfo.pages[activePage - 1]?.height || 0}</span>
        )}
      </div>
    </aside>
  );
};

export default RightPanel;
