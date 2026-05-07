import { create } from 'zustand';
import type { Message } from '../types/chat';

interface ChatState {
  messages: Message[];
  isProcessing: boolean;
  isLoading: boolean;
  addMessage: (message: Omit<Message, 'id'>) => string;
  updateMessage: (id: string, updates: Partial<Message>) => void;
  setProcessing: (val: boolean) => void;
  setLoading: (val: boolean) => void;
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isProcessing: false,
  isLoading: false,
  
  addMessage: (msg) => {
    const id = Math.random().toString(36).substring(7);
    set((state) => ({
      messages: [...state.messages, { ...msg, id }]
    }));
    return id;
  },
  
  updateMessage: (id, updates) => {
    set((state) => ({
      messages: state.messages.map((m) => (m.id === id ? { ...m, ...updates } : m))
    }));
  },
  
  setProcessing: (isProcessing) => set({ isProcessing }),
  setLoading: (isLoading) => set({ isLoading }),
}));
