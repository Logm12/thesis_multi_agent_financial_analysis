import React from 'react';
import { Sparkles, User, AlertCircle, Loader2 } from 'lucide-react';
import type { Message } from '../types/chat';
import DynamicChart from './DynamicChart';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

interface MessageBubbleProps {
  message: Message;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ message }) => {
  return (
    <div className={cn(
      "flex w-full mb-6 gap-4",
      message.isUser ? "flex-row-reverse" : "flex-row"
    )}>
      <div className={cn(
        "w-8 h-8 rounded-lg flex items-center justify-center shrink-0",
        message.isUser ? "bg-indigo-600 text-white" : "bg-white border border-slate-200 text-primary"
      )}>
        {message.isUser ? <User className="w-5 h-5" /> : <Sparkles className="w-5 h-5" />}
      </div>
      
      <div className={cn(
        "max-w-[80%] flex flex-col",
        message.isUser ? "items-end" : "items-start"
      )}>
        <div className={cn(
          "px-4 py-3 rounded-2xl text-sm leading-relaxed",
          message.isUser 
            ? "bg-primary text-white rounded-tr-none" 
            : message.isSystem 
              ? "bg-slate-100 text-slate-600 italic border border-slate-200"
              : message.isError
                ? "bg-red-50 text-red-600 border border-red-100"
                : "bg-white text-slate-700 border border-slate-200 shadow-sm rounded-tl-none"
        )}>
          {message.isError && <AlertCircle className="w-4 h-4 inline mr-2" />}
          {message.isSystem && <Loader2 className="w-4 h-4 inline mr-2 animate-spin" />}
          {message.text}
        </div>
        
        {message.hasChart && message.chartData && (
          <DynamicChart data={message.chartData} type={message.chartType} />
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
