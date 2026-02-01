/** Project intent detail page. */

import { MCPClient } from "@/lib/mcp-client";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";

export default async function ProjectIntentPage() {
  const client = new MCPClient();
  const projectIntent = await client.getProjectIntent();
  
  if ("error" in projectIntent) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Project Intent Not Found
        </h1>
        <p className="text-gray-600">{projectIntent.error}</p>
      </div>
    );
  }
  
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-4">
        <a
          href="/intent"
          className="text-blue-600 hover:text-blue-800 text-sm"
        >
          ← Back to Intent
        </a>
      </div>
      
      <div className="bg-white shadow rounded-lg p-6">
        <MarkdownRenderer content={projectIntent.content || ""} />
      </div>
    </div>
  );
}
