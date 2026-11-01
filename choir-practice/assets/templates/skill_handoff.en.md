# Skill session handoff – choir-practice vX.Y.Z
(file name always `session-handoff.md`, in the skill folder; git keeps the earlier versions; English, no piece-specific content)

**Date:** YYYY-MM-DD · **Skill version:** X.Y.Z

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
| | none (baseline) | | |

## 2. User requirements (new since the previous handoff)
| ID | Date | Requirement (short, near the user's wording) | Status (open / done in vX.Y.Z / rejected) | Implemented in |
|---|---|---|---|---|
| | | none yet | | |

## 3. Lessons (findings from a session that may help future scores)
| ID | Date | Finding | Cause | Decision (general rule / this piece only / dropped) | Version |
|---|---|---|---|---|---|
| | | none yet | | | |

## 4. Open points and ideas
| ID | Point | Type (test / idea / bug) | Status (open / done in vX.Y.Z / dropped) |
|---|---|---|---|
| | | | |

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
