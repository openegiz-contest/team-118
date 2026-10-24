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
- Browser observations confirmed the day-30 baseline (231.30 t U), delayed case (188.16 t U), six waiting groups, spatial twin inspection and day-38 ramping. Screenshots are in `evidence/`. Final browser/reset verification remains pending on the clean checkout.

## Pending clean-start verification

A source checkout with new generated credentials and a separate, initially empty Docker-volume project will be tested next. Downloaded images will be reused. Exact fresh KVM judge reproduction remains unverified.

## Environment limits

Ubuntu 24.04.5 amd64 under WSL2, Docker Engine 29.1.3, Compose 2.40.3, approximately 7 GiB guest RAM and 6 virtual CPUs. The official judge is an 8-vCPU/16-GiB Ubuntu 24.04.5 KVM machine. WSL is not an exact reproduction; download speed is network-dependent.

WSL stopped when its launcher ended; a persistent local WSL session was then used to keep Docker running. This WSL-specific issue does not apply to the KVM judge. No manual credentials or external datasets were needed for startup.
