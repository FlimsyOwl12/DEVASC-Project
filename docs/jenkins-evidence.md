# Jenkins verification evidence

Record only observed runs. Local links below work on the computer hosting Jenkins.

## Successful manual build — October 18, 2026

| Field | Observed result |
| --- | --- |
| Service | Jenkins 2.580.1 at `http://127.0.0.1:8080/` |
| Job / build | [DEVASC-GraphHopper #1](http://127.0.0.1:8080/job/DEVASC-GraphHopper/1/) |
| Cause | Started by a user; this run does not prove automatic triggering |
| Branch | `ci-jenkins-local-setup` |
| Commit | `001efafcb0abef8356c37cb3c75f8f92768b9673` |
| Checkout | Private GitHub repository checkout succeeded |
| Stages | Checkout, Install dependencies, Offline tests succeeded |
| Test result | 69 tests in 0.656 seconds; `OK` |
| Report | `test-results/unittest.txt` archived |
| Final result | `SUCCESS`; dedicated workspace cleaned |

The console's Git-installation advisory did not stop checkout: the default Git executable worked. No GraphHopper key is needed by this offline pipeline. The exact Python runtime version was not printed by this build and is not inferred from downloaded wheels.

## Automatic commit detection

- [x] Confirm the job targets `*/ci-jenkins-local-setup`.
- [x] Confirm build #1 installed `pollSCM('H/5 * * * *')`.
- [x] Push the evidence update, then observe a new build started by an SCM change.
- [x] Record the build number, checked-out SHA, cause, result and archived report.

[Build #2](http://127.0.0.1:8080/job/DEVASC-GraphHopper/2/) started automatically on October 18 at 20:40:12 Asia/Manila after the documentation push. Its recorded cause is `hudson.triggers.SCMTrigger$SCMTriggerCause` (serialized as `hudson.triggers.SCMTrigger_-SCMTriggerCause` in build metadata), and it checked out `21c323049e2d1b8061fa34bae1410aa95573d83e`. All 69 tests passed in 0.469 seconds, `test-results/unittest.txt` was archived, and the final result was `SUCCESS`. No manual build was requested for this check.

Keep Jenkins running and do not use **Build Now** during this check. Polling checks about every five minutes; it is not a GitHub webhook delivery. Dependency installation still requires internet access.

## Controlled failure and recovery

The separate `DEVASC-GraphHopper-Demo` job ran the disposable branch. [Demo build #1](http://127.0.0.1:8080/job/DEVASC-GraphHopper-Demo/1/) checked out `bdd74ce8de5b74a4cbeb4dfcabc881f0e5daeab6`, ran 70 tests in 0.477 seconds and failed exactly one test: `JenkinsFailureDemonstration.test_intentional_failure_for_jenkins_evidence`. The diagnostic was `Intentional Jenkins demonstration failure; revert this demo commit to recover.` Jenkins archived `test-results/unittest.txt`, propagated exit status 1 and finished `FAILURE` as intended.

Recovery commit `ed43bdee6e3b38954dd456286f9554297e79a2f1` reverts only that demonstration test. All 69 original tests passed locally before this recovery was pushed. SCM polling automatically started [Demo build #2](http://127.0.0.1:8080/job/DEVASC-GraphHopper-Demo/2/) on October 18 at 21:05:07 Asia/Manila. It checked out that exact recovery commit, passed 69 tests in 0.492 seconds, archived `test-results/unittest.txt` and finished `SUCCESS`. Build metadata records an SCM trigger cause; no manual recovery build was requested.

| Demonstration | Commit | Tests | Result | Archived report |
| --- | --- | --- | --- | --- |
| Demo #1 — manual failure | `bdd74ce8de5b74a4cbeb4dfcabc881f0e5daeab6` | 70, exactly one intentional failure | FAILURE | Yes |
| Demo #2 — automatic recovery | `ed43bdee6e3b38954dd456286f9554297e79a2f1` | 69, all passing | SUCCESS | Yes |

The controlled Jenkins failure/recovery and automatic commit-detection checks are now verified. See the [demonstration instructions](jenkins-failure-demo.md); never merge the disposable demonstration commits into main. Keep the demo job and branch until the team has saved needed screenshots and reports. No cleanup or instructor acceptance is claimed here.

## Final verification after merging PRs #30 and #28

PR #30 merged into main as `5bb38bb3ba7ab2648411bbb58516b14f8a711359`; PR #28 followed as `c6d34d534dcfd39915cfa8adc3fc21ee1c54b474`. GitHub checks passed on [the merged-main run](https://github.com/FlimsyOwl12/DEVASC-Project/actions/runs/39132132376).

The original `DEVASC-GraphHopper` job now targets `*/main`. [Build #5](http://127.0.0.1:8080/job/DEVASC-GraphHopper/5/) checked out `c6d34d534dcfd39915cfa8adc3fc21ee1c54b474`, passed all 69 offline tests in 0.486 seconds, archived `test-results/unittest.txt` and finished `SUCCESS` on October 18. This verifies the merged main revision, in addition to the earlier feature-branch runs.

`DEVASC-GraphHopper-Demo` is disabled, with Demo #1/#2 and their archived reports retained. Screenshot/report download instructions were given; confirm the team's saved evidence before deleting a job or volume. Keep the disposable branch out of main. Remote merged-branch cleanup should follow publication of the stable documentation links in this handoff.

## Still required

- [x] Actual failed Jenkins build and diagnostic report (Demo #1).
- [x] Successful automatic recovery on the same demonstration job (Demo #2).
- [ ] Instructor acceptance of the local environment and SCM polling, or a reachable webhook demonstration if required.
- [ ] Team presentation, official rubric and each member's actual reflection.

Do not add passwords, tokens, unlock values, credential files or raw environment dumps to evidence. Save needed screenshots and reports before deleting the demonstration job or Jenkins volume.
