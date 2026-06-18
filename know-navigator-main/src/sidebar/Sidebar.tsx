import { useState } from "react";
import { motion } from "motion/react";
import { BookOpen, Plus, Search, Settings, Trash2, Sparkles, MessageSquare, X, LogOut } from "lucide-react";
import type { Conversation } from "@/types/chat";
import { supabase } from "@/services/supabase";
import { Link } from "@tanstack/react-router";
import { toast } from "sonner";

type Props = {
  user: any;
  conversations: Conversation[];
  activeChatId: string | null;
  onSelectChat: (id: string | null) => void;
  onNewChat: () => void;
  onClear: () => void;
  hasMessages: boolean;
  onClose?: () => void;
};

export function Sidebar({ 
  user, 
  conversations, 
  activeChatId, 
  onSelectChat, 
  onNewChat, 
  onClear, 
  hasMessages, 
  onClose 
}: Props) {
  const [query, setQuery] = useState("");

  const filtered = conversations.filter((c) =>
    (c.title + " " + c.preview).toLowerCase().includes(query.toLowerCase())
  );

  // Extract user display details from metadata dynamically
  const userMetadata = user?.user_metadata || {};
  const metaFullName = userMetadata.full_name || "";
  const metaUsername = userMetadata.username || "";
  const userEmail = user?.email || "";

  const displayName = metaFullName.trim()
    ? metaFullName
    : metaUsername.trim()
    ? `@${metaUsername}`
    : userEmail
    ? userEmail.split("@")[0]
    : "Jane Researcher";

  const userInitials = metaFullName.trim()
    ? metaFullName.split(" ").filter(Boolean).map((n: string) => n[0]).join("").slice(0, 2).toUpperCase()
    : metaUsername.trim()
    ? metaUsername.slice(0, 2).toUpperCase()
    : userEmail
    ? userEmail.split("@")[0].slice(0, 2).toUpperCase()
    : "JR";

  const handleSignOut = async () => {
    const toastId = toast.loading("Signing out...");
    try {
      await supabase.auth.signOut();
      toast.success("Signed out successfully!", { id: toastId });
    } catch (err: any) {
      console.error("Failed to sign out:", err);
      toast.error(err.message || "Failed to sign out.");
    }
  };

  return (
    <aside className="flex h-full w-72 shrink-0 flex-col border-r border-sidebar-border bg-sidebar">
      {/* Brand */}
      <div className="flex items-center gap-3 px-4 pt-5 pb-4">
        <div className="grid h-9 w-9 shrink-0 place-items-center rounded-xl brand-gradient shadow-[0_0_20px_-4px_var(--color-primary)]">
          <BookOpen className="h-4 w-4 text-white" />
        </div>
        <div className="min-w-0 flex-1">
          <p className="truncate text-sm font-semibold tracking-tight text-sidebar-foreground">
            Wikipedia Research
          </p>
          <p className="truncate text-[11px] text-muted-foreground">AI Assistant · v0.1</p>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="grid h-8 w-8 shrink-0 place-items-center rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground lg:hidden"
            aria-label="Close sidebar"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      {/* New chat */}
      <div className="px-3">
        <button
          onClick={onNewChat}
          className="group flex w-full items-center gap-2 rounded-xl border border-border bg-gradient-to-b from-primary/15 to-primary/5 px-3 py-2.5 text-sm font-medium text-foreground transition-all hover:border-primary/40 hover:from-primary/25 hover:to-primary/10"
        >
          <Plus className="h-4 w-4 text-primary transition-transform group-hover:rotate-90" />
          New conversation
        </button>
      </div>

      {/* Search */}
      <div className="px-3 pt-3">
        <div className="relative">
          <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search conversations"
            className="w-full rounded-lg border border-border bg-background/40 py-2 pl-9 pr-3 text-xs text-foreground placeholder:text-muted-foreground focus:border-primary/40 focus:outline-none focus:ring-1 focus:ring-primary/30"
          />
        </div>
      </div>

      {/* Recents */}
      <div className="mt-4 flex-1 overflow-y-auto px-2">
        <p className="px-3 pb-2 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
          Recent
        </p>
        <ul className="space-y-0.5">
          {filtered.map((c, i) => (
            <motion.li
              key={c.id}
              initial={{ opacity: 0, x: -6 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.03 }}
            >
              <button
                onClick={() => onSelectChat(c.id)}
                className={`group flex w-full items-start gap-2.5 rounded-lg px-3 py-2 text-left transition-colors ${
                  c.id === activeChatId ? "bg-accent/80 text-foreground" : "hover:bg-accent/60"
                }`}
              >
                <MessageSquare className={`mt-0.5 h-3.5 w-3.5 shrink-0 ${
                  c.id === activeChatId ? "text-primary" : "text-muted-foreground group-hover:text-primary"
                }`} />
                <div className="min-w-0 flex-1">
                  <p className="truncate text-xs font-medium text-foreground">{c.title}</p>
                  <p className="truncate text-[11px] text-muted-foreground">{c.preview}</p>
                </div>
              </button>
            </motion.li>
          ))}
          {filtered.length === 0 && (
            <li className="px-3 py-6 text-center text-xs text-muted-foreground">No matches</li>
          )}
        </ul>
      </div>

      {/* Footer actions */}
      <div className="border-t border-sidebar-border px-3 py-3">
        <div className="flex items-center gap-1">
          <button
            onClick={onClear}
            disabled={!hasMessages}
            className="flex flex-1 items-center justify-center gap-1.5 rounded-lg px-2 py-2 text-xs text-muted-foreground transition-colors hover:bg-accent/60 hover:text-foreground disabled:opacity-40"
          >
            <Trash2 className="h-3.5 w-3.5" />
            Clear chat
          </button>
          <Link 
            to="/settings"
            className="grid h-8 w-8 place-items-center rounded-lg text-muted-foreground transition-colors hover:bg-accent/60 hover:text-foreground"
            aria-label="Settings"
            title="Account Settings"
          >
            <Settings className="h-4 w-4" />
          </Link>
        </div>

        <div className="mt-3 flex items-center gap-3 rounded-xl border border-border bg-background/40 p-2.5">
          <div className="relative grid h-8 w-8 shrink-0 place-items-center rounded-full brand-gradient text-xs font-semibold text-white">
            {userInitials}
            <span className="absolute -bottom-0.5 -right-0.5 grid h-3 w-3 place-items-center rounded-full bg-sidebar">
              <span className="h-2 w-2 rounded-full bg-emerald-400" />
            </span>
          </div>
          <div className="min-w-0 flex-1">
            <p className="truncate text-xs font-semibold text-foreground">{displayName}</p>
            <p className="flex items-center gap-1 truncate text-[10px] text-muted-foreground">
              <Sparkles className="h-2.5 w-2.5 text-primary" />
              Pro plan
            </p>
          </div>
          <button 
            onClick={handleSignOut}
            className="grid h-7 w-7 place-items-center rounded-md text-muted-foreground hover:bg-accent hover:text-foreground transition-colors"
            title="Sign Out"
          >
            <LogOut className="h-3.5 w-3.5" />
          </button>
        </div>
      </div>
    </aside>
  );
}
