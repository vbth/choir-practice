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

## 5. How to continue
Apply open points on request, add rows to sections 1 to 4 of the next handoff only, then release with `scripts/release.py` (see README section 11).
