'use client';

import React from 'react';
import Link from 'next/link';
import { Brain, Sparkles, Cpu, Shield, ArrowRight, Activity } from 'lucide-react';

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background-deep text-slate-100 flex flex-col relative overflow-hidden">
      {/* Dynamic Glowing Ambient Circles */}
      <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-brand-indigo/10 rounded-full blur-[120px] pointer-events-none" />
      <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-brand-violet/10 rounded-full blur-[120px] pointer-events-none" />

      {/* Navigation Header */}
      <header className="max-w-7xl mx-auto w-full px-6 py-6 flex items-center justify-between z-10">
        <div className="flex items-center gap-3">
          <div className="bg-brand-indigo/20 p-2 rounded-xl border border-brand-indigo/35">
            <Brain className="w-6 h-6 text-brand-indigo" />
          </div>
          <span className="font-bold text-lg tracking-tight bg-clip-text text-transparent bg-gradient-to-r from-white to-slate-200">
            Anubodh AI
          </span>
        </div>
        <Link
          href="/login"
          className="py-2 px-5 bg-white/5 border border-white/10 hover:bg-white/10 hover:border-brand-indigo/30 text-sm font-semibold rounded-xl transition-all duration-200"
        >
          Sign In
        </Link>
      </header>

      {/* Hero Section */}
      <main className="flex-1 max-w-7xl mx-auto w-full px-6 flex flex-col items-center justify-center text-center py-20 z-10 space-y-8">
        {/* Release Pill */}
        <div className="inline-flex items-center gap-2 px-3.5 py-1.5 rounded-full bg-brand-indigo/15 border border-brand-indigo/30 text-xs font-semibold text-indigo-300 shadow-lg shadow-brand-indigo/5">
          <Sparkles className="w-3.5 h-3.5" />
          <span>Next-Generation Cognitive Core</span>
        </div>

        {/* Hero Title */}
        <div className="space-y-4 max-w-3xl">
          <h1 className="text-5xl md:text-7xl font-extrabold tracking-tight text-white leading-tight">
            The AI assistant that{' '}
            <span className="bg-clip-text text-transparent bg-gradient-to-r from-brand-indigo via-brand-violet to-brand-cyan">
              actually remembers
            </span>
          </h1>
          <p className="text-slate-400 text-base md:text-lg max-w-xl mx-auto leading-relaxed">
            Anubodh is a personal cognitive partner. It automatically extracts memories, facts, and preferences in real time to form a permanent, contextual vector profile.
          </p>
        </div>

        {/* CTA */}
        <div className="pt-4">
          <Link
            href="/login"
            className="group inline-flex items-center gap-2.5 py-4 px-8 bg-gradient-to-r from-brand-indigo to-brand-violet hover:from-indigo-500 hover:to-violet-500 text-white font-bold rounded-2xl text-base transition-all duration-200 shadow-xl shadow-brand-indigo/25 border border-indigo-400/20 hover:scale-[1.02] active:scale-[0.98]"
          >
            Launch Core Space
            <ArrowRight className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
          </Link>
        </div>

        {/* Features Matrix Grid */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-5xl w-full pt-20">
          <div className="glass-panel p-6 rounded-2xl text-left border border-white/5 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-brand-indigo/10 border border-brand-indigo/20 text-brand-indigo flex items-center justify-center">
              <Activity className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Advanced RAG Architecture</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Queries are contextualized in real-time by running semantic searches against your personal vector database.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl text-left border border-white/5 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-brand-violet/10 border border-brand-violet/20 text-brand-violet flex items-center justify-center">
              <Cpu className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Intelligent Fact Extraction</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              Background LLM tasks automatically process dialogue, categorize data, and continuously resolve conflicting information.
            </p>
          </div>

          <div className="glass-panel p-6 rounded-2xl text-left border border-white/5 space-y-3">
            <div className="w-10 h-10 rounded-xl bg-brand-cyan/10 border border-brand-cyan/20 text-brand-cyan flex items-center justify-center">
              <Shield className="w-5 h-5" />
            </div>
            <h3 className="text-base font-bold text-white">Isolated Tenancy Security</h3>
            <p className="text-xs text-slate-400 leading-relaxed">
              JWT-restricted sessions paired with Qdrant vector-level metadata filtering ensure absolute privacy and data isolation.
            </p>
          </div>
        </div>
      </main>

      {/* Footer */}
      <footer className="max-w-7xl mx-auto w-full px-6 py-8 border-t border-slate-900 text-center text-xs text-slate-650 z-10">
        &copy; 2026 Anubodh AI Technologies. All rights reserved. Built with Gemini 2.5 and FastAPI.
      </footer>
    </div>
  );
}
