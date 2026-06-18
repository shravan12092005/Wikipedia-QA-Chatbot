export type Citation = {
  title: string;
  description: string;
  url: string;
};

export type AssistantMeta = {
  responseTimeMs: number;
  sourcesUsed: number;
  confidence: number; // 0..1
  citations: Citation[];
};

export type ChatMessage = {
  id: string;
  role: "user" | "assistant";
  content: string;
  createdAt: number;
  bookmarked?: boolean;
  meta?: AssistantMeta;
};

export type SessionState = {
  last_topic: string;
  last_article_title: string;
  last_article_url: string;
  last_article_word_count: number;
  last_article_summary_preview: string;
  last_intent: string;
  last_confidence: number;
  bart_summary: string;
  t5_summary: string;
  rouge_scores: {
    bart?: { rouge1: number; rouge2: number; rougeL: number };
    t5?: { rouge1: number; rouge2: number; rougeL: number };
  };
  rouge_winner: string;
  questions_asked: number;
  summaries_done: number;
  articles_fetched: number;
};

export type Conversation = {
  id: string;
  title: string;
  preview: string;
  messages: ChatMessage[];
  sessionState: SessionState | null;
  createdAt: number;
};
