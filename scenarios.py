# scenarios.py
#
# Each scenario is a dictionary with:
#   "name"   — a human-readable label shown in the visualiser
#   "inputs" — a full set of sensor readings passed straight to controller()
#
# Sign conventions (same as controller.py):
#   lane_offset_m:      negative = left of centre,  positive = right of centre
#   heading_error_deg:  negative = pointing left,    positive = pointing right
#
# Obstacle distance conventions:
#   999.0 = no obstacle (clear path ahead)
#   ≤ 2.0 = caution zone (controller slows)
#   ≤ 1.0 = danger zone (controller hard brakes)
#
# For a scenario to not crash in the visualiser, the controller output must
# physically allow the vehicle to avoid the obstacle before reaching it.
# Key rule of thumb: stopping distance = v² / (2 * 4.0) metres.
# At 1.0 m/s that's 0.125 m — safe for close obstacles.
# At 3.0 m/s that's 1.125 m — NOT safe for obstacles closer than ~1.5 m.

scenarios = [

    # ── Original scenarios ────────────────────────────────────────────────────
    # These cover the basic cases the controller was designed for.

    {
        # Happy path: nothing in the way, perfectly centred and aligned.
        # Expected: go straight and accelerate.
        "name": "[ORIGINAL] Clear Path, Centered",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 2.0,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        # Obstacle very close with nowhere to go.
        # Expected: stop dead, steer straight.
        "name": "[ORIGINAL] Close Obstacle Ahead, No Safe Side",
        "inputs": {
            "obstacle_distance_m": 0.8,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 2.5,
            "e_stop": False,
            "left_clear": False,
            "right_clear": False,
            "sensor_valid": True
        }
    },
    {
        # Obstacle in caution range, left side open for escape.
        # Expected: steer left, slow down.
        "name": "[ORIGINAL] Obstacle Ahead, Left Clear",
        "inputs": {
            "obstacle_distance_m": 1.8,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 3.0,
            "e_stop": False,
            "left_clear": True,
            "right_clear": False,
            "sensor_valid": True
        }
    },
    {
        # Mirror of above — only the right side is open.
        # Expected: steer right, slow down.
        "name": "[ORIGINAL] Obstacle Ahead, Right Clear",
        "inputs": {
            "obstacle_distance_m": 1.8,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 3.0,
            "e_stop": False,
            "left_clear": False,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        # No obstacle, but vehicle is going fast with a big heading error.
        # Expected: steer left to correct, slow down (both large error AND high speed).
        "name": "[ORIGINAL] Large Heading Error at Speed",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.1,
            "heading_error_deg": 22.0,
            "speed_mps": 4.5,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        # Emergency stop active — should override everything, including the nearby obstacle.
        # Expected: straight, stop — regardless of lane/heading state.
        "name": "[ORIGINAL] Emergency Stop Active",
        "inputs": {
            "obstacle_distance_m": 2.0,
            "lane_offset_m": -0.4,
            "heading_error_deg": -12.0,
            "speed_mps": 3.0,
            "e_stop": True,
            "left_clear": True,
            "right_clear": False,
            "sensor_valid": True
        }
    },
    {
        # Obstacle in caution zone, heading error and available escape are in opposite
        # directions. Right is clear so the controller picks that, ignoring heading.
        # Expected: steer right (escape route wins), slow down.
        "name": "[ORIGINAL] Obstacle Plus Heading Conflict",
        "inputs": {
            "obstacle_distance_m": 1.7,
            "lane_offset_m": -0.2,
            "heading_error_deg": 18.0,
            "speed_mps": 3.5,
            "e_stop": False,
            "left_clear": False,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        # No obstacle, drifting slightly right with a mild heading error.
        # Error is small so speed stays up, but steering corrects the drift.
        # Expected: steer left, accelerate.
        "name": "[ORIGINAL] Mild Drift, No Obstacle",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.25,
            "heading_error_deg": 5.0,
            "speed_mps": 2.2,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True
        }
    },

    # ── Added edge-case scenarios ─────────────────────────────────────────────
    # These probe corner cases: safety overrides, sensor failure, boundary
    # conditions, and combined inputs that could previously trigger bugs.

    {
        # e_stop should halt the vehicle even with no obstacle in sight.
        # Tests that e_stop is an unconditional override (Bug 2 fix).
        # Expected: straight, stop.
        "name": "[ADDED] e_stop with No Nearby Obstacle",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 2.5,
            "e_stop": True,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        # Bad sensor data — all other inputs are reasonable but should be ignored.
        # Tests that sensor_valid is the first check (Bug 1 fix).
        # Expected: straight, stop.
        "name": "[ADDED] Sensor Invalid",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 1.5,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": False
        }
    },
    {
        # BOUNDARY CASE — expected to crash in the visualiser.
        # Obstacle at 0.5 m, speed 2.0 m/s. Stopping distance at this speed is exactly
        # 0.5 m (v² / 2a = 4 / 8), leaving zero margin. Both sides are blocked so there
        # is no escape route either. The controller correctly outputs STRAIGHT, STOP —
        # the best possible response — but physics means the vehicle can't stop in time.
        # Tests that the danger zone triggers correctly and the right command is issued
        # even when a crash is unavoidable.
        "name": "[ADDED] Large Heading Error Plus Close Obstacle, Both Blocked",
        "inputs": {
            "obstacle_distance_m": 0.5,
            "lane_offset_m": 0.0,
            "heading_error_deg": 20.0,
            "speed_mps": 2.0,
            "e_stop": False,
            "left_clear": False,
            "right_clear": False,
            "sensor_valid": True
        }
    },
    {
        # BOUNDARY CASE — expected to crash in the visualiser.
        # Obstacle at 0.6 m, speed 3.0 m/s. Stopping distance is 1.125 m (v² / 2a = 9 / 8),
        # nearly double the available gap. The controller correctly picks LEFT + STOP —
        # steering toward the clear side and braking hard — but the vehicle is going
        # too fast to halt before impact. Tests the danger zone escape logic when the
        # vehicle enters it at a speed it can't recover from.
        "name": "[ADDED] Large Heading Error Plus Close Obstacle, Left Clear",
        "inputs": {
            "obstacle_distance_m": 0.6,
            "lane_offset_m": 0.0,
            "heading_error_deg": 20.0,
            "speed_mps": 3.0,
            "e_stop": False,
            "left_clear": True,
            "right_clear": False,
            "sensor_valid": True
        }
    },
    {
        # BOUNDARY CASE — expected to crash in the visualiser.
        # Obstacle at 1.8 m (inside the caution zone), vehicle travelling at 5.0 m/s.
        # The controller correctly outputs STRAIGHT, SLOW, but slowing from 5.0 to 1.5 m/s
        # requires roughly 5.7 m of travel — far more than the 1.8 m gap. The controller
        # is doing the right thing; the crash shows that the SLOW response is not enough
        # to save the vehicle when it enters the caution zone at this kind of speed.
        "name": "[ADDED] High Speed with Obstacle in Caution Zone",
        "inputs": {
            "obstacle_distance_m": 1.8,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 5.0,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        # BOUNDARY CASE — expected to crash in the visualiser.
        # Obstacle at 2.0 m (right at the caution threshold), both sides blocked.
        # The controller correctly outputs STRAIGHT, SLOW — the safest available action
        # when there is no escape route. But SLOW targets 1.5 m/s, not zero, so the vehicle
        # keeps moving and eventually crawls into the obstacle. Tests that the controller
        # picks the right command even in an unwinnable situation.
        "name": "[ADDED] Both Sides Blocked in Caution Zone",
        "inputs": {
            "obstacle_distance_m": 2.0,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 2.0,
            "e_stop": False,
            "left_clear": False,
            "right_clear": False,
            "sensor_valid": True
        }
    },
    {
        # No obstacle. Vehicle is well centred but heading significantly left.
        # Heading error is large enough to warrant slowing.
        # Expected: steer right to correct, slow down.
        "name": "[ADDED] Negative Large Heading Error, No Obstacle",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.0,
            "heading_error_deg": -20.0,
            "speed_mps": 2.0,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        # Vehicle has drifted 0.5 m right of centre — well past the LARGE_OFFSET
        # threshold. No obstacle ahead.
        # Expected: steer left to return to centre, slow down (large offset).
        "name": "[ADDED] Far Right Drift, No Obstacle",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.50,
            "heading_error_deg": 0.0,
            "speed_mps": 1.5,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        # Obstacle at 0.9 m (danger zone), left clear, vehicle heading left (negative).
        # Heading aligns with the safe escape direction, so LEFT + STOP works cleanly.
        # Tests that danger zone steers to the correct clear side (Bug 4 fix).
        # Expected: steer left, stop.
        "name": "[ADDED] Danger Zone, Left Clear, Heading Right",
        "inputs": {
            "obstacle_distance_m": 0.9,
            "lane_offset_m": 0.0,
            "heading_error_deg": 10.0,
            "speed_mps": 2.0,
            "e_stop": False,
            "left_clear": True,
            "right_clear": False,
            "sensor_valid": True
        }
    },
    {
        # Obstacle at exactly 2.0 m — right on the caution zone boundary (≤ 2.0 triggers).
        # Left is blocked, right is clear, so the controller slows and steers right.
        # The vehicle swings around the obstacle and clears it.
        # Expected: steer right, slow.
        "name": "[ADDED] At Exactly CAUTION Boundary",
        "inputs": {
            "obstacle_distance_m": 2.0,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 3.0,
            "e_stop": False,
            "left_clear": False,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        # Fast but perfectly aligned with a clear path. No reason to slow.
        # Expected: straight, accelerate.
        "name": "[ADDED] High Speed, Well Aligned, No Obstacle",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.0,
            "heading_error_deg": 0.0,
            "speed_mps": 5.0,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True
        }
    },
    {
        # Both e_stop AND sensor_invalid at the same time. sensor_valid is checked
        # first (Priority 1), so sensor failure takes the decision before e_stop even matters.
        # Expected: straight, stop.
        "name": "[ADDED] e_stop AND Sensor Invalid",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": 0.2,
            "heading_error_deg": 8.0,
            "speed_mps": 2.0,
            "e_stop": True,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": False
        }
    },
    {
        # Mirror of the "Mild Drift" original — drifting left with a mild leftward heading.
        # Expected: steer right to correct, accelerate (error is mild, not LARGE).
        "name": "[ADDED] Mild Drift Left, No Obstacle",
        "inputs": {
            "obstacle_distance_m": 999.0,
            "lane_offset_m": -0.25,
            "heading_error_deg": -5.0,
            "speed_mps": 2.0,
            "e_stop": False,
            "left_clear": True,
            "right_clear": True,
            "sensor_valid": True
        }
    },

]
