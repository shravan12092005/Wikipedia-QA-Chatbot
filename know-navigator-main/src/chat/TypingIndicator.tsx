import { BookOpen } from "lucide-react";
import { motion } from "motion/react";

export function TypingIndicator() {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex w-full gap-3"
    >
      <div className="grid h-8 w-8 shrink-0 place-items-center rounded-full brand-gradient text-white">
        <BookOpen className="h-4 w-4" />
      </div>
      <div className="rounded-2xl rounded-tl-md border border-border bg-surface/40 px-4 py-3">
        <div className="flex items-center gap-1.5">
          <span className="typing-dot h-1.5 w-1.5 rounded-full bg-primary" />
          <span className="typing-dot h-1.5 w-1.5 rounded-full bg-primary" />
          <span className="typing-dot h-1.5 w-1.5 rounded-full bg-primary" />
          <span className="ml-2 text-[11px] text-muted-foreground">Searching Wikipedia…</span>
        </div>
      </div>
    </motion.div>
  );
}
