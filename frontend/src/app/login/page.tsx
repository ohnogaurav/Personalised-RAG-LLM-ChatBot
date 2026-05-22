'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useStore } from '../../store/useStore';
import api from '../../lib/api';
import { Brain, Lock, Mail, User, Sparkles, AlertCircle } from 'lucide-react';

export default function LoginPage() {
  const router = useRouter();
  const { token, setToken, setUser } = useStore();
  
  const [isLogin, setIsLogin] = useState(true);
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [errorMsg, setErrorMsg] = useState('');
  const [loading, setLoading] = useState(false);

  // Redirect if user is already authenticated
  useEffect(() => {
    if (token) {
      router.push('/dashboard');
    }
  }, [token, router]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMsg('');
    setLoading(true);

    try {
      if (isLogin) {
        // Form Data serialization for standard OAuth2 endpoint in FastAPI
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);

        const response = await api.post('/auth/login', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        
        setToken(response.data.access_token);
        
        // Fetch current user details
        const meRes = await api.get('/auth/me');
        setUser(meRes.data);
        router.push('/dashboard');
      } else {
        // Register route
        const registerPayload = {
          email,
          password,
          full_name: fullName || null
        };
        await api.post('/auth/register', registerPayload);
        
        // Auto-login after registration
        const params = new URLSearchParams();
        params.append('username', email);
        params.append('password', password);
        const loginRes = await api.post('/auth/login', params, {
          headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
        });
        setToken(loginRes.data.access_token);
        
        const meRes = await api.get('/auth/me');
        setUser(meRes.data);
        router.push('/dashboard');
      }
    } catch (err: any) {
      console.error(err);
      setErrorMsg(err.response?.data?.detail || 'An error occurred. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex items-center justify-center bg-background-deep p-6 relative overflow-hidden">
      {/* Decorative Neon Blurs */}
      <div className="absolute top-1/4 left-1/4 w-96 h-96 bg-brand-indigo/10 rounded-full blur-[110px] pointer-events-none" />
      <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-brand-violet/10 rounded-full blur-[110px] pointer-events-none" />

      <div className="w-full max-w-md glass-panel p-8 rounded-3xl z-10 shadow-2xl relative border border-white/10">
        {/* Glowing border accent */}
        <div className="absolute -top-px left-10 right-10 h-px bg-gradient-to-r from-transparent via-brand-indigo/40 to-transparent" />

        {/* Logo and Header */}
        <div className="text-center mb-8">
          <div className="w-14 h-14 bg-brand-indigo/10 border border-brand-indigo/25 text-brand-indigo rounded-2xl flex items-center justify-center mx-auto mb-4">
            <Brain className="w-7 h-7" />
          </div>
          <h2 className="text-2xl font-bold tracking-tight text-white">
            {isLogin ? 'Welcome Back' : 'Create Account'}
          </h2>
          <p className="text-slate-400 text-xs mt-1">
            {isLogin ? 'Enter your details to log in to Aethera' : 'Get started with your personal AI assistant'}
          </p>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="space-y-4">
          {errorMsg && (
            <div className="p-3 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-xs flex items-center gap-2.5">
              <AlertCircle className="w-4 h-4 flex-shrink-0" />
              <span>{errorMsg}</span>
            </div>
          )}

          {!isLogin && (
            <div className="relative flex items-center">
              <User className="w-4 h-4 text-slate-500 absolute left-4" />
              <input
                type="text"
                placeholder="Full Name"
                value={fullName}
                onChange={(e) => setFullName(e.target.value)}
                className="w-full bg-white/5 text-slate-200 placeholder-slate-500 text-sm py-3 pl-11 pr-4 rounded-xl border border-white/10 focus:border-brand-indigo/60 outline-none transition-all"
              />
            </div>
          )}

          <div className="relative flex items-center">
            <Mail className="w-4 h-4 text-slate-500 absolute left-4" />
            <input
              type="email"
              placeholder="Email Address"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-white/5 text-slate-200 placeholder-slate-500 text-sm py-3 pl-11 pr-4 rounded-xl border border-white/10 focus:border-brand-indigo/60 outline-none transition-all"
            />
          </div>

          <div className="relative flex items-center">
            <Lock className="w-4 h-4 text-slate-500 absolute left-4" />
            <input
              type="password"
              placeholder="Password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-white/5 text-slate-200 placeholder-slate-500 text-sm py-3 pl-11 pr-4 rounded-xl border border-white/10 focus:border-brand-indigo/60 outline-none transition-all"
            />
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 bg-gradient-to-r from-brand-indigo to-brand-violet hover:from-indigo-500 hover:to-violet-500 text-white font-semibold rounded-xl text-sm transition-all duration-200 shadow-md shadow-brand-indigo/15 border border-indigo-400/20 active:scale-98 disabled:opacity-50"
          >
            {loading ? 'Authenticating...' : isLogin ? 'Sign In' : 'Sign Up'}
          </button>
        </form>

        {/* Toggle between Register/Login */}
        <div className="text-center mt-6">
          <button
            onClick={() => {
              setIsLogin(!isLogin);
              setErrorMsg('');
            }}
            className="text-xs text-slate-450 hover:text-brand-indigo transition-colors"
          >
            {isLogin ? "Don't have an account? Sign Up" : 'Already have an account? Sign In'}
          </button>
        </div>
      </div>
    </main>
  );
}
