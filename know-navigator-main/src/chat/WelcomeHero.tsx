import { motion } from "motion/react";
import { Sparkles, ArrowRight } from "lucide-react";

export const SUGGESTED_PROMPTS = [
  { title: "Explain Quantum Computing", subtitle: "Qubits, superposition, entanglement" },
  { title: "History of Artificial Intelligence", subtitle: "From Turing to transformers" },
  { title: "Who is Nikola Tesla?", subtitle: "Inventor of the AC induction motor" },
  { title: "Explain Blockchain Technology", subtitle: "Distributed ledgers and consensus" },
];

export function WelcomeHero({ onPick }: { onPick: (text: string) => void }) {
  return (
    <div className="relative mx-auto flex w-full max-w-3xl flex-col items-center px-4 pt-10 pb-6 text-center">
      <motion.div
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="mb-5 inline-flex items-center gap-2 rounded-full border border-primary/30 bg-primary/10 px-3 py-1 text-[11px] font-medium text-primary"
      >
        <Sparkles className="h-3 w-3" />
        Powered by Wikipedia · Cited sources
      </motion.div>

      <motion.h1
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.05 }}
        className="text-balance text-4xl font-semibold leading-[1.05] tracking-tight sm:text-5xl"
      >
        <span className="brand-gradient-text">Ask Anything</span>{" "}
        <span className="text-foreground">From Wikipedia</span>
      </motion.h1>

      <motion.p
        initial={{ opacity: 0, y: 14 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, delay: 0.15 }}
        className="mt-3 max-w-xl text-balance text-sm text-muted-foreground sm:text-base"
      >
        AI-powered research assistant with source citations.
      </motion.p>

      <div className="mt-10 grid w-full grid-cols-1 gap-3 sm:grid-cols-2">
        {SUGGESTED_PROMPTS.map((p, i) => (
          <motion.button
            key={p.title}
            onClick={() => onPick(p.title)}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.4, delay: 0.2 + i * 0.06 }}
            className="group relative overflow-hidden rounded-xl border border-border bg-surface/40 p-4 text-left transition-all hover:border-primary/40 hover:bg-surface/70"
          >
            <div className="flex items-start justify-between gap-3">
              <div className="min-w-0">
                <p className="truncate text-sm font-semibold text-foreground">{p.title}</p>
                <p className="mt-0.5 truncate text-xs text-muted-foreground">{p.subtitle}</p>
              </div>
              <ArrowRight className="mt-0.5 h-4 w-4 shrink-0 text-muted-foreground transition-all group-hover:translate-x-0.5 group-hover:text-primary" />
            </div>
            <div className="pointer-events-none absolute inset-x-0 -bottom-px h-px brand-gradient opacity-0 transition-opacity group-hover:opacity-100" />
          </motion.button>
        ))}
      </div>
    </div>
  );
}
