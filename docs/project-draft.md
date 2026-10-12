# DEVASC Project Draft — Option 1

Status: proposed team plan and partial starter; not a final submission.

## Project choice and rationale

We selected Option 1 of Project Activity 3: enhance the application developed in the *Integrate a REST API in a Python Application* lab. The instructor guide mentions MapQuest, while our supplied lab and reference repository use GraphHopper. Our proposed implementation therefore uses GraphHopper; the team should confirm this provider choice with the instructor.

The application helps a user obtain directions between a starting location and a destination. It uses Python to send REST GET requests over HTTPS, parse JSON responses, and display route distance, estimated duration, and instructions. The lab supports car, bicycle, and walking profile input, subject to the team's API account capabilities.

## Proposed objectives

1. Retain the lab's geocoding and routing workflow as the development baseline.
2. Add user-selectable metric or imperial units consistently throughout the output.
3. Improve readability with a structured summary and numbered directions.
4. Validate input and API responses, and test behavior with Python unit tests.
5. Use GitHub branches, issues, pull requests, and peer review to document team contributions.

## Partial implementation and remaining work

The starter adapts the linked lab scripts from reference commit `2289d4d`. Baseline routing already existed in that repository. The starter adds API key setup with automatic loading of the project-root `.env` file (exported environment variables take precedence), dependency instructions, importable functions, timeouts, basic request/JSON error handling, and a guard against routing with unresolved locations. It avoids displaying URLs containing credentials and uses the current `profile` parameter.

The new Option 1 features are pending. Unit selection, structured output, comprehensive response validation, a permanent test suite, and CI/CD have not been completed. Live GraphHopper functionality has not been verified with a team key. The README contains the authoritative task checklist and acceptance criteria.

## Proposed backlog and responsibilities

| Priority / task | Suggested responsibility | Owner | Estimate | Dependencies |
| --- | --- | --- | --- | --- |
| P1 / P0: agree scope, provider, repository, and schedule | Scrum lead and recorder | TBD | TBD | Instructor/team agreement |
| P1 / F1: metric/imperial selection | Input and formatting contributor | TBD | TBD | Approved scope |
| P1 / F2: summary/table and numbered directions | Presentation contributor | TBD | TBD | Coordinate with F1 |
| P1 / F4: API response validation | API contributor | TBD | TBD | Baseline |
| P1 / F5: mocked Python unit tests | QA contributor | TBD | TBD | Feature behavior agreed |
| P1 / F6: live API checks and evidence | QA and API contributors | TBD | TBD | Own key; core features |
| P2 / F3: summary/detail choice | Team assignment pending | TBD | TBD | F2 |
| P2 / F9: automated tests/pipeline for Activity 4 | CI contributor | TBD | TBD | F5 |
| P3 / F7–F8: export and candidate selection | Team assignment pending | TBD | TBD | Core sprint complete |

These are suggested work areas, not assigned team roles. The team must add actual members, owners, estimates, dates, and budget/API allowance before committing to a sprint. No cost or completion percentage has been established.

## Collaboration plan

The team will select a scrum lead and recorder, agree on meeting times and communication tools, and create issues for each selected task. Each contributor will work on a feature branch and submit a pull request for peer review. The README checklist will track completion against acceptance criteria. Optional features will remain in the backlog for a later iteration.

The current local workspace is configured with `FlimsyOwl12/DEVASC-Project` as its Git remote. `Cocoasaur/devasc-graphhopper-api` is the referenced lab repository. The team must agree on its shared collaboration repository before publishing work.

## Validation plan

Use mocked HTTP responses to test successful geocoding/routing, empty results, HTTP errors, timeouts, invalid JSON, malformed fields, unit conversion, output modes, and exit behavior. Live checks will use the team's own API key and reachable locations; evidence must hide credentials. Until these tests and checks are completed, the application is a starter rather than a verified final solution.

During starter preparation, both scripts passed syntax checks and nine temporary offline smoke checks passed, covering basic startup, mocked API requests and route output, empty/error results, credential redaction, quit handling, and request/JSON failures. This is limited baseline evidence; a committed team test suite, malformed-field coverage, enhancement acceptance tests, and live API evidence remain pending.

After fixing `.env` loading, six additional offline checks passed for file configuration, environment-variable precedence, and missing configuration across both scripts. Startup with the saved project key now reaches the application prompt. This verifies configuration loading; live API authentication remains unverified.

## Expected team deliverables

For Activity 3, prepare a demo-ready enhanced application, project overview presentation and demonstration, prioritized backlog, completed activity rubric, and team activities/reflection answers. For Activity 4, continue selected backlog features and document automated testing/deployment, test cases, GitHub changes, presentation, and rubric. The network automation work in Activity 5 is a separate activity outside this routing draft.

## Details to complete together

- [ ] Team name, members, scrum lead, and recorder.
- [ ] Confirmed scope, feature owners, effort estimates, schedule, and budget.
- [ ] Communication plan, meeting records, and shared repository.
- [ ] Actual enhancement results, test evidence, and demo screenshots.
- [ ] Presentation, rubric, and reflection based on the team's real work.

## Sources

The supplied *DEVASC Project* instructor guide, the supplied GraphHopper REST API lab, [the reference repository](https://github.com/Cocoasaur/devasc-graphhopper-api), and [GraphHopper documentation](https://docs.graphhopper.com/) informed this draft. An adapted version of this plan was added to the DRAFT tab of the [shared Draft Document](https://docs.google.com/document/d/1Q0knNhliyox7P0iDQgf0t-ZiOJ94uc_3q4Q7jl_njh8/edit) under Activities 3 and 4 on October 12, 2026. Readback verified the inserted content and preservation of the other tab; existing team placeholders remain for the group to complete.
