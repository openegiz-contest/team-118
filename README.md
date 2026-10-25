# MineMind: representative JV Inkai commissioning twin

OpenEgiz Contest 2026 · Team 118 · solo participant `ahsan-h-shihab`.

A source-informed **representative simulation** of how delayed sulphuric-acid deliveries can defer new wellfield commissioning. Nine synthetic groups in three areas connect acid stocks, lifecycle states, IX recovery and a bounded drying buffer. A 27-case assumption check exposes which conclusions depend on the selected coefficients. No site calibration, optimizer or actual operating forecast is claimed.

## Install and start from this repository root

Target: the [official judge environment](https://openegiz-contest.github.io/environment/), Ubuntu 24.04 amd64 with Docker Engine 29.1.3 and Compose 2.40.3. The judge already has Docker permissions and Python 3. Install `make`, which is absent from the judge base image:

```bash
sudo apt-get update && sudo apt-get install -y make
make inkai-test
make inkai
make inkai-smoke
```

`make inkai` generates local credentials, starts the supplied OpenEgiz platform, builds the application, creates 18 Ditto twins, publishes their features through MQTT and confirms their ingestion. It waits for readiness and prints the UI address. No API keys, external datasets, cloud services or manual configuration are needed. The first run downloads the platform images and builds its pinned extended API; network time matters within the official 75-minute startup limit.

The application adds only `paho-mqtt==2.1.0` to `python:3.12.12-slim`. All UI assets are included locally. Credentials stay in ignored `deploy/compose/.env`; never publish this file.

## Open and demonstrate

Open **http://localhost:8088/**, the submission's spatial interface. Grafana/OpenEgiz Twins remain at **http://localhost:3000/**; startup prints their generated credentials. The spatial UI needs no login because it is bound to localhost; Ditto credentials remain server-side.

1. The application opens at **baseline day 30**, with operating flows visible. **Baseline · day 30** restores this view.
2. Click **Delay 28 days · compare**. First arrivals move D3→D31. Six new groups wait for acid; the day-30 product becomes 188.16 t U versus 231.30 t U in the baseline.
3. Click a representative field, tank or IX plant. Follow separate commissioning-acid stocks, wellfield states, solution-equivalent flow, IX recovery, bounded work in process (WIP), and dried product.
4. Set **View day** to **38** and click **View day**: new groups start the assumed ramp after seven days of acidification. View **90** for the common-horizon comparison and equal delivered acid.
5. Read **Does the conclusion survive different assumptions?** The 27-case grid varies commissioning dose, acidification duration and WIP target. For a 28-day delay, 3–6 groups start late, but the day-90 product difference ranges from −61.66 to 0 t U. These are illustrative assumptions, not calibrated bounds.
6. Click **Reset · day 0** to undo everything. Day/delay, deliveries, stocks, schedules, lifecycle states, model uranium, product and WIP return to initial conditions. Existing groups are labelled **ready** because no time has elapsed. The transport revision changes; physical state matches baseline day 0.

Delay is 0–42 whole days. **Advance 7 days** and **Play days/Pause** traverse daily states. Applying a delay recomputes a counterfactual from the same initial conditions at the selected day. This is not a retroactive edit of a real operating event.

The explicit operating policy paces extraction against area IX limits, shared drying capacity and an assumed one-day end-of-day WIP target. Capacity-withheld potential uranium stays underground; the WIP target is not a measured physical tank size.

Purple stocks are **commissioning acid only**. Existing and sustaining-production acid supply is protected outside this model. Uranium-bearing solution goes to area IX; aggregate recovered-U transfer goes to MPP. Acid stock is separate from uranium/product inventory.

## Verification and source files

```bash
make inkai-test       # 29 unit tests: 26 model + 3 mocked read-contract tests
make inkai-smoke      # live MQTT -> Ditto -> UI, scenario, rerun and reset
make smoke           # original MQTT/Ditto/InfluxDB/Grafana platform check
python3 -m team.inkai.report
python3 -m team.inkai.report --sensitivity
```

`inkai-smoke` runs 12 check groups against all 18 platform-derived states, verifies day-0 reset, then leaves baseline/day 30. It changes the running scenario; run it on a dedicated test instance when preserving a demonstration. `INKAI_NAMESPACE` and `INKAI_URL` must match the target; the namespace guard refuses a different Stand before sending controls. Actual results and clean-start coverage are in [`team/inkai/EVIDENCE.md`](team/inkai/EVIDENCE.md). Internal consistency is not operational validation.

- `team/inkai/model.py`, `config.json`: deterministic model and values.
- `team/inkai/server.py`: REST twin initialization; MQTT runtime writes; Ditto-only reads. Missing twins/mixed revisions fail closed.
- `team/inkai/web/`: representative field footprints, process connections, controls, three projections, sensitivity table and inspector.
- `team/inkai/compose.yml`: application overlay on the supplied platform.
- [`team/inkai/PARAMETERS.md`](team/inkai/PARAMETERS.md): sources, provenance, equations and assumptions.
- [`SUBMISSION.md`](SUBMISSION.md), [`presentation.pdf`](presentation.pdf): Concept, submission description and presentation.
- [`OPENEGIZ.md`](OPENEGIZ.md): upstream platform reference. Example Mine is not this submission.

The revised runtime passed a fresh full-stack Ubuntu WSL2 startup with new credentials, isolated empty volumes and cached images/build layers in **83.60 seconds**. That run passed 29 unit tests, 12 live application check groups and 23 platform smoke checks. Project/image/port overrides isolated the acceptance run; runtime source was unchanged. Cold image downloads and exact judge-KVM startup remain unverified; see the evidence record.

## Operation

```bash
make ps
docker compose -f deploy/compose/docker-compose.yml -f team/inkai/compose.yml logs --tail=100 inkai
```

To stop the Stand after use, run `make down`; it preserves volumes and credentials. `make inkai` starts again; application restart deliberately restores baseline/day 30; the Reset control restores day 0. Port 8088 and upstream ports must be free. Platform failure produces a stale-state/error indication, never standalone model results.

Windows development uses Ubuntu 24.04 WSL2 with the checkout in Linux storage; see `OPENEGIZ.md`. When using Docker Engine inside WSL, keep the Ubuntu terminal/session open: systemd services alone [do not keep WSL alive](https://learn.microsoft.com/en-us/windows/wsl/systemd). Docker needs approximately 6 GiB available. The local WSL test machine is smaller than the judge's 16-GiB KVM environment; see the evidence record.

## Data, license and delivery

MineMind's code, configuration and schematic are MIT; see [`LICENSE`](LICENSE). Platform components retain their licenses and [`NOTICE`](NOTICE). No confidential/personal data, company PDFs, copied figures or third-party dataset is bundled. Research sources are references, not startup downloads. Simulated results are not measurements or advice to JV Inkai.

Submission is **`main`** at the freeze: 25 October 2026, 23:59 Astana (UTC+5).
