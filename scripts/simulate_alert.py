"""Send a mock alert to the AIOps Assistant API."""

import argparse
import json
from urllib.request import Request, urlopen

ALERTS = {
    "disk-full": {
        "title": "Disk Space Alert",
        "message": "Disk usage on /dev/sda1 has exceeded 90% threshold.",
        "source": "grafana",
        "severity": "high",
        "labels": {"alertname": "disk-full", "host": "web-01", "mount": "/dev/sda1"},
    },
    "high-cpu": {
        "title": "High CPU Usage",
        "message": "CPU usage at 92% for more than 5 minutes.",
        "source": "grafana",
        "severity": "high",
        "labels": {"alertname": "high-cpu", "host": "web-02"},
    },
    "service-down": {
        "title": "Service Unreachable",
        "message": "Health check failed for api-gateway service on port 443.",
        "source": "grafana",
        "severity": "critical",
        "labels": {"alertname": "service-down", "service": "api-gateway"},
    },
}


def send_alert(alert_name: str, base_url: str) -> None:
    payload = ALERTS.get(alert_name)
    if not payload:
        print(f"Unknown alert: {alert_name}. Available: {', '.join(ALERTS)}")
        return

    body = json.dumps(payload).encode()
    req = Request(
        f"{base_url}/incidents",
        data=body,
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urlopen(req) as resp:
        result = json.loads(resp.read().decode())
    print(f"Incident created: {result['id']}")
    print(f"Status: {result['status']}")
    print(f"Summary:\n{result.get('summary', 'N/A')}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Simulate an alert")
    parser.add_argument("alert", nargs="?", default="disk-full", choices=list(ALERTS), help="Alert type")
    parser.add_argument("--url", default="http://localhost:8000", help="API base URL")
    args = parser.parse_args()
    send_alert(args.alert, args.url)


if __name__ == "__main__":
    main()
