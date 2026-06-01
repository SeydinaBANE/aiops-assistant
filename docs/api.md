# API Reference

Base URL: `http://localhost:8000`

## Endpoints

### `POST /incidents`

Create an incident from an alert. Triggers the multi-agent investigation pipeline.

**Request body:**

```json
{
  "title": "Disk Space Alert",
  "message": "Disk usage on /dev/sda1 has exceeded 90% threshold.",
  "source": "grafana",
  "severity": "high",
  "labels": {
    "alertname": "disk-full",
    "host": "web-01"
  }
}
```

| Field | Type | Default | Description |
|---|---|---|---|
| `title` | `string` | — | Alert title (max 256 chars) |
| `message` | `string` | — | Alert description |
| `source` | `string` | `"grafana"` | Monitoring system name |
| `severity` | `string` | `"high"` | One of `critical`, `high`, `medium`, `low` |
| `labels` | `object` | `{}` | Key-value metadata (alertname, host, service, etc.) |

**Response:** `201 Created`

```json
{
  "id": "a1b2c3d4e5f6",
  "alert_title": "Disk Space Alert",
  "alert_severity": "high",
  "status": "investigating",
  "steps": [],
  "summary": null,
  "error": null,
  "created_at": "2026-06-01T12:00:00Z",
  "updated_at": "2026-06-01T12:00:00Z"
}
```

The investigation runs synchronously in the request handler. For long-running investigations (>30s), you would move this to a background task in production.

---

### `GET /incidents`

List all incidents, sorted by creation date (newest first).

**Response:** `200 OK`

```json
[
  {
    "id": "a1b2c3d4e5f6",
    "alert_title": "Disk Space Alert",
    "alert_severity": "high",
    "status": "resolved",
    "steps": [
      {
        "agent_name": "logs",
        "status": "success",
        "result": "Found high disk usage patterns...",
        "error": null,
        "duration_ms": 1200.5,
        "timestamp": "2026-06-01T12:00:01Z"
      }
    ],
    "summary": "## logs\nFound high disk usage...\n\n## knowledge\nRunbook suggests...\n\n## remediation\n1. Clear log files...",
    "error": null,
    "created_at": "2026-06-01T12:00:00Z",
    "updated_at": "2026-06-01T12:00:05Z"
  }
]
```

| Field | Type | Description |
|---|---|---|
| `id` | `string` | Unique ID (12-char hex from UUID) |
| `alert_title` | `string` | Original alert title |
| `alert_severity` | `string` | `critical`, `high`, `medium`, `low` |
| `status` | `string` | `pending`, `investigating`, `resolved`, `failed` |
| `steps` | `array` | Investigation steps (see below) |
| `summary` | `string\|null` | Merged report (resolved) or null |
| `error` | `string\|null` | Error message (failed) or null |
| `created_at` | `datetime` | ISO 8601 |
| `updated_at` | `datetime` | ISO 8601 |

**Step object:**

| Field | Type | Description |
|---|---|---|
| `agent_name` | `string` | `logs`, `knowledge`, or `remediation` |
| `status` | `string` | `running`, `success`, or `error` |
| `result` | `string` | Agent output text |
| `error` | `string\|null` | Error message if status is `error` |
| `duration_ms` | `number` | Execution time in milliseconds |
| `timestamp` | `datetime` | ISO 8601 |

---

### `GET /incidents/{id}`

Get a single incident by ID.

**Path parameters:**

| Parameter | Type | Description |
|---|---|---|
| `id` | `string` | Incident ID (12-char hex) |

**Response:** `200 OK` — same shape as a list item.

**Errors:**
- `404 Not Found` — `{"detail": "Incident not found"}`

---

### `GET /health`

Liveness probe.

**Response:** `200 OK`

```json
{
  "status": "ok"
}
```

## Enums

### `Severity`

| Value | Description |
|---|---|
| `critical` | Service down, data loss, security breach |
| `high` | Degraded performance, resource exhaustion |
| `medium` | Non-critical warning |
| `low` | Informational |

### `IncidentStatus`

| Value | Description |
|---|---|
| `pending` | Created, not yet investigated |
| `investigating` | Pipeline running |
| `resolved` | Investigation complete, no errors |
| `failed` | Investigation complete, one or more agents failed |

## Errors

All endpoints return standard FastAPI error responses:

```json
{
  "detail": "Error description"
}
```

| Status | Meaning |
|---|---|
| `201` | Created (POST /incidents) |
| `200` | Success (GET) |
| `404` | Incident not found |
| `422` | Validation error (malformed request body) |
| `500` | Internal server error |
