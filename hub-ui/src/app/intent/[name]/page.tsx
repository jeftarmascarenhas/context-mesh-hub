/** Feature intent detail page. */

import { MCPClient } from "@/lib/mcp-client";
import ReactMarkdown from "react-markdown";

export default async function FeatureIntentPage({
  params,
}: {
  params: { name: string };
}) {
  const client = new MCPClient();
  const feature =
    params.name === "project"
      ? await client.getProjectIntent()
      : await client.callTool("context_read", {
          artifact_type: "feature_intent",
          name: params.name,
        });
  
  if ("error" in feature) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Feature Intent Not Found
        </h1>
        <p className="text-gray-600">{feature.error}</p>
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
        <div className="prose max-w-none">
          <ReactMarkdown>{feature.content || ""}</ReactMarkdown>
        </div>
      </div>
    </div>
  );
}
