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

export interface ChatResponse {
  message: string;
  books: Book[] | null;
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
