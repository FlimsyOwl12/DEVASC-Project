# Verification record — October 18, 2026

Application revision: `9238164466fa18c5b9bcec394125f6c2514cfcef` (merged PR #27). This file records observed results, rather than committing generated console logs or credentials.

| Check | Observed result | Evidence |
| --- | --- | --- |
| Local offline run, Python 3.14 | 69 tests passed on October 18 | `python scripts/run_offline_tests.py`; run repeated after synchronizing merged main |
| Clean Git archive | 69 tests passed from source before PR #27 merged | Same tracked source at PR head; no `.env`, virtual environment, or tracked cache files in the archive |
| Merged-main GitHub Actions | 69 tests passed on both Python 3.10 and 3.14 | [Run 39121848255](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/39121848255) |
| Final F7/F8 PR checks | Both Python matrix jobs passed | [Run 39120102034](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/39120102034) |
| F6 live checks | Car/bike/foot reachable; disconnected route rejected, recorded October 14 | [Live evidence](live-verification.md) |
| Required Jenkins execution | Not yet verified | Server/job, successful/failed build links, and automatic-trigger evidence still required |

## Test distribution

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
| **Total** | **69** |

The export/candidate/history tests preserve previous F1–F5 coverage. The candidate regression checks that identical names show distinct coordinates, selected coordinates reach routing, and the dummy key stays out of displayed text. Runner fixtures verify that failure and empty discovery return a failing exit code and that an unmocked HTTP call is blocked.

## Reproduce offline

Install `requirements.txt` in a virtual environment, then run:

```bash
python scripts/run_offline_tests.py
```

The test command does not require a real API key, disables dotenv loading, and blocks HTTP/socket connections. Installation and CI checkout need network access. Its generated report is ignored locally; the GitHub workflow retains uploaded reports for 14 days, so download any evidence required for submission before it expires. Do not add the API key or credential-bearing request URLs to evidence.

The recorded F6 live run predates F7/F8. This verification did not rerun GraphHopper live requests or claim a Jenkins result.
