"""Reproduce the documented synthetic example, without Docker or downloads."""
import json

from .model import comparison, daily_capacity, load_config


def main():
    config = load_config()
    snapshot = comparison(28, 30)
    print(json.dumps({
        "classification": "simulated deterministic example; not an Inkai forecast or calibration",
        "delay_days": 28, "view_day": 30,
        "day30_baseline_t_u": snapshot["baseline_product_kg_u"] / 1000,
        "day30_delayed_t_u": snapshot["product_kg_u"] / 1000,
        "day90_product_difference_t_u": snapshot["projection"]["final_product_delta_kg_u"] / 1000,
        "equal_delivered_acid_at_day90": snapshot["projection"]["delivered_t_equal_at_horizon"],
        "derived_drying_limit_kg_u_day": daily_capacity(config["drying_capacity_mlb_u3o8_year"], config),
        "commission_days": {bid: {"baseline": block["baseline_commission_day"], "delayed": block["projected_commission_day"]}
                            for bid, block in snapshot["blocks"].items() if block["planned_acid_day"] is not None},
    }, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
