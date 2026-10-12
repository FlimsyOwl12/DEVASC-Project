# DEVASC project draft - Option 1

## Our project: Option 1 - GraphHopper REST API

We chose Option 1, which is improving the app from the Integrate a REST API in a Python Application lab. This is still our draft. The starter is ready, but the other features are left for our group to work on. Some of the team details is still blank for now.

## 1. What the app does and what we want to improve

The app asks where the user is starting from, where they want to go, and how they will travel. Python sends GET requests through HTTPS to GraphHopper. It reads the JSON reply and shows the distance, estimated travel time, and directions. The project guide mentions MapQuest, but our lab and the linked code use GraphHopper, so that is what we're using for this draft. We still need to confirm this with our instructor.

We want to let the user choose kilometers or miles and make the output easier to read. We also need to check the API replies, add Python unit tests, and use GitHub for sharing our work. The lab has car, bike, and foot options, but we need to check which ones our GraphHopper account supports.

## 2. Dividing the work

We still need to choose our scrum leader, recorder, and who will handle each task. One member could work on the units, another on the output, and the others on API checking and tests. We haven't assign the names yet, so these are just suggested tasks for now.

## 3. What is ready and what still needs work

The starter comes from the lab code in Cocoasaur/devasc-graphhopper-api, commit 2289d4d. It already had the basic routing. The adapted copy has API key setup, a requirements file, functions we can work on separately, request timeouts, and basic error messages. It also stops the route request if a location was not found. URLs containing the key are not printed. The remaining features still needs work from the other members.

P1 / F1 - Unit choice: add a choice between metric and imperial units. The choice should apply to the total distance and each direction step. For checking, 1,609.344 meters should show as 1.0 mile. The labels need to match, and q or quit should still close the app from the new prompt.

P1 / F2 - Better output: make a simple table or aligned summary, then number the directions. The starting point, destination, profile, distance, and time should be easy to find. If we use colors, the text should still be readable without them.

P1 / F4 - API reply checking: handle missing or invalid fields in the geocoding and routing reply. The app should show a useful message instead of crashing, and it should not show the API key.

P1 / F5 - Unit tests: add a permanent unittest suite with mocked HTTP calls. Cover normal routes, failed requests, empty results, invalid data, timeouts, input, quitting, and the new features. These tests should run without internet or a real API key.

P1 / F6 - Live checking: use our own key to try a reachable route for each supported profile and a route that cannot be connected. Save the actual results and any account limits we find, without showing the key.

For later: F3 can add a choice between a short summary and full directions (P2). F7 can export a route, and F8 can let the user choose between similar place names (P3). The full checklist and the expected results are in README.md.

The owners, time estimates, deadline, and budget are still TBD. We need to agree on these as a group before starting the sprint. We also haven't set a completion percentage or API allowance yet.

## 4. Working through GitHub

The lab reference is https://github.com/Cocoasaur/devasc-graphhopper-api . Our local origin points to FlimsyOwl12/DEVASC-Project, and the starter has separate commits ready. A push has not been confirmed in this chat. We still need to agree on the shared repo and add the members. Each feature can have its own issue and branch, then another member reviews the pull request. F1 and F2 both change display_route(), so those members should coordinate first.

## 5. Starting the app and checking it

The main file is labs/devnet-src/graphhopper/graphhopper_parse-json_7.py. The earlier geocoding exercise is graphhopper_parse-json_1.py. Follow README.md for setup and put GRAPHHOPPER_API_KEY in the project's .env file. Both scripts now load that file automatically. If the key is already exported in the terminal, that value is used first. Six extra offline checks passed for this setup, and the saved key now gets the app to its prompt. We still haven't confirmed whether GraphHopper accepts the key.

Both scripts passed syntax checks, and nine temporary offline checks passed using mocked API replies. A clean copy of the committed files also passed a mocked route after .env setup. These checks help us check the starter, but they are not the permanent test suite yet. Live routing, unit selection, better output, full response checking, tests, and CI/CD are still pending.

## 6. What we need for the presentation

Once the selected features are finished and checked, we need an app we can demo, a project overview presentation, the backlog, the activity rubric, and our reflection answers. We should show what the app can do, what still has limits, the test results, and each member's contribution.

## 7. Team reflection

We will answer the reflection questions based on our actual group work. Each member can add what they learned and the problems they ran into. Our team name, communication tools, meeting schedule, and final roles still need to be filled in together.

## References used

DEVASC Project.pdf, the Integrate a REST API in a Python Application lab, Cocoasaur/devasc-graphhopper-api, and the GraphHopper docs at https://docs.graphhopper.com/ .

## Plan for Activity 4

For Activity 4, we can continue the features left in the backlog and set up automated tests with Jenkins or another CI tool approved by our instructor. F9 needs the permanent tests from F5 first. After a commit, the pipeline should run the offline tests and report any failures.

We will need the code changes on GitHub, our test cases, an explanation of the pipeline, a presentation, and the Activity 4 rubric and reflection. The pipeline and deployment are not done yet. The owners, dates, and actual results still need to be added.

## Still to fill in together

- [ ] Team name, members, scrum leader, and recorder.
- [ ] Owners, time estimates, deadline, and budget for the chosen tasks.
- [ ] Meeting times, communication tools, and shared repository.
- [ ] Actual feature results, tests, and demo screenshots.
- [ ] Presentation, rubric, and our own reflection answers.

This wording was saved in the DRAFT tab of the [shared document](https://docs.google.com/document/d/1Q0knNhliyox7P0iDQgf0t-ZiOJ94uc_3q4Q7jl_njh8/edit) on October 12, 2026. README.md still has the full task tracker.
