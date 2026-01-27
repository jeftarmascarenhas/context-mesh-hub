/** Intent card component for displaying intent summaries. */

"use client";

import Link from "next/link";
import ReactMarkdown from "react-markdown";

interface IntentCardProps {
  intent: {
    artifact_type: string;
    name?: string;
    path: string;
    content: string;
  };
  type: "project" | "feature";
}

export function IntentCard({ intent, type }: IntentCardProps) {
  // Extract title from content (first # heading)
  const titleMatch = intent.content.match(/^#\s+(.+)$/m);
  const title = titleMatch
    ? titleMatch[1]
    : type === "project"
    ? "Project Intent"
    : intent.name || "Feature Intent";
  
  // Extract status
  const statusMatch = intent.content.match(/Status[:\s]+\*\*(.+?)\*\*/i);
  const status = statusMatch ? statusMatch[1] : "Active";
  
  // Extract first paragraph
  const whatMatch = intent.content.match(/##\s+What\s*\n\n(.+?)(?=\n##|$)/s);
  const description = whatMatch
    ? whatMatch[1].trim().split("\n")[0]
    : intent.content.split("\n").slice(0, 3).join(" ");
  
  const href =
    type === "project"
      ? "/intent/project"
      : `/intent/${intent.name}`;
  
  return (
    <Link href={href}>
      <div className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <span
            className={`px-2 py-1 text-xs rounded ${
              status === "Completed"
                ? "bg-green-100 text-green-800"
                : status === "Active"
                ? "bg-blue-100 text-blue-800"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            {status}
          </span>
        </div>
        <p className="text-sm text-gray-600 line-clamp-3">{description}</p>
        <div className="mt-4 text-xs text-gray-500">
          {intent.path}
        </div>
      </div>
    </Link>
  );
}
