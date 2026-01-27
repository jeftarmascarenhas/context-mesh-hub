/** Dashboard/home page. */

import { MCPClient } from "@/lib/mcp-client";
import { LifecycleIndicator } from "@/components/LifecycleIndicator";
import { ValidationResults } from "@/components/ValidationResults";
import { GuidancePanel } from "@/components/GuidancePanel";

export default async function HomePage() {
  const client = new MCPClient();
  const validation = await client.validate();
  const projectIntent = await client.getProjectIntent();
  
  return (
    <div className="px-4 py-6 sm:px-0">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          Context Mesh Hub Dashboard
        </h1>
        <p className="text-gray-600">
          Visualize and navigate your project context
        </p>
      </div>
      
      <div className="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <div>
          <LifecycleIndicator />
        </div>
        
        <div>
          <ValidationResults validation={validation} />
        </div>
      </div>
      
      <div className="mt-6">
        <GuidancePanel validation={validation} />
      </div>
      
      {projectIntent && !("error" in projectIntent) && (
        <div className="mt-6 bg-white shadow rounded-lg p-6">
          <h2 className="text-xl font-semibold text-gray-900 mb-4">
            Project Intent
          </h2>
          <div className="prose max-w-none">
            <p className="text-gray-700">
              {projectIntent.content?.split("\n").slice(0, 5).join(" ")}...
            </p>
            <a
              href="/intent"
              className="text-blue-600 hover:text-blue-800"
            >
              View full project intent →
            </a>
          </div>
        </div>
      )}
    </div>
  );
}
