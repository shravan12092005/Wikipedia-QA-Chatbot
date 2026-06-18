import { ExternalLink, BookOpen } from "lucide-react";
import { motion } from "motion/react";
import type { Citation } from "@/types/chat";

export function CitationCard({ citation, index }: { citation: Citation; index: number }) {
  return (
    <motion.a
      href={citation.url}
      target="_blank"
      rel="noreferrer"
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: 0.08 * index }}
      className="group relative flex flex-col gap-2 overflow-hidden rounded-xl border border-border bg-surface/60 p-3 transition-all hover:border-primary/40 hover:bg-surface"
    >
      <div className="flex items-center justify-between gap-2">
        <div className="flex items-center gap-2 min-w-0">
          <div className="grid h-6 w-6 shrink-0 place-items-center rounded-md bg-primary/15 text-primary">
            <BookOpen className="h-3 w-3" />
          </div>
          <p className="truncate text-xs font-semibold text-foreground">{citation.title}</p>
        </div>
        <span className="shrink-0 rounded bg-muted px-1.5 py-0.5 text-[10px] font-mono text-muted-foreground">
          [{index + 1}]
        </span>
      </div>
      <p className="line-clamp-2 text-[11px] leading-relaxed text-muted-foreground">
        {citation.description}
      </p>
      <div className="flex items-center gap-1 text-[11px] text-primary opacity-80 group-hover:opacity-100">
        <span>Open article</span>
        <ExternalLink className="h-3 w-3 transition-transform group-hover:translate-x-0.5" />
      </div>
    </motion.a>
  );
}
