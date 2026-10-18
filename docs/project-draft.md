# DEVASC project draft — Option 1

Updated October 18, 2026. This local draft summarizes the application; the shared Google Doc remains the team's record for roles, meetings and final reflection answers.

We chose Option 1 and improved the GraphHopper Python lab. The app now supports metric/imperial units, clearer terminal output, summary or detailed directions, validated API replies, TXT/JSON/CSV exports, and selection between matching places. A menu and session history let us view or export the last ten successful routes without making more API requests.

F1–F8 are implemented. F7/F8 were merged through PR #27 on October 18. The current suite has 69 offline tests. Both Python 3.10 and 3.14 passed on the merged-main GitHub Actions run. The recorded October 14 live checks cover car, bike, foot and a disconnected route; these results are kept separately from the mocked tests.

The team is PalpakGPT. The shared DRAFT tab records Justine Smith Rendaje as scrum leader and Wilhelm Ramesh Dimacisil as recorder. John Jessienel Arquesola and Janwel Gilo are listed as Prompt Engineers. Each person still needs to confirm their actual feature contribution and personal reflection. We should not infer sole authorship from who uploaded a file.

Jenkins is required by our instructor, as confirmed on October 18. We configured Jenkins and recorded manual success, automatic SCM triggering, an intentional failure and automatic recovery. After PRs #30/#28 merged, the original job was switched to main and build #5 passed all 69 tests with its report archived. The demo job is disabled and retains the failure/recovery evidence. GitHub Actions is supplementary; instructor acceptance of local SCM polling remains pending. GraphHopper/provider scope approval, feature owners, estimates, budget and the final team assessment also need confirmation where no actual record is available.

For current setup, features, limitations and evidence, use [the application report](final-report.md) and [test results](test-results.md). The full backlog and remaining course work stay in README.md. PRs #28/#30 are merged; report PR #29 and presentation PR #31 remain for review. Handoff PR #32 reconciles the shared checklist and final-main evidence. The team's exact rubric/reflection answers and actual presentation delivery remain outstanding. Activity 5 is a separate NETCONF/YANG and WebEx Teams proposal in the shared DRAFT; device changes and room messages have not been verified or implemented in this routing repository.

Shared document: https://docs.google.com/document/d/1Q0knNhliyox7P0iDQgf0t-ZiOJ94uc_3q4Q7jl_njh8/edit . The DRAFT tab is updated in place without changing the instructor-guide tab.
