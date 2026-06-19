import React from 'react';
import { 
  Compass, 
  Search, 
  Code, 
  RefreshCw, 
  CheckCircle2, 
  AlertTriangle,
  ChevronDown,
  ChevronRight
} from 'lucide-react';

interface AgentStepperProps {
  steps: string[];
  isStreaming?: boolean;
}

export const AgentStepper: React.FC<AgentStepperProps> = ({ steps, isStreaming = false }) => {
  const [isOpen, setIsOpen] = React.useState(true);

  if (!steps || steps.length === 0) return null;

  const parseStep = (stepText: string) => {
    let icon = <Compass className="w-4 h-4 text-indigo-500" />;
    let type = "system";
    let isError = false;
    let isWarning = false;

    if (stepText.includes('Retriever')) {
      icon = <Search className="w-4 h-4 text-sky-500" />;
      type = "retriever";
    } else if (stepText.includes('Coder')) {
      icon = <Code className="w-4 h-4 text-emerald-500" />;
      type = "coder";
    } else if (stepText.includes('attempting') || stepText.includes('tried') || stepText.includes('error') || stepText.includes('failed')) {
      icon = <RefreshCw className="w-4 h-4 text-amber-500 animate-spin-slow" />;
      type = "correction";
      isWarning = true;
    } else if (stepText.includes('Exception') || stepText.includes('Error')) {
      icon = <AlertTriangle className="w-4 h-4 text-rose-500" />;
      type = "error";
      isError = true;
    }

    return { icon, type, isError, isWarning };
  };

  return (
    <div id="reasoning-steps" className="w-full my-3 bg-slate-50/70 border border-slate-200/60 rounded-2xl overflow-hidden backdrop-blur-sm transition-all shadow-sm">
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="w-full px-4 py-3 flex items-center justify-between bg-slate-100/50 hover:bg-slate-100 transition-colors select-none"
      >
        <div className="flex items-center gap-2">
          <span className="flex h-5 w-5 items-center justify-center rounded-full bg-indigo-50 text-[10px] font-extrabold text-indigo-600 border border-indigo-100">
            {steps.length}
          </span>
          <span className="text-[12px] font-bold text-slate-700 tracking-tight">
            Multi-Agent Thought process
          </span>
          {isStreaming && (
            <span className="flex h-2 w-2 relative">
              <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-indigo-400 opacity-75"></span>
              <span className="relative inline-flex rounded-full h-2 w-2 bg-indigo-500"></span>
            </span>
          )}
        </div>
        {isOpen ? (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-slate-400" />
        )}
      </button>

      {isOpen && (
        <div className="p-4 space-y-3.5 border-t border-slate-100 bg-white/40">
          {steps.map((step, idx) => {
            const { icon, isError, isWarning } = parseStep(step);
            const isLast = idx === steps.length - 1;
            const isActive = isLast && isStreaming;

            return (
              <div key={idx} className="relative flex items-start gap-3 group">
                {/* Connecting Line */}
                {!isLast && (
                  <div className="absolute left-[9px] top-6 bottom-[-14px] w-[2px] bg-slate-200" />
                )}

                {/* Step Icon */}
                <div className={`
                  relative z-10 flex items-center justify-center w-5.5 h-5.5 rounded-lg border transition-all
                  ${isActive 
                    ? 'bg-indigo-50 border-indigo-300 ring-4 ring-indigo-50' 
                    : isError 
                      ? 'bg-rose-50 border-rose-200' 
                      : isWarning 
                        ? 'bg-amber-50 border-amber-200' 
                        : 'bg-slate-50 border-slate-200'
                  }
                `}>
                  {isActive ? (
                    <RefreshCw className="w-3.5 h-3.5 text-indigo-600 animate-spin" />
                  ) : (
                    icon
                  )}
                </div>

                {/* Step Content */}
                <div className="flex-1 min-w-0 pt-0.5">
                  <p className={`
                    text-xs leading-relaxed font-medium transition-all
                    ${isActive 
                      ? 'text-indigo-600 font-semibold' 
                      : isError 
                        ? 'text-rose-600' 
                        : 'text-slate-600'
                    }
                  `}>
                    {step}
                  </p>
                </div>

                {/* Completed Checkmark Indicator */}
                {!isLast && !isError && (
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400/80 mt-1 opacity-0 group-hover:opacity-100 transition-opacity shrink-0" />
                )}
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
};
