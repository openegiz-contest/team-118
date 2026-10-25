"""Reproduce the documented synthetic example, without Docker or downloads."""
import json
import argparse

from .model import comparison, daily_capacity, load_config, run, sensitivity


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sensitivity", action="store_true", help="Print the full illustrative 27-case assumption grid")
    args = parser.parse_args()
    config = load_config()
    if args.sensitivity:
        print(json.dumps(sensitivity(28), indent=2, allow_nan=False))
        return
    snapshot = comparison(28, 30)
    final = run(0)[-1]
    print(json.dumps({
        "classification": "simulated deterministic example; not an Inkai forecast or calibration",
        "delay_days": 28, "view_day": 30,
        "day30_baseline_t_u": snapshot["baseline_product_kg_u"] / 1000,
        "day30_delayed_t_u": snapshot["product_kg_u"] / 1000,
        "day90_product_difference_t_u": snapshot["projection"]["final_product_delta_kg_u"] / 1000,
        "equal_delivered_acid_at_day90": snapshot["projection"]["delivered_t_equal_at_horizon"],
        "derived_drying_limit_kg_u_day": daily_capacity(config["drying_capacity_mlb_u3o8_year"], config),
        "baseline_day90_wip_t_u": final["pending_kg_u"] / 1000,
        "assumed_wip_target_days": config["assumptions"]["wip_target_days"],
        "baseline_day90_solution_m3_h": final["solution_m3_day"] / 24,
        "baseline_day90_extracted_t_u": final["extracted_kg_u"] / 1000,
        "baseline_product_90day_annualized_mlb_u3o8": final["product_kg_u"] / 90 * 365 * 2.5998 / 1e6,
        "sensitivity": {k: v for k, v in snapshot["sensitivity"].items() if k != "rows"},
        "commission_days": {bid: {"baseline": block["baseline_commission_day"], "delayed": block["projected_commission_day"]}
                            for bid, block in snapshot["blocks"].items() if block["planned_acid_day"] is not None},
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
