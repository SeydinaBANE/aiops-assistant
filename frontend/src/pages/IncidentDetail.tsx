import { useEffect, useState } from "react";
import { useParams, Link } from "react-router-dom";
import { fetchIncident } from "../api/client";
import StepTimeline from "../components/StepTimeline";
import type { Incident } from "../types/incident";

const statusBadge: Record<string, string> = {
  pending: "bg-gray-100 text-gray-700",
  investigating: "bg-blue-100 text-blue-700 animate-pulse",
  resolved: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

export default function IncidentDetail() {
  const { id } = useParams<{ id: string }>();
  const [incident, setIncident] = useState<Incident | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!id) return;
    fetchIncident(id)
      .then(setIncident)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) {
    return (
      <div className="text-center py-12 text-gray-400">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-3" />
        Loading incident...
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4 text-sm text-red-700">
        {error}
      </div>
    );
  }

  if (!incident) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400 mb-4">Incident not found</p>
        <Link to="/incidents" className="text-blue-600 hover:underline text-sm">
          Back to incidents
        </Link>
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <Link to="/incidents" className="text-sm text-blue-600 hover:underline">
        &larr; Back to incidents
      </Link>

      <div className="bg-white border rounded-lg p-6 space-y-4">
        <div className="flex items-start justify-between gap-3">
          <div>
            <h1 className="text-2xl font-bold">{incident.alert_title}</h1>
            <p className="text-sm text-gray-500 mt-1">
              {new Date(incident.created_at).toLocaleString()}
            </p>
          </div>
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full shrink-0 ${statusBadge[incident.status] || statusBadge.pending}`}
          >
            {incident.status}
          </span>
        </div>

        {incident.summary && (
          <div className="bg-gray-50 border rounded-md p-4">
            <h3 className="text-sm font-medium text-gray-700 mb-1">Summary</h3>
            <p className="text-sm text-gray-600 whitespace-pre-wrap">{incident.summary}</p>
          </div>
        )}

        {incident.error && (
          <div className="bg-red-50 border border-red-200 rounded-md p-4">
            <h3 className="text-sm font-medium text-red-700 mb-1">Error</h3>
            <p className="text-sm text-red-600 whitespace-pre-wrap">{incident.error}</p>
          </div>
        )}
      </div>

      <div className="bg-white border rounded-lg p-6 space-y-4">
        <h2 className="font-semibold">Investigation Steps</h2>
        <StepTimeline steps={incident.steps} />
      </div>
    </div>
  );
}
