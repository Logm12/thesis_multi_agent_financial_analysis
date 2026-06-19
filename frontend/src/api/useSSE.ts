import { useEffect, useRef, useState, useCallback } from 'react';
import type { ChartData } from '../types/chat';

interface SSEOptions {
  onStep?: (data: { node: string; output: string }) => void;
  onFinalAnswer?: (data: { content: string; chart_url?: string | null; chart_data?: ChartData[] | null; chart_type?: 'bar' | 'line' }) => void;
  onDone?: () => void;
  onError?: (err: unknown) => void;
}

export const useSSE = () => {
  const [isConnected, setIsConnected] = useState(false);
  const eventSourceRef = useRef<EventSource | null>(null);

  const disconnect = useCallback(() => {
    if (eventSourceRef.current) {
      eventSourceRef.current.close();
      eventSourceRef.current = null;
      setIsConnected(false);
    }
  }, []);

  const connect = useCallback((url: string, options: SSEOptions = {}) => {
    disconnect();

    const eventSource = new EventSource(url, { withCredentials: true });
    eventSourceRef.current = eventSource;
    setIsConnected(true);

    eventSource.addEventListener('step', (event) => {
      try {
        const data = JSON.parse(event.data);
        if (options.onStep) {
          options.onStep(data);
        }
      } catch (e) {
        console.error('Error parsing SSE step event:', e);
      }
    });

    eventSource.addEventListener('final_answer', (event) => {
      try {
        const data = JSON.parse(event.data);
        if (options.onFinalAnswer) {
          options.onFinalAnswer(data);
        }
      } catch (e) {
        console.error('Error parsing SSE final_answer event:', e);
      }
    });

    eventSource.addEventListener('done', () => {
      disconnect();
      if (options.onDone) {
        options.onDone();
      }
    });

    eventSource.addEventListener('error', (event) => {
      disconnect();
      if (options.onError) {
        options.onError(event);
      }
    });
  }, [disconnect]);

  useEffect(() => {
    return () => {
      disconnect();
    };
  }, [disconnect]);

  return { connect, disconnect, isConnected };
};
