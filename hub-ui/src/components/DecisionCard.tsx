/** Decision card component. */

"use client";

import Link from "next/link";
import ReactMarkdown from "react-markdown";

interface DecisionCardProps {
  decision: {
    artifact_type: string;
    name: string;
    path: string;
    content: string;
  };
}

export function DecisionCard({ decision }: DecisionCardProps) {
  // Extract number from name (e.g., "001-tech-stack" -> "001")
  const numberMatch = decision.name.match(/^(\d+)/);
  const number = numberMatch ? numberMatch[1] : decision.name;
  
  // Extract title from content - try different patterns
  let title = `Decision ${number}`;
  const titlePatterns = [
    /^#\s+Decision\s+\d+:\s*(.+)$/m,  // # Decision 001: Title
    /^#\s+Decision:\s*(.+)$/m,         // # Decision: Title
    /^#\s+(.+)$/m,                      // # Title
  ];
  for (const pattern of titlePatterns) {
    const match = decision.content.match(pattern);
    if (match) {
      title = match[1].trim();
      break;
    }
  }
  
  // Extract status
  const statusMatch = decision.content.match(/Status[:\s]+\*\*(.+?)\*\*/i);
  const status = statusMatch ? statusMatch[1] : "Accepted";
  
  // Extract decision summary from Decision section
  const decisionMatch = decision.content.match(/##\s+Decision\s*\n+([\s\S]+?)(?=\n##|$)/);
  let summary = "";
  if (decisionMatch) {
    const paragraphs = decisionMatch[1].trim().split(/\n\n/);
    summary = paragraphs[0]?.trim() || "";
  } else {
    const lines = decision.content.split("\n").filter(l => l.trim() && !l.startsWith("#"));
    summary = lines.slice(0, 2).join(" ");
  }
  
  return (
    <Link href={`/decisions/${decision.name}`}>
      <div className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer border border-gray-100">
        <div className="flex items-start justify-between mb-2">
          <div>
            <span className="text-sm font-mono text-purple-600 font-medium">
              ADR-{number}
            </span>
            <h3 className="text-lg font-semibold text-gray-900 mt-1">
              {title}
            </h3>
          </div>
          <span
            className={`px-2 py-1 text-xs rounded ${
              status === "Accepted"
                ? "bg-green-100 text-green-800"
                : status === "Proposed"
                ? "bg-yellow-100 text-yellow-800"
                : status === "Superseded"
                ? "bg-red-100 text-red-800"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            {status}
          </span>
        </div>
        <div className="text-sm text-gray-600 line-clamp-3 prose prose-sm max-w-none">
          <ReactMarkdown>{summary}</ReactMarkdown>
        </div>
        <div className="mt-4 text-xs text-gray-400">
          {decision.path}
        </div>
      </div>
    </Link>
  );
}
