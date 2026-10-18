# Required Jenkins setup — local course environment

The instructor requires Jenkins (confirmed by the user on October 18, 2026). GraphHopper supplies routes; Jenkins checks code. A working GraphHopper key does not create a Jenkins project, and a passing GitHub Actions workflow does not replace the Jenkins requirement.

The local environment is running and build #1 passed all 69 offline tests on October 18, 2026. Automatic commit detection and a controlled failure/recovery must be verified separately. Nothing here embeds a GraphHopper key, GitHub token, Jenkins password, or webhook secret.

## Start the local service

Install/start Docker with the Compose plugin, then from the repository root:

```bash
docker compose -f ops/jenkins/compose.yaml config
docker compose -f ops/jenkins/compose.yaml up --build -d
```

The image extends the official `jenkins/jenkins:lts-jdk21` image with Python/venv, Git, and the Pipeline/Git/GitHub plugins. The build downloads the current LTS image and plugins, so record the actual installed Jenkins/plugin versions in your evidence. It needs internet and may take several minutes. Application dependencies are installed in the job's own `.venv-ci`.

Open http://127.0.0.1:8080 on the same machine. If another service already uses port 8080, change only the host port in `compose.yaml`, for example `127.0.0.1:8081:8080`, and open that port instead.

Jenkins starts its normal setup wizard. Obtain its initial unlock value locally using the Jenkins instructions shown by the wizard, complete setup, and create your own administrator account. Do not paste any initial/admin password into chat, Git, screenshots, or the project document. Jenkins home and credentials live in a named Docker volume outside the repository. The service binds to loopback; it is not a public webhook endpoint.

This configuration uses the local controller to execute this team's trusted lab job for a course demonstration. A shared/production installation should use separately managed agents and its administrator's security configuration. No privileged container, Docker socket mount, or public listener is required by this package.

## Create the private-repository job

1. In Jenkins, create a new **Pipeline** job called `DEVASC-GraphHopper` (or record the name you choose).
2. Select **Pipeline script from SCM → Git**. Repository URL: `https://github.com/FlimsyOwl12/DEVASC-Project.git`.
3. For this private repository, add a Jenkins Git checkout credential with read access only to this repository, using your organization's normal credential method. Store it in Jenkins Credentials, not in the repository or Jenkinsfile. Do not use the GraphHopper key as a checkout credential.
4. Select `*/ci-jenkins-local-setup` while reviewing this setup branch, then change it to `*/main` after this PR merges. Script Path: `Jenkinsfile`. Keep lightweight checkout enabled when supported.
5. Run **Build Now** once. The Jenkinsfile must be loaded once before its triggers are active.

The job runs **Checkout → Install dependencies → Offline tests**. It archives `test-results/unittest.txt` even on test failure and then clears only its dedicated Jenkins workspace. Do not point the Jenkins job at your personal checkout directory.

## Trigger from a new commit without a public URL

The Jenkinsfile includes `pollSCM('H/5 * * * *')`. After the first job run, Jenkins checks Git for a new commit about every five minutes and builds only when it detects a change. The private checkout credential also supports this polling. Record a new commit SHA, the SCM polling log, the build's checked-out SHA and its result. Polling is automatic commit detection, not a GitHub webhook delivery.

The existing `githubPush()` trigger also remains available if the school provides a reachable Jenkins server. An administrator can configure the repository's GitHub push webhook to that server's `/github-webhook/` endpoint. A webhook cannot reach your computer's `127.0.0.1` URL. Do not claim webhook verification when the demonstration uses polling. Confirm with the instructor whether polling satisfies the required trigger demonstration or whether a school-hosted webhook is needed.

## Demonstrate success and a controlled failure

For a success run, select the setup branch (or main after merging), build, and save the build URL/number, exact commit, Python version, stage results and archived test report. The current application has 69 offline tests. The runner disables dotenv loading and blocks HTTP/socket connections, so Jenkins needs no GraphHopper key.

For a failure demonstration, use a separate disposable branch and a separate copy of this job pointed at it. Add one deliberately failing unittest, push the commit, let polling detect it, and record the failed stage/report. Remove that demonstration test and push a recovery commit, record the successful recovery, then remove the disposable branch/job after the team saves its evidence. Do not merge the deliberate failure into main or disable tests to obtain a green build.

## Evidence to fill using actual results

| Field | Required record |
| --- | --- |
| Jenkins URL / job name | Actual local or school-server URL and selected job |
| Jenkins / Python versions | Values observed in the running service/job |
| Successful build | URL/number, commit SHA, date/time, 69-test result and report |
| Failed demonstration | Disposable branch/SHA, failed build URL and diagnostic report |
| Recovery | Recovery SHA and successful build URL |
| Automatic trigger | Polling log/new-commit build, or actual webhook delivery/build |
| Instructor acceptance | Who confirmed the environment/trigger and when |

See the [recorded Jenkins evidence](jenkins-evidence.md) for observed results and remaining checks. A local URL is only accessible on the machine hosting Jenkins; use screenshots or archived reports for presentation when the audience cannot open it.

## Stop the service

```bash
docker compose -f ops/jenkins/compose.yaml stop
```

To remove containers/network while retaining the named volume and job history:

```bash
docker compose -f ops/jenkins/compose.yaml down
```

Keep the volume until required evidence is saved. Removing it would remove Jenkins users, credentials, jobs and build history.

Sources: [official Jenkins Docker image](https://github.com/jenkinsci/docker/blob/master/README.md), [Jenkins Docker installation](https://www.jenkins.io/doc/book/installing/docker/), and [Pipeline triggers](https://www.jenkins.io/doc/book/pipeline/syntax/#triggers).
