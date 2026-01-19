"use client";

import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";
import {
  sendChatMessage,
  ChatMessage as ChatMessageType,
  Book,
} from "@/lib/api";

interface DisplayMessage extends ChatMessageType {
  books?: Book[] | null;
}

export default function Home() {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSend = async (content: string) => {
    const userMessage: DisplayMessage = { role: "user", content };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);

    const history: ChatMessageType[] = messages.map(({ role, content }) => ({
      role,
      content,
    }));

    try {
      const response = await sendChatMessage(content, history);
      const assistantMessage: DisplayMessage = {
        role: "assistant",
        content: response.message,
        books: response.books,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "エラーが発生しました"
      );
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col h-screen max-w-3xl mx-auto">
      <header className="px-4 py-6 border-b border-gray-200 dark:border-gray-700">
        <h1 className="text-2xl font-bold text-center">
          本を探す
        </h1>
        <p className="text-center text-gray-600 dark:text-gray-400 text-sm mt-1">
          読みたい本について、気軽に聞いてみてください
        </p>
      </header>

      <main className="flex-1 overflow-y-auto p-4">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full text-gray-500">
            <div className="text-center">
              <p className="text-lg mb-2">こんにちは！</p>
              <p className="text-sm">
                どんな本をお探しですか？<br />
                興味のあるテーマや、今の気分を教えてください。
              </p>
            </div>
          </div>
        ) : (
          <div>
            {messages.map((msg, i) => (
              <ChatMessage key={i} message={msg} books={msg.books} />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-100 dark:bg-gray-800 rounded-lg px-4 py-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" />
                    <span
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.1s" }}
                    />
                    <span
                      className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"
                      style={{ animationDelay: "0.2s" }}
                    />
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        )}
      </main>

      {error && (
        <div className="px-4 py-2 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-200 text-sm">
          {error}
        </div>
      )}

      <footer className="p-4 border-t border-gray-200 dark:border-gray-700">
        <ChatInput onSend={handleSend} disabled={isLoading} />
      </footer>
    </div>
  );
}
