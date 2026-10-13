# DEVASC Project — Option 1: GraphHopper REST API Enhancements

This is a **partial team project** based on the completed *Integrate a REST API in a Python Application* lab. The existing lab workflow is the starting point; selected enhancements are implemented while the remaining backlog is available for team members.

The customer goal is to make a Python directions application easier to use: accept an origin, destination, and travel profile, then present distance, duration, and directions clearly. Proposed enhancements include choosing metric/imperial units and improving terminal output.

## Requirements and scope

The supplied **DEVASC Project.pdf**, Project Activity 3 (Social Coding), defines Option 1 as enhancing the completed REST API lab. It calls for feature prioritization, team roles, a backlog with schedule/budget estimates, GitHub collaboration, application development, a demonstration/presentation, reflection, and a completed rubric. Its examples include unit selection and better output.

The guide refers to MapQuest. The supplied **Integrate a REST API in a Python Application** lab and the [reference repository](https://github.com/Cocoasaur/devasc-graphhopper-api) use **GraphHopper**, so this project follows that lab. Confirm this provider choice with the instructor when approving the scope.

Activity 4 adds backlog development and automated testing/deployment. Activity 5 is a separate network automation activity; it is outside this routing starter. The guide describes eventual team deliverables, while this handoff implements only the baseline preparation requested for now.

## Current status

Included from the lab: geocoding, car/bike/foot input, routing requests, distance in both units, duration, directions, and a repeat/quit loop. These are **baseline features**, not completed Option 1 enhancements.

Prepared for collaboration: environment-based API key configuration, dependency/setup files, importable functions, request timeouts, basic request/JSON error messages, and prevention of routing with missing coordinates. API request URLs containing the key are not printed. Requests use `profile` in place of the lab's `vehicle`, following [GraphHopper's migration guidance](https://www.graphhopper.com/blog/2021/12/15/new-and-customizable-routing-profiles/).

**Implemented enhancements:** F1 adds metric or imperial unit selection for all distances. F2 adds an aligned plain-text route summary and numbered directions, including readable output when no steps are returned.

**Pending:** optional exports, comprehensive response validation, comprehensive API tests, CI/CD, live API verification, and final team deliverables. No claim of final completion is made.

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

Enter `car`, `bike`, or `foot`, then choose `metric` or `imperial`, followed by the two locations. The selected unit applies to the route total and every direction step. Unknown units ask again. An unknown nonblank profile falls back to `car`; blank input asks again. Enter `q` or `quit` at any prompt to exit. Actual profile availability, quotas, and route coverage must be checked with the team's API account.

The earlier geocoding-only exercise is also included:

```bash
python labs/devnet-src/graphhopper/graphhopper_parse-json_1.py
```

## Before pushing

Commit application files, `requirements.txt`, `.gitignore`, the placeholder-only `.env.example`, and project documentation. Keep `.env`, virtual environments, caches, local agent settings, credential files, and logs out of Git. These are excluded by `.gitignore`; avoid force-adding ignored files.

Review `git status --short` and `git diff --cached --name-only` before each commit. Use explicit file paths when staging. Each teammate must install dependencies and create their own project-root `.env` after cloning; the real API key is never included in the repository. Startup and mocked routing have been verified; live routing still requires an accepted GraphHopper key, account-supported profiles, quota, and internet access.

## Files and contribution points

| File/function | Purpose / teammate contribution |
| --- | --- |
| `labs/devnet-src/graphhopper/graphhopper_parse-json_1.py` | Initial geocoding exercise |
| `labs/devnet-src/graphhopper/graphhopper_parse-json_7.py` | Working lab baseline; main enhancement target |
| `display_route()` / `format_distance()` | Selected-unit formatting, aligned summary, and numbered directions |
| `main()` / `read_input()` / `read_units()` | Travel, unit, and location prompts |
| `geocoding()` / `routing()` | F4 response validation and F5 mocked API tests |
| `requirements.txt` / `.env.example` | Dependency and configuration setup |
| `docs/project-draft.md` | Draft project write-up for the shared Draft Document |
| `tests/test_graphhopper_cli.py` | Offline acceptance tests for implemented CLI enhancements |

## Team task checklist

Checked items indicate starter work prepared here. Unchecked items require team contribution. Owners and estimates are **unassigned/TBD**; the suggested work areas below are not real team assignments. P1 = first sprint, P2 = after the core enhancements, P3 = optional/deferred.

Status updated October 13, 2026: starter preparation, offline verification, GitHub publication, and task-issue creation are complete. Issue links are included below. F1 unit selection and F2 clearer output are complete; remaining features and live API authentication are pending. Owners and estimates still need team agreement; focused acceptance tests do not complete F5's comprehensive API test-suite task.

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
- [ ] Record team name, members, scrum lead, recorder, and feature owners. [Issue #3](https://github.com/FlimsyOwl12/DEVASC-Project/issues/3)
- [ ] Set a meeting schedule, communication channel, and sprint deadline. [Issue #4](https://github.com/FlimsyOwl12/DEVASC-Project/issues/4)
- [ ] Add an effort estimate and dependency to each selected task; document the budget/API allowance. [Issue #5](https://github.com/FlimsyOwl12/DEVASC-Project/issues/5)
- [x] Configure the local Git repository with `FlimsyOwl12/DEVASC-Project` as `origin`; use `Cocoasaur/devasc-graphhopper-api` as the lab reference.
- [x] Confirm the shared repository with the team and invite collaborators.
- [x] Create 19 GitHub issues for the unfinished README tasks (issues #2–#20).
- [ ] Assign issue owners and track status on the team's board. [Issue #6](https://github.com/FlimsyOwl12/DEVASC-Project/issues/6)

### Core enhancements — P1

- [x] **F1 — Unit selection** (suggested area: input/formatting): add a metric/imperial prompt; apply the selected unit to the total **and every instruction**. Acceptance: switching units changes labels and values consistently; 1,609.344 m displays as 1.0 mile, and `q` still exits from the new prompt. [Issue #7](https://github.com/FlimsyOwl12/DEVASC-Project/issues/7)
- [x] **F2 — Clearer terminal output** (suggested area: presentation): add an aligned summary/table and numbered directions; optionally add color with a readable plain-text option. Acceptance: origin, destination, profile, distance, duration, and each step are easy to identify; output works without color. [Issue #8](https://github.com/FlimsyOwl12/DEVASC-Project/issues/8)
- [ ] **F4 — Response validation** (suggested area: API integration): handle missing/invalid coordinate fields, malformed `hits`/`paths`, missing distance/time/instructions, and non-dictionary JSON. Acceptance: representative malformed responses produce a helpful message and return to the prompt without a traceback or printing credentials. [Issue #9](https://github.com/FlimsyOwl12/DEVASC-Project/issues/9)
- [ ] **F5 — Python unit tests** (suggested area: QA): create tests with `unittest` and mock HTTP calls. Cover successful geocoding/routing, no hits/no paths, 401/429/errors, timeouts, malformed JSON/schema, blank input/quit, and F1/F2 acceptance cases. Acceptance: tests run offline without a real key, including a check that routing is skipped after unsuccessful geocoding. [Issue #10](https://github.com/FlimsyOwl12/DEVASC-Project/issues/10)
- [ ] **F6 — Live verification** (suggested area: QA + API integration): use the team's own key to verify one reachable route for each available profile and a route that cannot be connected. Acceptance: record actual inputs/results and any account limitations, with no key visible in evidence. [Issue #11](https://github.com/FlimsyOwl12/DEVASC-Project/issues/11)

### Follow-up / deferred features

- [ ] **F3 — Summary or detailed output** — P2: let users choose a summary-only view or full directions. Acceptance: summary mode suppresses instructions while keeping route totals. [Issue #12](https://github.com/FlimsyOwl12/DEVASC-Project/issues/12)
- [ ] **F7 — Export route results** — P3: agree on TXT/JSON/CSV, then save a route summary without secrets. Acceptance: exported values match the displayed route and existing files are handled deliberately. [Issue #13](https://github.com/FlimsyOwl12/DEVASC-Project/issues/13)
- [ ] **F8 — Multiple geocoding candidates** — P3: let users choose between ambiguous places instead of always accepting the first hit. Acceptance: the selected candidate's coordinates are used in routing. [Issue #14](https://github.com/FlimsyOwl12/DEVASC-Project/issues/14)

### Integration, evidence, and submission

- [ ] Review and merge each feature through a pull request, then update this checklist. [Issue #16](https://github.com/FlimsyOwl12/DEVASC-Project/issues/16)
- [ ] Record the final application's features, limitations, and test results. [Issue #17](https://github.com/FlimsyOwl12/DEVASC-Project/issues/17)
- [ ] Prepare the Activity 3 overview presentation and application demonstration. [Issue #18](https://github.com/FlimsyOwl12/DEVASC-Project/issues/18)
- [ ] Complete the supplied team reflection questions and activity rubric using actual team experience. [Issue #19](https://github.com/FlimsyOwl12/DEVASC-Project/issues/19)
- [ ] Review the backlog and explicitly defer unfinished features. [Issue #20](https://github.com/FlimsyOwl12/DEVASC-Project/issues/20)
- [ ] **F9 — Automated checks (Activity 4)** — P2: build a pipeline using Jenkins or an instructor-approved CI tool after F5 exists. Acceptance: a commit triggers offline tests and reports failures; include the test cases, pipeline explanation, GitHub changes, presentation, and Activity 4 rubric. [Issue #15](https://github.com/FlimsyOwl12/DEVASC-Project/issues/15)

## Working together

Agree on owners before coding. Use one branch per task (for example, `codex/feature-units`), describe the acceptance criteria in the issue/PR, and ask another member to review it. F1 and F2 both touch `display_route()`; coordinate their sequence to reduce conflicts. F5 follows the behavior agreed for each enhancement; F9 depends on F5. Keep optional F3/F7/F8 in the backlog until the core sprint is complete.

Starter verification: both scripts passed syntax checks and nine temporary offline smoke checks passed using mocked HTTP responses. These covered missing-key startup, geocoding parameters, empty hits skipping routing, route coordinates/profile, HTTP errors and key redaction, a full mocked route and formatting, quit/blank input, timeout/invalid JSON recovery, and the initial geocoding script. These checks were run during preparation; they are not a committed test suite.

Configuration fix verified: six additional offline checks covered `.env` loading from another working directory, exported-key precedence, and missing configuration for both scripts. Startup with the project's saved `.env` key now reaches the travel-profile prompt; no network request was made during that startup check. This confirms key loading, not GraphHopper's acceptance of the key.

No live API run has been verified with a team key. The starter still assumes the normal GraphHopper field structure; comprehensive validation is F4. Focused enhancement acceptance tests are committed; broader API coverage and CI remain F5/F9. Run the offline tests with `.venv/bin/python -m unittest discover -s tests -v`. F1 tests cover unit conversion, units applied to every instruction, invalid/blank unit input, quitting the unit prompt without HTTP calls, and passing the selection through the application. F2 tests cover aligned summary fields, numbered directions, plain-text imperial output, and an empty instruction list.

## References

- Supplied `DEVASC Project.pdf`: Activity 3 Option 1 and Activity 4 deliverables.
- Supplied `8_Integrate a REST API in a Python Application - ILM_Arquesola.docx (1).pdf`: GraphHopper geocoding/routing lab.
- [Cocoasaur/devasc-graphhopper-api](https://github.com/Cocoasaur/devasc-graphhopper-api/tree/2289d4d): source lab scripts, adapted here.
- [GraphHopper API documentation](https://docs.graphhopper.com/): verify request parameters and account-supported profiles before the live demo.
- [Shared Draft Document](https://docs.google.com/document/d/1Q0knNhliyox7P0iDQgf0t-ZiOJ94uc_3q4Q7jl_njh8/edit): an adapted project plan was added to the DRAFT tab under Activities 3 and 4 on October 12, 2026; the local draft is in `docs/project-draft.md`.
