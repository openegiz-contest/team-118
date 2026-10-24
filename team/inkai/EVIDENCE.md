# Execution evidence

Recorded on 25 October 2026 (Astana, UTC+5).

## Executed

- Participant-authored Concept committed as `9efe154` before implementation.
- 21 unit tests passed on Windows, Ubuntu WSL2 and the Python 3.12.12 application image: accounting, timing, thresholds, capacity, depletion, rerun/reset, bounded telemetry payloads and fail-closed platform-read contracts. Three contract tests use mocks and are not integration evidence.
- Combined platform/application Compose configuration validated with `docker compose -f deploy/compose/docker-compose.yml -f team/inkai/compose.yml config -q`.

## Live platform results

- `make inkai` started the actual application on the supplied OpenEgiz platform.
- `make inkai-smoke`: **8 checks passed**. All 18 Ditto-derived states matched the deterministic model, including delay propagation, day-38 commissioning, rerun, equal final deliveries, complete reset and input rejection.
- `make smoke`: **23 checks passed**, including MQTT -> Ditto -> Telegraf -> InfluxDB, Grafana and platform endpoints. Sanitized log: `evidence/platform-smoke.log`.
- The first full smoke exposed Telegraf OOM on the multi-array projection payload. Projections are now serialized losslessly into one Ditto string field. The regression test and the rerun above passed; this avoids expanding arrays in the telemetry parser.
- Browser observations confirmed the day-30 baseline (231.30 t U), delayed case (188.16 t U), six waiting groups, spatial twin inspection, day-38 ramping, seven-day advance, play/pause and reset. The clean-start Stand was left at baseline/day 0. Screenshots are in `evidence/`; the complete map is `evidence/delayed-spatial.png`. These were interactive browser checks, not a claim of an automated browser suite.

## Clean-start verification: passed

- Tested runtime commit: `152ad3bce01fdf6120ffd74a90e14e2a12e0b8e6`. A verified Git bundle of official Team-118 `main` was cloned into `/home/minemind/team-118-cleancheck`; origin was set to the official Team-118 URL. No ignored credentials, marker files or working-tree files were copied.
- Before startup there was no `.env` and no volume belonging to the isolated `minemind-clean` project. The six original development volumes were preserved.
- Ran the README prerequisites, `make inkai-test`, `make inkai`, `make inkai-smoke`, then `make smoke`. All passed. The independent project-name check and zero-Telegraf-restart assertion passed.
- `make inkai` reached readiness in **120 seconds with cached Docker images**. This is not a cold-download benchmark. The existing Ubuntu installation and downloaded images were reused; only the source checkout, generated credentials and project data volumes were fresh.
- Machine-readable details: `evidence/clean-start.json`. Exact fresh KVM judge reproduction remains unverified. Subsequent changes are evidence/documentation and the presentation builder; runtime code and startup commands remain the tested version.

## Static checks: passed

- `make lint`: Helm lint/template, shell syntax, ShellCheck, Python AST and Compose configuration all passed. Log: `evidence/lint.log`.
- Standalone checks covered all 32 tracked shell scripts and all 26 tracked Python files. The browser JavaScript passed `node --check`.
- Helm 3.19.0 (official release, verified SHA-256) and ShellCheck 0.9.0 were installed **after** clean Compose verification to complete development lint. They are not application startup dependencies. The original chart's icon recommendation is informational.
- The final presentation was rendered and visually reviewed. PDF/PNG files are explicitly binary in `.gitattributes` to preserve their bytes across Windows/Linux checkouts.

## Environment limits

Ubuntu 24.04.5 amd64 under WSL2, Docker Engine 29.1.3, Compose 2.40.3, approximately 7 GiB guest RAM and 6 virtual CPUs. The official judge is an 8-vCPU/16-GiB Ubuntu 24.04.5 KVM machine. WSL is not an exact reproduction; download speed is network-dependent.

WSL stopped when its launcher ended; a persistent local WSL session was then used to keep Docker running. This WSL-specific issue does not apply to the KVM judge. No manual credentials or external datasets were needed for startup.

The local demonstration currently runs from `/home/minemind/team-118-cleancheck` as project `minemind-clean`, at `http://localhost:8088/`. To operate that isolated instance from its directory, prefix commands with `COMPOSE_PROJECT_NAME=minemind-clean`, for example `COMPOSE_PROJECT_NAME=minemind-clean make down` after use. This project-name override is only for local test isolation; normal README startup uses the default project name.
