# Changelog

All notable changes to the skill. Newest first. Versions follow [SemVer](https://semver.org/); every release is a git tag `vX.Y.Z` with a GitHub release that carries the `.skill` file.

## Unreleased
- `score.json` is validated against a strict pydantic schema (`scripts/score_schema.py`, pydantic 2.13.5 added to `requirements-stable.txt`): `build_score.py` checks its input and `musicxml_to_spec.py` its output before writing, with one clear line per problem (key, voice, bar, token); unknown keys such as a misspelled `key_fifth` are errors. CI validates the example scores
- Website recordings (`docs/audio/`, 42 MP3, 9.9 MB) are no longer in git: the new workflow `pages.yml` builds them with `site/make_web_audio.py` from the example ZIP of the release v1.0.0 and deploys `docs/` to GitHub Pages (repository setting: Pages source "GitHub Actions")
- IBM Plex Sans is a system dependency instead of six TTFs in git: `setup.sh` installs the apt package `fonts-ibm-plex` (or, without apt, the new release asset `choir-practice-fonts.zip` into `~/.fonts/ibm-plex`), `common.register_plex()` loads them from there; `release.yml` builds that zip and uploads it with the `.skill`. `assets/fonts/` keeps only the licence text; the `.skill` is about 1.4 MB smaller
- Website, section "Rechte & KI": the rights text now says the details are recorded "danach" in the README file and that processing and passing on depend on "dem Urheber- und Lizenzrecht, unter dem sie stehen" (en: "the copyright and licence law they are subject to")
- Website: menu entry, heading, link and download button say "Beispiel" / "Example" instead of "Beispiel-ZIP" / "Example ZIP"
- Website: the red sound waves at the headphones pulse with the rhythm of the recording (Web Audio analyser): every note onset switches the three arcs per side on, they go off again from the outside in, and the inner arc stays on while it sounds; always full red, no fading. Without Web Audio, with reduced motion or if the audio context cannot start, the fixed animation stays as before
- Website: heading of section 04 now reads "Rechte & KI" / "Rights & AI" (like the menu entry); the menu collapses into the burger button only below 960 px instead of 1100 px, so a desktop window shows the full navigation
- Intro text of the website (lead, meta description) and of the READMEs: "Dokumentation eines agentischen KI-Musik-Workflows und -Skills entwickelt für und mit Claude Code als privates Code-Experiment." as its own paragraph, then "Es handelt sich ausschließlich um einen „Proof of Concept“. Aus Chornoten entsteht am Ende ein „KI-geprüftes“ ZIP, in dem sich für jede Stimme 10 Aufnahmen zum Üben befinden." (en equivalents); the README of the generated packages keeps its proof-of-concept statement
- Headline "Alleine üben, besser hören, überall singen." (en: "Listen better, practise solo, sing anywhere.") instead of "… sicher singen." / "… sing with confidence." on the website, in the page title and in the READMEs
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
