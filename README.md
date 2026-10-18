# DEVASC Project — Option 1: GraphHopper REST API Enhancements

This is a **partial team project** based on the completed *Integrate a REST API in a Python Application* lab. The existing lab workflow is the starting point; selected enhancements are implemented while the remaining backlog is available for team members.

The customer goal is to make a Python directions application easier to use: accept an origin, destination, and travel profile, then present distance, duration, and directions clearly. Implemented enhancements include metric/imperial units, clearer output, route exports, and location selection.

## Requirements and scope

The supplied **DEVASC Project.pdf**, Project Activity 3 (Social Coding), defines Option 1 as enhancing the completed REST API lab. It calls for feature prioritization, team roles, a backlog with schedule/budget estimates, GitHub collaboration, application development, a demonstration/presentation, reflection, and a completed rubric. Its examples include unit selection and better output.

The guide refers to MapQuest. The supplied **Integrate a REST API in a Python Application** lab and the [reference repository](https://github.com/Cocoasaur/devasc-graphhopper-api) use **GraphHopper**, so this project follows that lab. Confirm this provider choice with the instructor when approving the scope.

Activity 4 adds backlog development and automated testing/deployment. Activity 5 is a separate network automation activity; it is outside this routing starter. Application enhancements and verified automation are tracked below; instructor approvals and team assessment deliverables remain separate.

## Current status

Included from the lab: geocoding, car/bike/foot input, routing requests, distance, duration, directions, and a repeat/quit loop. These are **baseline features**, not completed Option 1 enhancements.

Prepared for collaboration: environment-based API key configuration, dependency/setup files, importable functions, request timeouts, basic request/JSON error messages, and prevention of routing with missing coordinates. API request URLs containing the key are not printed. Requests use `profile` in place of the lab's `vehicle`, following [GraphHopper's migration guidance](https://www.graphhopper.com/blog/2021/12/15/new-and-customizable-routing-profiles/).

**Implemented enhancements:** F1 adds metric or imperial unit selection for all distances. F2 adds an aligned plain-text route summary and numbered directions. F3 lets users choose a summary-only view or full directions for each route. F4 validates geocoding/routing response structure and numeric fields, reports malformed replies without a traceback, and keeps credentials out of displayed response text. F7 adds local route exports in TXT, JSON, and CSV formats with sanitized filenames and duplicate protection. F8 adds interactive selection from up to five validated geocoding candidates. The CLI also provides a main navigation menu and session route history (storing up to 10 routes for offline viewing and exporting).

**F9 automation implemented:** GitHub Actions and Jenkins run a shared offline test command with saved reports. See [Activity 4 pipeline setup and test plan](docs/automated-checks.md). Jenkins is required by the instructor (confirmed by the user on October 18). Local Jenkins success, automatic SCM detection, an isolated intentional failure and automatic recovery are verified with archived reports. Instructor acceptance and the team presentation/rubric remain pending.

**Pending:** final team deliverables. No claim of final completion is made.

## Setup and run

Use Python 3.10 or newer. From this project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

Obtain your own key from the [GraphHopper dashboard](https://graphhopper.com/dashboard/). Copy the example to `.env` in the project root if you have not already created that file:

```bash
cp -n .env.example .env
```

Edit `.env` and replace `replace_with_your_own_key` with your key, then run:

```bash
python labs/devnet-src/graphhopper/graphhopper_parse-json_7.py
```

Both scripts automatically load the project's `.env`, even when launched from a different working directory. An already exported `GRAPHHOPPER_API_KEY` takes precedence over the file. If your terminal has an outdated key, run `unset GRAPHHOPPER_API_KEY` before starting the script to use the value in `.env`. Do not commit keys or include them in screenshots.

Alternatively, on Linux/macOS, set the key for the current terminal without typing it into a command saved in shell history:

```bash
printf 'GraphHopper API key: '
read -r -s graphhopper_key
printf '\n'
export GRAPHHOPPER_API_KEY="$graphhopper_key"
unset graphhopper_key
python labs/devnet-src/graphhopper/graphhopper_parse-json_7.py
```

The [python-dotenv loader](https://bbc2.github.io/python-dotenv/) reads `.env` without executing it as a shell script. `.env.example` remains a template and is not loaded directly.

Use the main menu (`1. Find a Route`, `2. View Route History`, `3. Export Previous Route`, `4. Exit`) to navigate. When finding a route, enter `car`, `bike`, or `foot`, then choose `metric` or `imperial`, select `summary` or `detailed` output, and enter the two locations. When multiple geocoding candidates match a location, choose from the numbered candidate list (`1-5`), which shows latitude and longitude so same-name places can be distinguished, or use `R` to search again or `Q` to quit. After displaying a route, optionally export it to `exports/` as TXT, JSON, or CSV, or view/export any of the last 10 session routes from the main menu without additional API requests. Use menu option 4 or `q`/`quit` at the main menu to exit. In export/history-selection menus, `q`/`quit` cancels the operation and returns to the main menu. Actual profile availability, quotas, and route coverage must be checked with the team's API account.

The earlier geocoding-only exercise is also included:

```bash
python labs/devnet-src/graphhopper/graphhopper_parse-json_1.py
```

## Local Jenkins instance

Setup record — October 18, 2026:

- **Jenkins URL:** `http://127.0.0.1:8080/`. The setup wizard is complete.
- **Observed version:** Jenkins 2.580.1. The local `DEVASC-GraphHopper` job checks out the private repository and runs the offline suite.
- This address is accessible on the computer hosting Jenkins; it is not a public team URL or GitHub webhook endpoint.

- [x] Start the local Jenkins container and verify its web page responds.
- [x] Reach the **Instance Configuration** step of the setup wizard.
- [x] Save the instance URL and finish the wizard.
- [x] Configure the `DEVASC-GraphHopper` Pipeline job and its private-repository checkout credential in Jenkins.
- [x] Record [manual build #1](http://127.0.0.1:8080/job/DEVASC-GraphHopper/1/): commit `001efafcb0abef8356c37cb3c75f8f92768b9673`, 69 tests passed, report archived, `SUCCESS`.
- [x] Verify automatic detection through SCM polling: [build #2](http://127.0.0.1:8080/job/DEVASC-GraphHopper/2/) checked out `21c323049e2d1b8061fa34bae1410aa95573d83e`, passed all 69 tests and archived the report. Its recorded cause is an SCM trigger, not a manual build or verified webhook.
- [x] Prepare `demo/jenkins-failure-recovery` and separate-job [instructions in PR #30](docs/jenkins-failure-demo.md); its added test was verified locally to fail as intended.
- [x] Run the separate Jenkins demonstration job: [Demo #1](http://127.0.0.1:8080/job/DEVASC-GraphHopper-Demo/1/) at `bdd74ce` ran 70 tests with exactly one intentional failure and archived the report.
- [x] Revert only the demo test and verify automatic recovery: [Demo #2](http://127.0.0.1:8080/job/DEVASC-GraphHopper-Demo/2/) at `ed43bde` was SCM-triggered, passed all 69 original tests and archived the report (`SUCCESS`).
- [x] Switch the original job to `*/main` after PRs #30/#28 merged; [build #5](http://127.0.0.1:8080/job/DEVASC-GraphHopper/5/) checked out `c6d34d5`, passed 69 tests and archived the report (`SUCCESS`).
- [x] Disable `DEVASC-GraphHopper-Demo` while retaining both demonstration builds and reports.
- [ ] Confirm presentation screenshots/reports are saved and remove the disposable branch after team review; do not merge its commits.

Passwords, unlock values, tokens, and account details are not recorded in this README.

## Before pushing

Commit application files, `requirements.txt`, `.gitignore`, the placeholder-only `.env.example`, and project documentation. Keep `.env`, virtual environments, caches, local agent settings, credential files, and logs out of Git. These are excluded by `.gitignore`; avoid force-adding ignored files.

Review `git status --short` and `git diff --cached --name-only` before each commit. Use explicit file paths when staging. Each teammate must install dependencies and create their own project-root `.env` after cloning; the real API key is never included in the repository. Startup and mocked routing have been verified; live routing still requires an accepted GraphHopper key, account-supported profiles, quota, and internet access.

## Files and contribution points

| File/function | Purpose / teammate contribution |
| --- | --- |
| `labs/devnet-src/graphhopper/graphhopper_parse-json_1.py` | Initial geocoding exercise |
| `labs/devnet-src/graphhopper/graphhopper_parse-json_7.py` | Working lab baseline; main enhancement target |
| `display_route()` / `format_distance()` | Selected-unit formatting, aligned summary, and numbered directions |
| `main()` / `find_route_workflow()` / `RouteHistory` | Main menu navigation, route workflow, and 10-route session history |
| `geocoding()` / `extract_geocode_candidates()` / `routing()` | F4/F8 validated multi-candidate geocoding and routing |
| `export_route_txt()` / `export_route_json()` / `export_route_csv()` | F7 TXT, JSON, and CSV export functions with path safety |
| `labs/devnet-src/graphhopper/graphhopper_live_verify.py` | Manual F6 live API verification helper that avoids printing keys |
| `requirements.txt` / `.env.example` | Dependency and configuration setup |
| `scripts/run_offline_tests.py` | Shared credential-free, network-blocked CI test command |
| `.github/workflows/offline-tests.yml` / `Jenkinsfile` | Automatic GitHub checks and the course Jenkins pipeline |
| `docs/automated-checks.md` | F9 setup, test plan, evidence collection, and remaining Activity 4 deliverables |
| `tests/test_offline_runner.py` | CI runner isolation and failure-reporting regression tests |
| `docs/project-draft.md` | Local summary, refreshed by [report PR #29](https://github.com/FlimsyOwl12/DEVASC-Project/pull/29) |
| [Application report and results — PR #29](https://github.com/FlimsyOwl12/DEVASC-Project/pull/29) | Features, setup, limitations, and observed verification evidence |
| [Local Jenkins setup — PR #30](https://github.com/FlimsyOwl12/DEVASC-Project/pull/30) | Required server/job setup, SCM polling, and build-evidence guide |
| [Presentation/demo/reflection materials — PR #31](https://github.com/FlimsyOwl12/DEVASC-Project/pull/31) | Editable slides/PDF, speaker notes, offline replay, and evidence worksheet |
| `docs/live-verification.md` | F6 command, evidence checklist, and redaction guidance |
| `tests/test_graphhopper_api.py` | Offline F5 tests for mocked HTTP, failures, timeouts, input, and no-key behavior |
| `tests/test_graphhopper_cli.py` | Offline acceptance tests for F1/F2 |
| `tests/test_graphhopper_output_modes.py` | Offline F3 tests for output modes, prompt handling, and mocked routes |
| `tests/test_graphhopper_responses.py` | Offline validation and recovery tests for F4 |
| `tests/test_graphhopper_exports.py` | Offline F7 tests for TXT/JSON/CSV exports, path safety, and duplicate handling |
| `tests/test_graphhopper_geocoding_candidates.py` | Offline F8 tests for multi-candidate selection, retry, quit, and routing integration |
| `tests/test_graphhopper_history_menu.py` | Offline tests for main menu navigation and 10-route session history |

## Team task checklist

Checked items indicate completed work; unchecked items remain for the team. F7/F8 were merged in [PR #27](https://github.com/FlimsyOwl12/DEVASC-Project/pull/27); issues #13/#14 are closed. The remaining integration work is confirming the team review record. Record owners and estimates in the linked issues. Suggested work areas describe the type of contribution and do not assign a person. P1 = first sprint, P2 = after the core enhancements, P3 = optional/deferred.

Status updated October 18, 2026: starter preparation, offline verification, GitHub publication, and task-issue creation are complete. Issue links are included below. F1 unit selection, F2 clearer output, F3 summary/detail selection, F4 response validation, F5 offline unit tests, F6 live verification, F7 route exports, F8 multiple geocoding candidates, main menu navigation, and session route history are complete. F9 pipeline code and documentation are implemented; Jenkins success, automatic polling, intentional failure, recovery and the final merged-main build are verified. Instructor acceptance of the local environment/polling and the Activity 4 presentation/rubric remain open. The current offline suite has 69 tests, including a regression check for same-name candidates, selected routing coordinates, and key redaction. F6 live results are recorded in `docs/live-verification.md`.

### Starter preparation

- [x] Read both supplied PDFs and record the Option 1 scope.
- [x] Adapt the reference lab scripts from commit `2289d4d` without embedded keys.
- [x] Add environment configuration, setup instructions, and `.gitignore`.
- [x] Separate the baseline into functions with a `main()` entry point.
- [x] Add this prioritized backlog and a project draft.
- [x] Fix automatic project-root `.env` loading in both scripts while preserving exported-variable precedence.
- [x] Verify syntax and basic application behavior with nine temporary offline smoke checks.
- [x] Pass six additional configuration checks for `.env` loading, environment precedence, and missing configuration.
- [x] Verify startup reaches the travel-profile prompt with the saved project key, without making a live API request.
- [x] Verify a clean Git archive contains the required starter files and can run a full mocked route after `.env` setup.
- [x] Exclude `.env`, virtual environments, caches, local settings, credential files, and logs from Git; scan staged files and committed history for the saved key.
- [x] Create separate starter commits: exclusions (`30cd003`), application/configuration (`0fcd947`), and setup/backlog documentation (`706a782`).
- [x] Add the partial project plan and configuration update to the Google Doc's DRAFT tab and verify the edits.
- [x] Publish the starter commits to `origin/main` and verify they appear on GitHub. The starter history is present on the remote main branch.

### Planning and collaboration — P1; suggested area: scrum lead / recorder

- [ ] **P0** Agree on the customer problem, GraphHopper provider, and sprint scope with the instructor. [Issue #2](https://github.com/FlimsyOwl12/DEVASC-Project/issues/2)
- [ ] Confirm feature owners and complete the team responsibilities record; the team name, members, scrum lead and recorder are already recorded in the shared DRAFT. [Issue #3](https://github.com/FlimsyOwl12/DEVASC-Project/issues/3)
- [ ] Confirm the meeting timezone, resolve Saturday versus twice-daily wording, and agree on the application sprint deadline; Discord and meeting-note responsibilities are recorded. [Issue #4](https://github.com/FlimsyOwl12/DEVASC-Project/issues/4)
- [ ] Confirm effort estimates, dependencies, budget and API allowance against the team's actual agreement and account. [Issue #5](https://github.com/FlimsyOwl12/DEVASC-Project/issues/5)
- [x] Configure the local Git repository with `FlimsyOwl12/DEVASC-Project` as `origin`; use `Cocoasaur/devasc-graphhopper-api` as the lab reference.
- [x] Confirm the shared repository with the team and invite collaborators.
- [x] Create 19 GitHub issues for the unfinished README tasks (issues #2–#20).
- [ ] Confirm issue owners and the actual project-board status with the team. [Issue #6](https://github.com/FlimsyOwl12/DEVASC-Project/issues/6)

### Completed development — F1–F6

- [x] **F1 — Unit selection** (suggested area: input/formatting): add a metric/imperial prompt; apply the selected unit to the total **and every instruction**. Acceptance: switching units changes labels and values consistently; 1,609.344 m displays as 1.0 mile, and `q` still exits from the new prompt. [Issue #7](https://github.com/FlimsyOwl12/DEVASC-Project/issues/7) [Merged PR #21](https://github.com/FlimsyOwl12/DEVASC-Project/pull/21).
- [x] **F2 — Clearer terminal output** (suggested area: presentation): add an aligned summary/table and numbered directions; optionally add color with a readable plain-text option. Acceptance: origin, destination, profile, distance, duration, and each step are easy to identify; output works without color. [Issue #8](https://github.com/FlimsyOwl12/DEVASC-Project/issues/8) [Merged PR #22](https://github.com/FlimsyOwl12/DEVASC-Project/pull/22).
- [x] **F3 — Summary or detailed output** — P2: let users choose a summary-only view or full directions. Acceptance: summary mode suppresses instructions while keeping route totals. [Issue #12](https://github.com/FlimsyOwl12/DEVASC-Project/issues/12) [Merged PR #24](https://github.com/FlimsyOwl12/DEVASC-Project/pull/24).
- [x] **F4 — Response validation** (suggested area: API integration): handle missing/invalid coordinate fields, malformed `hits`/`paths`, missing distance/time/instructions, and non-dictionary JSON. Acceptance: representative malformed responses produce a helpful message and return to the prompt without a traceback or printing credentials. [Issue #9](https://github.com/FlimsyOwl12/DEVASC-Project/issues/9) [Merged PR #23](https://github.com/FlimsyOwl12/DEVASC-Project/pull/23).
- [x] **F5 — Python unit tests** (suggested area: QA): create tests with `unittest` and mock HTTP calls. Cover successful geocoding/routing, no hits/no paths, 401/429/errors, timeouts, malformed JSON/schema, blank input/quit, and F1/F2 acceptance cases. Acceptance: tests run offline without a real key, including a check that routing is skipped after unsuccessful geocoding. [Issue #10](https://github.com/FlimsyOwl12/DEVASC-Project/issues/10) Evidence: [mocked API tests](tests/test_graphhopper_api.py) and the offline suite.
- [x] **F6 — Live verification** (suggested area: QA + API integration): use the team's own key to verify one reachable route for each available profile and a route that cannot be connected. Acceptance: record actual inputs/results and any account limitations, with no key visible in evidence. [Issue #11](https://github.com/FlimsyOwl12/DEVASC-Project/issues/11) Evidence: [recorded live verification results](docs/live-verification.md).

### Development status — F7/F8

- [x] **F7 — Export route results** — P3: implemented and merged through PR #27. [Issue #13](https://github.com/FlimsyOwl12/DEVASC-Project/issues/13) [PR #27](https://github.com/FlimsyOwl12/DEVASC-Project/pull/27).
  - [x] Export route summaries and directions in TXT, JSON, and CSV with the selected units and no API key.
  - [x] Validate filenames and paths; prevent silent overwrites and support choosing another filename or automatic renaming.
  - [x] Verify exports, formatting, duplicate handling, filesystem errors, and key redaction with offline tests.
- [x] **F8 — Multiple geocoding candidates** — P3: implemented and merged through PR #27. [Issue #14](https://github.com/FlimsyOwl12/DEVASC-Project/issues/14) [PR #27](https://github.com/FlimsyOwl12/DEVASC-Project/pull/27).
  - [x] Show up to five validated candidates and use the selected candidate's coordinates in routing.
  - [x] Handle invalid choices, search retry, and quitting; skip selection when only one valid candidate exists.
  - [x] Display latitude and longitude so candidates with identical names can be distinguished.
  - [x] Add a regression test for same-name choices, selected routing coordinates, and key redaction.

### Additional implemented improvements

- [x] Add a main navigation menu and keep the last 10 successful routes in session history.
- [x] View or export stored routes without additional API requests.
- [x] Remove all nine tracked Python cache files; retain the existing ignore rules.
- [x] Pass all 69 offline tests locally and from a clean Git archive; pass Python 3.10 and 3.14 GitHub checks. [Verified PR run](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/39119946421).

### Activity 4 — F9

- [ ] **F9 — Automated checks (Activity 4)** — P2: pipeline implementation is ready; the complete Activity 4 acceptance checklist remains open. [Issue #15](https://github.com/FlimsyOwl12/DEVASC-Project/issues/15) [Pipeline setup and test plan](docs/automated-checks.md).
  - [x] Implement GitHub Actions for pushes/PRs and supply the course Jenkinsfile.
  - [x] Run offline tests without a real key; block network calls, fail on test errors/empty discovery, and retain reports.
  - [x] Document test cases, pipeline functionality, and evidence collection.
  - [x] Prepare the local Jenkins Docker/Compose package and five-minute SCM polling fallback in [PR #30](https://github.com/FlimsyOwl12/DEVASC-Project/pull/30).
  - [x] Configure local Jenkins and record successful manual build #1 with all 69 tests and an archived report.
  - [x] Record automatic SCM-triggered build #2: all 69 tests passed and the report was archived.
  - [x] Prepare Activity 4 presentation material in [PR #31](https://github.com/FlimsyOwl12/DEVASC-Project/pull/31); add the recorded Jenkins results during team rehearsal and complete the rubric/reflection.
  - [x] Verify published GitHub checks: [PR #26](https://github.com/FlimsyOwl12/DEVASC-Project/pull/26), [push run](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/38742491385), and [PR run](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/38742542685) passed 42 tests on both Python 3.10 and 3.14.
  - [x] Record actual failed/recovery builds and the final-main build #5, with reports archived; see [Jenkins evidence](docs/jenkins-evidence.md).
  - [ ] Obtain instructor acceptance of the local Jenkins environment and SCM polling, or demonstrate a reachable webhook if required.
  - [ ] Prepare the Activity 4 presentation and complete the team rubric/reflection.

### Integration, evidence, and submission

- [ ] Review and merge each feature through a pull request, then update this checklist. [Issue #16](https://github.com/FlimsyOwl12/DEVASC-Project/issues/16)
  - [x] Merge the F1/F2/F3/F4 changes through PRs #21–#24 and the F9 pipeline implementation through PR #26.
  - [x] Open [PR #27](https://github.com/FlimsyOwl12/DEVASC-Project/pull/27) for F7/F8 and resolve the same-name candidate and tracked-cache findings.
  - [x] Merge PR #27; issues #13 and #14 closed automatically.
  - [x] Merge Jenkins PR #30 (`5bb38bb`) and checklist PR #28 (`c6d34d5`); GitHub checks passed and Jenkins verified merged main.
  - [ ] Confirm the team review record; GitHub shows an `LGTM!` comment, with review state `COMMENTED`.
  - [x] Delete `F7---F8-Donezo` locally and on GitHub after merging, and synchronize local `main`.
- [x] Prepare the application report and test-results summary in [PR #29](https://github.com/FlimsyOwl12/DEVASC-Project/pull/29), covering features, setup, limitations and recorded evidence. [Issue #17](https://github.com/FlimsyOwl12/DEVASC-Project/issues/17). Review and merge the report PR before final submission.
- [ ] Complete the Activity 3 overview presentation and application demonstration. [Issue #18](https://github.com/FlimsyOwl12/DEVASC-Project/issues/18)
  - [x] Prepare the editable 12-slide deck, PDF, speaker notes and demo guide in [PR #31](https://github.com/FlimsyOwl12/DEVASC-Project/pull/31).
  - [x] Verify the synthetic offline demo: selected coordinates, imperial totals, TXT/JSON/CSV exports, and no extra HTTP for history.
  - [ ] Confirm individual contributions, rehearse with the team, and deliver/record the actual presentation.
- [ ] Complete the supplied team reflection questions and activity rubric using actual team experience. [Issue #19](https://github.com/FlimsyOwl12/DEVASC-Project/issues/19)
  - [x] Prepare a factual evidence worksheet and member-response form in [PR #31](https://github.com/FlimsyOwl12/DEVASC-Project/pull/31).
  - [ ] Obtain the exact student questions/rubrics; the supplied instructor guide does not contain their full text.
  - [ ] Each member supplies their own contribution, challenge and lesson; the recorder assembles the answers for member review.
- [ ] Review the backlog and explicitly defer unfinished features. [Issue #20](https://github.com/FlimsyOwl12/DEVASC-Project/issues/20)
  - [x] Prepare the [evidence-based backlog review](docs/backlog-review.md); F1–F8 are implemented and no longer deferred.
  - [ ] Have the team confirm owners, estimates, scope, and the next iteration on its project board.

PRs #28 and #30 are merged. Report PR #29 and presentation PR #31 remain open for team review, with refreshed Jenkins evidence. Presentation delivery, member reflections and instructor decisions are still outstanding. Activity 5 is a separate network-automation plan in the shared DRAFT, not implemented in this routing repository.

Status reconciliation: issues #10/#11 are closed on the permanent 69-test suite and the October 14 live record. Issues #3–#6 remain open for feature ownership, meeting/deadline clarification, estimates/budget and board confirmation. Their README entries are left unchecked until those criteria are met.

The [backlog/integration review](docs/backlog-review.md) records merge evidence, verified Jenkins execution, cleanup status, and the remaining team decisions.

## Working together

Agree on owners before coding. Use one separate branch per task with a short descriptive name, such as `f7-export-results` or `docs-readme-checklist`. Keep commits scoped to the task. Follow **branch → implementation → tests → PR → merge → delete the finished branch locally and on GitHub**. Describe the acceptance criteria and test evidence in the PR, and ask another member to review it.

F1–F6 are complete. F7 exports and F8 candidate selection are merged in [PR #27](https://github.com/FlimsyOwl12/DEVASC-Project/pull/27); F9 has verified Jenkins execution and a test plan; its remaining instructor acceptance and team deliverables are listed above. Coordinate changes that affect the same functions and update the relevant README and issue checklists when a task is completed.

Starter verification: both scripts passed syntax checks and nine temporary offline smoke checks passed using mocked HTTP responses. These covered missing-key startup, geocoding parameters, empty hits skipping routing, route coordinates/profile, HTTP errors and key redaction, a full mocked route and formatting, quit/blank input, timeout/invalid JSON recovery, and the initial geocoding script. The F5 committed test suite now preserves and expands that coverage with repeatable `unittest` tests.

Run the offline suite with dotenv loading disabled, the API key cleared, and network calls blocked (the same command used by CI):

```bash
python scripts/run_offline_tests.py
```

Configuration fix verified: six additional offline checks covered `.env` loading from another working directory, exported-key precedence, and missing configuration for both scripts. Startup with the project's saved `.env` key now reaches the travel-profile prompt; no network request was made during that startup check. This confirms key loading, not GraphHopper's acceptance of the key.

Live API verification with the team key succeeded on October 14, 2026; see `docs/live-verification.md` for the redacted evidence. F6 live verification can be rerun with `python labs/devnet-src/graphhopper/graphhopper_live_verify.py`. F4 validates object/list structure, coordinate ranges, place names, finite nonnegative route totals, and instruction fields before display. Invalid replies return to the prompt without routing with missing coordinates or exposing credentials. The application tests cover F1/F2/F3/F4/F5, including HTTP 401/429/server errors, timeouts, invalid JSON, malformed schemas, blank input, quit behavior, no-key execution, and routing skipped after bad geocoding. F3 coverage includes summary totals without directions, numbered detailed output in both units, mode validation, quitting without HTTP requests, and changing modes between mocked routes. The four F9 runner regression tests verify isolation, failure reporting, blocked HTTP, and empty discovery. F7/F8 export, candidate-selection, and history tests bring the current suite to 69 tests, including the same-name candidate regression. See `docs/automated-checks.md` for CI setup and remaining Activity 4 work. F7 and F8 share PR #27. Keep commits scoped and delete finished implementation branches after merging.

## References

- Supplied `DEVASC Project.pdf`: Activity 3 Option 1 and Activity 4 deliverables.
- Supplied `8_Integrate a REST API in a Python Application - ILM_Arquesola.docx (1).pdf`: GraphHopper geocoding/routing lab.
- [Cocoasaur/devasc-graphhopper-api](https://github.com/Cocoasaur/devasc-graphhopper-api/tree/2289d4d): source lab scripts, adapted here.
- [GraphHopper API documentation](https://docs.graphhopper.com/): verify request parameters and account-supported profiles before the live demo.
- [Shared Draft Document](https://docs.google.com/document/d/1Q0knNhliyox7P0iDQgf0t-ZiOJ94uc_3q4Q7jl_njh8/edit): an adapted project plan was added to the DRAFT tab under Activities 3 and 4 on October 12, 2026; the local draft is in `docs/project-draft.md`.
