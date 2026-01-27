/** Lifecycle phase indicator component. */

"use client";

type Phase = "Intent" | "Build" | "Learn";

interface LifecycleIndicatorProps {
  currentPhase?: Phase;
}

export function LifecycleIndicator({ currentPhase = "Intent" }: LifecycleIndicatorProps) {
  const phases: Phase[] = ["Intent", "Build", "Learn"];
  const currentIndex = phases.indexOf(currentPhase);
  
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Lifecycle Phase
      </h2>
      <div className="flex items-center space-x-4">
        {phases.map((phase, index) => (
          <div key={phase} className="flex items-center">
            <div
              className={`flex items-center justify-center w-10 h-10 rounded-full border-2 ${
                index <= currentIndex
                  ? "bg-blue-600 border-blue-600 text-white"
                  : "bg-gray-100 border-gray-300 text-gray-400"
              }`}
            >
              {index + 1}
            </div>
            <span
              className={`ml-2 font-medium ${
                index === currentIndex
                  ? "text-blue-600"
                  : index < currentIndex
                  ? "text-gray-600"
                  : "text-gray-400"
              }`}
            >
              {phase}
            </span>
            {index < phases.length - 1 && (
              <div
                className={`mx-4 h-0.5 w-8 ${
                  index < currentIndex ? "bg-blue-600" : "bg-gray-300"
                }`}
              />
            )}
          </div>
        ))}
      </div>
      <p className="mt-4 text-sm text-gray-600">
        Current phase: <strong>{currentPhase}</strong>
      </p>
    </div>
  );
}
