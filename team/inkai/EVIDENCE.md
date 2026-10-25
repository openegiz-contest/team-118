# Execution evidence

Recorded on 25 October 2026 (Astana, UTC+5). These records separate the current local revision from earlier startup evidence. A test pass is internal/software evidence, not site calibration or validation of acid-response coefficients.

## Current local revision

Based on `7db06b400d49f0dbfef53a29e1fea9810d8f93f2`, with uncommitted improvements. Tested runtime file hashes are recorded in `evidence/revision-manifest.json`; the baseline is recoverable outside the repository. The participant's original Concept was committed as `9efe154` before implementation. The current Concept removes the unimplemented policy/start-order promise while retaining the participant's chosen object, user and personal motivation.

### Unit and deterministic checks: passed

- **29 tests**, comprising **26 model tests and three mocked platform-read contract tests**, passed on Windows, Ubuntu WSL2 and the actual Python 3.12.12 application image.
- Commands: `python -B -m unittest discover -s team/inkai/tests -v` on Windows; `make inkai-test` in Ubuntu. Logs: `evidence/unit-tests.log`, `unit-tests-wsl.log`, `unit-tests-image.log`.
- The image stores the package as `/app/inkai`; its unit runner supplies a temporary in-memory `team` parent-package alias for the repository-style test imports. No image files are changed. This is unit testing, not the application startup command.
- Added checks cover a hand-calculated two-day dryer/buffer example, WIP draining after input depletion, WIP targets and delivery delays, uranium retained underground, ready/zero-flow day 0, all 27 sensitivity cases, central-case equivalence, zero-deficit/late-block coexistence, cache-copy isolation and serialization.
- `python3 -m team.inkai.report` and `python3 -m team.inkai.report --sensitivity` generated `model-results.json` and `sensitivity-results.json`. Conservation assertions execute at every simulated day. These cases use the same engine; the illustrative grid is not external validation.

### Built-image integration: passed

- Built the actual Dockerfile as `minemind/inkai:verified-20261025`; cached base image/dependencies were reused. Log: `evidence/image-build.log`.
- Started a separate application container on port 8091, namespace `org.minemind.inkai.verified20261025`, on the existing `minemind-clean_default` platform network. **No source bind mount** was used. The image reached 18 ingested twins in 3.62 seconds; this is application readiness on a warm platform, not full-stack startup timing.
- Ran `docker exec minemind-inkai-verification python -B -m inkai.integration_check`: **12 check groups passed**, with actual MQTT publication and Ditto REST reads. Logs: `integration-results.json`, `isolated-image-start.json`.
- The check guards the target namespace before mutations; compares all 18 twin states; verifies delivery effects, day-38 commissioning, deterministic reruns, equal final acid, bounded WIP/flow pacing, the lossless 27-case payload, complete day-0 reset, invalid-input rejection, health/UI assets, then baseline day 30.
- The 13 runtime/build/test files in `evidence/runtime-image-hashes.json` match the tested image byte for byte. Documentation/evidence records were finalized afterward.
- Comparisons against the same model test transport and synchronization. Independent arithmetic and invariants are in the unit tests. The HTML check does not claim visual correctness by itself.
- Only the verification container was stopped after testing. The original Stand's canonical API snapshot SHA-256 was unchanged before/after, and its app/Telegraf restart counts stayed zero. Credentials, original volumes and original namespace were preserved.

### Interactive browser observations: passed

The separate preview at `http://localhost:8089/`, namespace `org.minemind.inkai.preview20261025`, exercised the same runtime/UI source. This preview uses a read-only source bind mount; the independent image test above covers packaging without that mount.

Observed baseline day 30 (231.30 t U), delay 28 at day 30 (188.16 t U and six waiting groups), Sat-2 B1 inspection, day-38 ramping, advance to day 45, play/pause, day 90 (694.44 t U product and 8.75 t U WIP), sensitivity output, complete visible reset and baseline restoration. Captured browser warning/error log was empty. An in-flight daily request can finish after Pause; Pause prevents subsequent steps.

Actual captures: `baseline-day30.png`, `delayed-day30.png`, `delayed-spatial.png`, `sensitivity.png`. These are manual observations, not an automated browser suite. Current platform-outage browser behavior was not fault-injected; fail-closed reads have three mocked contract tests, and the original runtime had a manual outage check.

### Static and packaging checks: passed with documented scope

- JavaScript: `node --check team/inkai/web/app.js`.
- Python AST across tracked Python sources; shell syntax across 32 tracked shell scripts; ShellCheck; Helm lint and template; combined platform/application Compose configuration. Results: `static-checks.json`, `lint.log`.
- Individual lint commands were used instead of `make lint`, so no local credentials were generated. Compose read the existing isolated-platform environment file without printing or modifying secrets.
- WSL initially rejected Git access to the Windows-owned checkout. A per-command exact-path `safe.directory` setting was used for read-only file enumeration; no global Git setting changed.
- Unchanged upstream shell files in this Windows checkout have CRLF. Bash/ShellCheck used LF-normalized text via stdin, matching a normal Linux checkout. This is not a successful literal startup from the Windows-mounted directory. For WSL startup, use a native Linux checkout as README/OPENEGIZ describe.
- Initial Helm lint failed because it included an ignored local Git bundle under `tmp/`. Adding `tmp/` to `.helmignore` excludes local verification artifacts; the rerun passed. No bundle or other local data was deleted.
- PDF/PNG files remain binary in `.gitattributes`. The updated eight-page presentation was generated from model outputs, current evidence and actual screenshots, rendered with Poppler, and all eight pages were visually reviewed. No clipped or overlapping content was observed.

## What changed in model results

`evidence/before-after.json` executes the original model/config directly from commit `7db06b4` and compares the current model. These are simulated outcomes, not measured operational improvements.

| Baseline at day 90 | Original | Current |
|---|---:|---:|
| Recovered-U WIP | 365.993 t U | 8.747 t U |
| Actual solution-equivalent flow | 6,048.72 m³/h | 3,718.84 m³/h |
| Cumulative extracted U | 1,144.997 t U | 780.460 t U |
| Dried product | 756.104 t U | 756.104 t U |

Nominal potential extraction rates and commissioning doses are unchanged. The new assumed pacing policy retains excess potential extraction underground instead of building unbounded WIP. This improves constraint consistency, not evidence for real Inkai coefficients. The original 90-day dried product already annualized to approximately 7.97 Mlb U3O8; the major excess was upstream of drying, not the final product. Annualizing a short synthetic exercise is context only.

For delay 28, the default day-90 product difference remains −61.66 t U. Across the 27 illustrative cases it spans −61.66 to 0 t U, with 3–6 groups starting late. A production deficit is therefore not robust across this grid. This finding is visible in the interface and presentation.

## Fresh full-stack acceptance — current runtime

On 25 October 2026, the current working-tree runtime was exported to native Ubuntu 24.04.5 WSL2 storage and started as a separate Compose project, `minemind-acceptance-20261025-final`. New credentials, six new named volumes, two new anonymous volumes and an isolated network were used. No original Stand volume or credential was reused. Existing Stands were temporarily stopped for memory headroom and subsequently restored; their 36 physical twin states, container identities, volumes and credential hashes matched the preserved snapshots.

- **83.60 seconds to successful full-stack startup**, exit 0: all 16 services reached their expected states (14 running, health-checked services healthy; two one-shot jobs exited 0), and all 18 twins were ingested at baseline day 30.
- The unchanged `make inkai` recipe ran its credential/preflight, image build, Compose wait, initialization-exit and Ditto readiness steps. Command-line Make overrides supplied the isolated project, a unique application image tag and UI port 18088; other service ports were changed only in the new test `.env`. The exact commands are in `evidence/fresh-stack-acceptance.json`.
- **29 unit tests passed** via literal `make inkai-test`: `Ran 29 tests in 2.216s`, `OK`. **12 live check groups passed** via `INKAI_URL=http://127.0.0.1:18088 make inkai-smoke`; **23 platform checks passed** via `make smoke` with the isolated Compose project selected.
- Live checks covered MQTT -> Ditto -> UI, equal final delivered acid, commissioning, IX/drying/WIP constraints, deterministic reruns, all 27 sensitivity cases, complete reset, and the platform's MQTT -> Ditto -> Telegraf -> InfluxDB/Grafana loop. Additional direct Ditto reads matched all 18 reset states. Browser observations confirmed baseline, delay, spatial changes, projections and day-0 reset.
- The built image matched 16 source/config/UI/test/authoring files at test time. Only documentation, evidence and the offline presentation builder changed afterward. The remaining 15 checked files still match the tested image; their hashes are included in the acceptance record. No runtime or model parameter changed after this test.
- Images and dependency build layers were cached. Registry metadata was checked; this is **not an offline or cold-download test**. `make` was already installed, so the apt installation step was not rerun. Inherited shell scripts/Makefile were LF-normalized only in the Linux export; application source bytes were preserved.
- No automatic container restart or OOM kill occurred during the acceptance run. Collected post-readiness logs contained no error/exception candidates. Python application shutdown exhausted Docker's 60-second allowance and exited 137 without OOM; restarting the original containers restored their physical state. No original platform initialization job or HTTP reset control was run during restoration.

Sanitized logs: `evidence/fresh-stack-startup.log`, `fresh-stack-application-integration.log`, `fresh-stack-platform-smoke.log`. `fresh-stack-acceptance.json` records environment, commands, source hashes and test scope. Earlier records below remain historical and have not been relabelled.

## Historical startup/platform evidence — prior runtime only

- `evidence/clean-start.json` records runtime `152ad3bce01fdf6120ffd74a90e14e2a12e0b8e6`, a verified source clone, new credentials, empty project volumes, README commands and 120-second readiness **with cached Docker images**.
- That run passed 21 unit tests, eight live app checks and **23 full-platform smoke checks** including MQTT → Ditto → Telegraf → InfluxDB/Grafana. Original sanitized `platform-smoke.log` is retained unchanged.
- The original Telegraf OOM from expanded projection arrays was addressed by encoding the projection as one lossless string. The new sensitivity grid uses the same approach; serialization tests and live transport passed without restarting original Telegraf.
- The new model/server/UI runtime has changed since that fresh-volume test. The old record must **not** be represented as a clean full-stack test of this revision.

## Remaining startup and model limits

Fresh full-stack acceptance used Ubuntu 24.04.5 WSL2, Docker 29.1.3 and Compose 2.40.3 with six vCPUs and about 7 GiB guest RAM. The official judge uses eight vCPUs and 16 GiB in Ubuntu KVM. **Cold image/dependency downloads and the exact judge KVM remain unverified.** The fresh-volume cached-image test above verifies this runtime's startup and integration, not performance on every host. The root startup commands and platform deployment configuration are unchanged.

There is no calibrated acid response, measured block inventory, surveyed geometry, optimizer or probabilistic uncertainty estimate. The one-day WIP policy assumes instant daily coordination; hydraulic constraints, transport delays and actual storage capacity remain unknown. See `PARAMETERS.md` for every boundary and equation.
