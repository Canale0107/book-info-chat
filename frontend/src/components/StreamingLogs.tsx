"use client";

import { DebugLogEntry } from "@/lib/api";

interface Props {
  logs: DebugLogEntry[];
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

export function StreamingLogs({ logs }: Props) {
  return (
    <div className="flex justify-start mb-4">
      <div className="max-w-[80%] rounded-lg px-4 py-3 bg-gray-100 dark:bg-gray-800">
        <div className="flex items-center gap-2 mb-3">
          <div className="flex gap-1">
            <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" />
            <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: "0.2s" }} />
            <span className="w-2 h-2 bg-blue-500 rounded-full animate-pulse" style={{ animationDelay: "0.4s" }} />
          </div>
          <span className="text-xs text-gray-500 dark:text-gray-400">処理中...</span>
        </div>

        <div className="space-y-1.5 font-mono text-xs">
          {logs.map((log, i) => {
            const config = LOG_TYPE_CONFIG[log.type] || { icon: "•", color: "text-gray-500" };
            const isLatest = i === logs.length - 1;

            return (
              <div
                key={i}
                className={`flex items-start gap-2 ${isLatest ? "opacity-100" : "opacity-60"}`}
              >
                <span className={`${config.color} font-bold shrink-0 w-4 text-center`}>
                  {config.icon}
                </span>
                <span className="text-gray-600 dark:text-gray-300">
                  {log.summary}
                </span>
                {isLatest && (
                  <span className="w-1.5 h-4 bg-gray-400 animate-pulse ml-1" />
                )}
              </div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
