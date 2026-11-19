# Local Docker runtime - 30 October 2026

All 11 Compose services were rebuilt/started locally: MySQL, discovery, gateway, auth, business, monitoring, adaptive policy, AI inference, dashboard, Prometheus and Grafana. Published interfaces are bound to 127.0.0.1; Java services have bounded development heaps and container memory limits.

## Open the application

- Dashboard: http://127.0.0.1:8088/
- Eureka: http://127.0.0.1:8761/
- Prometheus: http://127.0.0.1:9090/
- Grafana: http://127.0.0.1:3000/
- Docker MySQL: 127.0.0.1:3307 (container port 3306)

The generated demonstration account is in the private, Git-ignored `.runtime/docker-login.json`. Do not upload or commit that file. Runtime keys are in `.runtime/docker-stack.env`, also ignored. The existing root `.env` was not rewritten. Existing Grafana storage was retained; its established administrator password is not necessarily replaced by an initialization environment value.

## Database preservation

The earlier `ai-pqc-security_mysql-data` volume rejected the current saved database password. It was not reset, deleted or migrated. This development run uses a separate `ai-pqc-security_mysql-dev-20261030` volume. Its four service schemas were initialized from the existing idempotent init.sql, and the verification suite created labelled test/demo records. This is not a recovery of earlier records. Do not delete either volume as routine cleanup.

## Commands

Run from the project root:

```powershell
docker compose -p ai-pqc-security --env-file .runtime/docker-stack.env -f docker-compose.yml -f .runtime/docker-local.override.yml --profile app up -d --no-build
docker compose -p ai-pqc-security --env-file .runtime/docker-stack.env -f docker-compose.yml -f .runtime/docker-local.override.yml --profile app ps
```

The local override and private environment file are intentionally not published. For routine stopping, use the same Compose arguments followed by `stop`. Never add `down -v` unless deliberately deleting the database/monitoring volumes is intended and approved.

## Verification

- `ml/artifacts/docker-runtime-20261030/verification.json`: 44 existing real API/MySQL checks passed using a Docker-specific SQL adapter.
- Three additional demonstration requests completed classical, hybrid and PQC round trips.
- `ml/artifacts/docker-runtime-20261030/web-monitoring.json`: dashboard HTTP 200; Nginx-proxied login/identity passed; three successful modes visible through the frontend proxy; Grafana database healthy; all seven configured Prometheus targets UP.
- In-app browser control was unavailable, so this run does not claim an interactive visual browser review. Open the dashboard link normally.
- The image build reported five npm dependency advisories (two moderate, three high). The build succeeded; no automatic forced dependency upgrade was performed. These advisories require separate dependency review and are not silently counted as resolved.
- External email remains unconfigured/unverified. Runtime checks are functional evidence, not new detection accuracy or production security certification.

Model loading uses the existing promoted local artifact. No retraining, model replacement, Windows security change, old database reset, or cloud deployment occurred.
