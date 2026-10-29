# Changelog

All notable changes to the skill. Newest first. Versions follow [SemVer](https://semver.org/); every release is a git tag `vX.Y.Z` with a GitHub release that carries the `.skill` file.

## Unreleased

## 1.0.0 – 2026-10-29
- Documents named in the READMEs (`SKILL.md`, workflows, `site/` files and others) are now links instead of plain code text
- Footer of every PDF and Markdown file: "KI-generiert. Urheber- und Lizenzrechte ohne Gewähr." with the date (en: "AI-generated. Copyright and licence rights without warranty."), same wording in the metadata of PDF, MP3, MusicXML and MIDI
- New project line one line above the footer, in every PDF and Markdown file: GitHub mark (linked to the repository) and "choir-practice – KI-Musik-Workflow und -Skill für Claude Code."
- README of every package starts with the statement that the skill is a private code experiment and a proof of concept only
- Rights check for third-party components (`check_third_party.py`) in setup, release and CI; `THIRD_PARTY_NOTICES.md` completed (bundled, repository-only and run-time components, GitHub mark)
- `LICENSE` renamed to `LICENSE.md`
