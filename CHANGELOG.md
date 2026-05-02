# Changes :)

## Task A — Controller Fix (Benjamin McLaren)

### Bugs Fixed
1. `sensor_valid` check was missing entirely — controller ran on bad data
2. `e_stop` was not an unconditional override — other logic could bypass it
3. Danger zone and caution zone checks were in the wrong priority order
4. Obstacle avoidance steered the wrong direction in some cases
5. Speed management did not always slow down for large errors
6. Normal driving fallthrough could override higher-priority decisions

### Other Changes
- Expanded test scenarios from 8 to 21 to cover edge cases
- Added `.gitignore` and `.gitattributes`

Full analysis of each bug, reproduction scenarios, and before/after code in the report. I tried not to clog the code with too much commenting and explaination lol :)
