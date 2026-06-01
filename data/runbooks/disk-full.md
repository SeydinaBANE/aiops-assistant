# Disk Full Runbook

## Symptoms
- Disk usage > 90%
- Write operations timeout
- Application errors: "No space left on device"

## Investigation
1. Check disk usage: `df -h`
2. Find large files: `du -sh /var/* | sort -rh | head -10`
3. Check inode usage: `df -i`
4. Identify deleted but open files: `lsof | grep '(deleted)'`

## Remediation
1. Clean log files older than 7 days: `find /var/log -name "*.log" -mtime +7 -delete`
2. Truncate large app logs: `truncate -s 0 /var/log/app/*.log`
3. Remove old Docker images: `docker image prune -a -f`
4. If using journald: `journalctl --vacuum-size=500M`
5. If urgent: add temporary space with LVM or resize partition

## Prevention
- Set disk alert at 80%
- Enable log rotation (logrotate)
- Monitor with Prometheus node_exporter
