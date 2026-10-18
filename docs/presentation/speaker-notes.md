# Suggested speaker notes — Activity 3/4

Review contribution statements and add real Jenkins build evidence before presenting.

## Slide 1 — Routes you can read, choose and save

Introduce the project as an enhancement of the supplied lab. This is a team project; do not claim that the group wrote the routing engine. Instructor scope approval and the required Jenkins evidence remain pending.

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

Run python scripts/run_offline_tests.py. The runner clears the real key, disables dotenv loading and blocks unmocked HTTP/socket connections. Failure and empty discovery return nonzero status. Merged-main run: https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/39121848255 .

## Slide 8 — Live evidence is a separate record

These observations were recorded October 14 using Manila City Hall to Quezon Memorial Circle. They predate F7/F8, are historical account-specific results, and are not a claim that this presentation made live requests. Source: docs/live-verification.md. Never show the API key or full credential-bearing URL.

## Slide 9 — Collaboration and review evidence

The DRAFT records Justine Smith Rendaje as scrum leader, Wilhelm Ramesh Dimacisil as recorder, and John Jessienel Arquesola / Janwel Gilo as Prompt Engineers. Each member should describe work they actually did and can explain. Personal contribution/challenge/lesson statements are still awaiting confirmation. PR #27 has an LGTM comment recorded as COMMENTED, not a formal APPROVED review.

## Slide 10 — Activity 4: Jenkins is required

Explain that GraphHopper provides routes while Jenkins tests the code. GitHub Actions is verified but supplementary. The local Jenkins package is prepared in a separate PR, not a running/verified service. Merge it, configure checkout credentials in Jenkins, run the job once and record real build evidence. Do not claim polling is a verified GitHub webhook.

## Slide 11 — Limits and the final team handoff

Close by distinguishing implemented application features from unfinished course deliverables. The supplied instructor guide lists required rubrics but does not include the detailed student questions/scoring criteria. Obtain the actual rubric, rather than inventing grades or personal experience.

## Slide 12 — Evidence to open during questions

Supporting local materials: docs/final-report.md and docs/test-results.md (final report PR); docs/demo-guide.md; docs/team-reflection.md; docs/jenkins-local-setup.md (Jenkins PR); docs/live-verification.md. Also use the supplied DEVASC Project.pdf and REST API lab. All four documentation/setup PRs should be reviewed and merged before using repository-relative links as a final submission.
