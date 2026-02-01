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
  
  // Extract description from "What" section or first meaningful paragraph
  const whatMatch = intent.content.match(/##\s+What\s*\n+([\s\S]+?)(?=\n##|$)/);
  let description = "";
  if (whatMatch) {
    // Get first non-empty paragraph
    const paragraphs = whatMatch[1].trim().split(/\n\n/);
    description = paragraphs[0]?.trim() || "";
  } else {
    // Fallback: get content after first heading
    const lines = intent.content.split("\n").filter(l => l.trim() && !l.startsWith("#"));
    description = lines.slice(0, 2).join(" ");
  }
  
  const href =
    type === "project"
      ? "/intent/project"
      : `/intent/${intent.name}`;
  
  return (
    <Link href={href}>
      <div className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer border border-gray-100">
        <div className="flex items-start justify-between mb-2">
          <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
          <span
            className={`px-2 py-1 text-xs rounded ${
              status === "Completed"
                ? "bg-green-100 text-green-800"
                : status === "In Progress"
                ? "bg-blue-100 text-blue-800"
                : status === "Draft"
                ? "bg-yellow-100 text-yellow-800"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            {status}
          </span>
        </div>
        <div className="text-sm text-gray-600 line-clamp-3 prose prose-sm max-w-none">
          <ReactMarkdown>{description}</ReactMarkdown>
        </div>
        <div className="mt-4 text-xs text-gray-400">
          {intent.path}
        </div>
      </div>
    </Link>
  );
}
