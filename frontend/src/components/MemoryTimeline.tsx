import React, { useEffect, useState } from 'react';
import { useStore, Memory } from '../store/useStore';
import api from '../lib/api';
import { ToggleLeft, ToggleRight, Trash2, Brain, Sparkles, AlertCircle, RefreshCw } from 'lucide-react';

export const MemoryTimeline: React.FC = () => {
  const { memories, setMemories, isMemoryLoading, setMemoryLoading } = useStore();
  const [filterCategory, setFilterCategory] = useState<string>('all');

  const fetchMemories = async () => {
    setMemoryLoading(true);
    try {
      const response = await api.get('/memories');
      setMemories(response.data);
    } catch (error) {
      console.error('Error fetching memories:', error);
    } finally {
      setMemoryLoading(false);
    }
  };

  useEffect(() => {
    fetchMemories();
  }, []);

  const handleToggleActive = async (memoryId: string, currentStatus: boolean) => {
    try {
      const response = await api.put(`/memories/${memoryId}`, { is_active: !currentStatus });
      setMemories(memories.map(m => m.id === memoryId ? response.data : m));
    } catch (error) {
      console.error('Error updating memory status:', error);
    }
  };

  const handleDeleteMemory = async (memoryId: string) => {
    try {
      await api.delete(`/memories/${memoryId}`);
      setMemories(memories.filter(m => m.id !== memoryId));
    } catch (error) {
      console.error('Error deleting memory:', error);
    }
  };

  // Get distinct categories
  const categories = ['all', ...Array.from(new Set(memories.map(m => m.category)))];

  const filteredMemories = filterCategory === 'all'
    ? memories
    : memories.filter(m => m.category === filterCategory);

  // Group facts by category for analytics cards
  const categoryCounts = memories.reduce((acc, m) => {
    acc[m.category] = (acc[m.category] || 0) + 1;
    return acc;
  }, {} as Record<string, number>);

  return (
    <div className="flex-1 flex flex-col h-full bg-background-deep overflow-y-auto px-8 py-10 relative">
      {/* Decorative Blur Backgrounds */}
      <div className="absolute top-10 right-10 w-96 h-96 bg-brand-violet/5 rounded-full blur-[120px] pointer-events-none" />

      {/* Header and Sync */}
      <div className="flex justify-between items-center mb-8 z-10">
        <div>
          <h2 className="text-2xl font-bold tracking-tight text-white flex items-center gap-3">
            <Brain className="w-7 h-7 text-brand-indigo" />
            Cognitive Memory Space
          </h2>
          <p className="text-slate-400 text-sm mt-1">
            Review, edit, and control everything Anubodh knows about your preferences and facts.
          </p>
        </div>
        <button
          onClick={fetchMemories}
          disabled={isMemoryLoading}
          className="flex items-center gap-2 py-2 px-4 rounded-xl text-xs font-semibold bg-white/5 hover:bg-white/10 text-slate-300 transition-all border border-white/5 active:scale-95"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isMemoryLoading ? 'animate-spin' : ''}`} />
          Refresh Core
        </button>
      </div>

      {/* Quick Analytics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-8 z-10">
        <div className="glass-panel p-5 rounded-2xl border border-white/5">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Total Facts learned</span>
          <div className="text-3xl font-extrabold text-white mt-1.5">{memories.length}</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl border border-white/5">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Active Memories</span>
          <div className="text-3xl font-extrabold text-brand-indigo mt-1.5">
            {memories.filter(m => m.is_active).length}
          </div>
        </div>
        <div className="glass-panel p-5 rounded-2xl border border-white/5">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Unique Categories</span>
          <div className="text-3xl font-extrabold text-brand-cyan mt-1.5">{categories.length - 1}</div>
        </div>
        <div className="glass-panel p-5 rounded-2xl border border-white/5">
          <span className="text-xs font-semibold text-slate-500 uppercase tracking-wider">Memory Confidence</span>
          <div className="text-3xl font-extrabold text-brand-emerald mt-1.5">
            {memories.length > 0
              ? `${Math.round((memories.reduce((acc, m) => acc + m.confidence, 0) / memories.length) * 100)}%`
              : 'N/A'}
          </div>
        </div>
      </div>

      {/* Filters */}
      <div className="flex gap-2 mb-6 overflow-x-auto pb-2 z-10 scrollbar-none">
        {categories.map(cat => (
          <button
            key={cat}
            onClick={() => setFilterCategory(cat)}
            className={`py-2 px-4 rounded-xl text-xs font-medium capitalize border transition-all duration-150 ${
              filterCategory === cat
                ? 'bg-brand-indigo/15 border-brand-indigo/35 text-indigo-300'
                : 'bg-white/5 border-transparent text-slate-400 hover:text-slate-200 hover:bg-white/10'
            }`}
          >
            {cat} {cat !== 'all' ? `(${categoryCounts[cat] || 0})` : ''}
          </button>
        ))}
      </div>

      {/* Timeline Section */}
      <div className="flex-1 z-10">
        {isMemoryLoading ? (
          <div className="text-center py-20 text-slate-400 text-sm">
            Syncing synapses...
          </div>
        ) : filteredMemories.length === 0 ? (
          <div className="glass-panel p-10 rounded-2xl text-center max-w-md mx-auto space-y-4 border border-white/5">
            <AlertCircle className="w-10 h-10 text-slate-600 mx-auto" />
            <h3 className="text-lg font-semibold text-slate-350">No memories found</h3>
            <p className="text-slate-500 text-xs leading-relaxed">
              When you talk to Anubodh, facts starting with things like "I am", "I love", or specific preferences will be automatically extracted and visible here.
            </p>
          </div>
        ) : (
          <div className="space-y-4 max-w-4xl">
            {filteredMemories.map((mem) => (
              <div
                key={mem.id}
                className={`glass-card p-5 rounded-2xl flex items-center justify-between gap-4 transition-all duration-200 ${
                  !mem.is_active ? 'opacity-40 hover:opacity-60' : ''
                }`}
              >
                <div className="flex items-center gap-4">
                  {/* Category icon indicator */}
                  <div className={`p-2.5 rounded-xl border flex-shrink-0 ${
                    mem.is_active
                      ? 'bg-brand-indigo/10 border-brand-indigo/20 text-brand-indigo'
                      : 'bg-slate-800/40 border-slate-700/30 text-slate-500'
                  }`}>
                    <Sparkles className="w-4 h-4" />
                  </div>
                  
                  <div>
                    <div className="flex items-center gap-2">
                      <span className="text-[10px] uppercase font-bold tracking-widest text-slate-500">
                        {mem.category}
                      </span>
                      <span className="text-[10px] bg-white/5 py-0.5 px-2 rounded-full border border-white/5 text-slate-400">
                        Conf: {Math.round(mem.confidence * 100)}%
                      </span>
                    </div>
                    <p className="text-sm font-medium text-slate-200 mt-1">{mem.fact}</p>
                    <span className="text-[10px] text-slate-500 block mt-1.5">
                      Learned on {new Date(mem.created_at).toLocaleDateString()}
                    </span>
                  </div>
                </div>

                {/* Control switches and actions */}
                <div className="flex items-center gap-3">
                  <button
                    onClick={() => handleToggleActive(mem.id, mem.is_active)}
                    className={`p-1.5 rounded-lg border transition-all duration-150 ${
                      mem.is_active
                        ? 'text-brand-indigo hover:bg-brand-indigo/10 border-brand-indigo/20'
                        : 'text-slate-500 hover:bg-slate-700/20 border-slate-700/30'
                    }`}
                    title={mem.is_active ? 'Deactivate Memory' : 'Activate Memory'}
                  >
                    {mem.is_active ? (
                      <ToggleRight className="w-6 h-6" />
                    ) : (
                      <ToggleLeft className="w-6 h-6" />
                    )}
                  </button>
                  
                  <button
                    onClick={() => handleDeleteMemory(mem.id)}
                    className="p-2 border border-transparent hover:border-red-500/25 hover:bg-red-500/10 rounded-lg text-slate-500 hover:text-red-400 transition-all duration-150"
                    title="Delete Memory"
                  >
                    <Trash2 className="w-4.5 h-4.5" />
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};
