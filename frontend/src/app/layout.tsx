import './globals.css';
import React from 'react';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: 'Anubodh AI | Next-Gen Cognitive Personal Assistant',
  description: 'Anubodh is a personal AI assistant built with Google Gemini and persistent semantic vector memory. It remembers preferences, facts, and styles to tailor every interaction.',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@350;400;500;600;700;800&display=swap" rel="stylesheet" />
      </head>
      <body className="bg-background-deep text-slate-100 min-h-screen antialiased">
        {children}
      </body>
    </html>
  );
}
