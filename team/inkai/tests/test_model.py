import copy
import json
import unittest

from team.inkai.model import comparison, daily_capacity, load_config, run, twin_definitions, twin_states


class AccountingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config = load_config()
        cls.base = run(0)
        cls.late = run(28)

    def test_acid_conservation_every_day_and_area(self):
        for delay in (0, 1, 7, 28, 42):
            for state in run(delay):
                for area in state["areas"].values():
                    self.assertGreaterEqual(area["acid_inventory_t"], 0)
                    self.assertAlmostEqual(area["initial_acid_t"] + area["acid_received_t"],
                                           area["acid_used_t"] + area["acid_inventory_t"])

    def test_uranium_conservation_and_nonnegative_inventory(self):
        for state in self.base + self.late:
            self.assertAlmostEqual(state["extracted_kg_u"], state["product_kg_u"] + state["pending_kg_u"] + state["unrecovered_kg_u"], places=6)
            for block in state["blocks"].values():
                self.assertGreaterEqual(block["remaining_uranium_kg"], -1e-8)
                self.assertAlmostEqual(block["initial_uranium_kg"], block["remaining_uranium_kg"] + block["extracted_kg_u"], places=6)

    def test_delivery_exact_day_and_same_cumulative_supply(self):
        self.assertEqual(self.base[2]["acid_received_t"], 0)
        self.assertEqual(self.base[3]["acid_received_t"], 900)
        self.assertEqual(self.late[30]["acid_received_t"], 0)
        self.assertEqual(self.late[31]["acid_received_t"], 900)
        self.assertEqual(self.base[-1]["acid_received_t"], self.late[-1]["acid_received_t"])

    def test_no_acidification_without_whole_dose(self):
        self.assertEqual(self.late[20]["blocks"]["mpp-b1"]["state"], "waiting_acid")
        self.assertIsNone(self.late[20]["blocks"]["mpp-b1"]["acid_start_day"])
        self.assertEqual(self.late[31]["blocks"]["mpp-b1"]["acid_start_day"], 31)

    def test_area_acid_stocks_are_independent(self):
        config = copy.deepcopy(self.config)
        config["areas"][0]["initial_acid_t"] = 900
        state = run(28, config)[20]
        self.assertEqual(state["blocks"]["mpp-b1"]["commission_day"], 12)
        self.assertEqual(state["blocks"]["sat1-b1"]["state"], "waiting_acid")
        self.assertEqual(state["areas"]["sat1"]["acid_inventory_t"], 80)

    def test_exact_threshold_is_sufficient(self):
        config = copy.deepcopy(self.config)
        config["areas"][0]["initial_acid_t"] = 120
        history = run(28, config)
        self.assertEqual(history[5]["blocks"]["mpp-b1"]["acid_start_day"], 5)
        self.assertEqual(history[5]["areas"]["mpp"]["acid_inventory_t"], 0)

    def test_fixed_acidification_and_ramp(self):
        self.assertEqual(self.base[11]["blocks"]["mpp-b1"]["state"], "acidifying")
        self.assertEqual(self.base[12]["blocks"]["mpp-b1"]["state"], "ramping")
        self.assertEqual(self.base[18]["blocks"]["mpp-b1"]["state"], "producing")
        self.assertEqual(self.late[38]["blocks"]["mpp-b1"]["commission_day"], 38)

    def test_ix_and_drying_limits_every_day(self):
        bound = False
        for state in self.base + self.late:
            self.assertLessEqual(state["drying_kg_u_day"], state["drying_capacity_kg_u_day"] + 1e-8)
            for area in state["areas"].values():
                self.assertLessEqual(area["ix_output_kg_u_day"], area["ix_capacity_kg_u_day"] + 1e-8)
            bound |= any(b["capacity_factor"] < 1 for b in state["blocks"].values())
        self.assertTrue(bound, "The capacity constraint must actually bind in this fixture")
        self.assertGreater(self.base[-1]["pending_kg_u"], 0)

    def test_delay_changes_states_start_dates_and_product(self):
        self.assertEqual(self.base[20]["blocks"]["mpp-b1"]["state"], "producing")
        self.assertEqual(self.late[20]["blocks"]["mpp-b1"]["state"], "waiting_acid")
        self.assertLess(self.late[30]["product_kg_u"], self.base[30]["product_kg_u"])
        self.assertLess(self.late[-1]["product_kg_u"], self.base[-1]["product_kg_u"])

    def test_existing_production_not_scaled_by_acid_delay(self):
        # Before new blocks compete for IX capacity, protected existing groups agree.
        for bid in ("mpp-b0", "sat1-b0", "sat2-b0"):
            self.assertEqual(self.base[10]["blocks"][bid], self.late[10]["blocks"][bid])

    def test_reruns_and_reset_are_exact(self):
        initial = comparison(0, 0)
        comparison(28, 60)
        self.assertEqual(initial, comparison(0, 0))
        self.assertEqual(self.late, run(28))
        self.assertEqual(self.config, load_config())

    def test_published_definitions_cover_each_state(self):
        states = twin_states(comparison(28, 20))
        self.assertEqual(set(states), set(twin_definitions()))
        self.assertEqual(len(states), 18)
        self.assertTrue(all(d["policyId"] == "default:basic_policy" for d in twin_definitions().values()))
        json.dumps(states, allow_nan=False)

    def test_telemetry_has_no_expanding_arrays_and_projection_is_lossless(self):
        snapshot = comparison(28, 30)
        states = twin_states(snapshot)

        def check(value):
            self.assertNotIsInstance(value, list, "Feature arrays can expand catastrophically in Telegraf json_v2")
            if isinstance(value, dict):
                for child in value.values():
                    check(child)
        check(states)
        scenario = states["org.minemind.inkai:scenario"]
        self.assertEqual(json.loads(scenario["projection"]), snapshot["projection"])

    def test_daily_capacity_conversion(self):
        self.assertAlmostEqual(daily_capacity(8.3, self.config) * 365 * self.config["lb_u3o8_per_kg_u"], 8_300_000)

    def test_solution_volume_is_consistent_with_assumed_grade(self):
        for area in self.base[20]["areas"].values():
            extracted_today = sum(b["extraction_kg_u_day"] for b in self.base[20]["blocks"].values() if b["area"] == area["id"])
            self.assertAlmostEqual(area["solution_m3_day"] * 0.1, extracted_today)

    def test_depletion_does_not_create_uranium(self):
        config = copy.deepcopy(self.config)
        config["assumptions"]["uranium_inventory_days_at_nominal_rate"] = 1
        final = run(0, config)[-1]
        self.assertTrue(all(b["state"] == "depleted" for b in final["blocks"].values()))
        self.assertAlmostEqual(final["extracted_kg_u"], sum(b["initial_uranium_kg"] for b in final["blocks"].values()))

    def test_input_bounds(self):
        for value in (-1, 43, 1.5, True, "28"):
            with self.assertRaises(ValueError):
                run(value)
        for value in (-1, 91, False):
            with self.assertRaises(ValueError):
                comparison(0, value)

    def test_projection_and_physical_snapshot_agree(self):
        state = comparison(28, 30)
        self.assertEqual(state["product_kg_u"], state["projection"]["scenario_product_kg_u"][30])
        self.assertEqual(state["baseline_product_kg_u"], state["projection"]["baseline_product_kg_u"][30])
        self.assertTrue(state["projection"]["delivered_t_equal_at_horizon"])


if __name__ == "__main__":
    unittest.main()
