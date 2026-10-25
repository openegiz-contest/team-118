# Parameters, provenance and equations

This is a **synthetic 90-day commissioning exercise**, not a reconstruction of an Inkai operating year. No annual totals have been fitted. Parameters are in `config.json`; both projections and runtime snapshots use `model.py`.

## Public facts used

| Parameter | Value | Primary source and scope |
|---|---|---|
| Production areas | MPP, Sat-1, Sat-2 | Cameco 2024 Inkai technical report, §17.1, printed pp.80–82 |
| Demonstrated IX capacities | MPP 2.7; Sat-1 6.3; Sat-2 4.5 Mlb U3O8/year | Same report §17.1, printed p.80. Demonstrated under high head-grade conditions; not measured instantaneous hydraulic capacities. |
| Drying/packaging capacity | 8.3 Mlb U3O8/year | Same report §17.1, printed p.80; the operator also describes toll processing. This model omits toll processing. |
| Plant recovery | approximately 98% | Same report §17.3, printed p.82; used as a constant assumption, not a fitted block-leach recovery. |
| Conversion | 2.5998 lb U3O8 per kg elemental U | Kazatomprom 3Q24 update, conversion note. The uranium and U3O8 mass bases are never interchangeable. |
| Timing mechanism | Small mid-April–mid-May 2024 delivery deviations shifted new-block acidification; nine-month acid requirements fulfilled at 106% | Kazatomprom 3Q24 update, Inkai discussion. This supports a qualitative mechanism, not the synthetic 28-day delay or any dose/duration. |
| 2024 production context | 7.8 Mlb U3O8 actual; 8.3 Mlb target, both 100% basis | Cameco 2024 annual filing, AIF printed p.67 (PDF p.76). Context only; not a calibration target. |

Sources:

- [Cameco 2024 Inkai technical report](https://www.cameco.com/sites/default/files/documents/Cameco-2024-Inkai-Technical%20Report.pdf), effective 30 September 2024.
- [Kazatomprom 3Q24 update](https://www.kazatomprom.kz/en/media/view/3Q24_operations_and_trading_update).
- [Cameco 2024 annual filing](https://www.cameco.com/sites/default/files/documents/cameco-2024-40-F.pdf#page=76).

No company PDF, figure, map, third-party dataset or digitized historical chart is redistributed or required at startup. The authored configuration, code and schematic are MIT. Published numerical facts are attributed; the reports remain under their respective owners' terms.

## Synthetic inputs and assumptions

Each area has one existing group B0 (ready at day 0, producing from day 1) and two new groups B1/B2. These labels do not identify real Inkai wellfields. Each area's acid tank is separate; there is no cross-area transfer.

| Area | Initial commissioning acid (t) | Deliveries (t, days 3 / 60) | B1/B2 whole acid dose (t) | B0/B1/B2 nominal extraction (kg U/day) |
|---|---:|---:|---:|---:|
| MPP | 100 | 300 / 120 | 120 / 150 | 1800 / 800 / 900 |
| Sat-1 | 80 | 300 / 120 | 100 / 130 | 2600 / 2000 / 2200 |
| Sat-2 | 110 | 300 / 120 | 140 / 160 | 2000 / 1500 / 1700 |

All values in this table are **synthetic**, chosen to exercise stock shortage, commissioning, IX throttling and bounded drying WIP within a short demonstration. They are not inferred from site-wide acid-consumption totals.

- B1/B2 planned acidification starts: days 5/18. Whole acid dose is reserved at start; an insufficient tank defers the group. Within an area B1 is checked before B2, a fixed rule with no optimality claim.
- Acidification: 7 whole days. Ramp: 1/7 nominal flow on commissioning day, increasing to full flow over 7 days. Both are **assumptions without Inkai-specific coefficients**.
- First delivery moves from day 3 to day `3 + delay`, independently in all three tanks with the same selected delay. Second delivery remains day 60. Delay is an integer 0–42; horizon is 90 days. Therefore cumulative delivered acid is equal at the common horizon.
- The tanks account for **new-group commissioning only**. Existing groups' ongoing acid supply and sustaining acid for new producing groups are assumed available outside this boundary. There is no acid-to-grade response and no producing-group curtailment scenario.
- Uranium head grade: constant synthetic 100 mg U/L. Initial recoverable model uranium per group: 180 times its nominal kg U/day. No claim that this is a real resource estimate or acid-leach recovery curve.
- Plant rates are uniform daily limits obtained from annual demonstrated capacities. Proportional curtailment of all producing flows in an area enforces its IX limit. Commissioning itself is not postponed by IX capacity; flow is throttled afterward.
- Recovered uranium from satellites is represented as an aggregate transfer to MPP. Individual loaded-resin/eluate transport, timing and chemistry are omitted. This is **not** the entire wellfield solution being pumped to the drying plant.
- Shared drying and an **assumed one-day end-of-day WIP target** pace all areas proportionally after their IX limits. This policy allows recovered inflow up to today’s dryer throughput plus remaining WIP headroom. Nominal potential rates are unchanged; withheld potential extraction stays underground. There is no claim that the target describes Inkai storage geometry, an actual control policy, or a measured process residence time. Daily coordination is instantaneous in the model; hydraulic transients and transport/control lags are omitted.
- The drying queue holds recovered elemental-U equivalents. No toll processing, transport delay or packaging-loss factor is added. A forecast deficit is a difference within this horizon, not uranium destroyed or a permanent site production loss.

## Derived quantities and accounting

`IX_or_drying_limit_kg_U/day = capacity_Mlb_U3O8/year * 1,000,000 / 2.5998 / 365`

Annual-to-daily conversion is a modelling approximation. The approximately 98% plant factor is independently reported; no 82% utilization factor is used.

For every daily step and every area:

`acid_stock = initial_stock + received_deliveries - whole_doses_reserved`

For each producing group, extraction demand is `nominal_rate * ramp`, bounded by remaining model uranium. In each area:

`IX_factor[area] = min(1, IX_limit / (sum_extraction_demand * 0.98))`

`possible_recovered_U = sum(demand * IX_factor[area] * 0.98)`

`WIP_target_U = drying_limit * assumed_WIP_target_days`

`admitted_recovered_U = max(0, drying_limit + WIP_target_U - previous_end_of_day_WIP)`

`drying_factor = min(1, admitted_recovered_U / possible_recovered_U)` (1 if no potential flow)

`actual_extraction = demand * IX_factor[area] * drying_factor`

Daily balances process incoming material before recording day-end WIP; instantaneous tank fill is not modelled. End-of-day WIP is asserted nonnegative and no larger than the target. Potential extraction minus actual extraction is a daily curtailment measure, not a unique resource or permanent loss.

`solution_m3/day = extracted_kg_U/day / (100 mg/L * 0.001)`

The recovered stream is `0.98 * extracted U`; the other 2% is recorded as an **unrecovered uranium stream**, not destroyed mass. Recovered U joins the drying queue. Daily dried product is `min(queue, drying_limit)`; the remainder stays in inventory.

`cumulative_extracted_U = cumulative_dried_U + queue_U + cumulative_unrecovered_U`

`initial_group_U = remaining_group_U + cumulative_extracted_group_U`

## Simulated outputs

All lifecycle states, stocks, flows, commissioning dates, product totals, differences and chart trajectories are **simulated**. Day 0 has initial stocks and zero accumulated production; production begins on day 1 for existing groups. The day selector shows daily accounting states, while projections cover the same 90-day horizon.

The multi-series projection is serialized as a JSON string in the scenario twin's `state` feature. The UI parses that string received from Ditto. This preserves the complete projection without Telegraf's `json_v2` expanding multiple arrays into a very large metric set. Scalar live state remains structured JSON.

## Reproducible assumption sensitivity

`python3 -m team.inkai.report --sensitivity` prints all 27 cases also carried in the scenario twin and displayed by the interface:

- Commissioning doses ×0.75, ×1 and ×1.25.
- Acidification durations 3, 7 and 14 days; the seven-day ramp is unchanged.
- WIP targets 0, 1 and 7 days of drying capacity.

These axes are illustrative perturbations, not sourced plausible ranges or a probability distribution. Each case runs its own baseline and delayed scenario with the same deterministic engine and conservation assertions. The visible 3×3 table holds WIP at the default one day; the summary covers all 27 cases. The grid uses simultaneous changes, not a fitted response surface.

At delay 28, all grid cases have 3–6 late groups, but the day-90 product difference spans −61.66 to 0 t U. Lower doses let B1 start from initial stock, and binding processing capacity can hide the delayed B2 contribution. The result supports investigating commissioning risk; it does not support a robust estimate of uranium loss. Similar differences across acidification-duration cases arise from this exercise's common shifts and fixed bottleneck, not evidence that acidification duration never matters.

The sensitivity result is serialized as a JSON string for the same telemetry-size reason as the projection. No new runtime dependencies or external services are used.

Reproduce the documented example with `python3 -m team.inkai.report`. Annual production accounting or internal mass conservation does not validate real short-term acidification behaviour. Chemical transport, real wellfield schedules and operational validation remain outside the MVP. The 27-case assumption check is internal scenario analysis, not validation against observations.
