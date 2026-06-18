import { motion } from "motion/react";
import { useState } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { Check, Copy, Star, BookOpen, Gauge, Clock, FileText, Share2 } from "lucide-react";
import type { ChatMessage } from "@/types/chat";
import { CitationCard } from "./CitationCard";

type Props = {
  message: ChatMessage;
  onToggleBookmark: (id: string) => void;
};

export function MessageBubble({ message, onToggleBookmark }: Props) {
  const [copied, setCopied] = useState(false);
  const isUser = message.role === "user";

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(message.content);
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    } catch {}
  };

  if (isUser) {
    return (
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        className="flex w-full justify-end gap-3"
      >
        <div className="max-w-[80%] rounded-2xl rounded-tr-md brand-gradient px-4 py-2.5 text-sm text-white shadow-[0_8px_30px_-12px_var(--color-primary)]">
          {message.content}
        </div>
        <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full bg-surface text-xs font-semibold text-foreground ring-1 ring-border">
          JR
        </div>
      </motion.div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex w-full gap-3"
    >
      <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full brand-gradient text-white shadow-[0_0_20px_-6px_var(--color-primary)]">
        <BookOpen className="h-4 w-4" />
      </div>

      <div className="min-w-0 flex-1 space-y-3">
        <div className="md-content max-w-none rounded-2xl rounded-tl-md border border-border bg-surface/40 px-4 py-3 text-sm leading-relaxed text-foreground/90">
          <ReactMarkdown remarkPlugins={[remarkGfm]}>{message.content}</ReactMarkdown>
        </div>

        {/* Meta strip */}
        {message.meta && (
          <div className="flex flex-wrap items-center gap-2 text-[11px] text-muted-foreground">
            <span className="flex items-center gap-1 rounded-md border border-border bg-surface/40 px-2 py-1">
              <Clock className="h-3 w-3 text-primary" />
              {(message.meta.responseTimeMs / 1000).toFixed(2)}s
            </span>
            <span className="flex items-center gap-1 rounded-md border border-border bg-surface/40 px-2 py-1">
              <FileText className="h-3 w-3 text-accent2" />
              {message.meta.sourcesUsed} sources
            </span>
            <span className="flex items-center gap-1 rounded-md border border-border bg-surface/40 px-2 py-1">
              <Gauge className="h-3 w-3 text-emerald-400" />
              {(message.meta.confidence * 100).toFixed(0)}% confidence
            </span>
          </div>
        )}

        {/* Citations */}
        {message.meta?.citations && message.meta.citations.length > 0 && (
          <div>
            <p className="mb-2 px-1 text-[10px] font-semibold uppercase tracking-wider text-muted-foreground">
              Sources from Wikipedia
            </p>
            <div className="grid gap-2 sm:grid-cols-2 lg:grid-cols-3">
              {message.meta.citations.map((c, i) => (
                <CitationCard key={c.url} citation={c} index={i} />
              ))}
            </div>
          </div>
        )}

        {/* Actions */}
        <div className="flex items-center gap-1 pt-1">
          <ActionButton onClick={copy} label={copied ? "Copied" : "Copy"}>
            {copied ? <Check className="h-3.5 w-3.5 text-emerald-400" /> : <Copy className="h-3.5 w-3.5" />}
          </ActionButton>
          <ActionButton
            onClick={() => onToggleBookmark(message.id)}
            label={message.bookmarked ? "Bookmarked" : "Bookmark"}
          >
            <Star className={`h-3.5 w-3.5 ${message.bookmarked ? "fill-yellow-400 text-yellow-400" : ""}`} />
          </ActionButton>
          <ActionButton onClick={() => {}} label="Share">
            <Share2 className="h-3.5 w-3.5" />
          </ActionButton>
        </div>
      </div>
    </motion.div>
  );
}

function ActionButton({
  onClick,
  label,
  children,
}: {
  onClick: () => void;
  label: string;
  children: React.ReactNode;
}) {
  return (
    <button
      onClick={onClick}
      className="flex items-center gap-1.5 rounded-md px-2 py-1 text-[11px] text-muted-foreground transition-colors hover:bg-accent hover:text-foreground"
    >
      {children}
      <span>{label}</span>
    </button>
  );
}
