# Changelog

All notable changes to the skill. Newest first. Versions follow [SemVer](https://semver.org/); every release is a git tag `vX.Y.Z` with a GitHub release that carries the `.skill` file.

## Unreleased

## 1.1.0 – 2026-10-29
- Footer of every PDF and Markdown file: "KI-generiert. Urheber- und Lizenzrechte beachten. Nutzung auf eigene Gefahr." with the date (en: "AI-generated. Observe copyright and licence rights. Use at your own risk."), same wording in the metadata of PDF, MP3, MusicXML and MIDI
- New project line one line above the footer, in every PDF and Markdown file: GitHub mark (linked to the repository) and "choir-practice – Proof of Concept: KI-Musik-Workflow/-Skill entwickelt für/von Claude Code. Nutzung auf eigene Gefahr."
- README of every package starts with the statement that the skill is a private code experiment and a proof of concept only
- Rights check for third-party components (`check_third_party.py`) in setup, release and CI; `THIRD_PARTY_NOTICES.md` completed (bundled, repository-only and run-time components, GitHub mark)
- `LICENSE` renamed to `LICENSE.md`
