import type { InvestigationStep } from "../types/incident";

const agentLabels: Record<string, string> = {
  logs: "Log Analysis",
  knowledge: "Knowledge Base",
  remediation: "Remediation",
};

function StepIcon({ status }: { status: InvestigationStep["status"] }) {
  if (status === "running") {
    return (
      <svg className="animate-spin h-5 w-5 text-blue-500" viewBox="0 0 24 24">
        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
        <path
          className="opacity-75"
          fill="currentColor"
          d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"
        />
      </svg>
    );
  }
  if (status === "success") {
    return (
      <svg className="h-5 w-5 text-green-500" viewBox="0 0 20 20" fill="currentColor">
        <path
          fillRule="evenodd"
          d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.857-9.809a.75.75 0 00-1.214-.882l-3.483 4.79-1.88-1.88a.75.75 0 10-1.06 1.061l2.5 2.5a.75.75 0 001.137-.089l4-5.5z"
          clipRule="evenodd"
        />
      </svg>
    );
  }
  return (
    <svg className="h-5 w-5 text-red-500" viewBox="0 0 20 20" fill="currentColor">
      <path
        fillRule="evenodd"
        d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.28 7.22a.75.75 0 00-1.06 1.06L8.94 10l-1.72 1.72a.75.75 0 101.06 1.06L10 11.06l1.72 1.72a.75.75 0 101.06-1.06L11.06 10l1.72-1.72a.75.75 0 00-1.06-1.06L10 8.94 8.28 7.22z"
        clipRule="evenodd"
      />
    </svg>
  );
}

export default function StepTimeline({ steps }: { steps: InvestigationStep[] }) {
  if (steps.length === 0) {
    return <p className="text-sm text-gray-400 italic">Waiting for investigation to start...</p>;
  }

  return (
    <div className="space-y-3">
      {steps.map((step, i) => (
        <div key={i} className="flex gap-3 items-start">
          <div className="mt-0.5">
            <StepIcon status={step.status} />
          </div>
          <div className="flex-1 min-w-0">
            <div className="flex items-center gap-2">
              <span className="font-medium text-sm">
                {agentLabels[step.agent_name] || step.agent_name}
              </span>
              {step.duration_ms > 0 && (
                <span className="text-xs text-gray-400">
                  {(step.duration_ms / 1000).toFixed(1)}s
                </span>
              )}
            </div>
            {step.status === "error" && step.error && (
              <p className="text-sm text-red-600 mt-1">{step.error}</p>
            )}
            {step.status === "success" && step.result && (
              <p className="text-sm text-gray-600 mt-1 whitespace-pre-wrap line-clamp-3">
                {step.result}
              </p>
            )}
          </div>
        </div>
      ))}
    </div>
  );
}
