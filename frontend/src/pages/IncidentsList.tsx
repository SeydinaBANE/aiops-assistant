import { useEffect, useState } from "react";
import { fetchIncidents } from "../api/client";
import IncidentCard from "../components/IncidentCard";
import type { Incident } from "../types/incident";

export default function IncidentsList() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchIncidents()
      .then(setIncidents)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="text-center py-12 text-gray-400">
        <div className="animate-spin h-8 w-8 border-4 border-blue-500 border-t-transparent rounded-full mx-auto mb-3" />
        Loading incidents...
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

  if (incidents.length === 0) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-400 mb-4">No incidents yet</p>
        <a
          href="/"
          className="inline-block bg-blue-600 text-white rounded-md px-4 py-2 text-sm font-medium hover:bg-blue-700"
        >
          Start an Investigation
        </a>
      </div>
    );
  }

  return (
    <div className="space-y-4">
      <h1 className="text-2xl font-bold">Incidents</h1>
      <p className="text-gray-500 text-sm">{incidents.length} incident{incidents.length !== 1 ? "s" : ""}</p>
      <div className="space-y-3">
        {incidents.map((incident) => (
          <IncidentCard key={incident.id} incident={incident} />
        ))}
      </div>
    </div>
  );
}
