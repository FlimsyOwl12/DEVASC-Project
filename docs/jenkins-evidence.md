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

Use the [separate demonstration instructions](jenkins-failure-demo.md). A prepared failing commit is not evidence of a failed Jenkins build: the separate job must actually run it, archive its failure, and then run the recovery commit successfully. Do not merge the intentional failure into application branches or main.

## Still required

- [ ] Actual failed Jenkins build and diagnostic report.
- [ ] Successful recovery on the same demonstration job.
- [ ] Instructor acceptance of the local environment and SCM polling, or a reachable webhook demonstration if required.
- [ ] Team presentation, official rubric and each member's actual reflection.

Do not add passwords, tokens, unlock values, credential files or raw environment dumps to evidence. Save needed screenshots and reports before deleting the demonstration job or Jenkins volume.
