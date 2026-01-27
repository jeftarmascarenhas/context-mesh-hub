/** Decision card component. */

"use client";

import Link from "next/link";

interface DecisionCardProps {
  decision: {
    artifact_type: string;
    number: string;
    path: string;
    content: string;
  };
}

export function DecisionCard({ decision }: DecisionCardProps) {
  // Extract title from content
  const titleMatch = decision.content.match(/^#\s+Decision:\s*(.+)$/m);
  const title = titleMatch
    ? titleMatch[1]
    : `Decision ${decision.number}`;
  
  // Extract status
  const statusMatch = decision.content.match(/Status[:\s]+\*\*(.+?)\*\*/i);
  const status = statusMatch ? statusMatch[1] : "Accepted";
  
  // Extract decision summary
  const decisionMatch = decision.content.match(/##\s+Decision\s*\n\n(.+?)(?=\n##|$)/s);
  const summary = decisionMatch
    ? decisionMatch[1].trim().split("\n")[0]
    : decision.content.split("\n").slice(0, 3).join(" ");
  
  return (
    <Link href={`/decisions/${decision.number}`}>
      <div className="bg-white shadow rounded-lg p-6 hover:shadow-lg transition-shadow cursor-pointer">
        <div className="flex items-start justify-between mb-2">
          <div>
            <span className="text-sm font-mono text-gray-500">
              {decision.number}
            </span>
            <h3 className="text-lg font-semibold text-gray-900 mt-1">
              {title}
            </h3>
          </div>
          <span
            className={`px-2 py-1 text-xs rounded ${
              status === "Accepted"
                ? "bg-green-100 text-green-800"
                : "bg-gray-100 text-gray-800"
            }`}
          >
            {status}
          </span>
        </div>
        <p className="text-sm text-gray-600 line-clamp-3">{summary}</p>
        <div className="mt-4 text-xs text-gray-500">
          {decision.path}
        </div>
      </div>
    </Link>
  );
}
