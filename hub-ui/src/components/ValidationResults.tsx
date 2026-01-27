/** Validation results display component. */

"use client";

interface ValidationIssue {
  message: string;
  artifact?: string;
}

interface ValidationResultsProps {
  validation: {
    valid?: boolean;
    errors?: ValidationIssue[];
    warnings?: ValidationIssue[];
    info?: ValidationIssue[];
  };
}

export function ValidationResults({ validation }: ValidationResultsProps) {
  const errors = validation.errors || [];
  const warnings = validation.warnings || [];
  const info = validation.info || [];
  const isValid = validation.valid !== false && errors.length === 0;
  
  return (
    <div className="bg-white shadow rounded-lg p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-4">
        Validation Status
      </h2>
      
      <div className={`mb-4 p-3 rounded ${
        isValid ? "bg-green-50 text-green-800" : "bg-red-50 text-red-800"
      }`}>
        <div className="flex items-center">
          <span className="text-2xl mr-2">{isValid ? "✓" : "✗"}</span>
          <span className="font-medium">
            {isValid ? "Valid" : `${errors.length} error(s) found`}
          </span>
        </div>
      </div>
      
      {errors.length > 0 && (
        <div className="mb-4">
          <h3 className="font-medium text-red-800 mb-2">Errors</h3>
          <ul className="list-disc list-inside space-y-1 text-sm text-red-700">
            {errors.map((error, i) => (
              <li key={i}>
                {error.message}
                {error.artifact && (
                  <span className="text-red-500 ml-2">({error.artifact})</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {warnings.length > 0 && (
        <div className="mb-4">
          <h3 className="font-medium text-yellow-800 mb-2">Warnings</h3>
          <ul className="list-disc list-inside space-y-1 text-sm text-yellow-700">
            {warnings.map((warning, i) => (
              <li key={i}>
                {warning.message}
                {warning.artifact && (
                  <span className="text-yellow-600 ml-2">({warning.artifact})</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
      
      {info.length > 0 && (
        <div>
          <h3 className="font-medium text-blue-800 mb-2">Info</h3>
          <ul className="list-disc list-inside space-y-1 text-sm text-blue-700">
            {info.map((item, i) => (
              <li key={i}>
                {item.message}
                {item.artifact && (
                  <span className="text-blue-600 ml-2">({item.artifact})</span>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
