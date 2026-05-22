import React, { useState, useEffect, useRef } from 'react';
import { useStore, Message } from '../store/useStore';
import api, { WS_BASE_URL } from '../lib/api';
import { Send, ArrowDown, Bot, User, Sparkles } from 'lucide-react';

export const ChatArea: React.FC = () => {
  const { activeSessionId, messages, setMessages, addMessage, token } = useStore();
  const [inputText, setInputText] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [streamingContent, setStreamingContent] = useState('');
  const [socket, setSocket] = useState<WebSocket | null>(null);
  
  const chatEndRef = useRef<HTMLDivElement>(null);
  const socketRef = useRef<WebSocket | null>(null);

  // Fetch chat history when session changes
  useEffect(() => {
    if (!activeSessionId) return;

    const fetchHistory = async () => {
      try {
        const response = await api.get(`/chats/${activeSessionId}`);
        setMessages(response.data.messages);
      } catch (error) {
        console.error('Error fetching chat history:', error);
      }
    };

    fetchHistory();
  }, [activeSessionId, setMessages]);

  // Establish WebSocket connection
  useEffect(() => {
    if (!activeSessionId || !token) return;

    // Close existing socket
    if (socketRef.current) {
      socketRef.current.close();
    }

    const wsUrl = `${WS_BASE_URL}/chats/ws/${activeSessionId}?token=${token}`;
    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;
    setSocket(ws);

    ws.onopen = () => {
      console.log('WebSocket connection established');
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);

      if (data.type === 'status' && data.content === 'thinking') {
        setIsTyping(true);
      } else if (data.type === 'content') {
        setIsTyping(false);
        setStreamingContent((prev) => prev + data.content);
      } else if (data.type === 'done') {
        // Chat generation complete, clear streaming state and refresh session
        setIsTyping(false);
        setStreamingContent('');
        
        // Refresh local message list from DB
        const refreshMessages = async () => {
          const res = await api.get(`/chats/${activeSessionId}`);
          setMessages(res.data.messages);
        };
        refreshMessages();
      } else if (data.type === 'error') {
        console.error('WebSocket Error message:', data.content);
        setIsTyping(false);
      }
    };

    ws.onclose = () => {
      console.log('WebSocket connection closed');
    };

    return () => {
      ws.close();
    };
  }, [activeSessionId, token, setMessages]);

  // Auto-scroll to bottom of chat
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, streamingContent, isTyping]);

  const handleSendMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inputText.trim() || !socket || socket.readyState !== WebSocket.OPEN) return;

    // Add user message locally for immediate UI update
    const tempUserMsg: Message = {
      id: Date.now().toString(),
      session_id: activeSessionId!,
      role: 'user',
      content: inputText,
      created_at: new Date().toISOString()
    };
    addMessage(tempUserMsg);

    // Send via socket
    socket.send(JSON.stringify({ content: inputText }));
    setInputText('');
  };

  if (!activeSessionId) {
    return (
      <div className="flex-1 flex flex-col items-center justify-center p-8 text-center bg-background-deep relative">
        {/* Futuristic glowing ambient background circles */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-96 h-96 bg-brand-indigo/10 rounded-full blur-[100px] pointer-events-none" />
        <div className="absolute top-1/3 left-1/2 -translate-x-1/2 w-64 h-64 bg-brand-violet/10 rounded-full blur-[80px] pointer-events-none" />

        <div className="max-w-md space-y-6 z-10">
          <div className="w-16 h-16 bg-white/5 border border-white/10 rounded-2xl flex items-center justify-center mx-auto text-brand-indigo shadow-inner">
            <Sparkles className="w-8 h-8 animate-pulse" />
          </div>
          <div>
            <h2 className="text-2xl font-bold tracking-tight text-white mb-2">Welcome to Aethera</h2>
            <p className="text-slate-400 text-sm leading-relaxed">
              Your next-generation personal assistant platform. Select a chat from the sidebar or start a new thread to begin learning and reasoning.
            </p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex-1 flex flex-col h-full bg-background-deep relative overflow-hidden">
      {/* Dynamic Background Aura */}
      <div className="absolute -top-40 -right-40 w-96 h-96 bg-brand-indigo/5 rounded-full blur-[120px] pointer-events-none" />

      {/* Message History area */}
      <div className="flex-1 overflow-y-auto px-6 py-8 space-y-6 scroll-smooth">
        {messages.map((msg) => (
          <div
            key={msg.id}
            className={`flex gap-4 max-w-3xl ${
              msg.role === 'user' ? 'ml-auto flex-row-reverse' : ''
            }`}
          >
            {/* Avatar */}
            <div
              className={`w-9 h-9 rounded-xl flex items-center justify-center font-semibold text-sm border flex-shrink-0 ${
                msg.role === 'user'
                  ? 'bg-brand-indigo/20 border-brand-indigo/35 text-indigo-300'
                  : 'bg-white/5 border-white/10 text-slate-300'
              }`}
            >
              {msg.role === 'user' ? <User className="w-4 h-4" /> : <Bot className="w-4 h-4 text-brand-indigo" />}
            </div>

            {/* Bubble */}
            <div
              className={`p-4 rounded-2xl text-sm leading-relaxed ${
                msg.role === 'user'
                  ? 'bg-brand-indigo/20 border border-brand-indigo/30 text-slate-100 rounded-tr-none'
                  : 'bg-white/[0.03] border border-white/[0.05] text-slate-350 rounded-tl-none backdrop-blur-sm'
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {/* Typing indicator */}
        {isTyping && (
          <div className="flex gap-4 max-w-3xl">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-white/5 border border-white/10 flex-shrink-0">
              <Bot className="w-4 h-4 text-brand-indigo" />
            </div>
            <div className="bg-white/[0.03] border border-white/[0.05] p-4 rounded-2xl rounded-tl-none flex items-center gap-1.5 backdrop-blur-sm">
              <div className="w-2 h-2 bg-brand-indigo rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
              <div className="w-2 h-2 bg-brand-indigo rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
              <div className="w-2 h-2 bg-brand-indigo rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
            </div>
          </div>
        )}

        {/* Real-time Streaming assistant reply */}
        {streamingContent && (
          <div className="flex gap-4 max-w-3xl">
            <div className="w-9 h-9 rounded-xl flex items-center justify-center bg-white/5 border border-white/10 flex-shrink-0">
              <Bot className="w-4 h-4 text-brand-indigo" />
            </div>
            <div className="bg-white/[0.03] border border-white/[0.05] p-4 rounded-2xl rounded-tl-none text-sm leading-relaxed text-slate-300 backdrop-blur-sm">
              {streamingContent}
            </div>
          </div>
        )}

        <div ref={chatEndRef} />
      </div>

      {/* Input panel */}
      <div className="p-6 border-t border-slate-900 bg-black/10 backdrop-blur-md">
        <form onSubmit={handleSendMessage} className="max-w-3xl mx-auto relative flex items-center">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder="Talk to Aethera... (e.g. 'I love vanilla ice cream')"
            className="w-full bg-white/5 focus:bg-white/[0.08] text-slate-100 placeholder-slate-500 text-sm py-3.5 pl-5 pr-14 rounded-2xl border border-white/10 focus:border-brand-indigo/60 focus:ring-1 focus:ring-brand-indigo/40 outline-none transition-all duration-200"
          />
          <button
            type="submit"
            disabled={!inputText.trim()}
            className="absolute right-2 p-2 bg-brand-indigo hover:bg-indigo-500 disabled:opacity-30 text-white rounded-xl transition-all duration-150 shadow-md shadow-brand-indigo/20 border border-indigo-400/20"
          >
            <Send className="w-4.5 h-4.5" />
          </button>
        </form>
        <p className="text-[10px] text-center text-slate-500 mt-3 tracking-wide">
          Aethera auto-extracts memory facts in the background to continuously adapt to you.
        </p>
      </div>
    </div>
  );
};
