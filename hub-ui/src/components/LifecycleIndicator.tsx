/** Lifecycle workflow indicator component. 
 * Shows the Context Mesh workflow: Intent → Build → Learn
 * This is informational - showing the workflow, not a project state.
 */

"use client";

interface LifecycleIndicatorProps {
  /** Optional: Highlight a specific phase */
  highlightPhase?: "Intent" | "Build" | "Learn";
}

const phases = [
  {
    name: "Intent",
    icon: "📝",
    description: "Define WHAT and WHY",
    color: "purple",
  },
  {
    name: "Build", 
    icon: "🔨",
    description: "Implement with AI",
    color: "blue",
  },
  {
    name: "Learn",
    icon: "💡",
    description: "Update context",
    color: "green",
  },
];

export function LifecycleIndicator({ highlightPhase }: LifecycleIndicatorProps) {
  return (
    <div className="bg-gradient-to-r from-purple-50 via-blue-50 to-green-50 rounded-lg p-6 border border-gray-200">
      <h2 className="text-lg font-semibold text-gray-900 mb-1">
        Context Mesh Workflow
      </h2>
      <p className="text-sm text-gray-500 mb-4">
        Continuous cycle for AI-assisted development
      </p>
      
      <div className="flex items-center justify-between">
        {phases.map((phase, index) => (
          <div key={phase.name} className="flex items-center flex-1">
            <div className="flex flex-col items-center text-center flex-1">
              <div
                className={`flex items-center justify-center w-12 h-12 rounded-full text-xl mb-2 ${
                  highlightPhase === phase.name
                    ? phase.color === "purple"
                      ? "bg-purple-600 text-white shadow-lg"
                      : phase.color === "blue"
                      ? "bg-blue-600 text-white shadow-lg"
                      : "bg-green-600 text-white shadow-lg"
                    : "bg-white border-2 border-gray-200"
                }`}
              >
                {phase.icon}
              </div>
              <span
                className={`font-medium text-sm ${
                  highlightPhase === phase.name
                    ? phase.color === "purple"
                      ? "text-purple-700"
                      : phase.color === "blue"
                      ? "text-blue-700"
                      : "text-green-700"
                    : "text-gray-700"
                }`}
              >
                {phase.name}
              </span>
              <span className="text-xs text-gray-500 mt-1">
                {phase.description}
              </span>
            </div>
            {index < phases.length - 1 && (
              <div className="flex items-center px-2">
                <div className="text-gray-400 text-lg">→</div>
              </div>
            )}
          </div>
        ))}
      </div>
      
      <div className="mt-4 pt-4 border-t border-gray-200/50">
        <p className="text-xs text-gray-500 text-center">
          💡 Use the chat to navigate: "add feature", "create plan", "sync learnings"
        </p>
      </div>
    </div>
  );
}
