import type { AlertPayload, Incident, InvestigationStep, WsMessage } from "../types/incident";

export async function fetchIncidents(): Promise<Incident[]> {
  const res = await fetch("/api/incidents");
  if (!res.ok) throw new Error(`Failed to fetch incidents: ${res.statusText}`);
  return res.json();
}

export async function fetchIncident(id: string): Promise<Incident> {
  const res = await fetch(`/api/incidents/${id}`);
  if (!res.ok) throw new Error(`Failed to fetch incident: ${res.statusText}`);
  return res.json();
}

export type WsCallbacks = {
  onInvestigating: (id: string) => void;
  onStep: (step: InvestigationStep) => void;
  onComplete: (incident: Incident) => void;
  onError: (message: string) => void;
};

export function createInvestigationWs(payload: AlertPayload, callbacks: WsCallbacks): WebSocket {
  const protocol = location.protocol === "https:" ? "wss:" : "ws:";
  const ws = new WebSocket(`${protocol}//${location.host}/ws/incidents`);

  ws.onopen = () => {
    ws.send(JSON.stringify(payload));
  };

  ws.onmessage = (event) => {
    const msg: WsMessage = JSON.parse(event.data);
    switch (msg.type) {
      case "investigating":
        callbacks.onInvestigating(msg.incident_id);
        break;
      case "step":
        callbacks.onStep(msg.step);
        break;
      case "complete":
        callbacks.onComplete(msg.incident);
        ws.close();
        break;
      case "error":
        callbacks.onError(msg.message);
        ws.close();
        break;
    }
  };

  ws.onerror = () => {
    callbacks.onError("WebSocket connection failed");
  };

  return ws;
}
