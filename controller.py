# controller.py — Autonomous vehicle controller
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

# Valid outputs — anything outside these sets is a bug
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
    Autonomous vehicle controller that makes steering and speed decisions
    based on sensor inputs.

    The controller uses a strict priority-based decision system — each level
    is checked in order and returns immediately if it applies. This means
    safety-critical conditions (sensor failure, emergency stop) always take
    precedence over normal driving logic, with no risk of being overridden.

      Priority 1 — Sensor validity:  if sensors are bad, don't trust any input
      Priority 2 — Emergency stop:   unconditional halt regardless of anything else
      Priority 3 — Danger zone:      obstacle within 1.0m — brake and dodge NOW
      Priority 4 — Caution zone:     obstacle within 2.0m — slow and plan escape
      Priority 5 — Normal driving:   correct lane position and manage speed

    Returns:
      steering:     "LEFT" | "RIGHT" | "STRAIGHT"
      speed_action: "ACCELERATE" | "SLOW" | "STOP"
    """

    # Distance thresholds for obstacle detection zones
    DANGER_OBSTACLE_M  = 1.0   # Within this distance: hard brake required
    CAUTION_OBSTACLE_M = 2.0   # Within this distance: reduce speed and start planning

    # Thresholds for deciding when heading/offset errors are significant enough to act on
    MILD_HEADING_DEG  = 3.0    # Small enough to ignore — within normal sensor noise
    LARGE_HEADING_DEG = 15.0   # Large enough to warrant slowing down to correct safely

    MILD_OFFSET_M  = 0.15      # Close enough to lane centre — no correction needed
    LARGE_OFFSET_M = 0.40      # Far enough from centre to require reduced speed

    # If going faster than this, we need good alignment before we're allowed to accelerate
    HIGH_SPEED_MPS = 3.0

    # ── Priority 1: Sensor validity ──────────────────────────────────────────
    # If the sensor data is flagged as unreliable, we have no trustworthy
    # information about the world. The only safe response is to stop in place.
    if not sensor_valid:                        # FIX bug 1: check was missing entirely
        return "STRAIGHT", "STOP"

    # ── Priority 2: Emergency stop ───────────────────────────────────────────
    # An e_stop is a direct signal from the driver or safety system to halt
    # immediately, regardless of what the sensors say about the environment.
    # This must be checked unconditionally before anything else.
    if e_stop:                                  # FIX bug 2: was nested inside obstacle logic, could be bypassed
        return "STRAIGHT", "STOP"

    # ── Priority 3: Danger zone (≤ 1.0 m) ───────────────────────────────────
    # Obstacle is critically close. Brake hard. If one side is open, steer
    # toward it to maximise clearance — but stopping is the priority either way.
    if obstacle_distance_m <= DANGER_OBSTACLE_M:    # FIX bug 3: was checked after caution zone, never reached
        if left_clear and not right_clear:
            return "LEFT", "STOP"              # FIX bug 4: was "RIGHT" (steered into blocked side)
        elif right_clear and not left_clear:
            return "RIGHT", "STOP"             # FIX bug 4: was "LEFT"
        else:
            # Both sides blocked — can't dodge, just stop and hope for the best
            return "STRAIGHT", "STOP"

    # ── Priority 4: Caution zone (≤ 2.0 m) ──────────────────────────────────
    # Obstacle is nearby but not yet critical. Slow down and prefer whichever
    # side gives us an escape route.
    if obstacle_distance_m <= CAUTION_OBSTACLE_M:   # FIX bug 3: was checked before danger zone
        if not left_clear and not right_clear:
            return "STRAIGHT", "SLOW"
        elif left_clear and not right_clear:
            return "LEFT", "SLOW"              # FIX bug 4: was "RIGHT"
        elif right_clear and not left_clear:
            return "RIGHT", "SLOW"             # FIX bug 4: was "LEFT"
        else:
            # Both sides are clear — slow down and use heading/offset to stay aligned
            # while closing on the obstacle
            if heading_error_deg > MILD_HEADING_DEG or lane_offset_m > MILD_OFFSET_M:
                return "LEFT", "SLOW"
            elif heading_error_deg < -MILD_HEADING_DEG or lane_offset_m < -MILD_OFFSET_M:
                return "RIGHT", "SLOW"
            else:
                return "STRAIGHT", "SLOW"

    # ── Priority 5: Normal driving ────────────────────────────────────────────
    # No safety condition was triggered. Focus on keeping the vehicle aligned
    # and at a reasonable speed. Heading error and lane offset are checked
    # together — heading takes implicit priority because it determines where
    # the vehicle will be in the near future, not just where it is now.

    centered            = abs(lane_offset_m)     <= MILD_OFFSET_M
    small_heading_error = abs(heading_error_deg) <= MILD_HEADING_DEG

    # Well aligned and centred — safe to accelerate
    if centered and small_heading_error:
        return "STRAIGHT", "ACCELERATE"

    # Determine which direction needs correction
    # Positive heading/offset = drifting right → steer LEFT to correct
    # Negative heading/offset = drifting left  → steer RIGHT to correct
    if heading_error_deg > MILD_HEADING_DEG or lane_offset_m > MILD_OFFSET_M:
        steering = "LEFT"
    elif heading_error_deg < -MILD_HEADING_DEG or lane_offset_m < -MILD_OFFSET_M:
        steering = "RIGHT"
    else:
        steering = "STRAIGHT"

    # Slow down if the correction is large (harder to control at speed) or
    # if we're already going fast (want good alignment before pushing further)
    large_error = (
        abs(heading_error_deg) > LARGE_HEADING_DEG or
        abs(lane_offset_m)     > LARGE_OFFSET_M
    )

    speed_action = "SLOW" if (large_error or speed_mps >= HIGH_SPEED_MPS) else "ACCELERATE"  # FIX bug 5: speed_mps cap was missing

    return steering, speed_action  # FIX bug 6: explicit returns throughout prevent fallthrough to this point
