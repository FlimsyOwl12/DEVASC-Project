# F6 Live GraphHopper Verification

Use a team-owned GraphHopper key only from `.env` or the local environment. Do
not paste keys into screenshots, issue comments, exports, or committed files.

## Command

```bash
python labs/devnet-src/graphhopper/graphhopper_live_verify.py
```

The helper checks `car`, `bike`, and `foot` on a reachable Metro Manila route,
then records the behavior for a deliberately disconnected route. It prints
inputs, status messages, distance, duration, step count, supported profiles, and
failed or unavailable profiles without printing the API key or full request URL.

## Evidence Template

- Date:
- Key source: team-owned key loaded from local `.env` or environment
- Reachable route:
- Profiles verified:
- Profiles unavailable or limited by account/quota:
- Disconnected route:
- Disconnected-route result:
- Notes:

## Latest Local Result

- Date: October 14, 2026
- Key source: team-owned key loaded from local `.env`
- Reachable route: Manila City Hall, Manila -> Quezon Memorial Circle, Quezon City
- Profiles verified:
  - `car`: route returned, 11.6 km, 1,079,659 ms, 10 steps
  - `bike`: route returned, 12.4 km, 2,532,665 ms, 39 steps
  - `foot`: route returned, 11.6 km, 8,585,308 ms, 72 steps
- Profiles unavailable or limited by account/quota: none observed
- Disconnected route: Manila, Philippines -> Honolulu, Hawaii
- Disconnected-route result: routing status 400, "Connection between locations not found"; application returned no route
- Notes: no API key or full request URL was printed by the helper output.
