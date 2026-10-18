# DEVASC Option 1 — application report

Prepared October 18, 2026 for PalpakGPT. Verified main baseline: `c6d34d534dcfd39915cfa8adc3fc21ee1c54b474`, after F7/F8 and Jenkins/checklist PRs #30/#28. This report documents implemented behavior and observed GitHub/Jenkins results. Instructor approval and personal/team assessment responses remain outstanding.

## Problem and scope

The team chose to improve the Python directions application from the *Integrate a REST API in a Python Application* lab. A user needs to choose the intended places, read route information in familiar units, and save a route without having to inspect JSON. The supplied lab and reference repository use GraphHopper. The instructor guide mentions MapQuest; confirmation of GraphHopper as the project provider is still tracked in issue #2.

Python makes HTTPS GET requests to GraphHopper's geocoding and routing endpoints, validates JSON responses, and displays the route in a terminal. This is an enhancement of the supplied lab, rather than an independently implemented routing engine. Activity 5 is implemented in a separate `network_automation/` package; see the [implementation guide](activity5-implementation.md). This routing report retains the historical routing/Jenkins results. The new package has local simulated/protocol validation; real device and WebEx evidence remain pending.

## Implemented features

| Feature | Actual behavior | Evidence |
| --- | --- | --- |
| F1 units | Metric or imperial totals and every instruction distance | PR #21; CLI tests |
| F2 output | Aligned route summary, HH:MM:SS duration, numbered directions, plain text | PR #22; CLI tests |
| F3 output mode | Summary retains totals; detailed mode also lists instructions | PR #24; output-mode tests |
| F4 validation | Check JSON/schema, finite numbers, coordinate ranges and instruction fields; recover without exposing the key | PR #23; response tests |
| F5 tests | Repeatable unittest suite, dummy keys and mocked HTTP | API/CLI/response/runner tests |
| F6 live evidence | Reachable car/bike/foot routes and disconnected-route error recorded October 14 | [Live verification record](live-verification.md) |
| F7 exports | TXT, JSON and CSV retain units and directions; filenames are checked and collisions cannot silently overwrite files | PR #27; export tests |
| F8 place choice | Up to five valid results; retry/quit; show coordinates for same-name places; route to selected coordinates | PR #27; candidate tests |
| Session UX | Main menu; last ten successful routes; history viewing/export without further HTTP requests | PR #27; history tests |
| F9 CI execution | GitHub Actions and Jenkins run offline checks; SCM polling, controlled failure/recovery and final-main build #5 verified | PRs #26/#30; [Pipeline guide](automated-checks.md); [Jenkins evidence](jenkins-evidence.md) |

PR links: [#21](https://github.com/FlimsyOwl12/DEVASC-Project/pull/21), [#22](https://github.com/FlimsyOwl12/DEVASC-Project/pull/22), [#23](https://github.com/FlimsyOwl12/DEVASC-Project/pull/23), [#24](https://github.com/FlimsyOwl12/DEVASC-Project/pull/24), [#26](https://github.com/FlimsyOwl12/DEVASC-Project/pull/26), [#27](https://github.com/FlimsyOwl12/DEVASC-Project/pull/27).

## Install and use

Use Python 3.10 or newer. From the project root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp -n .env.example .env
```

Edit the local `.env` with your own GraphHopper key, then run:

```bash
python labs/devnet-src/graphhopper/graphhopper_parse-json_7.py
```

An exported `GRAPHHOPPER_API_KEY` takes precedence over `.env`. The key is required for ordinary application startup; it is not required for the offline tests.

1. Select **Find a Route** from the menu, choose `car`, `bike`, or `foot`, then units and output mode.
2. Enter the origin. If several places match, choose the intended numbered result using its name and coordinates. `R` searches again; `Q` quits from candidate selection.
3. Enter/select the destination. The application requests routing for those chosen coordinates.
4. Read the summary and, in detailed mode, numbered directions.
5. Answer yes to export and choose TXT/JSON/CSV. Files go to the project-root `exports/` directory. On a collision, choose a different filename or press Enter for a numeric suffix; the original remains intact.
6. Use **View Route History** or **Export Previous Route** to reuse a stored route. Exit with menu option 4 or `q`/`quit` at the main menu. Within export/history-selection menus, `q`/`quit` cancels that operation and returns to the main menu.

The earlier geocoding-only exercise is `graphhopper_parse-json_1.py`. It remains a separate lab exercise, not the enhanced menu application.

## Architecture and data flow

```text
Menu / profile / units / output mode
    -> origin geocoding -> validate candidates -> choose coordinates
    -> destination geocoding -> validate candidates -> choose coordinates
    -> routing GET with repeated point parameters and selected profile
    -> validate route -> display -> store RouteRecord in session history
    -> optional local TXT / JSON / CSV export
```

`RouteRecord` stores route metadata and instructions without storing the API key or request URL. `RouteHistory` keeps at most ten records in memory. Input prompts, geocoding/routing, output, and export functions have separate responsibilities within the main lab script. No database or persistent route-history service is used.

## Verification and evidence

The [test-results summary](test-results.md) records the original 69 passing offline tests and links to actual GitHub runs on Python 3.10 and 3.14, including the merged-main run. A clean Git archive also passed 69 tests, confirming that tracked cache files are unnecessary. The local October 18 verification used the same network-blocked runner.

```bash
python scripts/run_offline_tests.py
```

The runner clears the GraphHopper key, disables dotenv loading, blocks unmocked HTTP/socket calls, and fails on test failures or empty discovery. Dependency installation still needs internet access. Reports are written to ignored `test-results/unittest.txt` and uploaded by CI.

The October 14 live record reports Manila City Hall to Quezon Memorial Circle: car 11.6 km, bike 12.4 km, foot 11.6 km. Manila to Honolulu returned HTTP 400, connection not found. These are historical observations from that account/date, not a guarantee of future provider behavior. No new live request was made for this report, and the later F7/F8 UI has offline coverage rather than newly recorded live evidence.

### Observed Jenkins results — October 18

| Run | Observed result | Commit |
| --- | --- | --- |
| Original job #1 | Manual success; 69 tests; report archived | `001efaf` |
| Original job #2 | SCM-triggered success; 69 tests; report archived | `21c3230` |
| Demo #1 | 70 tests; exactly one intentional failure; report archived; FAILURE | `bdd74ce` |
| Demo #2 | Automatic SCM-triggered recovery; 69 tests; report archived; SUCCESS | `ed43bde` |
| Original job #5 | Merged main; 69 tests in 0.486 seconds; report archived; SUCCESS | `c6d34d5` |

The original job now targets `*/main`. Demo #2 reverted only the disposable failure test; neither demonstration commit belongs in main. Local Jenkins links are usable only on the hosting machine, so save screenshots/reports for presentation. SCM polling detected pushes without a public listener; this is not verified webhook delivery. Exact branch-run SHAs and diagnostics are in [Jenkins evidence](jenkins-evidence.md), with the final-main follow-up in [handoff PR #32](https://github.com/FlimsyOwl12/DEVASC-Project/pull/32).

## Limitations and required follow-up

- Routing quality, coverage, quota, and profile access depend on the external API/account. No monthly quota or budget has been verified for this report.
- There is no map, GUI, waypoint editor, database, or persistent history. History disappears on exit and retains only ten successful routes per session.
- Export files are plaintext and may contain users' locations/directions. Review them before sharing or adding them to Git.
- Place-choice coordinates distinguish identical labels, but no map preview is provided. The user must choose the intended candidate.
- JSON numeric distances retain two decimal places while display labels use one; JSON also includes the formatted distance. CSV/TXT use the displayed precision.
- Known API failures are reported with safe messages; the application does not automatically retry rate limits or network failures.
- Jenkins 2.580.1 is configured and verified: manual success, automatic SCM triggering, one intentional test failure, automatic recovery and final-main build #5. The demo job is disabled with reports retained. Instructor acceptance of the local environment/polling remains outstanding; no GitHub webhook delivery or deployment is claimed.
- P0 scope approval, confirmed feature ownership/estimates, the final presentation rehearsal/delivery, the actual student rubric, and member reflections remain team/instructor actions.

## Team records and contribution attribution

The DRAFT tab records PalpakGPT, scrum leader Justine Smith Rendaje, recorder Wilhelm Ramesh Dimacisil, and members John Jessienel Arquesola and Janwel Gilo (both listed as Prompt Engineer). Preserve those recorded roles unless the team changes them.

Git records `JL`/`FlimsyOwl12` commits for starter/enhancement/testing work and the F9 pipeline, and a `Tin-axle` upload for F7/F8 plus menu/history. Commit/upload identity is evidence of publication, not proof of sole authorship. Each member must confirm their actual contribution, challenges, and lessons before the presentation or reflection attributes individual work.

## Submission readiness

- [x] Document implemented behavior, setup, architecture and limitations.
- [x] Include permanent offline results, CI links, and recorded live evidence without credentials.
- [x] Identify incomplete course deliverables explicitly.
- [ ] Team reviews this report and confirms contribution/ownership statements.
- [x] Record Jenkins success, automatic SCM detection, controlled failure/recovery and final-main build #5.
- [ ] Instructor confirms provider/scope and accepts the actual Jenkins environment/trigger.
- [ ] Team completes presentation delivery and the official reflection/rubric.

Sources: supplied *DEVASC Project.pdf* and REST API lab; repository source/tests at the baseline above; linked PRs and CI; `docs/live-verification.md`. The instructor guide states deliverables but does not include the detailed student rubric/reflection questions.
