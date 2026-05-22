import React from 'react';
import { useStore, ChatSession } from '../store/useStore';
import api from '../lib/api';
import { MessageSquare, Plus, LogOut, Brain, User, Trash2 } from 'lucide-react';

interface SidebarProps {
  activeTab: 'chat' | 'memory';
  setActiveTab: (tab: 'chat' | 'memory') => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const { sessions, setSessions, activeSessionId, setActiveSessionId, user, logout } = useStore();

  const handleCreateSession = async () => {
    try {
      const response = await api.post('/chats', { title: `Chat #${sessions.length + 1}` });
      setSessions([response.data, ...sessions]);
      setActiveSessionId(response.data.id);
      setActiveTab('chat');
    } catch (error) {
      console.error('Error creating chat session:', error);
    }
  };

  const handleDeleteSession = async (e: React.MouseEvent, sessionId: string) => {
    e.stopPropagation();
    try {
      await api.delete(`/chats/${sessionId}`);
      const updated = sessions.filter(s => s.id !== sessionId);
      setSessions(updated);
      if (activeSessionId === sessionId) {
        setActiveSessionId(updated.length > 0 ? updated[0].id : null);
      }
    } catch (error) {
      console.error('Error deleting session:', error);
    }
  };

  return (
    <aside className="w-80 glass-panel border-r border-slate-800 flex flex-col h-full z-10">
      {/* Brand Header */}
      <div className="p-6 border-b border-slate-800 flex items-center gap-3">
        <div className="bg-brand-indigo/20 p-2.5 rounded-xl border border-brand-indigo/30">
          <Brain className="w-6 h-6 text-brand-indigo animate-pulse-slow" />
        </div>
        <div>
          <h1 className="text-xl font-bold tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white via-indigo-100 to-indigo-300">
            Aethera AI
          </h1>
          <span className="text-[10px] uppercase font-semibold text-brand-indigo tracking-widest">
            Cognitive Core
          </span>
        </div>
      </div>

      {/* Tabs Switcher */}
      <div className="px-4 py-4 border-b border-slate-850 flex gap-2">
        <button
          onClick={() => setActiveTab('chat')}
          className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium flex items-center justify-center gap-2 transition-all duration-200 ${
            activeTab === 'chat'
              ? 'bg-brand-indigo text-white shadow-lg shadow-brand-indigo/20'
              : 'bg-white/5 text-slate-400 hover:text-white hover:bg-white/10'
          }`}
        >
          <MessageSquare className="w-4 h-4" />
          Chats
        </button>
        <button
          onClick={() => setActiveTab('memory')}
          className={`flex-1 py-2 px-3 rounded-lg text-sm font-medium flex items-center justify-center gap-2 transition-all duration-200 ${
            activeTab === 'memory'
              ? 'bg-brand-indigo text-white shadow-lg shadow-brand-indigo/20'
              : 'bg-white/5 text-slate-400 hover:text-white hover:bg-white/10'
          }`}
        >
          <Brain className="w-4 h-4" />
          Memory
        </button>
      </div>

      {/* New Conversation Button */}
      <div className="p-4">
        <button
          onClick={handleCreateSession}
          className="w-full py-2.5 px-4 bg-gradient-to-r from-brand-indigo to-brand-violet hover:from-indigo-500 hover:to-violet-500 text-white font-medium rounded-xl text-sm flex items-center justify-center gap-2 transition-all duration-200 shadow-md shadow-brand-indigo/10 border border-indigo-400/20"
        >
          <Plus className="w-4 h-4" />
          New Conversation
        </button>
      </div>

      {/* Sessions list */}
      <div className="flex-1 overflow-y-auto px-3 space-y-1 py-2">
        {sessions.length === 0 ? (
          <div className="text-center text-xs text-slate-500 py-8">
            No conversations yet
          </div>
        ) : (
          sessions.map((session) => (
            <div
              key={session.id}
              onClick={() => {
                setActiveSessionId(session.id);
                setActiveTab('chat');
              }}
              className={`group flex items-center justify-between p-3 rounded-xl cursor-pointer transition-all duration-150 ${
                activeSessionId === session.id
                  ? 'bg-brand-indigo/15 text-indigo-200 border border-brand-indigo/35'
                  : 'text-slate-400 hover:bg-white/5 hover:text-slate-200 border border-transparent'
              }`}
            >
              <div className="flex items-center gap-3 overflow-hidden">
                <MessageSquare className={`w-4.5 h-4.5 flex-shrink-0 ${activeSessionId === session.id ? 'text-brand-indigo' : 'text-slate-500'}`} />
                <span className="text-sm font-medium truncate">{session.title}</span>
              </div>
              <button
                onClick={(e) => handleDeleteSession(e, session.id)}
                className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/10 rounded text-slate-500 hover:text-red-400 transition-all duration-150"
              >
                <Trash2 className="w-3.5 h-3.5" />
              </button>
            </div>
          ))
        )}
      </div>

      {/* User footer profile */}
      <div className="p-4 border-t border-slate-800 bg-black/20 flex items-center justify-between">
        <div className="flex items-center gap-3 overflow-hidden">
          <div className="w-9 h-9 rounded-full bg-brand-violet/20 border border-brand-violet/30 flex items-center justify-center text-brand-violet font-bold flex-shrink-0">
            {user?.email[0].toUpperCase() || <User className="w-4 h-4" />}
          </div>
          <div className="overflow-hidden">
            <h4 className="text-xs font-semibold text-white truncate">
              {user?.full_name || 'User'}
            </h4>
            <p className="text-[10px] text-slate-500 truncate">{user?.email}</p>
          </div>
        </div>
        <button
          onClick={logout}
          className="p-2 hover:bg-white/5 rounded-lg text-slate-500 hover:text-white transition-all duration-150"
          title="Sign Out"
        >
          <LogOut className="w-4.5 h-4.5" />
        </button>
      </div>
    </aside>
  );
};
