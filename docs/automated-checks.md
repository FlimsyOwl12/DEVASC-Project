# F9 — Activity 4 automated checks

## What is implemented

The project guide directs the team to use Jenkins and explore other CI/CD tools. This repository provides both a Jenkins pipeline and a GitHub Actions workflow. They run the same offline test command. The user confirmed on October 18 that Jenkins is required; GitHub Actions is supplementary evidence and does not replace the required Jenkins execution. A [local setup package and guide](jenkins-local-setup.md) are provided.

GitHub Actions runs on every branch push, on pull requests targeting `main`, and manually from the Actions page after the workflow reaches the default branch. It tests Python 3.10 (the supported minimum) and Python 3.14. Each job checks out the source, installs `requirements.txt`, runs the tests, and uploads the text report even when a test fails. A failed test returns a nonzero exit code, which makes the job and PR check fail. Dependency/setup failures also fail the job, but may occur before a test report exists.

The workflow has read-only repository permissions, does not retain checkout credentials, and pins third-party actions to commit hashes. Reports are retained for 14 days. No GraphHopper secret needs to be added to GitHub or Jenkins. Dependency installation needs internet access; the Python test run blocks HTTP and socket connection calls. The manual F6 live-verification helper is outside test discovery and is never executed by either pipeline.

This is continuous integration for a terminal application. It validates code; it does not publish or deploy the application.

## Run the same checks locally

After installing the normal application requirements in your virtual environment:

```bash
python scripts/run_offline_tests.py
```

The command works from any directory. It clears `GRAPHHOPPER_API_KEY`, disables and mocks the dotenv loader before discovering tests, and blocks unmocked requests and socket connections. Existing tests can still supply dummy keys and mocked responses. Empty discovery and failed tests return exit status 1. The combined console/test output is saved to `test-results/unittest.txt`, which is ignored by Git along with `.venv-ci/`.

## Test plan and cases

| Test file | Cases covered |
| --- | --- |
| `tests/test_graphhopper_cli.py` | Metric/imperial totals and steps, prompts/quit, aligned summaries and numbered plain-text directions |
| `tests/test_graphhopper_output_modes.py` | Summary/detail selection, totals without directions, input validation, changing modes between routes |
| `tests/test_graphhopper_responses.py` | Invalid JSON/schema, coordinates and numeric ranges, missing fields, safe recovery and credential redaction |
| `tests/test_graphhopper_api.py` | Mocked request parameters/success, empty results, HTTP 401/429/500, timeout, missing key and skipped routing |
| `tests/test_graphhopper_exports.py` | TXT/JSON/CSV exports, metric/imperial consistency, direction preservation, path traversal protection, duplicate handling, and key redaction |
| `tests/test_graphhopper_geocoding_candidates.py` | Multiple candidate display (including coordinates for identical names), selected candidate coordinates in routing, invalid selections, retry/quit, and malformed candidate filtering |
| `tests/test_graphhopper_history_menu.py` | Main menu navigation, 10-route session history cap, failed route exclusion, and history view/export without network requests |
| `tests/test_offline_runner.py` | Subprocess checks for credential isolation, disabled dotenv loading, usable mocks, blocked connections, failed tests and empty discovery |

The suite contains 69 tests. The runner's regression tests create temporary miniature projects and deliberately exercise success/failure paths; expected fixture failures do not make the real suite fail. They never need a real API key or network request.

## View GitHub evidence

Open [Actions](https://github.com/FlimsyOwl12/DEVASC-Project/actions) and select **Offline Python tests**. A push runs the suite on both supported matrix versions; a PR also displays its checks. Expand **Run offline tests** to inspect named tests and failure tracebacks. Download `offline-tests-python-3.10` or `offline-tests-python-3.14` for the text report. A push to a branch with an open PR can produce separate push and PR runs; this is expected.

Record the actual PR URL, commit SHA, successful run URL, date, and test results in the team's Activity 4 evidence. To demonstrate failure handling, use a disposable team branch with a deliberately failing test and link its failed run, then remove the test/branch. Do not add a real key or run the live helper for this demonstration.

### Recorded GitHub evidence — October 15, 2026

[PR #26](https://github.com/FlimsyOwl12/DEVASC-Project/pull/26), branch `f9-automated-checks`, added the implementation in three scoped commits: `55b0237` (runner/tests), `4dea5cd` (pipelines), and `dc8e491` (documentation). At commit `dc8e491205902554cbf3377dcd8d27a732926a69`, both the [push run](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/38742491385) and [PR run](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/38742542685) succeeded. Each ran 42 tests on Python 3.10 and Python 3.14 and uploaded its test report. The workflow also passed actionlint v1.7.12 validation. Jenkins execution is still pending; no deployment or instructor approval is claimed.

## Set up Jenkins for the course

No configured Jenkins server/job was confirmed during implementation. Jenkins execution and an automatic new-commit build remain required. The Jenkinsfile supports both `githubPush()` for a reachable server and five-minute SCM polling for local Jenkins; see the local setup guide.

1. Use a dedicated Linux Jenkins agent with Python 3.10 or newer, `venv`, Git, and access to the dependency package index. The pipeline clears its Jenkins workspace before checkout and after the build; do not point it at a personal working folder.
2. Install the Pipeline, Git, and GitHub plugins. Create a **Pipeline** job, choose **Pipeline script from SCM**, select this Git repository, set the branch to `*/main` (or the feature branch for verification), and set **Script Path** to `Jenkinsfile`. For this private repository, configure a read-only checkout credential in Jenkins, never in the repository.
3. Run **Build Now** once to load the Jenkinsfile and its `githubPush()` trigger. Under the repository's webhook settings, configure a push webhook to `https://YOUR-JENKINS-HOST/github-webhook/` using the team's Jenkins/GitHub configuration. An administrator must configure and secure the reachable endpoint; do not commit webhook credentials.
4. Push a new commit and check the webhook delivery and triggered build. The stages are **Checkout → Install dependencies → Offline tests**. The test command's exit status determines success/failure; **Archived Artifacts** retains the report even when tests fail.
5. Record a successful build and a controlled failed build, including links and actual results. Confirm the instructor accepts the actual Jenkins environment and trigger demonstration; local SCM polling is not a verified GitHub webhook.

## Activity 4 handoff checklist

- [x] Supply a Jenkinsfile and GitHub Actions workflow triggered by repository changes.
- [x] Supply one offline command with failure exit codes and saved diagnostics.
- [x] Document the test cases, pipeline stages, and GitHub evidence collection.
- [ ] Confirm the demonstration tool/environment with the instructor.
- [x] Prepare a local Docker/Compose setup with Python/venv and the required Jenkins plugins.
- [ ] Configure the required Jenkins checkout/job and record successful/failed builds and automatic commit detection.
- [x] Record the PR and actual GitHub Actions results after publication (links above).
- [ ] Prepare the Activity 4 presentation with actual evidence.
- [ ] Complete the rubric and reflection using the team's own experience.

Suggested presentation order: the CLI enhancements; why HTTP is mocked; a successful test run; how a failed test appears; the Jenkins stages and GitHub changes; limitations and remaining work. The team must supply the presentation and reflection rather than treating this outline as completed assessment evidence.

Implementation references: [GitHub's Python workflow guide](https://docs.github.com/en/actions/tutorials/build-and-test-code/python), [GitHub Actions security guidance](https://docs.github.com/en/actions/reference/security/secure-use), and [Jenkins Declarative Pipeline syntax](https://www.jenkins.io/doc/book/pipeline/syntax/).
