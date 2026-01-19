"use client";

import ReactMarkdown from "react-markdown";
import { ChatMessage as ChatMessageType, Book } from "@/lib/api";

interface Props {
  message: ChatMessageType;
  books?: Book[] | null;
}

export function ChatMessage({ message, books }: Props) {
  const isUser = message.role === "user";

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
      </div>
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
