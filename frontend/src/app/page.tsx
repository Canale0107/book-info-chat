"use client";

import { useState, useRef, useEffect } from "react";
import { ChatMessage } from "@/components/ChatMessage";
import { ChatInput } from "@/components/ChatInput";
import { StreamingLogs } from "@/components/StreamingLogs";
import {
  sendChatMessageStream,
  createFrontendLog,
  ChatMessage as ChatMessageType,
  Book,
  DebugLogEntry,
} from "@/lib/api";

interface DisplayMessage extends ChatMessageType {
  books?: Book[] | null;
  debugLogs?: DebugLogEntry[] | null;
}

export default function Home() {
  const [messages, setMessages] = useState<DisplayMessage[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [streamingLogs, setStreamingLogs] = useState<DebugLogEntry[]>([]);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages, streamingLogs]);

  const handleSend = async (content: string) => {
    const userMessage: DisplayMessage = { role: "user", content };
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);
    setError(null);
    setStreamingLogs([]);

    // Frontend → Backend のログを追加
    const frontendLog = createFrontendLog(
      "Frontend → Backend: チャットリクエスト",
      { message: content, historyLength: messages.length }
    );
    setStreamingLogs([frontendLog]);

    const history: ChatMessageType[] = messages.map(({ role, content }) => ({
      role,
      content,
    }));

    const collectedLogs: DebugLogEntry[] = [frontendLog];
    let resultMessage: string = "";
    let resultBooks: Book[] | null = null as Book[] | null;

    try {
      await sendChatMessageStream(content, history, (event) => {
        if (event.type === "log") {
          const logData = event.data as DebugLogEntry;
          collectedLogs.push(logData);
          setStreamingLogs([...collectedLogs]);
        } else if (event.type === "done") {
          const doneData = event.data as { message: string; books: Book[] | null };
          resultMessage = doneData.message;
          resultBooks = doneData.books;
        } else if (event.type === "error") {
          const errorData = event.data as { message: string };
          setError(errorData.message);
        }
      });

      // Backend → Frontend のログを追加
      const responseLog = createFrontendLog(
        "Backend → Frontend: 最終レスポンス",
        { messageLength: resultMessage.length, booksCount: resultBooks ? resultBooks.length : 0 }
      );
      collectedLogs.push(responseLog);

      const assistantMessage: DisplayMessage = {
        role: "assistant",
        content: resultMessage,
        books: resultBooks,
        debugLogs: collectedLogs,
      };
      setMessages((prev) => [...prev, assistantMessage]);
    } catch (err) {
      setError(
        err instanceof Error ? err.message : "エラーが発生しました"
      );
    } finally {
      setIsLoading(false);
      setStreamingLogs([]);
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
        {messages.length === 0 && !isLoading ? (
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
              <ChatMessage key={i} message={msg} books={msg.books} debugLogs={msg.debugLogs} />
            ))}
            {isLoading && (
              <StreamingLogs logs={streamingLogs} />
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
