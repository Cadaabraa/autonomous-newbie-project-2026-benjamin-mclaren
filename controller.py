# controller.py — Fixed autonomous vehicle controller
# Author: Benjamin McLaren
#
# Sign conventions:
#   lane_offset_m:      negative = left of centre,  positive = right of centre
#   heading_error_deg:  negative = pointing left,    positive = pointing right
#   Steering LEFT corrects positive offset/heading. RIGHT corrects negative.

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
    if not sensor_valid:
        return "STRAIGHT", "STOP"

    # 2. Emergency stop — unconditional hard override
    if e_stop:
        return "STRAIGHT", "STOP"

    # 3. Danger zone — brake hard, steer to clear side if one exists
    if obstacle_distance_m <= DANGER_OBSTACLE_M:
        if left_clear and not right_clear:
            return "LEFT", "STOP"
        elif right_clear and not left_clear:
            return "RIGHT", "STOP"
        else:
            return "STRAIGHT", "STOP"

    # 4. Caution zone — slow down, prefer clear side
    if obstacle_distance_m <= CAUTION_OBSTACLE_M:
        if not left_clear and not right_clear:
            return "STRAIGHT", "SLOW"
        elif left_clear and not right_clear:
            return "LEFT", "SLOW"
        elif right_clear and not left_clear:
            return "RIGHT", "SLOW"
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

    speed_action = "SLOW" if (large_error or speed_mps >= HIGH_SPEED_MPS) else "ACCELERATE"

    return steering, speed_action
