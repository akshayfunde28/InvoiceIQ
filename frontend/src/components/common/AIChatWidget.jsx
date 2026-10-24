import React, { useState, useRef, useEffect } from "react";
import { Sparkles, X, Send, Loader2, Bot, ChevronDown } from "lucide-react";
import { apiClient } from "../../api/client";

function MessageBubble({ msg }) {
  const isUser = msg.role === "user";
  return (
    <div className={`flex gap-2.5 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shrink-0 mt-0.5 shadow-md">
          <Bot className="w-3.5 h-3.5 text-white" />
        </div>
      )}
      <div
        className={`max-w-[80%] rounded-2xl px-3.5 py-2.5 text-xs leading-relaxed ${
          isUser
            ? "bg-indigo-600 text-white rounded-tr-sm"
            : "bg-slate-100 text-slate-800 rounded-tl-sm"
        }`}
      >
        {msg.content.split("\n").map((line, i) => (
          <span key={i}>
            {line
              .split(/(\*\*[^*]+\*\*)/g)
              .map((part, j) =>
                part.startsWith("**") && part.endsWith("**") ? (
                  <strong key={j}>{part.slice(2, -2)}</strong>
                ) : (
                  part
                )
              )}
            {i < msg.content.split("\n").length - 1 && <br />}
          </span>
        ))}
      </div>
    </div>
  );
}

const QUICK_PROMPTS = [
  "What is my total GST paid?",
  "Which month had the highest expenses?",
  "Who are my top vendors?",
  "Show me my expense summary",
];

export default function AIChatWidget() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      role: "assistant",
      content:
        "Hi! I am your InvoiceIQ AI Assistant. Ask me anything about your expenses, GST, vendors, or invoices.",
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  useEffect(() => {
    if (open && messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages, open]);

  useEffect(() => {
    if (open && inputRef.current) {
      inputRef.current.focus();
    }
  }, [open]);

  const sendMessage = async (question) => {
    const q = question || input.trim();
    if (!q || loading) return;

    setMessages((prev) => [...prev, { role: "user", content: q }]);
    setInput("");
    setLoading(true);

    try {
      const result = await apiClient.askAssistant(q);
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: result.answer || "Sorry, I could not get a response." },
      ]);
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I encountered an error. Please ensure the backend is running and try again.",
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      <button
        onClick={() => setOpen((v) => !v)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 rounded-2xl bg-gradient-to-tr from-indigo-600 to-violet-500 text-white shadow-xl shadow-indigo-500/40 flex items-center justify-center hover:scale-105 active:scale-95 transition-transform cursor-pointer border-2 border-white/20"
        title="Open AI Assistant"
      >
        {open ? <ChevronDown className="w-5 h-5" /> : <Sparkles className="w-6 h-6" />}
      </button>

      {open && (
        <div className="fixed bottom-24 right-6 z-50 w-80 sm:w-96 bg-white rounded-3xl shadow-2xl shadow-slate-900/20 border border-slate-200/80 flex flex-col overflow-hidden animate-fade-in">
          <div className="flex items-center justify-between px-5 py-4 bg-gradient-to-r from-indigo-600 to-violet-600 text-white">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-xl bg-white/20 flex items-center justify-center">
                <Sparkles className="w-4 h-4" />
              </div>
              <div>
                <p className="text-sm font-bold tracking-tight">AI Tax Auditor</p>
                <p className="text-[10px] text-indigo-200 font-medium">Powered by Groq LLM</p>
              </div>
            </div>
            <button
              onClick={() => setOpen(false)}
              className="w-7 h-7 rounded-lg bg-white/10 hover:bg-white/20 flex items-center justify-center transition-colors cursor-pointer"
            >
              <X className="w-4 h-4" />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto p-4 space-y-3 min-h-0 max-h-80">
            {messages.map((msg, i) => (
              <MessageBubble key={i} msg={msg} />
            ))}
            {loading && (
              <div className="flex items-center gap-2 text-slate-400 text-xs">
                <div className="w-7 h-7 rounded-full bg-gradient-to-tr from-indigo-600 to-violet-500 flex items-center justify-center shrink-0">
                  <Loader2 className="w-3.5 h-3.5 text-white animate-spin" />
                </div>
                <span className="bg-slate-100 px-3 py-2 rounded-2xl rounded-tl-sm">Thinking...</span>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {messages.length <= 1 && (
            <div className="px-4 pb-2 flex flex-wrap gap-1.5">
              {QUICK_PROMPTS.map((prompt) => (
                <button
                  key={prompt}
                  onClick={() => sendMessage(prompt)}
                  className="text-[10px] font-medium px-2.5 py-1.5 rounded-full bg-indigo-50 text-indigo-700 border border-indigo-200/80 hover:bg-indigo-100 transition-colors cursor-pointer"
                >
                  {prompt}
                </button>
              ))}
            </div>
          )}

          <div className="px-4 py-3 border-t border-slate-100 flex items-center gap-2">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask about your expenses..."
              className="flex-1 text-xs px-3.5 py-2.5 bg-slate-50 border border-slate-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-indigo-500/20 focus:border-indigo-500 transition-all"
              disabled={loading}
            />
            <button
              onClick={() => sendMessage()}
              disabled={!input.trim() || loading}
              className="w-9 h-9 rounded-xl bg-indigo-600 text-white flex items-center justify-center hover:bg-indigo-700 disabled:opacity-40 disabled:cursor-not-allowed transition-colors cursor-pointer shrink-0"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
