import { useState, useRef, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { createInvestigationWs } from "../api/client";
import StepTimeline from "../components/StepTimeline";
import type { AlertPayload, InvestigationStep, Severity } from "../types/incident";

const severities: Severity[] = ["critical", "high", "medium", "low"];

const AGENTS = ["logs", "knowledge", "remediation"] as const;

function runningPlaceholder(agent: string): InvestigationStep {
  return {
    agent_name: agent,
    status: "running",
    result: "",
    error: null,
    duration_ms: 0,
    timestamp: "",
  };
}

export default function NewInvestigation() {
  const navigate = useNavigate();
  const wsRef = useRef<WebSocket | null>(null);

  const [title, setTitle] = useState("");
  const [message, setMessage] = useState("");
  const [source, setSource] = useState("grafana");
  const [severity, setSeverity] = useState<Severity>("high");
  const [connecting, setConnecting] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [steps, setSteps] = useState<InvestigationStep[]>([]);
  const [incidentId, setIncidentId] = useState<string | null>(null);
  const [done, setDone] = useState(false);

  const handleSubmit = useCallback(
    (e: React.FormEvent) => {
      e.preventDefault();
      setError(null);
      setSteps(AGENTS.map((a) => runningPlaceholder(a)));
      setIncidentId(null);
      setDone(false);
      setConnecting(true);

      const payload: AlertPayload = { title, message, source, severity };

      wsRef.current = createInvestigationWs(payload, {
        onInvestigating: (id) => {
          setIncidentId(id);
          setConnecting(false);
        },
        onStep: (step) => {
          const stepTyped = step as InvestigationStep;
          setSteps((prev) =>
            prev.map((s) => (s.agent_name === stepTyped.agent_name ? stepTyped : s)),
          );
        },
        onComplete: (incident) => {
          setSteps(incident.steps);
          setDone(true);
        },
        onError: (msg) => {
          setError(msg);
          setConnecting(false);
        },
      });
    },
    [title, message, source, severity],
  );

  const handleViewIncident = () => {
    if (incidentId) navigate(`/incidents/${incidentId}`);
  };

  const handleReset = () => {
    setSteps([]);
    setDone(false);
    setIncidentId(null);
    wsRef.current?.close();
  };

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-bold">New Investigation</h1>
        <p className="text-gray-500 mt-1">Trigger a multi-agent incident investigation</p>
      </div>

      <form onSubmit={handleSubmit} className="bg-white border rounded-lg p-6 space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Title</label>
          <input
            type="text"
            required
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            placeholder="e.g. Disk Space Alert"
            className="w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">Message</label>
          <textarea
            required
            rows={3}
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="e.g. Disk usage exceeded 90% on host web-01"
            className="w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
          />
        </div>

        <div className="flex gap-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Source</label>
            <input
              type="text"
              value={source}
              onChange={(e) => setSource(e.target.value)}
              className="w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            />
          </div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-700 mb-1">Severity</label>
            <select
              value={severity}
              onChange={(e) => setSeverity(e.target.value as Severity)}
              className="w-full border rounded-md px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 outline-none"
            >
              {severities.map((s) => (
                <option key={s} value={s}>
                  {s.charAt(0).toUpperCase() + s.slice(1)}
                </option>
              ))}
            </select>
          </div>
        </div>

        <button
          type="submit"
          disabled={connecting}
          className="w-full bg-blue-600 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          {connecting ? "Connecting..." : "Start Investigation"}
        </button>
      </form>

      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
          {error}
        </div>
      )}

      {(steps.length > 0 || connecting) && (
        <div className="bg-white border rounded-lg p-6 space-y-4">
          <h2 className="font-semibold">Investigation Progress</h2>
          <StepTimeline steps={steps} />
          {done && (
            <div className="flex gap-3 pt-2">
              <button
                onClick={handleViewIncident}
                className="bg-gray-900 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-gray-800 transition-colors"
              >
                View Details
              </button>
              <button
                onClick={handleReset}
                className="border rounded-md px-4 py-2 text-sm font-medium hover:bg-gray-50 transition-colors"
              >
                New Investigation
              </button>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
