"""Run against the actual app and compare its Ditto-derived state with the model.

This is an integration check, not a mock: failure to ingest MQTT cannot pass.
It verifies a complete day-0 reset, then leaves the informative baseline day 30.
"""
import json
import os
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from .model import NAMESPACE, comparison, load_config, twin_states

URL = os.environ.get("INKAI_URL", "http://localhost:8088").rstrip("/")


def request(path, body=None):
    request = Request(URL + path, data=json.dumps(body).encode() if body is not None else None,
                      headers={"Content-Type": "application/json"})
    with urlopen(request, timeout=90) as response:
        return json.load(response)


def expect(response, delay, day):
    assert response["source"] == "Eclipse Ditto REST /api/2/things"
    expected = twin_states(comparison(delay, day))
    actual = {tid: twin["state"] for tid, twin in response["twins"].items()}
    assert actual == expected, "Ditto state differs from the deterministic model"
    assert len(actual) == 18
    return actual


def main():
    checks = []
    first = request("/api/state")
    # Refuse to mutate a different namespace, including a protected old Stand.
    assert first["namespace"] == NAMESPACE, "Wrong namespace: refusing to change this Stand"
    site = first["twins"][f"{NAMESPACE}:site"]["state"]
    expect(first, site["delay_days"], site["day"])
    checks.append("namespace guard and initial platform snapshot")
    initial = request("/api/control", {"action": "reset"})
    baseline_zero = expect(initial, 0, 0)
    checks.append("18 Ditto twins, initial baseline and MQTT ingestion")
    baseline = expect(request("/api/control", {"action": "configure", "day": 30}), 0, 30)
    late = expect(request("/api/control", {"action": "configure", "delay_days": 28, "day": 30}), 28, 30)
    assert late[f"{NAMESPACE}:mpp-b1"]["state"] == "waiting_acid"
    assert baseline[f"{NAMESPACE}:mpp-b1"]["state"] == "producing"
    assert late[f"{NAMESPACE}:site"]["product_kg_u"] < baseline[f"{NAMESPACE}:site"]["product_kg_u"]
    checks.append("delay propagates through acid inventory, lifecycle and product")
    expect(request("/api/control", {"action": "advance", "days": 8}), 28, 38)
    checks.append("runtime advance and commissioning at day 38")
    repeat = expect(request("/api/control", {"action": "configure", "day": 30, "delay_days": 28}), 28, 30)
    assert late == repeat
    checks.append("deterministic runtime rerun")
    final = expect(request("/api/control", {"action": "configure", "day": 90}), 28, 90)
    assert json.loads(final[f"{NAMESPACE}:scenario"]["projection"])["delivered_t_equal_at_horizon"]
    checks.append("equal cumulative supply at the common horizon")
    final_site = final[f"{NAMESPACE}:site"]
    assert final_site["pending_kg_u"] <= final_site["wip_limit_kg_u"] + 1e-7
    assert final_site["drying_factor"] < 1
    assert final_site["withheld_kg_u_day"] > 0
    checks.append("drying/WIP pacing reaches all platform states without unbounded stock")
    grid = json.loads(final[f"{NAMESPACE}:scenario"]["sensitivity"])
    assert grid["case_count"] == 27
    assert abs(grid["max_product_delta_kg_u"]) < 1e-6
    assert grid["min_delayed_groups"] == 3 and grid["max_delayed_groups"] == 6
    checks.append("27 assumption cases arrive losslessly through MQTT and Ditto")
    reset = expect(request("/api/control", {"action": "reset"}), 0, 0)
    assert reset == baseline_zero
    assert expect(request("/api/state"), 0, 0) == baseline_zero
    checks.append("complete reset of all 18 physical twin states")
    for invalid in ({"action": "configure", "delay_days": 43}, {"action": "configure", "day": -1}, {"action": "configure", "delay_days": True}, {"action": "unknown"}):
        try:
            request("/api/control", invalid)
        except HTTPError as error:
            assert error.code == 400
        else:
            raise AssertionError("Invalid runtime input was accepted")
    checks.append("runtime input validation")
    health = request("/health")
    assert health["status"] == "ok" and health["twins"] == 18
    with urlopen(URL, timeout=10) as response:
        html = response.read().decode()
        assert all(f'id="{name}"' in html for name in ("map", "reset", "production-chart", "wip-chart", "sensitivity-grid", "causal-chain"))
    checks.append("platform-dependent health and spatial UI assets")
    expect(request("/api/control", {"action": "configure", "day": load_config()["demo_day"], "delay_days": 0}), 0, 30)
    checks.append("informative baseline day 30 restored after reset verification")
    print(json.dumps({"status": "passed", "checks": checks, "count": len(checks)}, indent=2))


if __name__ == "__main__":
    main()
