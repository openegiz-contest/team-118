# SUBMISSION - MineMind

## Concept

**Enterprise:** This digital twin represents part of JV Inkai, an in-situ uranium recovery operation in Kazakhstan. It focuses on three areas: MPP, Sat-1 and Sat-2. It also includes the area ion-exchange plants and the limit of MPP drying and packaging.

**Users:** The main user is a wellfield production planner. This person plans when new blocks should receive acid and when they can start production. A production manager is a second user. They can use the twin to compare area production and possible curtailment. The model does not represent the internal logistics system of Kazatomprom.

**Decision:** If sulphuric acid arrives later than planned, how should the planner change the acidification and start dates of new blocks? When the delivery returns to normal, in which order can the delayed blocks start without going over the plant limits? The twin will compare a few clear policies. It will not claim to find the best possible or a proven operating plan.

**Why this choice:** I have always been interested in Kazakhstan's large mineral resources. I want to use data science to study a real problem in this area. Kazatomprom reported that changes in acid delivery timing in 2024 delayed the acidification schedule of new Inkai blocks. This happened even though acid requirements were fulfilled at 106% for the first nine months. Cameco later reported 7.8 million pounds of U₃O₈ production for 2024, compared with a target of 8.3 million pounds. This makes delivery timing a useful problem to study with a digital twin. I want the model to show its assumptions and compare scenarios instead of showing simulated results as real operating facts.

**Real or fictional:** JV Inkai and its main operating details are real. This project is a representative simulation based on public sources. It is not a site-calibrated copy of Inkai. I will use public capacities and historical totals where available. Block group locations, individual block details, acid dose and duration, commissioning delays and production ramp-up are synthetic or assumed unless a source directly supports them. The map will be drawn for this project. It will not copy a published site figure.

## Team

| GitHub |
|---|
| ahsan-h-shihab |

**MineMind**, solo participant.

## Mine

One representative commissioning-delay exercise, with **18 Eclipse Ditto twins** in namespace `org.minemind.inkai`:

| IDs | Type, state and connections |
|---|---|
| `site` | Aggregate stock, extraction, product, unrecovered uranium, drying queue and baseline difference. |
| `mpp`, `sat1`, `sat2` | Area/IX: solution flow, recovered-U output, capacity/utilization; feed `packaging`. |
| `acid-mpp`, `acid-sat1`, `acid-sat2` | Separate synthetic commissioning-only stocks, deliveries and reserved acid; supply their area's new groups. |
| `mpp-b0`…`mpp-b2`, `sat1-b0`…`sat1-b2`, `sat2-b0`…`sat2-b2` | Nine synthetic groups: B0 already producing, B1/B2 new. Spatial position, lifecycle, acid dose/start, commissioning, extraction and remaining model uranium. |
| `packaging` | Shared MPP drying limit, recovered-U queue and cumulative product. |
| `scenario` | Applied delay/day, baseline/delayed projections and assumptions. |

Definitions/relationships: `team/inkai/model.py::twin_definitions`; parameters: `team/inkai/config.json`. Spatial geometry is independently authored and synthetic.

Data path: model → MQTT `telemetry/inkai-*` → platform MQTT source connection → Ditto `/features` → server-side Ditto REST reads → browser SVG/table/charts. `server.py` initializes twins with REST; **all runtime feature changes use MQTT**. All 18 twins must share one revision before a snapshot is served. There is no direct model-state fallback.

Acid stock/commissioning is separate from uranium-bearing solution → area IX → aggregate recovered-U transfer → MPP drying queue. Satellite loaded-resin/eluate transport is omitted. Existing/sustaining-production acid supply is protected outside the commissioning boundary. No cross-area acid transfer is assumed.

## Modules and What-if Scenarios

| Scenario | What it does | How to see it on the Stand | How to undo |
|---|---|---|---|
| Acid-delivery timing and commissioning | Delay first deliveries by 0–42 days; second stays day 60. Changes stock, acidification/start dates, lifecycle, area flow, product and drying queue. Delivered totals agree at day 90. | Open `http://localhost:8088/`. Reset; view day 30; apply delay 28. New groups change from producing/ramping to waiting for acid; first arrival D3→D31. View day 38 for commissioning/ramping, day 90 for horizon comparison. Click twins for details. | **Reset baseline** restores day/delay 0, original deliveries/stocks, lifecycles, model uranium, product/queues/counters and projections. Transport revision changes; physical state matches day 0 exactly. |

This is **one scenario with baseline comparison**, not an optimizer or several policy modules. Runtime controls require no code changes. Applying delay recomputes a counterfactual from the same initial state. **View day**, **Advance 7 days**, and **Play days/Pause** expose the daily states.

## What works and what does not

Implemented: deterministic model, related twin definitions, MQTT publisher, Ditto-only gateway, spatial UI, adjustable delay, baseline comparison, stock/lifecycle/product display, reset and automated checks.

**Verified:** 21 unit tests, eight live Inkai integration checks, all 23 platform smoke checks and the full repository lint target passed. Browser checks covered the spatial view, delay, twin inspection, time controls and reset. The README startup commands succeeded from a clean source checkout with new credentials and empty project volumes, using cached images on Ubuntu WSL2. Exact KVM judge reproduction and real-world model validation remain unverified. Commands, logs, screenshots and limits: `team/inkai/EVIDENCE.md`.

Not implemented: optimization, D1/D2 curtailment policies, outages, individual wells, chemistry/transport, company telemetry, uncertainty forecasting or site calibration. The original Example Mine remains upstream reference only.

## Data and Assumptions

Detailed parameter inventory/equations: `team/inkai/PARAMETERS.md`; executable values: `team/inkai/config.json`.

**Public facts:** Cameco's 2024 technical report, printed p.80, gives demonstrated IX capacities MPP 2.7, Sat-1 6.3, Sat-2 4.5 Mlb U3O8/year and MPP drying/packaging 8.3 Mlb/year; p.82 gives approximately 98% plant recovery. These are annual capacities, not measured instantaneous hydraulic limits. Kazatomprom's 3Q24 update supplies the qualitative acidification-timing mechanism and conversion 2.5998 lb U3O8/kg U. Cameco's annual filing, AIF p.67, supplies the contextual 7.8 Mlb 2024 actual and 8.3 Mlb target; neither is a fitting target.

**Derived estimates:** annual Mlb U3O8 → daily kg elemental U: multiply by 1,000,000, divide by 2.5998 and 365. Uniform daily limits are a modelling approximation. `python3 -m team.inkai.report` reproduces the synthetic example. No chart digitization, 82% utilization or site acid-per-tonne ratio is used.

**Synthetic:** group identities/positions, nominal rates and uranium inventories, commissioning-only tanks, delivery amounts/dates, planned starts and selected delay. No real block measurements or 2023 operating baseline are claimed.

**Assumptions:** B1/B2 whole doses MPP 120/150 t, Sat-1 100/130 t, Sat-2 140/160 t; initial stocks 100/80/110 t. Each area receives 300 t on day 3 and 120 t on day 60; only the first arrival moves. Acidification is planned on days 5/18, starts only with the whole dose, takes 7 days, then ramps over 7 days. Constant head grade is 100 mg U/L; starting model uranium is 180 nominal-rate days per group. Proportional flow curtailment enforces area IX capacity; recovered U queues at drying capacity. No toll processing is modelled. These block-level coefficients are not calibrated.

**Simulated outputs:** every displayed state, stock, flow, start date, product total, difference and trajectory. Acid/uranium conservation establishes internal consistency, not operational validation. The 2% unrecovered stream preserves mass accounting; it is not destroyed uranium. A product difference is horizon-dependent, not a permanent resource loss.

Sources:

1. [Cameco 2024 Inkai technical report](https://www.cameco.com/sites/default/files/documents/Cameco-2024-Inkai-Technical%20Report.pdf), effective 30 September 2024, §§17.1–17.3.
2. [Kazatomprom 3Q24 Operations and Trading Update](https://www.kazatomprom.kz/en/media/view/3Q24_operations_and_trading_update), Inkai discussion and conversion note.
3. [Cameco 2024 annual filing](https://www.cameco.com/sites/default/files/documents/cameco-2024-40-F.pdf#page=76), AIF printed p.67 / PDF p.76.

Only team-authored MIT code/configuration/geometry is redistributed. No company PDFs, copied figures, third-party datasets, confidential or personal data are bundled. Reports are source references, not startup downloads, and retain their publishers' terms. Platform licenses/notices remain intact.

## Mine visualization

`http://localhost:8088/`: three representative areas, nine groups, separate acid stocks, IX plants and shared drying/queue. Lifecycle colours and delayed-start outlines show consequences. Inspector, commissioning table, product projection and acid-stock chart all read platform state. Legend/disclosures distinguish public facts, synthetic inputs, assumptions, derived conversions and simulated outputs. Platform failure produces error/stale-state indication.

## Limitations

- Representative simulation, not site calibration or actual Inkai forecast/control.
- Public capacities/mechanism are sourced; doses, durations, rates and schedules remain synthetic/assumed.
- Commissioning-only acid boundary; no producing-group acid balance or acid-to-grade response.
- Daily steps, fixed acidification/ramp and group order. Capacity limits extraction/processing, not administrative commissioning dates.
- Annual-to-daily capacity approximation; constant recovery; no chemistry, transport, toll processing, energy or economics.
- Sensitivity/operational validation is unfinished. Different assumptions or binding bottlenecks can change or mask product differences. No optimal schedule or general production-loss estimate is claimed.
- Local WSL differs from the official KVM judge; startup coverage is documented in `team/inkai/EVIDENCE.md`.

## Presentation

Root `presentation.pdf`: implemented scope, assumptions, supported evidence and instructions to observe/undo the scenario. No video.

---

Platform: OpenEgiz v1.0.4.
