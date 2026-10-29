# Skill session handoff – choir-practice v1.0.0
(file name always `session-handoff.md`, in the skill folder; git keeps the earlier versions; English, no piece-specific content)

**Date:** 2026-10-28 · **Skill version:** 1.0.0

## 0. Instructions for the next chat
Unpack the .skill, run `scripts/setup.sh`, read this file. The skill in the user's account is not updated automatically. Do not start open items unprompted.

## Logging rules (apply to every handoff)
- One handoff per skill version; the file `session-handoff.md` is rewritten for each release, git history keeps the earlier ones.
- Log only what is new since the previous release. Do not copy earlier rows.
- One row per item, short, English. Never delete a row inside a handoff; change its status instead.
- IDs run per handoff (C1, R1, L1, O1 …) and are not reused.

## 1. Changes (what changed in this version)
| ID | Change | Reason | Files |
|---|---|---|---|
| C1 | Licence stays PolyForm Noncommercial; no more request for a commercial licence by issue; LICENSE also in the repo root | owner's decision: keep PolyForm, but no pointer to a commercial licence by issue | LICENSE, READMEs, site, release.py, checks.yml |
| C2 | One footer everywhere: `[EU label] <ai_note_info>, <date>`, 8 pt on every PDF, label sized to the cap height of the text; Markdown footer with the label linked from the repo | one look on PDF, README and website | common.py (FOOT_PT, ICON_H, ICON_BASE, md_footer), render_score.py, make_overview.py, check_templates.py, SKILL.md |
| C3 | Score cover: title 30 pt with tracking −0.015 em, value column 22 mm | title too large, gap after the labels too wide | render_score.py (make_cover), SKILL.md |
| C4 | Website: quote as banner caption, full-width hero, new headphone drawing, switches below it, footer reversed, 4 steps in "Get started", previews as PNG from a script, render test in the repo, player one column up to 900 px | owner's review of the site | site/build_site.py, site/make_previews.py, site/render_test.js, site/README.md |

## 2. User requirements (new since the previous handoff)
| ID | Date | Requirement (short, near the user's wording) | Status (open / done in v1.0.0 / rejected) | Implemented in |
|---|---|---|---|---|
| R1 | 2026-10-27 | Licence PolyForm Noncommercial without a commercial-licence-by-issue pointer, link to the LICENSE in the repo | done (unreleased) | C1 |
| R2 | 2026-10-27 | Footer "[AI icon] KI-generiert, ohne Gewähr, [Datum]" in every PDF and every Markdown (label linked from the repo), same font size in all footers, text capitals as high as the capitals in the label | done (unreleased) | C2 |
| R3 | 2026-10-27 | Rules for the footers written into the scripts and the template checks | done (unreleased) | C2 |
| R4 | 2026-10-27 | Quote as caption below the header image, three lines, quotation marks, "– Claude" (website and README) | done (unreleased) | C4 |
| R5 | 2026-10-27 | Website: no grey text in the footer; shared steps read "Claude + Du" | done (unreleased) | C4 |

## 3. Lessons (findings from a session that may help future scores)
| ID | Date | Finding | Cause | Decision (general rule / this piece only / dropped) | Version |
|---|---|---|---|---|---|
| | | none yet | | | |

## 4. Open points and ideas
| ID | Point | Type (test / idea / bug) | Status (open / done in v1.0.0 / dropped) |
|---|---|---|---|
| O1 | Repo move to vbth/choir-practice-material: update common.MD_LABEL, GH/SITE in site/build_site.py and the README links | test | open |
| O2 | Website block order: example first, then package, practice, get started, workflow, rights, licence | idea | open |
| O3 | Headphone graphic: draw the melody voice at the height of the own voice (height reads as "front"); caption "Kopfhörer, aus deiner Sicht" | idea | open |
| O4 | Towel in `site/header/header-src.svg` (group `towel`): remove the black arc and the red dot (with its white glyph), then rebuild all assets for the website and the README (`site/header/build.sh` → `docs/img/header.png`, `site/make_previews.py`, `site/build_site.py`) | idea | open |
| O5 | Logo on the website and in both READMEs links to the URL of the main page (site root, `/en/` for English), not to an anchor | idea | done in PR 4 |
| O6 | Mobile website: gap between headline and header image equals the gap between menu and header image (72 px visible) | idea | done in PR 4 |
| O7 | Website statistics block: "2 Fassungen: normal und langsam" instead of "75 % Tempo der langsamen Fassung", because the slow tempo is adjustable | idea | done in PR 4 |
| O8 | Website section 01 workflow: call to action "Unten einen Schritt anklicken, hier erscheinen die Details." / "Click a step below, its details appear here." instead of "Einen Schritt anklicken." (the detail box sits above the step row, so "here:" would point at the wrong element) | idea | done in PR 4 |
| O9 | Website section 01 workflow, step 2: title "Stopp A" / "Stop A" without "Einrichtung" / "Setup" | idea | done in PR 4 |
| O10 | Website section 01 workflow texts (dictated): step 2 "Angaben über Rechte und Verwendungszweck.", step 3 "Als PDF oder Foto.", step 10 check "Alle Inhalte vorhanden?", step 11 "Die Entscheidung über die Umsetzung liegt beim Nutzer.", step 12 "ZIP herunterladen und die Audiodateien der einzelnen Stimmen an den Chor weitergeben." (dictation read "Tipp" as "ZIP"); English equivalents | idea | done in PR 4 |
| O11 | Website workflow: review the "Check at the end" lines of steps 6 to 10 as a whole. Step 6 "Fehlerfrei?" and step 7 "Alles sauber?" overlap; steps 8 and 9 are unclear from the dictation (keep or reword?) | idea | open |
| O12 | Website section 02 intro: "Jeweils eine Stimme liegt in der Mitte" / "In each mix one voice sits in the middle" instead of "Die eigene Stimme ..." (the captions under the graphic still say "eigene Stimme") | idea | done in PR 4 |
| O13 | Website section 02: whole headphone block incl. controls centred; caption under the graphic always centred | idea | done in PR 4 |
| O14 | Website section 02: a click on a voice always restarts the recording from the beginning (stage, sound and tempo still keep the position) | idea | done in PR 4 |
| O15 | Website section 02: sound waves at both ear cups while a recording plays, hidden when paused (static under reduced motion) | idea | done in PR 4 |
| O16 | Website section 02: letters in the circles centred on the cap height (also on phones) and larger on wide screens | idea | done in PR 4 |
| O17 | Website section 02: tutti circles further apart horizontally (spread factor 270 instead of 190) | idea | done in PR 4 |
| O18 | Website section 03: example ZIP button without the size ("32 MB"), so it stays narrow | idea | done in PR 4 |
| O19 | Website section 04, rights: "Die Angaben des Nutzers vermerkt er in der README" instead of "Die Antwort vermerkt er" | idea | done in PR 4 |
| O20 | Website section 04, rights: replace "Lizenzen für Noten müssen eingehalten werden." Three alternatives were offered, the owner has not chosen | idea | open |
| O21 | Website section 06 licence: sentence that third-party licences must be observed, linked to `choir-practice/THIRD_PARTY_NOTICES.md` in the repository (assumed: the dictated "kommerzielle" meant "nichtkommerzielle"; the licence stays PolyForm Noncommercial) | idea | done in PR 4 |
| O22 | Labelling: label "AI" without GENERATED / MODIFIED in every PDF footer, every Markdown footer and the example previews (`assets/eu-ai-basic.svg`, the official round icon `LABEL_AI_black.svg` supplied by the owner; `common.py`, `build_site.py`, READMEs, SKILL.md, notices). Album art, header image and website footer keep "AI GENERATED"; the texts stay. The released example ZIPs still carry the old footers until a new release | idea | done in PR 4 |
| O23 | Disclaimer wording fixed everywhere (language packs `ai_note`, `ai_note_info`, `ai_meta`, SKILL.md, READMEs, website footer, `release.py`): de "KI-generiert, Urheber- und Lizenzrechte beachten, ohne Gewähr", en "AI-generated, observe copyright and licence rights, no warranty" (English wording proposed by Claude, owner to confirm). Not changed: the parenthesis in the example docs (`site/example/docs.*.json`), which is running text | idea | done in PR 4, English wording to confirm |
| O24 | Question whether `LICENSE` should be `LICENSE.md` (the PolyForm text is Markdown, GitHub shows a file without extension as plain text); touches release.py, checks.yml, READMEs, site | idea | open |
| O25 | Markdown files in the package: the grey inline-code references to files and folders should also be links to the file in the package or the repository | idea | open |
| O26 | Rights review together with the owner (later): walk through every right and every third-party component (fonts, EU label, Verovio, Leland, soundfonts, Python and apt packages, website assets), decide per item where use must be documented (package, README, website, `THIRD_PARTY_NOTICES.md`) and whether publicly; decide whether `THIRD_PARTY_NOTICES.md` needs a clearer name; confirm that no third-party right is infringed. No legal advice, a technical check against the licence texts | idea | open, scheduled by the owner for later |
| O27 | Website: menu entry and section 06 heading "Lizenzen" / "Licences" (plural) | idea | done in PR 4 |
| O28 | Website footer: GitHub icon with "vbth, privates Projekt" is one link to the repository (before: profile) | idea | done in PR 4 |
| O29 | Third-party rights check built into installation and development: `scripts/check_third_party.py` (bundled vs repository only vs run time against `THIRD_PARTY_NOTICES.md`), called by `setup.sh`, SKILL.md first step, `release.py` (stops on failure), CI, mandatory section 5 in the skill handoff template | idea | done in PR 4 |
| O30 | `THIRD_PARTY_NOTICES.md` made complete: added poppler-utils, DejaVu fonts and the repository label copies, new section "Repository only", removed OpenCV (not used); five entries still marked "to check" | idea | done in PR 4, "to check" entries open (see O26) |
| O31 | EU label set complete: all 12 official SVG (AI, AI GENERATED, AI MODIFIED; black, white, 50 % transparent) supplied by the owner and bundled unchanged in `assets/eu-labels/`; dark-mode copies for the website and Markdown footers now come from the official white files instead of a script recolouring | test | done in PR 4 |
| O33 | Dates: ISO (YYYY-MM-DD) in every language, German too, in every PDF and Markdown footer (`common.human_date`, `release.py`, `check_templates.py`, SKILL.md, README footers); website footer shows only the year of the last release (from the `Date` line of this handoff, which `release.py` rewrites), so it changes with every release | idea | done in PR 4 |
| O34 | One label everywhere: the round "AI" icon in every PDF and Markdown footer (also the repo READMEs), the album art (`make_cover.py`, height 14 % of the cover, black circle must stay legible) and the website footer; the website player covers are rebuilt by `site/make_player_covers.py`. "AI GENERATED" remains only in the header image of the website (`assets/eu-ai-generated.svg`); the `docs/img/ai-generated*.svg` copies are gone. Written into SKILL.md (album art rule, label rule) and the notices | idea | done in PR 4 |
| O35 | Website footer wording "privates Projekt": decide whether to add "nichtkommerziell" (matches the PolyForm Noncommercial licence) and check, as part of the rights review O26, whether the site needs an imprint (Impressum) and a privacy notice (hosted on GitHub Pages); a self-label alone does not settle that, no legal advice | idea | open |
| O36 | Website footer, second line: `[GitHub icon] choir-practice Skill` as one link to the repo, then "privates Experiment: ein agentischer Workflow für Claude, entwickelt mit Claude Code." (en "private experiment: an agentic workflow for Claude, developed with Claude Code."); the link "vbth, privates Projekt" on the right is gone. Owner chose variant 2 of three; does not settle the imprint question (O35) | idea | done in PR 4 |
| O37 | The project documents a private experiment: no call to install and no how-to instructions. Website: hero button "Skill installieren", menu entry and section 05 "Loslegen" (steps, "Skill herunterladen" button) and `downloadUrl` in the JSON-LD removed, Licences is now section 05, footer note (see O39). READMEs (both languages and the copies in the skill folder): section 3 "Usage" removed, sections renumbered (10 sections), sentence on downloading the `.skill` from Releases removed. Not changed: hero lead ("praktischer Claude-Skill, der viel Zeit spart"), README intro, the served file `docs/choir-practice.skill`, release workflow | idea | done in PR 4 |
| O38 | Decide on the rest of the "experiment" framing: reword the hero lead and the README intro; remove the unlinked `docs/choir-practice.skill` (and its build step) from the site; keep or drop the GitHub release asset `.skill` | idea | open |
| O39 | Framing as documentation: footer second line `[GitHub icon, link to the repo, no repo name] choir-practice – KI-Musik-Workflow/-Skill entwickelt für/mit Claude Code` (en: "Docs – agentic AI music workflow/skill developed for/with Claude Code"; owner's short form of 2026-10-29, the longer wording stays in the website lead and the README intro); the phrase "Dokumentation eines privaten Code-Experiments" is gone; website lead and meta description and the README intro (both languages, with the copies in the skill folder) say the same instead of "practical Claude skill that saves you time"; the install parts of O37 stay removed on this branch (the live site shows them until PR 4 is merged, it publishes from `main`) | idea | done in PR 4, English wording to confirm |
| O40 | Entry text (website lead and meta description, README intro in both languages and the skill-folder copies) now reads "Dokumentation eines privaten Code-Experiments zur Erstellung und Weiterentwicklung eines agentischen KI-Musik-Workflows und Claude Skills." followed by the choir example (en: "Documentation of a private code experiment on building and developing an agentic AI music workflow and Claude skills.", English wording by Claude, owner to confirm); the footer keeps the short form of O39 | idea | done, English wording to confirm |

## 5. Third-party rights check (mandatory for every release)
Run `python3 scripts/check_third_party.py` and record the result. It lists what the skill bundles, what lives only in the repository and what is installed at run time, and fails when a component is missing from `THIRD_PARTY_NOTICES.md`. A release is not prepared while it fails (`release.py` stops).
| ID | Check | Result | Action |
|---|---|---|---|
| T1 | Output of `check_third_party.py` (date, `ok` or missing components) | | |
| T2 | New or changed components since the previous release (bundled, repository only, run time: pip, apt, fonts, images) and their licences | none / list | |
| T3 | Entries marked "to check" in `THIRD_PARTY_NOTICES.md`: resolved or still open | | |
| T4 | EU label SVGs: complete set in the bundle, terms of the official page unchanged | | |
| T5 | Public documentation (README, website, `THIRD_PARTY_NOTICES.md`) matches the notices | | |

## 6. How to continue
Apply open points on request, add rows to sections 1 to 5 of the next handoff only, then release with `scripts/release.py` (see README section 10).
