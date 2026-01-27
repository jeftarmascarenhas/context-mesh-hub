/** Guidance panel component. */

"use client";

interface GuidancePanelProps {
  validation: {
    valid?: boolean;
    errors?: Array<{ message: string; artifact?: string }>;
    warnings?: Array<{ message: string; artifact?: string }>;
  };
}

export function GuidancePanel({ validation }: GuidancePanelProps) {
  const errors = validation.errors || [];
  const warnings = validation.warnings || [];
  const hasIssues = errors.length > 0 || warnings.length > 0;
  
  const guidance = [];
  
  if (errors.length > 0) {
    guidance.push({
      type: "error",
      title: "Fix Validation Errors",
      message: "Resolve validation errors before proceeding.",
      action: "Run 'cm doctor' for diagnostics",
    });
  }
  
  if (warnings.length > 0) {
    guidance.push({
      type: "warning",
      title: "Review Warnings",
      message: "Some warnings were detected. Review and address as needed.",
      action: "Check validation results above",
    });
  }
  
  if (!hasIssues) {
    guidance.push({
      type: "success",
      title: "Context is Valid",
      message: "Your Context Mesh structure is valid. You can proceed with development.",
      action: "Navigate to Intent or Decisions to explore context",
    });
  }
  
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Guidance
      </h2>
      
      {guidance.length === 0 ? (
        <p className="text-gray-600">No specific guidance at this time.</p>
      ) : (
        <div className="space-y-4">
          {guidance.map((item, i) => (
            <div
              key={i}
              className={`p-4 rounded-lg border ${
                item.type === "error"
                  ? "bg-red-50 border-red-200"
                  : item.type === "warning"
                  ? "bg-yellow-50 border-yellow-200"
                  : "bg-green-50 border-green-200"
              }`}
            >
              <h3 className="font-medium text-gray-900 mb-1">
                {item.title}
              </h3>
              <p className="text-sm text-gray-700 mb-2">{item.message}</p>
              <p className="text-xs text-gray-600">
                <strong>Action:</strong> {item.action}
              </p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
