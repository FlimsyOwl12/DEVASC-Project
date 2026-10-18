# Verification record — October 18, 2026

Earlier verified main revision: `c6d34d534dcfd39915cfa8adc3fc21ee1c54b474` (merged PRs #30/#28). The earlier F7/F8 verification used `9238164`; both records are retained below. This file records observed results, rather than committing generated console logs or credentials.

| Check | Observed result | Evidence |
| --- | --- | --- |
| Local offline run, Python 3.14 | 69 tests passed on October 18 | `python scripts/run_offline_tests.py`; run repeated after synchronizing merged main |
| Clean Git archive | 69 tests passed from source before PR #27 merged | Same tracked source at PR head; no `.env`, virtual environment, or tracked cache files in the archive |
| Merged-main GitHub Actions | 69 tests passed on both Python 3.10 and 3.14 | [Run 39121848255](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/39121848255) |
| Final F7/F8 PR checks | Both Python matrix jobs passed | [Run 39120102034](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/39120102034) |
| F6 live checks | Car/bike/foot reachable; disconnected route rejected, recorded October 14 | [Live evidence](live-verification.md) |
| Jenkins manual and SCM-triggered success | Original #1/#2 passed 69 tests and archived reports | [Jenkins evidence](jenkins-evidence.md) |
| Jenkins controlled failure | Demo #1 at `bdd74ce`: 70 tests, exactly one intentional failure; report archived | [Demo #1](http://127.0.0.1:8080/job/DEVASC-GraphHopper-Demo/1/) |
| Jenkins automatic recovery | Demo #2 at `ed43bde`: SCM-triggered, 69 passing tests; report archived | [Demo #2](http://127.0.0.1:8080/job/DEVASC-GraphHopper-Demo/2/) |
| Jenkins merged-main verification | Original #5 at `c6d34d5`: 69 tests in 0.486 seconds, SUCCESS; report archived | [Build #5](http://127.0.0.1:8080/job/DEVASC-GraphHopper/5/) |
| Current-main GitHub Actions | Python 3.10/3.14 passed after PRs #30/#28 merged | [Run 39132132376](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/39132132376) |

## Activity 5 branch verification — October 18

The `activity5-netconf-automation` branch passes **100 offline tests** (69 original plus 31 Activity 5 cases). The no-account example completes preview, edit, readback and a simulated notification. The request model passes pyang validation. A separate fixture completes real SSH/NETCONF lock, read, edit, readback, unlock and close using ncclient and a pinned ephemeral key on loopback.

These are local tests with a simulated device and notification. No real IOS XE configuration or WebEx message was verified. The user has no room/API access yet. See the [Activity 5 guide](activity5-implementation.md) for reproducible commands and the live-evidence checklist. At implementation head `20cefbb`, the [PR run](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/39141681773) and [push run](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/39141677148) passed all four jobs. The PR run completed 100 tests in 0.882 seconds on Python 3.10 and 0.911 seconds on Python 3.14; both protocol/model jobs passed. [PR #33](https://github.com/FlimsyOwl12/DEVASC-Project/pull/33) remains open for team review. The historical Jenkins results above remain 69-test evidence.

## Current test distribution

| File | Tests |
| --- | ---: |
| `test_graphhopper_cli.py` | 9 |
| `test_graphhopper_output_modes.py` | 8 |
| `test_graphhopper_responses.py` | 12 |
| `test_graphhopper_api.py` | 9 |
| `test_graphhopper_exports.py` | 10 |
| `test_graphhopper_geocoding_candidates.py` | 11 |
| `test_graphhopper_history_menu.py` | 6 |
| `test_offline_runner.py` | 4 |
| `test_network_automation.py` | 31 |
| **Total** | **100** |

The export/candidate/history tests preserve previous F1–F5 coverage. The candidate regression checks that identical names show distinct coordinates, selected coordinates reach routing, and the dummy key stays out of displayed text. Runner fixtures verify that failure and empty discovery return a failing exit code and that an unmocked HTTP call is blocked.

## Reproduce offline

Install `requirements.txt` in a virtual environment, then run:

```bash
python scripts/run_offline_tests.py
```

The test command does not require a real API key, disables dotenv loading, and blocks HTTP/socket connections. Installation and CI checkout need network access. Its generated report is ignored locally; the GitHub workflow retains uploaded reports for 14 days, so download any evidence required for submission before it expires. Do not add the API key or credential-bearing request URLs to evidence.

The recorded F6 live run predates F7/F8. No new GraphHopper live requests were made for this report. Jenkins results above were observed on October 18. The original job targets main and the demo job is disabled with history retained. Local build links require the Jenkins host; keep exported reports/screenshots for submission. Polling is verified, not webhook delivery; instructor acceptance remains pending.
