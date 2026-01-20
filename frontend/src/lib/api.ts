const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface Book {
  id: string;
  title: string;
  authors: string[];
  publisher: string | null;
  year: string | null;
  isbn: string | null;
  description: string | null;
  owner_count: number | null;
  cinii_url: string;
}

export interface DebugLogEntry {
  timestamp: string;
  type: "frontend_request" | "openai_request" | "openai_response" | "tool_call" | "tool_result" | "cinii_request" | "cinii_response" | "error";
  summary: string;
  details?: Record<string, unknown>;
}

export interface ChatResponse {
  message: string;
  books: Book[] | null;
  debug_logs?: DebugLogEntry[] | null;
}

export interface StreamEvent {
  type: "log" | "done" | "error";
  data: DebugLogEntry | { message: string; books: Book[] | null } | { message: string };
}

export async function sendChatMessage(
  message: string,
  history: ChatMessage[]
): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE_URL}/chat`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  return response.json();
}

export async function sendChatMessageStream(
  message: string,
  history: ChatMessage[],
  onEvent: (event: StreamEvent) => void
): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/chat/stream`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ message, history }),
  });

  if (!response.ok) {
    throw new Error(`API error: ${response.status}`);
  }

  const reader = response.body?.getReader();
  if (!reader) {
    throw new Error("Response body is not readable");
  }

  const decoder = new TextDecoder();
  let buffer = "";

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });

    // SSEイベントをパース
    const lines = buffer.split("\n");
    buffer = lines.pop() || "";

    for (const line of lines) {
      if (line.startsWith("data: ")) {
        const data = line.slice(6);
        if (data.trim()) {
          try {
            const event = JSON.parse(data) as StreamEvent;
            onEvent(event);
          } catch {
            console.error("Failed to parse SSE event:", data);
          }
        }
      }
    }
  }
}

export function createFrontendLog(summary: string, details?: Record<string, unknown>): DebugLogEntry {
  return {
    timestamp: new Date().toISOString(),
    type: "frontend_request",
    summary,
    details,
  };
}
