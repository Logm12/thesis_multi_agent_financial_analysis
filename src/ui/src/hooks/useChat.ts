import { useState, useCallback, useRef } from 'react';

const API_BASE = "http://localhost:8001";

export function useChat() {
    const [messages, setMessages] = useState<any[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [currentStep, setCurrentStep] = useState<string | null>(null);
    const threadId = useRef(Math.random().toString(36).substring(7));

    const sendMessage = useCallback(async (text: string) => {
        if (!text.trim()) return;

        const userMsg = { role: 'user', content: text };
        setMessages(prev => [...prev, userMsg]);
        setIsLoading(true);
        setCurrentStep("Initializing...");

        const assistantMsgId = Date.now();
        setMessages(prev => [...prev, { id: assistantMsgId, role: 'assistant', content: '', steps: [] }]);

        try {
            const url = `${API_BASE}/chat-stream?message=${encodeURIComponent(text)}&thread_id=${threadId.current}`;
            const eventSource = new EventSource(url);

            eventSource.addEventListener('step', (event) => {
                const data = JSON.parse(event.data);
                setCurrentStep(data.output);
                setMessages(prev => prev.map(m => 
                    m.id === assistantMsgId 
                    ? { ...m, steps: [...(m.steps || []), data.output] } 
                    : m
                ));
            });

            eventSource.addEventListener('final_answer', (event) => {
                const data = JSON.parse(event.data);
                setMessages(prev => prev.map(m => 
                    m.id === assistantMsgId 
                    ? { ...m, content: data.content } 
                    : m
                ));
            });

            eventSource.addEventListener('done', () => {
                eventSource.close();
                setIsLoading(false);
                setCurrentStep(null);
            });

            eventSource.addEventListener('error', (event) => {
                console.error("SSE Error:", event);
                eventSource.close();
                setIsLoading(false);
                setCurrentStep("Error occurred.");
            });

        } catch (error) {
            console.error("Failed to connect to chat stream:", error);
            setIsLoading(false);
        }
    }, []);

    return { messages, sendMessage, isLoading, currentStep };
}
