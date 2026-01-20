"use client";

import { useState } from "react";
import ReactMarkdown from "react-markdown";
import { ChatMessage as ChatMessageType, Book, DebugLogEntry } from "@/lib/api";

interface Props {
  message: ChatMessageType;
  books?: Book[] | null;
  debugLogs?: DebugLogEntry[] | null;
}

const LOG_TYPE_CONFIG: Record<string, { icon: string; color: string }> = {
  frontend_request: { icon: "→", color: "text-orange-500" },
  openai_request: { icon: "→", color: "text-blue-500" },
  openai_response: { icon: "←", color: "text-blue-500" },
  tool_call: { icon: "⚙", color: "text-purple-500" },
  tool_result: { icon: "→", color: "text-purple-500" },
  cinii_request: { icon: "→", color: "text-green-500" },
  cinii_response: { icon: "←", color: "text-green-500" },
  error: { icon: "✕", color: "text-red-500" },
};

export function ChatMessage({ message, books, debugLogs }: Props) {
  const isUser = message.role === "user";
  const [isLogOpen, setIsLogOpen] = useState(false);

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-4`}>
      <div
        className={`max-w-[80%] rounded-lg px-4 py-3 ${
          isUser
            ? "bg-blue-600 text-white"
            : "bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100"
        }`}
      >
        <div className="prose prose-sm dark:prose-invert max-w-none">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>

        {books && books.length > 0 && (
          <div className="mt-4 space-y-3">
            {books.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        )}

        {debugLogs && debugLogs.length > 0 && (
          <div className="mt-3 pt-3 border-t border-gray-300 dark:border-gray-600">
            <button
              onClick={() => setIsLogOpen(!isLogOpen)}
              className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-200"
            >
              <span className={`transition-transform ${isLogOpen ? "rotate-90" : ""}`}>
                ▶
              </span>
              内部通信ログ ({debugLogs.length}件)
            </button>

            {isLogOpen && (
              <div className="mt-2 space-y-2">
                {debugLogs.map((log, i) => (
                  <DebugLogItem key={i} log={log} />
                ))}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

function DebugLogItem({ log }: { log: DebugLogEntry }) {
  const [isDetailOpen, setIsDetailOpen] = useState(false);
  const config = LOG_TYPE_CONFIG[log.type] || { icon: "•", color: "text-gray-500" };

  return (
    <div className="text-xs font-mono">
      <div className="flex items-start gap-2">
        <span className={`${config.color} font-bold shrink-0 w-4 text-center`}>
          {config.icon}
        </span>
        <span className="text-gray-600 dark:text-gray-300">{log.summary}</span>
      </div>

      {log.details && (
        <div className="ml-6 mt-1">
          <button
            onClick={() => setIsDetailOpen(!isDetailOpen)}
            className="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 text-[10px]"
          >
            {isDetailOpen ? "[-] 詳細を隠す" : "[+] 詳細を見る"}
          </button>

          {isDetailOpen && (
            <pre className="mt-1 p-2 bg-gray-200 dark:bg-gray-900 rounded text-[10px] overflow-x-auto">
              {JSON.stringify(log.details, null, 2)}
            </pre>
          )}
        </div>
      )}
    </div>
  );
}

function BookCard({ book }: { book: Book }) {
  return (
    <a
      href={book.cinii_url}
      target="_blank"
      rel="noopener noreferrer"
      className="block p-3 bg-white dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600 hover:border-blue-400 transition-colors"
    >
      <h4 className="font-semibold text-gray-900 dark:text-white text-sm">
        {book.title}
      </h4>
      <p className="text-xs text-gray-600 dark:text-gray-300 mt-1">
        {book.authors.join(", ")}
      </p>
      <div className="flex gap-3 mt-2 text-xs text-gray-500 dark:text-gray-400">
        {book.publisher && <span>{book.publisher}</span>}
        {book.year && <span>{book.year}</span>}
        {book.owner_count !== null && (
          <span>所蔵: {book.owner_count}館</span>
        )}
      </div>
    </a>
  );
}
