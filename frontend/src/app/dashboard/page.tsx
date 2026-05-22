'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '../../store/useStore';
import api from '../../lib/api';
import { Sidebar } from '../../components/Sidebar';
import { ChatArea } from '../../components/ChatArea';
import { MemoryTimeline } from '../../components/MemoryTimeline';

export default function DashboardPage() {
  const router = useRouter();
  const { token, setUser, setSessions, setActiveSessionId, logout } = useStore();
  const [activeTab, setActiveTab] = useState<'chat' | 'memory'>('chat');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Redirect if there is no token
    if (!token) {
      router.push('/login');
      return;
    }

    const initDashboard = async () => {
      try {
        // Fetch current user details
        const meRes = await api.get('/auth/me');
        setUser(meRes.data);

        // Fetch user chat sessions
        const sessionsRes = await api.get('/chats');
        setSessions(sessionsRes.data);

        // Auto-select the most recent session if available
        if (sessionsRes.data.length > 0) {
          setActiveSessionId(sessionsRes.data[0].id);
        }
      } catch (error: any) {
        console.error('Failed to initialize dashboard:', error);
        // If credentials expire, log out and redirect
        if (error.response?.status === 401) {
          logout();
          router.push('/login');
        }
      } finally {
        setLoading(false);
      }
    };

    initDashboard();
  }, [token, router, setUser, setSessions, setActiveSessionId, logout]);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-background-deep">
        <div className="text-center space-y-4">
          {/* Glowing orbital loading indicator */}
          <div className="relative w-12 h-12 mx-auto">
            <div className="absolute inset-0 rounded-full border-2 border-brand-indigo/25" />
            <div className="absolute inset-0 rounded-full border-2 border-t-brand-indigo animate-spin" />
          </div>
          <p className="text-slate-400 text-xs tracking-wider uppercase font-semibold">
            Connecting to Cognitive Core...
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="h-screen flex overflow-hidden bg-background-deep">
      {/* Interactive Sidebar */}
      <Sidebar activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* Main Workspace content */}
      <main className="flex-1 flex flex-col min-w-0 overflow-hidden relative">
        {activeTab === 'chat' ? (
          <ChatArea />
        ) : (
          <MemoryTimeline />
        )}
      </main>
    </div>
  );
}
