# Activity 3/4 presentation and demo guide

Prepared October 18, 2026. The deck is in `docs/presentation/devasc-overview.pptx`; the PDF is a presentation copy. Speaker notes and rebuild instructions are alongside it. Review the contribution and pending-work slides with the team before presenting. Preparing materials is not evidence that the class presentation has already occurred.

## Rehearsal without an API key

Activate the project environment with its normal requirements installed, then:

```bash
python scripts/demo_offline.py
```

The script replays the real enhanced CLI using clearly labelled synthetic replies and a dummy key. Dotenv loading and network connections are blocked. It verifies the chosen coordinates, route totals, all three export formats, and that history requires no further mocked HTTP calls. It exits with an error if the expected behavior no longer matches the application.

To keep the three synthetic export files for inspection:

```bash
python scripts/demo_offline.py --keep-exports
```

It prints a newly created temporary directory. The files are not written into the repository. Default mode deletes its temporary exports when finished. Never describe these synthetic results as a newly verified live GraphHopper route.

## Demonstration sequence (about five minutes)

1. Introduce the customer problem: clear directions, familiar units, the intended location, and a reusable route.
2. Run the offline replay. Show two identical place labels with different coordinates; the replay chooses the second candidate.
3. Show the imperial total (**2.0 miles**) and duration (**00:10:00**) and two numbered **1.0-mile** steps. Explain that these are fixed synthetic values used to make the demonstration repeatable.
4. Show the JSON export. Then show viewing history and exporting the same stored route to TXT and CSV. Only three mocked HTTP calls are used for the original route; history adds none.
5. Run `python scripts/run_offline_tests.py` and show 69 passing tests. Open the actual merged-main GitHub run linked in the slides.
6. Describe the historical October 14 live checks separately using `docs/live-verification.md`. If the team chooses to demonstrate the live app, run the ordinary CLI with its local key and allow for account/quota/network limits; do not display `.env` or credentials. No new live result is claimed by this guide.
7. For Activity 4, show the Jenkinsfile stages and the required local setup PR/guide. Add real successful/failed Jenkins build and automatic-trigger evidence before claiming that the required Jenkins demonstration is complete. GitHub Actions evidence is supplementary.

## Questions to rehearse

- How does selecting another candidate change the routing coordinates?
- Why do tests mock HTTP instead of using a real key?
- How are existing export files handled?
- What happens when the API times out or returns invalid JSON?
- How long does history last, and how many routes can it retain?
- How do GitHub Actions, Jenkins, and GraphHopper serve different purposes?
- Which features and review changes can each member personally explain and confirm?

## Evidence and presentation checklist

- [x] Prepare an editable slide deck, PDF copy, speaker notes, and runnable offline demo.
- [x] Include feature rationale, tests, actual GitHub/live evidence, limitations and remaining work.
- [ ] Each member confirms their contribution statement and adds their actual challenge/lesson.
- [ ] Record required Jenkins success/failure/recovery and automatic-trigger evidence.
- [ ] Rehearse with all speakers and confirm the allocated class time.
- [ ] Present the application and record the actual presentation date.

The supplied instructor guide lists Activity 3/4 deliverables but does not include the full student presentation rubric. Compare these materials with the actual rubric when the instructor provides it; no score or approval is prefilled.
