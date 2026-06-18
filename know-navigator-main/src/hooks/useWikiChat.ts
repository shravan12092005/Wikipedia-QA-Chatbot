import { useCallback, useEffect, useState } from "react";
import type { ChatMessage, Conversation } from "@/types/chat";
import { sendChatMessage, clearChatSession } from "@/services/api/chat";

const CONVERSATIONS_STORAGE_KEY = "wiki-assistant:conversations_v2";
const ACTIVE_CHAT_ID_KEY = "wiki-assistant:active_chat_id";

export function newId() {
  return Math.random().toString(36).slice(2) + Date.now().toString(36);
}

export function useWikiChat() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [activeChatId, setActiveChatId] = useState<string | null>(null);
  const [isStreaming, setIsStreaming] = useState(false);

  // Load conversations and active ID from localStorage on mount
  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      const savedConv = localStorage.getItem(CONVERSATIONS_STORAGE_KEY);
      if (savedConv) {
        setConversations(JSON.parse(savedConv));
      }
      const savedActiveId = localStorage.getItem(ACTIVE_CHAT_ID_KEY);
      if (savedActiveId) {
        setActiveChatId(savedActiveId);
      }
    } catch {}
  }, []);

  // Save conversations to localStorage when they change
  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      localStorage.setItem(CONVERSATIONS_STORAGE_KEY, JSON.stringify(conversations));
    } catch {}
  }, [conversations]);

  // Save activeChatId to localStorage when it changes
  useEffect(() => {
    if (typeof window === "undefined") return;
    try {
      if (activeChatId) {
        localStorage.setItem(ACTIVE_CHAT_ID_KEY, activeChatId);
      } else {
        localStorage.removeItem(ACTIVE_CHAT_ID_KEY);
      }
    } catch {}
  }, [activeChatId]);

  // Compute active conversation metrics
  const activeChat = conversations.find((c) => c.id === activeChatId) || null;
  const messages = activeChat ? activeChat.messages : [];
  const sessionState = activeChat ? activeChat.sessionState : null;

  const send = useCallback(async (text: string) => {
    const prompt = text.trim();
    if (!prompt || isStreaming) return;

    let currentChatId = activeChatId;
    let targetConversations = [...conversations];
    let chatToUpdate: Conversation;

    // 1. Create a new conversation if none is active or selected
    if (!currentChatId) {
      currentChatId = newId();
      chatToUpdate = {
        id: currentChatId,
        title: prompt.length > 24 ? prompt.slice(0, 24) + "..." : prompt,
        preview: prompt,
        messages: [],
        sessionState: null,
        createdAt: Date.now(),
      };
      targetConversations.push(chatToUpdate);
      setConversations(targetConversations);
      setActiveChatId(currentChatId);
    } else {
      const found = targetConversations.find((c) => c.id === currentChatId);
      if (!found) {
        // Fallback in case activeChatId is out of sync
        chatToUpdate = {
          id: currentChatId,
          title: prompt.length > 24 ? prompt.slice(0, 24) + "..." : prompt,
          preview: prompt,
          messages: [],
          sessionState: null,
          createdAt: Date.now(),
        };
        targetConversations.push(chatToUpdate);
        setConversations(targetConversations);
      } else {
        chatToUpdate = found;
      }
    }

    // 2. Append User Message
    const userMsg: ChatMessage = {
      id: newId(),
      role: "user",
      content: prompt,
      createdAt: Date.now(),
    };

    chatToUpdate.messages = [...chatToUpdate.messages, userMsg];
    chatToUpdate.preview = prompt;
    setConversations([...targetConversations]);
    setIsStreaming(true);

    try {
      const data = await sendChatMessage(currentChatId, prompt);
      
      const assistantMsg: ChatMessage = {
        id: newId(),
        role: "assistant",
        content: data.message.content,
        createdAt: Date.now(),
        meta: data.message.meta,
      };

      // 3. Update title if it was a default placeholder topic
      if (data.session_state && data.session_state.last_article_title) {
        chatToUpdate.title = data.session_state.last_article_title;
      }

      chatToUpdate.messages = [...chatToUpdate.messages, assistantMsg];
      chatToUpdate.sessionState = data.session_state;
      setConversations([...targetConversations]);
    } catch (error) {
      console.error("Chat request failed:", error);
      const errorMsg: ChatMessage = {
        id: newId(),
        role: "assistant",
        content: "⚠️ **Network Error**: Unable to reach the backend QA server. Please make sure that the Python API server is running.",
        createdAt: Date.now(),
      };
      chatToUpdate.messages = [...chatToUpdate.messages, errorMsg];
      setConversations([...targetConversations]);
    } finally {
      setIsStreaming(false);
    }
  }, [isStreaming, activeChatId, conversations]);

  const clear = useCallback(async () => {
    if (!activeChatId) return;

    // Remove the current active chat from conversations list
    const updated = conversations.filter((c) => c.id !== activeChatId);
    setConversations(updated);
    setActiveChatId(null);

    // Call backend API to reset session statistics
    try {
      await clearChatSession(activeChatId);
    } catch (err) {
      console.error("Failed to clear backend session state:", err);
    }
  }, [activeChatId, conversations]);

  const toggleBookmark = useCallback((id: string) => {
    if (!activeChatId) return;
    setConversations((prev) =>
      prev.map((c) => {
        if (c.id !== activeChatId) return c;
        return {
          ...c,
          messages: c.messages.map((msg) =>
            msg.id === id ? { ...msg, bookmarked: !msg.bookmarked } : msg
          ),
        };
      })
    );
  }, [activeChatId]);

  const selectChat = useCallback((id: string | null) => {
    setActiveChatId(id);
  }, []);

  const deleteChat = useCallback((id: string) => {
    setConversations((prev) => prev.filter((c) => c.id !== id));
    if (activeChatId === id) setActiveChatId(null);
  }, [activeChatId]);

  return {
    conversations,
    activeChatId,
    messages,
    sessionState,
    isStreaming,
    send,
    clear,
    selectChat,
    toggleBookmark,
    deleteChat,
  };
}
