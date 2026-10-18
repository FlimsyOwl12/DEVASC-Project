# DEVASC presentation materials

- `devasc-overview.pptx`: editable Activity 3/4 slides.
- `devasc-overview.pdf`: presentation/printing copy.
- `speaker-notes.md`: suggested narration and evidence links.
- `build_deck.py`: source for the deck; edit its slide data and rebuild rather than treating exported slides as application source.

The deck clearly distinguishes implemented/verified work from the required but unverified Jenkins environment and the team's unconfirmed personal contributions. Rehearse and complete those sections before presenting. These materials do not claim that a class presentation has occurred.

To rebuild, use a separate tooling environment with `python-pptx` installed (generated with version 1.0.2):

```bash
python docs/presentation/build_deck.py
```

PowerPoint or LibreOffice can export the deck to PDF. Neither `python-pptx` nor LibreOffice is required to run the application or tests. See `../demo-guide.md` for the reproducible synthetic demo and `../team-reflection.md` for the pending member responses/official rubric.
