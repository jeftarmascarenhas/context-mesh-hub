/** Decisions listing page. */

import { MCPClient } from "@/lib/mcp-client";
import { DecisionCard } from "@/components/DecisionCard";

export default async function DecisionsPage() {
  const client = new MCPClient();
  const decisions = await client.getDecisions();
  
  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Decisions</h1>
      
      <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
        {Array.isArray(decisions) &&
          decisions.map((decision: any, i: number) => {
            if ("error" in decision) return null;
            return <DecisionCard key={i} decision={decision} />;
          })}
      </div>
      
      {(!Array.isArray(decisions) || decisions.length === 0) && (
        <p className="text-gray-600">No decisions found.</p>
      )}
    </div>
  );
}
