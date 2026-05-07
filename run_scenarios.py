# run_scenarios.py
#
# Quick sanity check: runs every scenario through the controller and prints
# the steering + speed decision for each one. Useful for a fast eyeball test
# before launching the full visualiser.
#
# Usage:
#   python run_scenarios.py

from scenarios import scenarios
from controller import controller

summary = []

for scenario in scenarios:
    inputs = scenario["inputs"]

    # Pass all sensor inputs to the controller and collect its decision
    steering, speed_action = controller(
        inputs["obstacle_distance_m"],
        inputs["lane_offset_m"],
        inputs["heading_error_deg"],
        inputs["speed_mps"],
        inputs["e_stop"],
        inputs["left_clear"],
        inputs["right_clear"],
        inputs["sensor_valid"]
    )

    summary.append({
        "name": scenario["name"],
        "steering": steering,
        "speed_action": speed_action
    })

print("Summary:")
for item in summary:
    print(
        " ",
        item["name"] + ":",
        "steering =", item["steering"] + ",",
        "speed_action =", item["speed_action"]
    )
