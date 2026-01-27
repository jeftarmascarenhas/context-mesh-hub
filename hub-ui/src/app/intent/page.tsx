/** Intent listing page. */

import { MCPClient } from "@/lib/mcp-client";
import { IntentCard } from "@/components/IntentCard";

export default async function IntentPage() {
  const client = new MCPClient();
  const projectIntent = await client.getProjectIntent();
  const features = await client.getFeatureIntents();
  
  return (
    <div className="px-4 py-6 sm:px-0">
      <h1 className="text-3xl font-bold text-gray-900 mb-6">Intent</h1>
      
      {projectIntent && !("error" in projectIntent) && (
        <div className="mb-8">
          <h2 className="text-2xl font-semibold text-gray-900 mb-4">
            Project Intent
          </h2>
          <IntentCard intent={projectIntent} type="project" />
        </div>
      )}
      
      <div>
        <h2 className="text-2xl font-semibold text-gray-900 mb-4">
          Feature Intents
        </h2>
        <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
          {Array.isArray(features) && features.map((feature: any, i: number) => {
            if ("error" in feature) return null;
            return (
              <IntentCard key={i} intent={feature} type="feature" />
            );
          })}
        </div>
        {(!Array.isArray(features) || features.length === 0) && (
          <p className="text-gray-600">No feature intents found.</p>
        )}
      </div>
    </div>
  );
}
