"use client";

import { useState } from "react";
import Link from "next/link";
import { getCatalogMethod } from "@/lib/valuation/catalog";

interface Message {
  role: "user" | "assistant";
  content: string;
}

export default function AIAdvisorPage() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    const text = input.trim();
    if (!text || loading) return;
    setInput("");

    const next: Message[] = [...messages, { role: "user", content: text }];
    setMessages(next);
    setLoading(true);

    try {
      const res = await fetch("/v1/ai/chat", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ history: next }),
      });
      const data = await res.json();
      setMessages((prev) => [...prev, { role: "assistant", content: data.reply ?? "Sorry, the advisor is unavailable." }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "Sorry, the advisor failed." }]);
    } finally {
      setLoading(false);
    }
  };

  // Surface recommended methods as runnable calculator links (the advisor
  // recommends; the engine computes).
  const lastReply = [...messages].reverse().find((m) => m.role === "assistant")?.content ?? "";
  const suggestedSlugs = [...new Set(
    (lastReply.match(/slug: ([a-z0-9-]+)/g) ?? []).map((s) => s.replace("slug: ", ""))
  )].filter((slug) => getCatalogMethod(slug));

  return (
    <div className="container-narrow py-12">
      <h1 className="text-display-sm text-primary-500 mb-2">AI Valuation Advisor</h1>
      <p className="text-neutral-500 mb-6">
        Describe your asset and situation. The advisor recommends methods and parameters — it never
        computes numbers itself; every calculation runs through the auditable engine.
      </p>

      <div className="card-elevated p-4 mb-4 min-h-64 max-h-96 overflow-y-auto space-y-3">
        {messages.length === 0 && (
          <p className="text-sm text-neutral-400 text-center py-12">
            e.g. &ldquo;I want to value a pre-revenue SaaS startup&rsquo;s proprietary software.&rdquo;
          </p>
        )}
        {messages.map((m, i) => (
          <div key={i} className={`text-sm ${m.role === "user" ? "text-right" : "text-left"}`}>
            <div
              className={`inline-block max-w-[85%] rounded-xl px-4 py-2 whitespace-pre-wrap ${
                m.role === "user"
                  ? "bg-primary-500 text-white"
                  : "bg-neutral-100 dark:bg-neutral-800 text-neutral-800 dark:text-neutral-200"
              }`}
            >
              {m.content}
            </div>
          </div>
        ))}
        {loading && <p className="text-xs text-neutral-400">Thinking…</p>}
      </div>

      {suggestedSlugs.length > 0 && (
        <div className="mb-4 flex flex-wrap gap-2">
          {suggestedSlugs.map((slug) => {
            const m = getCatalogMethod(slug);
            return (
              <Link key={slug} href={`/calculator/${slug}`} className="text-xs px-3 py-1.5 rounded-full bg-primary-50 dark:bg-primary-950 text-primary-600 dark:text-primary-300 border border-primary-200 dark:border-primary-800 hover:bg-primary-100">
                Run {m?.name ?? slug}
              </Link>
            );
          })}
        </div>
      )}

      <div className="flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Describe your valuation situation…"
          className="flex-1 px-4 py-2.5 rounded-lg border border-neutral-300 dark:border-neutral-700 bg-white dark:bg-neutral-900 text-sm focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="rounded-lg bg-primary-500 text-white px-5 py-2.5 text-sm font-semibold hover:bg-primary-600 disabled:opacity-50"
        >
          Ask
        </button>
      </div>
    </div>
  );
}
