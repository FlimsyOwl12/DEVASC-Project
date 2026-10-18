# Suggested speaker notes — Activity 3/4

Review contribution statements and show the recorded Jenkins failure, recovery and final-main reports/screenshots before presenting.

## Slide 1 — Routes you can read, choose and save

Introduce the project as an enhancement of the supplied lab. This is a team project; do not claim that the group wrote the routing engine. Jenkins success, SCM triggering, failure/recovery and final-main build #5 are verified. Instructor scope/polling acceptance and actual team assessment remain pending.

## Slide 2 — What problem are we solving?

Explain the customer problem before the implementation. The supplied lab uses GraphHopper; the instructor guide mentions MapQuest, so provider approval is still an explicit team action.

## Slide 3 — From terminal input to a reusable route

Trace one route through the actual functions. Geocoding and routing use HTTPS GET requests. History and exports reuse validated route data without making additional requests.

## Slide 4 — Core enhancements: F1 to F4

Show the command-line output in the demonstration. Point out that readable plain text works without color and that malformed replies do not need to become tracebacks or expose the key.

## Slide 5 — F7 / Save a route. F8 / Choose a place.

Run python scripts/demo_offline.py. The banner says SYNTHETIC: these are fixed mocked replies, not a new live GraphHopper route. The second coordinates must reach routing. Exports retain directions even when terminal summary mode is selected.

## Slide 6 — Menu and session history

In the offline replay, show history viewing and TXT/CSV export after the initial JSON export. The script verifies that only the initial three mocked HTTP calls occurred. Explain that there is no persistent database.

## Slide 7 — Verification we can reproduce

Run python scripts/run_offline_tests.py. The runner clears the real key, disables dotenv loading and blocks unmocked HTTP/socket connections. Failure and empty discovery return nonzero status. Merged-main run: https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/39132132376 .

## Slide 8 — Live evidence is a separate record

These observations were recorded October 14 using Manila City Hall to Quezon Memorial Circle. They predate F7/F8, are historical account-specific results, and are not a claim that this presentation made live requests. Source: docs/live-verification.md. Never show the API key or full credential-bearing URL.

## Slide 9 — Collaboration and review evidence

The DRAFT records Justine Smith Rendaje as scrum leader, Wilhelm Ramesh Dimacisil as recorder, and John Jessienel Arquesola / Janwel Gilo as Prompt Engineers. Each member should describe work they actually did and can explain. Personal contribution/challenge/lesson statements are still awaiting confirmation. PR #27 has an LGTM comment recorded as COMMENTED, not a formal APPROVED review.

## Slide 10 — Activity 4: Jenkins is required

Jenkins 2.580.1 is running. Original #1 passed manually, and SCM polling started #2 automatically. On the separate demo job, #1 at bdd74ce failed exactly one intentional test; reverting only that test produced ed43bde and automatic Demo #2 passed 69 tests. After PRs #30/#28 merged, original build #5 checked out c6d34d5 and passed 69 tests in 0.486 seconds with its report archived. The original job targets main and the demo job is disabled with its history retained. Open the saved failure/recovery/main reports and screenshots. See docs/jenkins-evidence.md and handoff PR #32. Polling is verified; webhook delivery and instructor acceptance are not.

## Slide 11 — Limits and the final team handoff

Close by distinguishing implemented application features from unfinished course deliverables. The supplied instructor guide lists required rubrics but does not include the detailed student questions/scoring criteria. Obtain the actual rubric, rather than inventing grades or personal experience.

## Slide 12 — Evidence to open during questions

Supporting local materials: docs/final-report.md and docs/test-results.md (final report PR); docs/demo-guide.md; docs/team-reflection.md; docs/jenkins-local-setup.md (Jenkins PR); docs/live-verification.md. Also use the supplied DEVASC Project.pdf and REST API lab. PRs #28/#30 are merged. Report PR #29, presentation PR #31 and shared handoff PR #32 still need review/merge. Build #5 verified main at c6d34d5; do not describe later documentation as already merged.
