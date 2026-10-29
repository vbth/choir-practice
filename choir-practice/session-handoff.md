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

## 5. How to continue
Apply open points on request, add rows to sections 1 to 4 of the next handoff only, then release with `scripts/release.py` (see README section 11).
