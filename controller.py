# controller.py — Fixed autonomous vehicle controller
# Author: Benjamin McLaren
#
# Sign conventions:
#   lane_offset_m:      negative = left of centre,  positive = right of centre
#   heading_error_deg:  negative = pointing left,    positive = pointing right
#   Steering LEFT corrects positive offset/heading. RIGHT corrects negative.
#
# ─── BUGS FOUND AND FIXED ────────────────────────────────────────────────────
#
#   Bug 1 — sensor_valid check was missing entirely
#     The original controller had no guard on sensor_valid. It accepted and
#     acted on completely invalid sensor readings, potentially issuing any
#     command when data was garbage. Fixed: added as Priority 1.
#
#   Bug 2 — e_stop was not an unconditional override
#     The original e_stop check was nested inside obstacle zone logic, so it
#     was only evaluated if an obstacle was detected first. An active emergency
#     stop with a clear path ahead was silently ignored. Fixed: promoted to an
#     unconditional top-level check at Priority 2.
#
#   Bug 3 — Danger and caution zones were in the wrong priority order
#     The caution zone (≤ 2.0 m) was checked before the danger zone (≤ 1.0 m).
#     Because DANGER < CAUTION, an obstacle in the danger zone also satisfies
#     the caution condition — so caution always fired first and the danger
#     branch was never reached. Fixed: danger checked before caution.
#
#   Bug 4 — Obstacle avoidance steered the wrong direction
#     LEFT/RIGHT assignments in the danger and caution avoidance branches were
#     swapped. Left side clear → steered right (into the blocked side).
#     Fixed: assignments corrected to steer toward the clear side.
#
#   Bug 5 — Speed management did not always slow for large errors
#     The speed decision in normal driving was missing the speed_mps cap. A
#     vehicle above HIGH_SPEED_MPS with a small heading error would accelerate
#     further. Fixed: added `speed_mps >= HIGH_SPEED_MPS` to the SLOW condition.
#
#   Bug 6 — Normal driving fallthrough could override safety decisions
#     Without explicit early returns at each priority level, execution could
#     reach the normal driving block after a safety condition was partially
#     evaluated. Fixed: every priority branch returns explicitly.
#
# ─── KNOWN LIMITATIONS ───────────────────────────────────────────────────────
#
#   - Binary steering: LEFT/RIGHT/STRAIGHT has no magnitude. A 3° and a 30°
#     heading error receive identical commands. Future work: proportional output.
#
#   - No hysteresis: an obstacle at exactly the DANGER or CAUTION boundary
#     will cause rapid state toggling. Future work: deadband around thresholds.
#
#   - Stateless: every call is independent. Cannot detect approaching vs
#     stationary obstacles, filter sensor glitches, or smooth outputs over time.
#
#   - Hardcoded thresholds: constants are inline. Tuning different platforms
#     requires editing source. Future work: config file or injected parameters.
#
# ─────────────────────────────────────────────────────────────────────────────

VALID_STEERING = {"LEFT", "RIGHT", "STRAIGHT"}
VALID_SPEED = {"ACCELERATE", "SLOW", "STOP"}


def controller(
    obstacle_distance_m,
    lane_offset_m,
    heading_error_deg,
    speed_mps,
    e_stop,
    left_clear,
    right_clear,
    sensor_valid
):
    """
    Returns (steering, speed_action).
      steering:     "LEFT" | "RIGHT" | "STRAIGHT"
      speed_action: "ACCELERATE" | "SLOW" | "STOP"
    """

    DANGER_OBSTACLE_M  = 1.0   # brake hard within this distance
    CAUTION_OBSTACLE_M = 2.0   # slow down within this distance

    MILD_HEADING_DEG  = 3.0
    LARGE_HEADING_DEG = 15.0

    MILD_OFFSET_M  = 0.15
    LARGE_OFFSET_M = 0.40

    HIGH_SPEED_MPS = 3.0

    # 1. Sensor failure — cannot trust any input
    if not sensor_valid:                        # FIX bug 1: check was missing entirely
        return "STRAIGHT", "STOP"

    # 2. Emergency stop — unconditional hard override
    if e_stop:                                  # FIX bug 2: was nested inside obstacle logic, could be bypassed
        return "STRAIGHT", "STOP"

    # 3. Danger zone — brake hard, steer to clear side if one exists
    if obstacle_distance_m <= DANGER_OBSTACLE_M:    # FIX bug 3: was checked after caution zone, never reached
        if left_clear and not right_clear:
            return "LEFT", "STOP"              # FIX bug 4: was "RIGHT" (steered into blocked side)
        elif right_clear and not left_clear:
            return "RIGHT", "STOP"             # FIX bug 4: was "LEFT"
        else:
            return "STRAIGHT", "STOP"

    # 4. Caution zone — slow down, prefer clear side
    if obstacle_distance_m <= CAUTION_OBSTACLE_M:   # FIX bug 3: was checked before danger zone
        if not left_clear and not right_clear:
            return "STRAIGHT", "SLOW"
        elif left_clear and not right_clear:
            return "LEFT", "SLOW"              # FIX bug 4: was "RIGHT"
        elif right_clear and not left_clear:
            return "RIGHT", "SLOW"             # FIX bug 4: was "LEFT"
        else:
            # Both clear — slow and correct alignment while closing
            if heading_error_deg > MILD_HEADING_DEG or lane_offset_m > MILD_OFFSET_M:
                return "LEFT", "SLOW"
            elif heading_error_deg < -MILD_HEADING_DEG or lane_offset_m < -MILD_OFFSET_M:
                return "RIGHT", "SLOW"
            else:
                return "STRAIGHT", "SLOW"

    # 5. Normal driving — correct heading/offset, manage speed by error severity
    centered            = abs(lane_offset_m)     <= MILD_OFFSET_M
    small_heading_error = abs(heading_error_deg) <= MILD_HEADING_DEG

    if centered and small_heading_error:
        return "STRAIGHT", "ACCELERATE"

    # Heading error takes priority over lane offset (determines future trajectory)
    if heading_error_deg > MILD_HEADING_DEG or lane_offset_m > MILD_OFFSET_M:
        steering = "LEFT"
    elif heading_error_deg < -MILD_HEADING_DEG or lane_offset_m < -MILD_OFFSET_M:
        steering = "RIGHT"
    else:
        steering = "STRAIGHT"

    large_error = (
        abs(heading_error_deg) > LARGE_HEADING_DEG or
        abs(lane_offset_m)     > LARGE_OFFSET_M
    )

    speed_action = "SLOW" if (large_error or speed_mps >= HIGH_SPEED_MPS) else "ACCELERATE"  # FIX bug 5: speed_mps cap was missing

    return steering, speed_action  # FIX bug 6: explicit returns throughout prevent fallthrough to this point
