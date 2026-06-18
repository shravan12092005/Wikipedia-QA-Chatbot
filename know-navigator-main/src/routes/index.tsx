import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import { Download, Menu, Moon, Share2, Sun, BarChart3, Loader2 } from "lucide-react";
import { Sidebar } from "@/sidebar/Sidebar";
import { WelcomeHero } from "@/chat/WelcomeHero";
import { ChatInput } from "@/chat/ChatInput";
import { MessageBubble } from "@/chat/MessageBubble";
import { TypingIndicator } from "@/chat/TypingIndicator";
import { ResearchPanel } from "@/dashboard/ResearchPanel";
import { AuthPage } from "@/auth/AuthPage";
import { useWikiChat } from "@/hooks/useWikiChat";
import { supabase } from "@/services/supabase";
import type { User } from "@supabase/supabase-js";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Wikipedia Research Assistant — AI-powered research with citations" },
      { name: "description", content: "Premium AI chatbot that answers your questions with cited Wikipedia sources, confidence scores, and beautiful citation cards." },
      { property: "og:title", content: "Wikipedia Research Assistant" },
      { property: "og:description", content: "AI-powered research assistant with source citations." },
      { property: "og:type", content: "website" },
    ],
  }),
  component: Index,
});

function Index() {
  const [user, setUser] = useState<User | null>(null);
  const [authLoading, setAuthLoading] = useState(true);

  // Subscribe to authentication session state
  useEffect(() => {
    supabase.auth.getSession().then(({ data: { session } }) => {
      setUser(session?.user ?? null);
      setAuthLoading(false);
    });

    const { data: { subscription } } = supabase.auth.onAuthStateChange((_event, session) => {
      setUser(session?.user ?? null);
      setAuthLoading(false);
    });

    return () => {
      subscription.unsubscribe();
    };
  }, []);

  const { 
    conversations, 
    activeChatId, 
    messages, 
    sessionState, 
    isStreaming, 
    send, 
    clear, 
    selectChat, 
    toggleBookmark 
  } = useWikiChat();

  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [researchPanelOpen, setResearchPanelOpen] = useState(true);
  const [light, setLight] = useState(false);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    el.scrollTo({ top: el.scrollHeight, behavior: "smooth" });
  }, [messages, isStreaming]);

  useEffect(() => {
    if (typeof document === "undefined") return;
    document.documentElement.classList.toggle("light", light);
  }, [light]);

  // Loader screen
  if (authLoading) {
    return (
      <div className="flex h-screen w-full items-center justify-center bg-background">
        <Loader2 className="h-8 w-8 animate-spin text-primary" />
      </div>
    );
  }

  // Redirect to login if not authenticated
  if (!user) {
    return <AuthPage />;
  }

  return (
    <div className="relative flex h-screen w-full overflow-hidden bg-background">
      {/* Background aurora */}
      <div className="aurora pointer-events-none absolute inset-0 opacity-60" />

      {/* Sidebar desktop */}
      <div className="hidden lg:flex relative z-10">
        <Sidebar 
          user={user} 
          conversations={conversations}
          activeChatId={activeChatId}
          onSelectChat={selectChat}
          onNewChat={() => selectChat(null)}
          onClear={clear} 
          hasMessages={messages.length > 0} 
        />
      </div>

      {/* Sidebar mobile drawer */}
      {sidebarOpen && (
        <div className="fixed inset-0 z-40 lg:hidden">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setSidebarOpen(false)} />
          <div className="absolute left-0 top-0 h-full">
            <Sidebar
              user={user}
              conversations={conversations}
              activeChatId={activeChatId}
              onSelectChat={(id) => { selectChat(id); setSidebarOpen(false); }}
              onNewChat={() => { selectChat(null); setSidebarOpen(false); }}
              onClear={() => { clear(); setSidebarOpen(false); }}
              hasMessages={messages.length > 0}
              onClose={() => setSidebarOpen(false)}
            />
          </div>
        </div>
      )}

      {/* Main */}
      <main className="relative z-10 flex min-w-0 flex-1 flex-col">
        {/* Top bar */}
        <header className="flex h-14 shrink-0 items-center justify-between border-b border-border/60 px-4 backdrop-blur-md">
          <div className="flex items-center gap-2">
            <button
              onClick={() => setSidebarOpen(true)}
              className="grid h-9 w-9 place-items-center rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground lg:hidden"
              aria-label="Open sidebar"
            >
              <Menu className="h-4 w-4" />
            </button>
            <div className="hidden items-center gap-2 sm:flex">
              <span className="text-sm font-medium text-foreground">Wikipedia Assistant</span>
              <span className="rounded-full border border-border bg-surface/60 px-2 py-0.5 text-[10px] text-muted-foreground">
                Wiki-AI · NLP Engine
              </span>
            </div>
          </div>
          <div className="flex items-center gap-1">
            <IconBtn 
              label="Research Dashboard" 
              onClick={() => setResearchPanelOpen((o) => !o)}
            >
              <BarChart3 className={`h-4 w-4 transition-colors ${researchPanelOpen ? "text-primary" : ""}`} />
            </IconBtn>
            <IconBtn label="Export PDF"><Download className="h-4 w-4" /></IconBtn>
            <IconBtn label="Share"><Share2 className="h-4 w-4" /></IconBtn>
            <IconBtn label="Toggle theme" onClick={() => setLight((l) => !l)}>
              {light ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
            </IconBtn>
          </div>
        </header>

        {/* Scroll area */}
        <div ref={scrollRef} className="flex-1 overflow-y-auto">
          {messages.length === 0 ? (
            <WelcomeHero onPick={send} />
          ) : (
            <div className="mx-auto w-full max-w-3xl space-y-6 px-4 py-8">
              {messages.map((m) => (
                <MessageBubble key={m.id} message={m} onToggleBookmark={toggleBookmark} />
              ))}
              {isStreaming && <TypingIndicator />}
            </div>
          )}
        </div>

        {/* Composer */}
        <div className="shrink-0 px-4 pb-4">
          <div className="mx-auto w-full max-w-3xl">
            <ChatInput onSend={send} disabled={isStreaming} />
          </div>
        </div>
      </main>

      {/* Research Panel desktop */}
      {researchPanelOpen && (
        <div className="hidden xl:flex relative z-10 h-full">
          <ResearchPanel sessionState={sessionState} />
        </div>
      )}

      {/* Research Panel mobile drawer */}
      {researchPanelOpen && (
        <div className="fixed inset-0 z-40 xl:hidden">
          <div className="absolute inset-0 bg-black/60 backdrop-blur-sm" onClick={() => setResearchPanelOpen(false)} />
          <div className="absolute right-0 top-0 h-full shadow-2xl">
            <ResearchPanel
              sessionState={sessionState}
              onClose={() => setResearchPanelOpen(false)}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function IconBtn({
  children,
  label,
  onClick,
}: {
  children: React.ReactNode;
  label: string;
  onClick?: () => void;
}) {
  return (
    <button
      onClick={onClick}
      aria-label={label}
      title={label}
      className="grid h-9 w-9 place-items-center rounded-lg text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
    >
      {children}
    </button>
  );
}
