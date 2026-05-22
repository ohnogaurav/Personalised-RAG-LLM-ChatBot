import { create } from 'zustand';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  created_at: string;
}

export interface ChatSession {
  id: string;
  user_id: string;
  title: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  session_id: string;
  role: 'user' | 'assistant';
  content: string;
  created_at: string;
}

export interface Memory {
  id: string;
  user_id: string;
  category: string;
  fact: string;
  confidence: number;
  is_active: boolean;
  created_at: string;
}

interface AppState {
  token: string | null;
  user: User | null;
  sessions: ChatSession[];
  activeSessionId: string | null;
  messages: Message[];
  memories: Memory[];
  isChatLoading: boolean;
  isMemoryLoading: boolean;
  
  // Setters & Actions
  setToken: (token: string | null) => void;
  setUser: (user: User | null) => void;
  setSessions: (sessions: ChatSession[]) => void;
  setActiveSessionId: (id: string | null) => void;
  setMessages: (messages: Message[]) => void;
  addMessage: (message: Message) => void;
  setMemories: (memories: Memory[]) => void;
  addMemory: (memory: Memory) => void;
  setChatLoading: (loading: boolean) => void;
  setMemoryLoading: (loading: boolean) => void;
  logout: () => void;
}

export const useStore = create<AppState>((set) => ({
  token: typeof window !== 'undefined' ? localStorage.getItem('token') : null,
  user: null,
  sessions: [],
  activeSessionId: null,
  messages: [],
  memories: [],
  isChatLoading: false,
  isMemoryLoading: false,

  setToken: (token) => {
    if (token) {
      localStorage.setItem('token', token);
    } else {
      localStorage.removeItem('token');
    }
    set({ token });
  },
  setUser: (user) => set({ user }),
  setSessions: (sessions) => set({ sessions }),
  setActiveSessionId: (activeSessionId) => set({ activeSessionId }),
  setMessages: (messages) => set({ messages }),
  addMessage: (message) => set((state) => ({ messages: [...state.messages, message] })),
  setMemories: (memories) => set({ memories }),
  addMemory: (memory) => set((state) => ({ memories: [memory, ...state.memories] })),
  setChatLoading: (isChatLoading) => set({ isChatLoading }),
  setMemoryLoading: (isMemoryLoading) => set({ isMemoryLoading }),
  logout: () => {
    localStorage.removeItem('token');
    set({ token: null, user: null, sessions: [], activeSessionId: null, messages: [], memories: [] });
  }
}));
