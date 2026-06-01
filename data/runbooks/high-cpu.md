# High CPU Runbook

## Symptoms
- CPU > 90% for 5+ minutes
- Slow application response times
- Load average exceeds CPU core count

## Investigation
1. Identify top CPU consumers: `top -b -n 1 | head -20`
2. Per-process CPU: `ps aux --sort=-%cpu | head -10`
3. Thread-level analysis: `top -H -p <PID>`
4. Check for runaway processes: `pgrep -fl <process_name>`
5. Review recent deployments or code changes

## Remediation
1. Kill runaway process: `kill -15 <PID>` (graceful) or `kill -9 <PID>` (force)
2. Restart the service: `systemctl restart <service>`
3. Scale horizontally if load is legitimate
4. Add CPU limits via systemd or container runtime
5. Enable CPU throttling as temporary measure

## Prevention
- Set CPU alerts at 85%
- Implement auto-scaling (HPA in Kubernetes)
- Profile and optimize CPU-heavy code paths
