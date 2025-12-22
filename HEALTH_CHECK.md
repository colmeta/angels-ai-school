# Angels AI School - UptimeRobot Health Check

This app is configured with a robust health check endpoint at `/api/health` that:
- Accepts both GET and HEAD requests (UptimeRobot compatibility)
- Performs real database connectivity checks using IPv4-forced connections
- Returns 503 status when database is unreachable
- Returns 200 OK when system is healthy

Last updated: 2025-12-22
