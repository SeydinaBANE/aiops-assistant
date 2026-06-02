export type Severity = "critical" | "high" | "medium" | "low";

export type IncidentStatus = "pending" | "investigating" | "resolved" | "failed";

export type StepStatus = "running" | "success" | "error";

export interface InvestigationStep {
  agent_name: string;
  status: StepStatus;
  result: string;
  error: string | null;
  duration_ms: number;
  timestamp: string;
}

export interface Incident {
  id: string;
  alert_title: string;
  alert_severity: Severity;
  status: IncidentStatus;
  steps: InvestigationStep[];
  summary: string | null;
  error: string | null;
  created_at: string;
  updated_at: string;
}

export interface AlertPayload {
  title: string;
  message: string;
  source?: string;
  severity?: Severity;
  labels?: Record<string, string>;
}

export interface WsInvestigating {
  type: "investigating";
  incident_id: string;
}

export interface WsStep {
  type: "step";
  step: InvestigationStep;
}

export interface WsComplete {
  type: "complete";
  incident: Incident;
}

export interface WsError {
  type: "error";
  message: string;
}

export type WsMessage = WsInvestigating | WsStep | WsComplete | WsError;
