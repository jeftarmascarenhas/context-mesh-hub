/** Evolution/changelog page. */

import { MCPClient } from "@/lib/mcp-client";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";

export default async function EvolutionPage() {
  const client = new MCPClient();
  const changelog = await client.getChangelog();
  
  if ("error" in changelog) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Evolution</h1>
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-yellow-800">Changelog not found.</p>
        </div>
      </div>
    );
  }
  
  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Evolution</h1>
      
      <div className="bg-white shadow rounded-lg p-6">
        <MarkdownRenderer content={changelog.content || ""} />
      </div>
    </div>
  );
}
