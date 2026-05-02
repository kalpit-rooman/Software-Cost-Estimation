"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import {
  type ChatMessage,
  type EstimationContext,
  sendChatMessage,
} from "@/lib/api";

const GREETING: ChatMessage = {
  role: "assistant",
  content:
    "Hi! I have your estimation results. Ask me anything — why the effort is this high, how to reduce cost, what the assumptions mean, or anything about the methodology used.",
};

const DEFAULT_SUGGESTED_QUESTIONS = [
  "Why is the effort estimate this high?",
  "How can I reduce the cost?",
  "What do the assumptions mean?",
  "How accurate is this estimate?",
];

export default function ChatPanel({
  context,
  suggestedQuestions,
}: {
  context: EstimationContext;
  suggestedQuestions?: string[];
}) {
  const [history, setHistory] = useState<ChatMessage[]>([GREETING]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const bottomRef = useRef<HTMLDivElement>(null);
  const questions = suggestedQuestions ?? DEFAULT_SUGGESTED_QUESTIONS;

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [history, loading]);

  async function sendMessage(msg: string): Promise<void> {
    if (!msg || loading) return;

    setInput("");
    setError(null);

    const optimistic: ChatMessage[] = [
      ...history,
      { role: "user", content: msg },
    ];
    setHistory(optimistic);
    setLoading(true);

    try {
      const apiHistory = history.slice(1);
      const res = await sendChatMessage({
        message: msg,
        context,
        history: apiHistory,
      });
      setHistory([GREETING, ...res.history]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "Something went wrong. Try again.",
      );
      setHistory(history);
    } finally {
      setLoading(false);
    }
  }

  async function handleSend(e: FormEvent) {
    e.preventDefault();
    await sendMessage(input.trim());
  }

  const suggestedQuestionsList = questions;
  const showSuggestions = history.length === 1;

  return (
    <div className="flex flex-col">
      {/* Message list */}
      <div className="flex max-h-[420px] min-h-[280px] flex-col gap-3 overflow-y-auto px-6 py-5 sm:px-8">
        {history.map((msg, i) => (
          <div
            key={i}
            className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-fade-in`}
          >
            <div
              className={`max-w-[85%] rounded-2xl px-4 py-3 text-sm leading-7 ${
                msg.role === "user"
                  ? "bg-primary text-white rounded-br-md"
                  : "bg-background border border-line/50 text-foreground rounded-bl-md"
              }`}
            >
              {msg.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start animate-fade-in">
            <div className="bg-background border border-line/50 rounded-2xl rounded-bl-md px-4 py-3">
              <span className="flex gap-1.5">
                {[0, 1, 2].map((i) => (
                  <span
                    key={i}
                    className="inline-block h-2 w-2 rounded-full bg-teal"
                    style={{ animation: `pulse-dot 1.2s ease-in-out ${i * 0.2}s infinite` }}
                  />
                ))}
              </span>
            </div>
          </div>
        )}

        {error && (
          <div className="rounded-xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-700">
            {error}
          </div>
        )}

        <div ref={bottomRef} />
      </div>

      {/* Suggested questions */}
      {showSuggestions && (
        <div className="border-t border-line/30 px-6 py-4 sm:px-8">
          <p className="mb-2.5 text-[0.65rem] font-semibold uppercase tracking-[0.2em] text-muted">
            Suggested questions
          </p>
          <div className="flex flex-wrap gap-2">
            {suggestedQuestionsList.map((q) => (
              <button
                key={q}
                onClick={() => sendMessage(q)}
                className="rounded-lg border border-line/50 bg-background px-3 py-1.5 text-xs text-muted transition-all duration-200 hover:border-primary/40 hover:text-primary hover:shadow-sm"
              >
                {q}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input */}
      <form
        onSubmit={handleSend}
        className="border-t border-line/30 flex items-center"
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about your estimate…"
          disabled={loading}
          className="flex-1 border-0 bg-transparent px-6 py-4 sm:px-8 text-sm text-foreground outline-none placeholder:text-muted/50 disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={loading || !input.trim()}
          className="mr-3 sm:mr-6 flex h-9 w-9 shrink-0 items-center justify-center rounded-lg bg-primary text-white transition-all duration-200 hover:bg-primary/90 hover:shadow-[0_2px_8px_rgba(44,76,59,0.3)] disabled:opacity-30 disabled:cursor-not-allowed"
        >
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="m22 2-7 20-4-9-9-4Z"/><path d="M22 2 11 13"/></svg>
        </button>
      </form>
    </div>
  );
}
