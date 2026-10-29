# Changelog

All notable changes to the skill. Newest first. Versions follow [SemVer](https://semver.org/); every release is a git tag `vX.Y.Z` with a GitHub release that carries the `.skill` file.

## Unreleased
- Website: the red sound waves at the headphones now follow the level of the recording (Web Audio analyser): up to three arcs per side light up as it gets louder and fade in quiet passages and pauses. Without Web Audio, with reduced motion or if the audio context cannot start, the fixed animation stays as before
- Website: heading of section 04 now reads "Rechte & KI" / "Rights & AI" (like the menu entry); the menu collapses into the burger button only below 960 px instead of 1100 px, so a desktop window shows the full navigation
- Intro text of the website (lead, meta description) and of the READMEs: "Dokumentation eines agentischen KI-Musik-Workflows und -Skills entwickelt für und mit Claude Code als privates Code-Experiment." as its own paragraph, then "Es handelt sich ausschließlich um einen „Proof of Concept“. Aus Chornoten entsteht am Ende ein „KI-geprüftes“ ZIP, in dem sich für jede Stimme 10 Aufnahmen zum Üben befinden." (en equivalents); the README of the generated packages keeps its proof-of-concept statement
- Headline "Hören, üben, besser singen." (en: "Listen, practise, sing better.") instead of "… sicher singen." / "… sing with confidence." on the website, in the page title and in the READMEs
- Project line of every footer now reads "choir-practice – KI-Musik-Workflow/-Skill für Claude." (en: "choir-practice – AI music workflow/skill for Claude."), without "Code"; a word joiner keeps "-Skill" together in Markdown and on the website
- Website: headphone graphic wider, so the red sound waves keep more distance to the circles; menu entry "Rechte und KI" / "Rights and AI" now reads "Rechte & KI" / "Rights & AI", the second item of that section is headed "KI-Kennzeichnung" / "AI labelling"
- `THIRD_PARTY_NOTICES.md`: all entries checked against the licence texts (GitHub mark/Octicons, poppler-utils, DejaVu, FluidSynth, FFmpeg); none is marked "to check" any more
- Session handoff reset to the empty form, `TODO.md` removed
- Self-check in `make_layout.py`: the mandatory AI note ("Use at your own risk") no longer counts as addressing the reader in shared documents of the English package

## 1.0.0 – 2026-10-29
- Documents named in the READMEs (`SKILL.md`, workflows, `site/` files and others) are now links instead of plain code text
- Footer of every PDF and Markdown file: "KI-generiert. Urheber- und Lizenzrechte ohne Gewähr." with the date (en: "AI-generated. Copyright and licence rights without warranty."), same wording in the metadata of PDF, MP3, MusicXML and MIDI
- New project line one line above the footer, in every PDF and Markdown file: GitHub mark (linked to the repository) and "choir-practice – KI-Musik-Workflow und -Skill für Claude Code."
- README of every package starts with the statement that the skill is a private code experiment and a proof of concept only
- Rights check for third-party components (`check_third_party.py`) in setup, release and CI; `THIRD_PARTY_NOTICES.md` completed (bundled, repository-only and run-time components, GitHub mark)
- `LICENSE` renamed to `LICENSE.md`
