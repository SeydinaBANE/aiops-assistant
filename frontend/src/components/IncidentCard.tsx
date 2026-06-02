import type { Incident } from "../types/incident";

const severityColors: Record<string, string> = {
  critical: "bg-red-100 text-red-800 border-red-200",
  high: "bg-orange-100 text-orange-800 border-orange-200",
  medium: "bg-yellow-100 text-yellow-800 border-yellow-200",
  low: "bg-green-100 text-green-800 border-green-200",
};

const statusBadge: Record<string, string> = {
  pending: "bg-gray-100 text-gray-700",
  investigating: "bg-blue-100 text-blue-700 animate-pulse",
  resolved: "bg-green-100 text-green-700",
  failed: "bg-red-100 text-red-700",
};

export default function IncidentCard({ incident }: { incident: Incident }) {
  return (
    <a
      href={`/incidents/${incident.id}`}
      className="block border rounded-lg p-4 hover:shadow-md transition-shadow bg-white"
    >
      <div className="flex items-start justify-between gap-3">
        <div className="min-w-0 flex-1">
          <h3 className="font-semibold text-base truncate">{incident.alert_title}</h3>
          <p className="text-sm text-gray-500 mt-1">
            {new Date(incident.created_at).toLocaleString()}
          </p>
        </div>
        <div className="flex gap-2 shrink-0">
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full border ${severityColors[incident.alert_severity] || severityColors.high}`}
          >
            {incident.alert_severity}
          </span>
          <span
            className={`text-xs font-medium px-2 py-0.5 rounded-full ${statusBadge[incident.status] || statusBadge.pending}`}
          >
            {incident.status}
          </span>
        </div>
      </div>
      {incident.summary && (
        <p className="text-sm text-gray-600 mt-2 line-clamp-2">{incident.summary}</p>
      )}
    </a>
  );
}
