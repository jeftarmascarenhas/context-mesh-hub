/** Feature intent detail page. */

import { MCPClient, ContextArtifact, MCPError } from "@/lib/mcp-client";
import { MarkdownRenderer } from "@/components/MarkdownRenderer";

function isError(result: unknown): result is MCPError {
  return typeof result === "object" && result !== null && "error" in result;
}

function isArtifact(result: unknown): result is ContextArtifact {
  return typeof result === "object" && result !== null && "content" in result;
}

export default async function FeatureIntentPage({
  params,
}: {
  params: Promise<{ name: string }>;
}) {
  const { name } = await params;
  const client = new MCPClient();
  const feature =
    name === "project"
      ? await client.getProjectIntent()
      : await client.callTool("context_read", {
          artifact_type: "feature_intent",
          name: name,
        });
  
  if (isError(feature)) {
    return (
      <div className="px-4 py-6 sm:px-0">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">
          Feature Intent Not Found
        </h1>
        <p className="text-gray-600">{feature.error}</p>
      </div>
    );
  }
  
  const content = isArtifact(feature) ? feature.content : "";
  
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
        <MarkdownRenderer content={content} />
      </div>
    </div>
  );
}
