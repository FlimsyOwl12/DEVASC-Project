# Team reflection and rubric evidence worksheet

Prepared October 18, 2026 for PalpakGPT. This is an evidence worksheet, **not the official student rubric** and not a completed personal reflection. The supplied instructor guide mentions reflection questions and rubrics but does not contain their exact prompts/scoring criteria. Insert the actual student questions/rubric before final submission.

## Recorded team roles

| Member | Role recorded in the shared DRAFT | Actual contribution / challenge / lesson |
| --- | --- | --- |
| Justine Smith Rendaje | Agile Scrum Leader | Awaiting member confirmation |
| Wilhelm Ramesh Dimacisil | Recorder | Awaiting member confirmation |
| John Jessienel Arquesola | Prompt Engineer | Awaiting member confirmation |
| Janwel Gilo | Prompt Engineer | Awaiting member confirmation |

These roles are copied from the DRAFT tab. They do not prove who originally wrote particular code. Git records the account that committed/uploaded a change; members should confirm actual authorship and collaboration before attributing individual work.

## Verified facts that can support the team's answers

- F1/F2/F4/F3 were integrated through PRs #21/#22/#23/#24; F9 pipeline code through PR #26; F7/F8 and menu/history through PR #27.
- The review found identical labels for different geocoding coordinates and nine tracked cache files. Follow-up commits added visible coordinates plus a regression test and removed the caches from Git tracking.
- The 69-test suite passed locally, from a clean archive, and on Python 3.10/3.14 CI. Tests use dummy keys and mocked HTTP.
- The October 14 live record includes car/bike/foot routes and a disconnected-route response, with no key/full request URL in the evidence.
- PR #27 has an `LGTM!` comment recorded as `COMMENTED` and was merged October 18. Do not turn that record into an invented formal approval or meeting attendance record.
- Required Jenkins execution is observed: original #1/#2 passed 69 tests, Demo #1 failed one intentional test, Demo #2 recovered automatically with 69 passing, and final-main #5 at c6d34d5 passed 69 tests with its report archived. The original job targets main and the demo job is disabled. These are technical facts; each member still supplies their own challenge/lesson. Instructor acceptance of polling remains pending.

## Member response form (complete individually)

Copy this form once for each member and answer in that person's own words. These are preparation prompts, not a substitute for the instructor's exact questions.

- Name:
- Work I actually did, with file/issue/commit/PR evidence:
- Work I reviewed or helped another member complete:
- A problem I personally encountered and what I tried:
- What changed after my work or review:
- A lesson I can explain from this experience:
- How we coordinated and one improvement for next time:
- Corrections to any contribution statement in the slides/report:
- Date I confirmed this response:

## Deliverable-to-evidence map

| Activity / requirement in the supplied guide | Available evidence | Remaining action |
| --- | --- | --- |
| Activity 3 application suitable for demo | Merged F1–F8; CLI/tests; offline replay | Team rehearses and demonstrates |
| Overview presentation and demo | Editable deck, PDF, notes, demo guide/script | Confirm individual claims and present |
| Team activities/reflection | This factual evidence list and member form | Obtain exact prompts; members answer and review |
| Completed Activity 3 rubric | No official rubric provided | Recorder obtains/fills actual rubric; members review |
| Backlog | README issues; integration/backlog review PR | Team confirms owners, estimates and next iteration |
| Activity 4 application changes on GitHub | PR #27 and merged feature history | Explain changes during presentation |
| Activity 4 test cases / pipeline explanation | Test files; GitHub runs; Jenkinsfile; manual/SCM success, Demo failure/recovery and final-main #5 | Present saved reports/screenshots; obtain instructor acceptance |
| Activity 4 presentation | Refreshed CI/Jenkins slides and speaker notes with actual build results | Confirm saved screenshots/reports, rehearse and present |
| Activity 4 rubric/reflection | This evidence map; pending official rubric | Complete from actual experience; no invented score |

## Official question/rubric transcription

Awaiting the exact student-facing questions and scoring criteria from the instructor. Preserve their wording when adding them. For each criterion, link relevant evidence, record the team's actual answer/self-assessment if requested, and leave instructor-only grading fields for the instructor.

## Completion checklist

- [x] Record confirmed roles and technical/review evidence.
- [x] Provide a response structure and deliverable-to-evidence map.
- [ ] Obtain and transcribe the official Activity 3/4 questions/rubrics.
- [ ] Each member supplies their own contribution, challenge and lesson.
- [ ] Resolve attribution or meeting-record discrepancies with the members involved.
- [ ] Recorder assembles the actual answers and requested rubric fields.
- [ ] All members review corrections and record their real review dates.

Sources: the existing shared DRAFT tab, supplied *DEVASC Project.pdf*, merged repository history, CI and `docs/live-verification.md`. No meeting date, attendance, personal experience, approval or grade is invented here.
