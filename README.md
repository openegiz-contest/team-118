# MineMind: representative JV Inkai commissioning twin

OpenEgiz Contest 2026 · Team 118 · solo participant `ahsan-h-shihab`.

A source-informed **representative simulation** of how delayed sulphuric-acid deliveries can defer new wellfield commissioning. Nine synthetic groups in three areas connect acid stocks, lifecycle states, IX recovery and drying inventory. No site calibration, optimizer or actual operating forecast is claimed.

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

1. Click **Reset baseline**. Applied delay and day become 0; stocks, schedules, model uranium inventories, product and queues return to the initial baseline.
2. Set **View day** to **30**, click **View day**, and observe the baseline.
3. Set **First delivery delay** to **28**, click **Apply delay**. First arrivals move D3→D31. New groups wait for acid; stocks, states, start dates and product change.
4. View day **38**. New groups finish the assumed seven-day acidification and begin ramping. Click a block, tank or IX plant to inspect its Ditto state.
5. View day **90**. Compare product, drying queue and equal cumulative delivered acid. Outlined blocks have delayed commissioning.
6. Click **Reset baseline** to undo everything. The transport revision changes; all physical states match original day 0 exactly.

Delay is 0–42 whole days. **Advance 7 days** and **Play days/Pause** traverse daily states. Applying a delay recomputes a counterfactual from the same initial conditions at the selected day. This is not a retroactive edit of a real operating event.

Purple stocks are **commissioning acid only**. Existing and sustaining-production acid supply is protected outside this model. Uranium-bearing solution goes to area IX; aggregate recovered-U transfer goes to MPP. Acid stock is separate from uranium/product inventory.

## Verification and source files

```bash
make inkai-test       # 21 standard-library unit tests
make inkai-smoke      # live MQTT -> Ditto -> UI, scenario, rerun and reset
make smoke           # original MQTT/Ditto/InfluxDB/Grafana platform check
python3 -m team.inkai.report
```

`inkai-smoke` checks all 18 platform-derived states against the model and leaves the Stand at baseline/day 0. Actual results and clean-start coverage are in [`team/inkai/EVIDENCE.md`](team/inkai/EVIDENCE.md). Internal consistency is not operational validation.

- `team/inkai/model.py`, `config.json`: deterministic model and values.
- `team/inkai/server.py`: REST twin initialization; MQTT runtime writes; Ditto-only reads. Missing twins/mixed revisions fail closed.
- `team/inkai/web/`: independent SVG spatial view, controls, projections and inspector.
- `team/inkai/compose.yml`: application overlay on the supplied platform.
- [`team/inkai/PARAMETERS.md`](team/inkai/PARAMETERS.md): sources, provenance, equations and assumptions.
- [`SUBMISSION.md`](SUBMISSION.md), [`presentation.pdf`](presentation.pdf): Concept, submission description and presentation.
- [`OPENEGIZ.md`](OPENEGIZ.md): upstream platform reference. Example Mine is not this submission.

## Operation

```bash
make ps
docker compose -f deploy/compose/docker-compose.yml -f team/inkai/compose.yml logs --tail=100 inkai
```

To stop the Stand after use, run `make down`; it preserves volumes and credentials. `make inkai` starts again; application restart deliberately resets the scenario. Port 8088 and upstream ports must be free. Platform failure produces a stale-state/error indication, never standalone model results.

Windows development uses Ubuntu 24.04 WSL2 with the checkout in Linux storage; see `OPENEGIZ.md`. When using Docker Engine inside WSL, keep the Ubuntu terminal/session open: systemd services alone [do not keep WSL alive](https://learn.microsoft.com/en-us/windows/wsl/systemd). Docker needs approximately 6 GiB available. The local WSL test machine is smaller than the judge's 16-GiB KVM environment; see the evidence record.

## Data, license and delivery

MineMind's code, configuration and schematic are MIT; see [`LICENSE`](LICENSE). Platform components retain their licenses and [`NOTICE`](NOTICE). No confidential/personal data, company PDFs, copied figures or third-party dataset is bundled. Research sources are references, not startup downloads. Simulated results are not measurements or advice to JV Inkai.

Submission is **`main`** at the freeze: 25 October 2026, 23:59 Astana (UTC+5).
