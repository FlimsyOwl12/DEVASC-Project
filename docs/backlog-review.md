# Backlog and integration review — October 18, 2026

Baseline: merged `main` commit `9238164466fa18c5b9bcec394125f6c2514cfcef`. This review records repository evidence and a proposed order for the remaining course work. It does not record an instructor approval or a team meeting that has not occurred.

## Completed application work

| Task | Evidence | Result |
| --- | --- | --- |
| F1 — metric/imperial units | [PR #21](https://github.com/FlimsyOwl12/DEVASC-Project/pull/21) | Merged |
| F2 — clearer output | [PR #22](https://github.com/FlimsyOwl12/DEVASC-Project/pull/22) | Merged |
| F3 — summary/detailed view | [PR #24](https://github.com/FlimsyOwl12/DEVASC-Project/pull/24) | Merged |
| F4 — response validation | [PR #23](https://github.com/FlimsyOwl12/DEVASC-Project/pull/23) | Merged |
| F5 — permanent offline tests | Commit `efc40b6`, expanded to 69 tests | Implemented; [issue #10](https://github.com/FlimsyOwl12/DEVASC-Project/issues/10) still needs status reconciliation |
| F6 — live verification | [Recorded October 14 results](live-verification.md) | Car/bike/foot and disconnected route recorded; [issue #11](https://github.com/FlimsyOwl12/DEVASC-Project/issues/11) still needs status reconciliation |
| F7/F8 — exports and location selection | [PR #27](https://github.com/FlimsyOwl12/DEVASC-Project/pull/27) | Merged October 18; issues #13/#14 closed |
| Main menu and session history | PR #27 | Last 10 successful routes can be viewed/exported without HTTP |
| F9 — pipeline implementation | [PR #26](https://github.com/FlimsyOwl12/DEVASC-Project/pull/26) | GitHub Actions verified; Jenkins execution is still required |

F3, F7, and F8 are no longer deferred. No unimplemented F1–F8 feature is being carried into the next iteration. Future application enhancements should become new team-approved issues, rather than reusing completed task IDs.

## Integration and cleanup evidence

PR #27 merged as `9238164`. GitHub records an `LGTM!` comment by `FlimsyOwl12` at 19:05:12 Asia/Manila on October 18; its review state is `COMMENTED`, not a formal `APPROVED` review. This is recorded without assigning an unverified peer reviewer. The team should confirm any additional reviews performed outside GitHub.

Both Python 3.10 and 3.14 passed 69 tests on the [merged-main run](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/39121848255). Local offline verification passed the same 69 tests on October 18. The suite disables dotenv loading and real HTTP/socket connections. Earlier clean-archive verification also passed 69 tests from source.

The remote `F7---F8-Donezo` branch was deleted after merging. Local `main` was fast-forwarded to the merge; local `F7---F8-Donezo` and the already-merged `f9-automated-checks` branches were deleted. The separate local history-message preview was preserved; no published history was rewritten.

F7 and F8 intentionally share one branch and PR. Earlier features used their own PRs. This batch structure is an exception to the original one-feature-per-PR plan, not evidence of missing code.

## Required next iteration

| Order | Task | State / completion evidence needed |
| --- | --- | --- |
| 1 | P0 / #2 | Instructor confirmation of GraphHopper and project scope; no approval is recorded yet |
| 2 | F9 / #15 | The user confirmed that Jenkins is required. Configure the project on the team's Jenkins server, verify a push-triggered successful build and a controlled failed build, and retain links/reports. GitHub Actions does not replace this requirement. |
| 3 | Final documentation / #17 | Prepare a report covering features, setup, limitations, and actual test/live evidence; review and merge its documentation PR |
| 4 | Presentation / #18 | Prepare the slide deck and reproducible demo; confirm contribution statements, rehearse, and present |
| 5 | Reflection / #19 | Obtain the exact student questions/rubric; each member supplies their actual experience; the recorder assembles it for team review |
| 6 | Integration / #16 | Retain the merge/cleanup evidence and confirm the team's review record |
| 7 | Backlog review / #20 | Team ratifies this remaining scope, records actual owners/estimates, and updates the project board |

Do not assign fictitious owners, deadlines, budgets, meeting attendance, rubric scores, or personal lessons. Existing planning checkmarks in the README are previous team entries; issues #3–#6 remain open for reconciliation with their criteria. The DRAFT tab records team roles, but feature-owner/estimate fields still need team confirmation.

## Review checklist

- [x] Compare F1–F9 with merged code, PRs, and recorded evidence.
- [x] Record that F3/F7/F8 are implemented, rather than deferred.
- [x] Record completed merge and branch cleanup.
- [x] List mandatory Jenkins work and course deliverables separately from application features.
- [ ] Confirm instructor scope approval, feature owners, estimates, and budget with the team.
- [ ] Confirm peer-review evidence and reconcile old checked-but-open issues.
- [ ] Ratify the next iteration and update the team's project board.
