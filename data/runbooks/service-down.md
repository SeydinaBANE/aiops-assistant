# Service Down Runbook

## Symptoms
- Health check failures
- Port unreachable errors
- 5xx errors in API responses

## Investigation
1. Check service status: `systemctl status <service>` or `kubectl get pods -n <ns>`
2. Check recent logs: `journalctl -u <service> --since "10 min ago"`
3. Verify port listening: `ss -tlnp | grep <port>`
4. Check upstream dependencies (database, message queue, etc.)
5. Check recent deployments or config changes

## Remediation
1. Restart the service: `systemctl restart <service>`
2. In Kubernetes: `kubectl rollout restart deployment/<name> -n <ns>`
3. Rollback recent change if cause is identified
4. Scale up replicas if under load: `kubectl scale deployment/<name> --replicas=3 -n <ns>`
5. Drain and cordon unhealthy nodes if infrastructure issue

## Prevention
- Use readiness probes in Kubernetes
- Implement circuit breakers for downstream dependencies
- Run chaos engineering experiments regularly
