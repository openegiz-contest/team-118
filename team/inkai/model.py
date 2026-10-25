"""Deterministic daily accounting. All masses are elemental U unless named otherwise.

This model deliberately makes no acid-to-grade or optimal-allocation claim.
run() is pure: both the platform publisher and tests use this same implementation.
"""

import copy
import json
import os
import re
from functools import lru_cache
from pathlib import Path

CONFIG_PATH = Path(__file__).with_name("config.json")
NAMESPACE = os.environ.get("INKAI_NAMESPACE", "org.minemind.inkai")
if not re.fullmatch(r"[A-Za-z0-9_.-]{1,100}", NAMESPACE):
    raise ValueError("Invalid INKAI_NAMESPACE")


def load_config():
    return json.loads(CONFIG_PATH.read_text(encoding="utf-8"))


def daily_capacity(mlb, config):
    """Annual U3O8 capacity -> assumed uniform daily elemental-U capacity."""
    return mlb * 1_000_000 / config["lb_u3o8_per_kg_u"] / 365


def validate_integer(value, minimum, maximum, name):
    if isinstance(value, bool) or not isinstance(value, int) or not minimum <= value <= maximum:
        raise ValueError(f"{name} must be an integer in [{minimum}, {maximum}]")


def run(delay_days=0, config=None):
    """Return all day-end states, including initial day 0. No hidden/random state.

    The first scheduled delivery to EACH area moves from day 3 to day 3+delay.
    The second delivery stays at day 60. All deliveries remain inside day 90.
    Acid is reserved/consumed in a lump at acidification start (explicit assumption).
    Extraction -> IX recovery/loss -> bounded recovered-U WIP -> dried product.
    A stated operating policy paces upstream flow against drying plus available
    end-of-day WIP headroom. It is not an estimate of Inkai's physical tank size.
    """
    config = copy.deepcopy(config or load_config())
    validate_integer(delay_days, 0, config["max_delay_days"], "delay_days")
    assumptions = config["assumptions"]
    recovery = config["plant_recovery"]
    conversion = config["lb_u3o8_per_kg_u"]
    dry_cap = daily_capacity(config["drying_capacity_mlb_u3o8_year"], config)
    wip_limit = dry_cap * assumptions["wip_target_days"]
    areas, blocks = {}, {}
    for area in config["areas"]:
        aid = area["id"]
        areas[aid] = {
            "id": aid, "label": area["label"], "initial_acid_t": area["initial_acid_t"],
            "acid_inventory_t": area["initial_acid_t"], "acid_received_t": 0.0,
            "acid_used_t": 0.0, "ix_capacity_kg_u_day": daily_capacity(area["ix_capacity_mlb_u3o8_year"], config),
            "extracted_kg_u": 0.0, "recovered_kg_u": 0.0, "unrecovered_kg_u": 0.0,
            "ix_output_kg_u_day": 0.0, "solution_m3_day": 0.0, "ix_utilization": 0.0,
            "potential_extraction_kg_u_day": 0.0, "withheld_kg_u_day": 0.0,
            "map_x": area["map_x"], "map_y": area["map_y"],
        }
        rates = [area["existing_kg_u_day"], *area["new_kg_u_day"]]
        for index, rate in enumerate(rates):
            bid = f"{aid}-b{index}"
            initial_u = rate * assumptions["uranium_inventory_days_at_nominal_rate"]
            blocks[bid] = {
                "id": bid, "area": aid, "label": f"{area['label']} {'existing' if index == 0 else 'new '+str(index)}",
                "synthetic": True, "x": area["map_x"] + 35 + index * 132, "y": area["map_y"] + 105,
                "nominal_kg_u_day": rate, "acid_requirement_t": 0 if index == 0 else area["new_acid_t"][index - 1],
                "planned_acid_day": None if index == 0 else config["planned_acidification_days"][index - 1],
                "acid_start_day": None, "commission_day": 0 if index == 0 else None,
                "state": "ready" if index == 0 else "planned", "initial_uranium_kg": initial_u,
                "remaining_uranium_kg": initial_u, "extracted_kg_u": 0.0,
                "extraction_kg_u_day": 0.0, "capacity_factor": 1.0,
                "potential_kg_u_day": 0.0, "ix_factor": 1.0, "drying_factor": 1.0,
            }
    pending, product, loss, extracted, withheld = 0.0, 0.0, 0.0, 0.0, 0.0
    history = []
    for day in range(config["horizon_days"] + 1):
        dry_today = 0.0
        drying_factor, potential_today, withheld_today = 1.0, 0.0, 0.0
        if day:
            # First stage: lifecycle and potential demand, before removing U.
            area_demands = {}
            for definition in config["areas"]:
                area = areas[definition["id"]]
                for delivery_day, quantity in (
                    (config["delivery_days"][0] + delay_days, definition["delivery_t"]),
                    (config["delivery_days"][1], definition["second_delivery_t"]),
                ):
                    if day == delivery_day:
                        area["acid_inventory_t"] += quantity
                        area["acid_received_t"] += quantity
                demands = []
                for block in (b for b in blocks.values() if b["area"] == area["id"]):
                    if block["planned_acid_day"] is not None and block["commission_day"] is None:
                        if day >= block["planned_acid_day"]:
                            if block["acid_start_day"] is None:
                                if area["acid_inventory_t"] + 1e-9 >= block["acid_requirement_t"]:
                                    area["acid_inventory_t"] -= block["acid_requirement_t"]
                                    area["acid_used_t"] += block["acid_requirement_t"]
                                    block["acid_start_day"] = day
                                else:
                                    block["state"] = "waiting_acid"
                            if block["acid_start_day"] is not None:
                                ready = block["acid_start_day"] + assumptions["acidification_days"]
                                if day >= ready:
                                    block["commission_day"] = ready
                                else:
                                    block["state"] = "acidifying"
                    demand = 0.0
                    if block["commission_day"] is not None:
                        # The existing block is already at full rate on day 1.
                        ramp = 1.0 if block["planned_acid_day"] is None else min(
                            1.0, (day - block["commission_day"] + 1) / assumptions["ramp_days"])
                        block["state"] = "ramping" if ramp < 1 else "producing"
                        demand = min(block["nominal_kg_u_day"] * ramp, block["remaining_uranium_kg"])
                    demands.append((block, demand))
                demand_total = sum(demand for _, demand in demands)
                factor = min(1.0, area["ix_capacity_kg_u_day"] / (demand_total * recovery)) if demand_total else 1.0
                area_demands[area["id"]] = (demands, factor)
                area["potential_extraction_kg_u_day"] = demand_total
                potential_today += demand_total

            # Daily mass-flow policy: the dryer can process dry_cap today, and
            # only wip_limit may remain at day-end. Excess stays underground.
            ix_available = sum(sum(d for _, d in ds) * factor * recovery
                               for ds, factor in area_demands.values())
            admitted_recovered_u = max(0.0, dry_cap + wip_limit - pending)
            drying_factor = min(1.0, admitted_recovered_u / ix_available) if ix_available else 1.0
            for aid, (demands, ix_factor) in area_demands.items():
                area = areas[aid]
                input_today = 0.0
                for block, demand in demands:
                    actual = demand * ix_factor * drying_factor
                    block["potential_kg_u_day"] = demand
                    block["extraction_kg_u_day"] = actual
                    block["ix_factor"] = ix_factor if demand else 1.0
                    block["drying_factor"] = drying_factor if demand else 1.0
                    block["capacity_factor"] = ix_factor * drying_factor if demand else 1.0
                    block["remaining_uranium_kg"] -= actual
                    block["extracted_kg_u"] += actual
                    input_today += actual
                    if block["remaining_uranium_kg"] < 1e-7:
                        block["state"] = "depleted"
                output_today = input_today * recovery
                area["extracted_kg_u"] += input_today
                area["recovered_kg_u"] += output_today
                area["unrecovered_kg_u"] += input_today - output_today
                area["ix_output_kg_u_day"] = output_today
                area["solution_m3_day"] = input_today / (assumptions["head_grade_mg_u_l"] / 1000)
                area["ix_utilization"] = output_today / area["ix_capacity_kg_u_day"]
                area["withheld_kg_u_day"] = area["potential_extraction_kg_u_day"] - input_today
                withheld_today += area["withheld_kg_u_day"]
                pending += output_today
                loss += input_today - output_today
                extracted += input_today
            dry_today = min(pending, dry_cap)
            pending -= dry_today
            product += dry_today
            withheld += withheld_today
        for area in areas.values():
            assert abs(area["initial_acid_t"] + area["acid_received_t"] - area["acid_used_t"] - area["acid_inventory_t"]) < 1e-7
            assert area["acid_inventory_t"] >= -1e-7
        assert abs(extracted - product - pending - loss) < 1e-6
        assert -1e-7 <= pending <= wip_limit + 1e-7
        history.append(copy.deepcopy({
            "day": day, "delay_days": delay_days, "areas": areas, "blocks": blocks,
            "product_kg_u": product, "product_lb_u3o8": product * conversion,
            "pending_kg_u": pending, "unrecovered_kg_u": loss, "extracted_kg_u": extracted,
            "drying_kg_u_day": dry_today, "drying_capacity_kg_u_day": dry_cap,
            "wip_limit_kg_u": wip_limit, "drying_factor": drying_factor,
            "potential_extraction_kg_u_day": potential_today,
            "withheld_kg_u_day": withheld_today, "withheld_kg_u": withheld,
            "solution_m3_day": sum(a["solution_m3_day"] for a in areas.values()),
            "recovered_kg_u_day": sum(a["ix_output_kg_u_day"] for a in areas.values()),
            "acid_inventory_t": sum(a["acid_inventory_t"] for a in areas.values()),
            "acid_received_t": sum(a["acid_received_t"] for a in areas.values()),
            "acid_used_t": sum(a["acid_used_t"] for a in areas.values()),
        }))
    return history


@lru_cache(maxsize=48)
def _sensitivity_json(delay_days, config_json):
    """Illustrative stress grid, not a probability distribution or site bounds.

    Cache immutable JSON so callers cannot change another run's evidence.
    All cases use run(), including the same mass and capacity invariants.
    """
    config = json.loads(config_json)
    grid = config["sensitivity_grid"]
    rows = []
    for dose in grid["dose_multipliers"]:
        for acid_days in grid["acidification_days"]:
            for wip_days in grid["wip_target_days"]:
                altered = copy.deepcopy(config)
                altered["assumptions"]["acidification_days"] = acid_days
                altered["assumptions"]["wip_target_days"] = wip_days
                for area in altered["areas"]:
                    area["new_acid_t"] = [value * dose for value in area["new_acid_t"]]
                base = run(0, altered)[-1]
                late = run(delay_days, altered)[-1]
                new = [bid for bid, b in late["blocks"].items() if b["planned_acid_day"] is not None]
                delays = [late["blocks"][bid]["commission_day"] - base["blocks"][bid]["commission_day"]
                          for bid in new]
                rows.append({"dose_multiplier": dose, "acidification_days": acid_days,
                             "wip_target_days": wip_days,
                             "product_delta_kg_u": late["product_kg_u"] - base["product_kg_u"],
                             "delayed_groups": sum(d > 0 for d in delays),
                             "max_commission_delay_days": max(delays),
                             "final_wip_kg_u": late["pending_kg_u"],
                             "wip_limit_kg_u": late["wip_limit_kg_u"]})
    result = {"classification": "Illustrative assumption stress grid; not calibrated bounds or confidence intervals",
              "case_count": len(rows), "rows": rows,
              "dose_multipliers": grid["dose_multipliers"], "acidification_days": grid["acidification_days"],
              "wip_target_days": grid["wip_target_days"],
              "min_product_delta_kg_u": min(r["product_delta_kg_u"] for r in rows),
              "max_product_delta_kg_u": max(r["product_delta_kg_u"] for r in rows),
              "min_delayed_groups": min(r["delayed_groups"] for r in rows),
              "max_delayed_groups": max(r["delayed_groups"] for r in rows)}
    return json.dumps(result, separators=(",", ":"), allow_nan=False)


def sensitivity(delay_days, config=None):
    config = config or load_config()
    validate_integer(delay_days, 0, config["max_delay_days"], "delay_days")
    return json.loads(_sensitivity_json(delay_days, json.dumps(config, sort_keys=True)))


def comparison(delay_days, day, config=None):
    config = config or load_config()
    validate_integer(delay_days, 0, config["max_delay_days"], "delay_days")
    validate_integer(day, 0, config["horizon_days"], "day")
    baseline = run(0, config)
    scenario = baseline if delay_days == 0 else run(delay_days, config)
    current = copy.deepcopy(scenario[day])
    for bid, block in current["blocks"].items():
        base = baseline[-1]["blocks"][bid]
        forecast = scenario[-1]["blocks"][bid]
        block["baseline_commission_day"] = base["commission_day"]
        block["projected_commission_day"] = forecast["commission_day"]
        block["commission_delay_days"] = ((forecast["commission_day"] - base["commission_day"])
                                             if forecast["commission_day"] is not None and base["commission_day"] is not None else None)
    current["baseline_product_kg_u"] = baseline[day]["product_kg_u"]
    current["product_delta_kg_u"] = current["product_kg_u"] - baseline[day]["product_kg_u"]
    current["projection"] = {
        "days": list(range(config["horizon_days"] + 1)),
        "baseline_product_kg_u": [s["product_kg_u"] for s in baseline],
        "scenario_product_kg_u": [s["product_kg_u"] for s in scenario],
        "baseline_acid_t": [s["acid_inventory_t"] for s in baseline],
        "scenario_acid_t": [s["acid_inventory_t"] for s in scenario],
        "baseline_wip_kg_u": [s["pending_kg_u"] for s in baseline],
        "scenario_wip_kg_u": [s["pending_kg_u"] for s in scenario],
        "horizon_days": config["horizon_days"],
        "final_product_delta_kg_u": scenario[-1]["product_kg_u"] - baseline[-1]["product_kg_u"],
        "delivered_t_equal_at_horizon": scenario[-1]["acid_received_t"] == baseline[-1]["acid_received_t"],
        "baseline_deliveries": config["delivery_days"],
        "scenario_deliveries": [config["delivery_days"][0] + delay_days, config["delivery_days"][1]],
    }
    current["assumptions"] = config["assumptions"]
    current["sensitivity"] = sensitivity(delay_days, config)
    return current


def twin_definitions(config=None):
    """Attributes carry spatial/operational relationships; features arrive via MQTT."""
    config = config or load_config()
    attrs = {
        "site": {"kind": "mine", "label": "MineMind / representative JV Inkai", "provenance": "source-informed representative simulation"},
        "scenario": {"kind": "scenario", "_parents": [f"{NAMESPACE}:site"], "controls": "delivery delay, day, reset"},
        "packaging": {"kind": "plant", "_parents": [f"{NAMESPACE}:site"], "receivesFrom": [f"{NAMESPACE}:{a['id']}" for a in config["areas"]]},
    }
    initial = run(0, config)[0]
    for aid, area in initial["areas"].items():
        attrs[aid] = {"kind": "area_ix", "label": area["label"], "_parents": [f"{NAMESPACE}:site"], "feeds": f"{NAMESPACE}:packaging"}
        attrs[f"acid-{aid}"] = {"kind": "acid_tank", "provenance": "synthetic commissioning-only stock", "_parents": [f"{NAMESPACE}:{aid}"], "supplies": [f"{NAMESPACE}:{bid}" for bid, b in initial["blocks"].items() if b["area"] == aid and b["planned_acid_day"] is not None]}
    for bid, block in initial["blocks"].items():
        attrs[bid] = {"kind": "block_group", "provenance": "synthetic", "_parents": [f"{NAMESPACE}:{block['area']}"], "feeds": f"{NAMESPACE}:{block['area']}", "x": block["x"], "y": block["y"]}
        if block["planned_acid_day"] is not None:
            attrs[bid]["acidFrom"] = f"{NAMESPACE}:acid-{block['area']}"
        else:
            attrs[bid]["acidSupply"] = "Protected outside the commissioning-only boundary"
    return {f"{NAMESPACE}:{name}": {"policyId": "default:basic_policy", "attributes": values, "features": {}} for name, values in attrs.items()}


def twin_states(snapshot):
    states = {"site": {k: v for k, v in snapshot.items() if k not in ("areas", "blocks", "projection", "assumptions", "sensitivity")}}
    # Telegraf json_v2 expands arrays into metrics. Several 91-element arrays
    # in one object can explode the record count and exhaust its memory limit.
    # Keep the lossless projection in Ditto as one string field; the UI parses it.
    states["scenario"] = {"day": snapshot["day"], "delay_days": snapshot["delay_days"], "projection": json.dumps(snapshot["projection"], separators=(",", ":"), allow_nan=False), "assumptions": snapshot["assumptions"], "sensitivity": json.dumps(snapshot["sensitivity"], separators=(",", ":"), allow_nan=False)}
    states["packaging"] = {k: snapshot[k] for k in ("pending_kg_u", "product_kg_u", "drying_kg_u_day", "drying_capacity_kg_u_day", "unrecovered_kg_u", "extracted_kg_u", "wip_limit_kg_u", "drying_factor", "withheld_kg_u_day")}
    for aid, area in snapshot["areas"].items():
        states[aid] = area
        states[f"acid-{aid}"] = {k: area[k] for k in ("initial_acid_t", "acid_inventory_t", "acid_received_t", "acid_used_t")}
    states.update(snapshot["blocks"])
    return {f"{NAMESPACE}:{name}": state for name, state in states.items()}
