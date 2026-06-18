import { motion } from "motion/react";
import { BookOpen, Gauge, BarChart3, Trophy, X, ExternalLink } from "lucide-react";
import type { SessionState } from "@/types/chat";

type Props = {
  sessionState: SessionState | null;
  onClose?: () => void;
};

export function ResearchPanel({ sessionState, onClose }: Props) {
  const state = sessionState || {
    last_topic: "",
    last_article_title: "",
    last_article_url: "",
    last_article_word_count: 0,
    last_article_summary_preview: "",
    last_intent: "—",
    last_confidence: 0,
    bart_summary: "",
    t5_summary: "",
    rouge_scores: {},
    rouge_winner: "",
    questions_asked: 0,
    summaries_done: 0,
    articles_fetched: 0,
  };

  // Intent styles helper
  const getIntentBadgeStyles = (intent: string) => {
    const defaultStyles = "bg-muted text-muted-foreground border-border";
    const mapping: Record<string, string> = {
      greeting: "bg-indigo-500/10 text-indigo-400 border-indigo-500/25",
      topic_request: "bg-purple-500/10 text-purple-400 border-purple-500/25",
      question_answering: "bg-sky-500/10 text-sky-400 border-sky-500/25",
      summarization: "bg-emerald-500/10 text-emerald-400 border-emerald-500/25",
      farewell: "bg-amber-500/10 text-amber-400 border-amber-500/25",
    };
    return mapping[intent.toLowerCase()] || defaultStyles;
  };

  const formattedIntent = state.last_intent
    ? state.last_intent.replace("_", " ").replace(/\b\w/g, (c) => c.toUpperCase())
    : "—";

  const hasCores = state.rouge_scores && state.rouge_scores.bart;

  return (
    <aside className="flex h-full w-80 shrink-0 flex-col border-l border-border bg-sidebar overflow-y-auto">
      {/* Header */}
      <div className="flex items-center justify-between border-b border-border/60 px-4 py-4">
        <div className="flex items-center gap-2">
          <BarChart3 className="h-4 w-4 text-primary" />
          <h2 className="text-sm font-semibold tracking-tight text-foreground">Research Dashboard</h2>
        </div>
        {onClose && (
          <button
            onClick={onClose}
            className="grid h-7 w-7 place-items-center rounded-lg text-muted-foreground hover:bg-accent hover:text-foreground"
            aria-label="Close dashboard"
          >
            <X className="h-4 w-4" />
          </button>
        )}
      </div>

      <div className="flex-1 space-y-4 p-4">
        {/* Active Topic */}
        <section className="rounded-xl border border-border bg-surface/30 p-4 backdrop-blur-md">
          <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-3">
            <BookOpen className="h-3 w-3 text-primary" />
            <span>Active Topic</span>
          </div>
          {state.last_article_title ? (
            <div className="space-y-2">
              <h3 className="text-sm font-semibold text-foreground leading-tight">
                {state.last_article_title}
              </h3>
              <p className="text-[11px] text-muted-foreground">
                {state.last_article_word_count.toLocaleString()} words fetched
              </p>
              <a
                href={state.last_article_url}
                target="_blank"
                rel="noreferrer"
                className="inline-flex items-center gap-1 text-[11px] text-primary font-medium hover:underline pt-1"
              >
                View on Wikipedia <ExternalLink className="h-2.5 w-2.5" />
              </a>
            </div>
          ) : (
            <p className="text-xs text-muted-foreground leading-relaxed">
              No topic researched in this session. Ask about a topic (e.g. "Tell me about Albert Einstein") to load one.
            </p>
          )}
        </section>

        {/* Intent Detector */}
        <section className="rounded-xl border border-border bg-surface/30 p-4 backdrop-blur-md">
          <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-3">
            <Gauge className="h-3 w-3 text-accent2" />
            <span>Intent Analysis</span>
          </div>
          <div className="space-y-3">
            <div className="flex items-center justify-between">
              <span className="text-[11px] text-muted-foreground">Detected Intent</span>
              <span className={`rounded-full border px-2 py-0.5 text-[10px] font-medium ${getIntentBadgeStyles(state.last_intent)}`}>
                {formattedIntent}
              </span>
            </div>
            <div className="space-y-1.5">
              <div className="flex justify-between text-[11px]">
                <span className="text-muted-foreground">Confidence</span>
                <span className="font-semibold text-foreground">{state.last_confidence}%</span>
              </div>
              <div className="h-1.5 w-full rounded-full bg-muted overflow-hidden">
                <div
                  className="h-full brand-gradient transition-all duration-500 ease-out"
                  style={{ width: `${state.last_confidence}%` }}
                />
              </div>
            </div>
          </div>
        </section>

        {/* Statistics Grid */}
        <section className="rounded-xl border border-border bg-surface/30 p-4 backdrop-blur-md">
          <div className="text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-3">
            Session Statistics
          </div>
          <div className="grid grid-cols-2 gap-2">
            <div className="rounded-lg bg-background/50 border border-border/40 p-2.5 text-center">
              <span className="block text-lg font-bold text-foreground">{state.articles_fetched}</span>
              <span className="text-[9px] font-medium uppercase tracking-wider text-muted-foreground">Articles</span>
            </div>
            <div className="rounded-lg bg-background/50 border border-border/40 p-2.5 text-center">
              <span className="block text-lg font-bold text-foreground">{state.questions_asked}</span>
              <span className="text-[9px] font-medium uppercase tracking-wider text-muted-foreground">Questions</span>
            </div>
            <div className="rounded-lg bg-background/50 border border-border/40 p-2.5 text-center">
              <span className="block text-lg font-bold text-foreground">{state.summaries_done}</span>
              <span className="text-[9px] font-medium uppercase tracking-wider text-muted-foreground">Summaries</span>
            </div>
            <div className="rounded-lg bg-background/50 border border-border/40 p-2.5 text-center">
              <span className="block text-lg font-bold text-foreground">
                {state.articles_fetched > 0 ? "BERT/RoB" : "—"}
              </span>
              <span className="text-[9px] font-medium uppercase tracking-wider text-muted-foreground">ML Engine</span>
            </div>
          </div>
        </section>

        {/* ROUGE Evaluation Card */}
        <section className="rounded-xl border border-border bg-surface/30 p-4 backdrop-blur-md">
          <div className="flex items-center gap-2 text-[10px] font-bold uppercase tracking-wider text-muted-foreground mb-3">
            <Trophy className="h-3 w-3 text-yellow-500" />
            <span>ROUGE Scores (BART vs T5)</span>
          </div>

          {hasCores ? (
            <div className="space-y-4">
              <div className="overflow-hidden rounded-lg border border-border/60 bg-background/30">
                <table className="w-full border-collapse text-left text-xs">
                  <thead>
                    <tr className="border-b border-border/60 bg-muted/30 text-[10px] font-semibold text-muted-foreground">
                      <th className="px-2 py-1.5">Metric</th>
                      <th className="px-2 py-1.5 text-right text-sky-400">BART</th>
                      <th className="px-2 py-1.5 text-right text-amber-500">T5</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-border/40 text-foreground/80 font-mono">
                    <tr>
                      <td className="px-2 py-1.5 text-left font-sans text-muted-foreground">ROUGE-1</td>
                      <td className="px-2 py-1.5 text-right text-sky-400 font-semibold">
                        {state.rouge_scores.bart?.rouge1.toFixed(3)}
                      </td>
                      <td className="px-2 py-1.5 text-right text-amber-500 font-semibold">
                        {state.rouge_scores.t5?.rouge1.toFixed(3)}
                      </td>
                    </tr>
                    <tr>
                      <td className="px-2 py-1.5 text-left font-sans text-muted-foreground">ROUGE-2</td>
                      <td className="px-2 py-1.5 text-right text-sky-400 font-semibold">
                        {state.rouge_scores.bart?.rouge2.toFixed(3)}
                      </td>
                      <td className="px-2 py-1.5 text-right text-amber-500 font-semibold">
                        {state.rouge_scores.t5?.rouge2.toFixed(3)}
                      </td>
                    </tr>
                    <tr>
                      <td className="px-2 py-1.5 text-left font-sans text-muted-foreground">ROUGE-L</td>
                      <td className="px-2 py-1.5 text-right text-sky-400 font-semibold">
                        {state.rouge_scores.bart?.rougeL.toFixed(3)}
                      </td>
                      <td className="px-2 py-1.5 text-right text-amber-500 font-semibold">
                        {state.rouge_scores.t5?.rougeL.toFixed(3)}
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <div className="flex items-center justify-between rounded-lg bg-emerald-500/5 border border-emerald-500/10 p-2 text-xs">
                <span className="text-muted-foreground">Evaluation Winner</span>
                <span className="font-semibold text-emerald-400 flex items-center gap-1">
                  {state.rouge_winner === "BART" && (
                    <span className="rounded bg-sky-500/15 text-sky-400 px-1.5 py-0.5 font-bold text-[10px]">
                      BART Wins
                    </span>
                  )}
                  {state.rouge_winner === "T5" && (
                    <span className="rounded bg-amber-500/15 text-amber-400 px-1.5 py-0.5 font-bold text-[10px]">
                      T5 Wins
                    </span>
                  )}
                  {state.rouge_winner === "Tie" && (
                    <span className="rounded bg-neutral-500/15 text-neutral-400 px-1.5 py-0.5 font-bold text-[10px]">
                      Tie
                    </span>
                  )}
                </span>
              </div>
            </div>
          ) : (
            <p className="text-xs text-muted-foreground leading-relaxed text-center py-4">
              Summarize an article (e.g. "Summarize it") to run evaluation and compare summaries.
            </p>
          )}
        </section>
      </div>
    </aside>
  );
}
