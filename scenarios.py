# scenarios.py
#
# Sign conventions:
#   lane_offset_m:      negative = left of centre,  positive = right of centre
#   heading_error_deg:  negative = pointing left,    positive = pointing right

scenarios = [

    # ── Original scenarios ────────────────────────────────────────────────────

    {
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

    {
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
        "name": "[ADDED] High Speed with Obstacle in Caution Zone",
        "inputs": {
            "obstacle_distance_m": 2.5,
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
        "name": "[ADDED] At Exactly CAUTION Boundary",
        "inputs": {
            "obstacle_distance_m": 3.0,
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
