const API_BASE_URL = import.meta.env.VITE_API_URL || "http://localhost:8000/api";

export interface ChatResponse {
  message: {
    content: string;
    meta?: {
      responseTimeMs: number;
      sourcesUsed: number;
      confidence: number;
      citations: Array<{
        title: string;
        description: string;
        url: string;
      }>;
    };
  };
  session_state: any;
}

/**
 * Sends a chat message to the FastAPI backend.
 */
export async function sendChatMessage(sessionId: string, message: string): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      message,
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Clears the chat session metrics on the FastAPI backend.
 */
export async function clearChatSession(sessionId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/clear`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      session_id: sessionId,
    }),
  });

  if (!response.ok) {
    throw new Error(`API Error: ${response.statusText}`);
  }
}
