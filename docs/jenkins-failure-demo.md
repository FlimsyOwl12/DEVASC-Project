# Controlled Jenkins failure and recovery

This demonstration uses a disposable `demo/jenkins-failure-recovery` branch. Its only intentional failure is `tests/test_jenkins_failure_demo.py`; the normal application and setup branch keep their passing tests. Do not open a merge PR for this demonstration branch. Red GitHub checks on its failing commit are expected and do not prove the Jenkins demonstration ran.

## Run the failure in a separate job

1. On the Jenkins dashboard, choose **New Item**, name it `DEVASC-GraphHopper-Demo`, and use **Copy from** `DEVASC-GraphHopper`.
2. In the copied job's **Configure → Pipeline**, keep the existing repository and read-only checkout credential. Change **Branch Specifier** to `*/demo/jenkins-failure-recovery`. Keep **Script Path** `Jenkinsfile`, then save.
3. Click **Build Now** once on this copied job. It must load its own Jenkinsfile before polling becomes active. Leave the original job pointed at the setup branch (or main after merging).
4. Expect **Offline tests** to fail with `Intentional Jenkins demonstration failure; revert this demo commit to recover.` The suite should run 70 tests with exactly one failure. The post-build step should still archive `test-results/unittest.txt`.
5. Save the copied job's build URL, exact commit, failed test and report. If checkout or dependencies fail first, fix that setup issue; it is not the intended test-failure evidence.

## Push recovery after observing the failed run

From a clean repository checkout, run:

```bash
git fetch origin
git switch demo/jenkins-failure-recovery
git pull --ff-only origin demo/jenkins-failure-recovery
git log -1 --oneline
```

Confirm the latest commit is **test: add isolated Jenkins failure demonstration** and changes only `tests/test_jenkins_failure_demo.py`. Then:

```bash
git revert --no-edit HEAD
git push origin demo/jenkins-failure-recovery
```

The revert removes only the intentional demonstration test. Do not use this command if another commit has become the branch tip; identify the original demonstration commit with `git log -- tests/test_jenkins_failure_demo.py` and revert that exact SHA instead.

Keep Jenkins running, wait about five minutes, and **do not click Build Now**. The copied job should detect the recovery commit through SCM polling and pass the original 69 tests. Record **Started by an SCM change**, the checked-out recovery SHA, `SUCCESS`, and the archived report. A manual recovery run verifies recovery but does not independently prove automatic commit detection.

## Record and clean up

Update `docs/jenkins-evidence.md` and the README checklist through their existing documentation PRs after the results are observed. Keep F9 open until all instructor and team requirements are satisfied.

After the team has saved the failure/recovery evidence, disable or delete only `DEVASC-GraphHopper-Demo`. Switch away from the disposable branch, delete it remotely, and remove the local branch only after confirming it contains no contribution to preserve. Its demonstration commits must never be merged into main. Do not delete the original job or Jenkins volume.
