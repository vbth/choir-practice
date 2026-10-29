#!/usr/bin/env python3
"""Prepare a release of the skill: bump VERSION, update CHANGELOG and the date of the README footers, build the .skill file.

Usage: release.py SKILL_DIR --out OUT_DIR [--repo REPO_DIR] --bump patch|minor|major [--note "text" ...]

Source of truth: VERSION (in SKILL_DIR). CHANGELOG.md, README.md and README.de.md live in REPO_DIR (default: SKILL_DIR)
and are copied into SKILL_DIR so that they travel inside the .skill.
Notes come from --note and from the bullets under "## Unreleased" in CHANGELOG.md.
Writes OUT_DIR/choir-practice.skill (constant name, so an upload replaces the skill) and OUT_DIR/RELEASE_NOTES.md,
and prints the git commands. It does not touch git and does not change the user's account skill.
"""
import argparse, datetime, pathlib, re, shutil, subprocess, sys, zipfile

ap = argparse.ArgumentParser()
ap.add_argument('skill_dir'); ap.add_argument('--out', required=True); ap.add_argument('--repo')
ap.add_argument('--bump', choices=['patch', 'minor', 'major'], default='patch')
ap.add_argument('--note', action='append', default=[])
a = ap.parse_args()
sk = pathlib.Path(a.skill_dir).resolve(); root = pathlib.Path(a.repo).resolve() if a.repo else sk
out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
name = sk.name

# third-party rights check (mandatory): no release while a component is missing from THIRD_PARTY_NOTICES.md
if subprocess.run([sys.executable, str(sk / 'scripts' / 'check_third_party.py')]).returncode:
    raise SystemExit('Third-party rights check failed: complete THIRD_PARTY_NOTICES.md first.')

vf = sk / 'VERSION'
cur = vf.read_text().strip() if vf.exists() else '0.0.0'
M, m, p = map(int, cur.split('.'))
M, m, p = {'major': (M + 1, 0, 0), 'minor': (M, m + 1, 0), 'patch': (M, m, p + 1)}[a.bump]
new = f'{M}.{m}.{p}'; today = datetime.date.today().isoformat()

# CHANGELOG: move the bullets under "## Unreleased" (plus --note) into a new dated section
cl = root / 'CHANGELOG.md'
text = cl.read_text(encoding='utf-8') if cl.exists() else '# Changelog\n\n## Unreleased\n'
mo = re.search(r'^## Unreleased[ \t]*\n(.*?)(?=^## |\Z)', text, re.S | re.M)
pending = [l.strip() for l in (mo.group(1).splitlines() if mo else []) if l.strip().startswith('- ')]
bullets = pending + [f'- {n}' for n in a.note]
if not bullets: raise SystemExit('No release notes: add bullets under "## Unreleased" or pass --note.')
section = f'## {new} – {today}\n' + '\n'.join(bullets) + '\n'
if mo: text = text[:mo.start()] + '## Unreleased\n\n' + section + '\n' + text[mo.end():]
else:
    head, _, rest = text.partition('\n')
    text = head + '\n\n## Unreleased\n\n' + section + '\n' + rest.lstrip('\n')
cl.write_text(text.rstrip('\n') + '\n', encoding='utf-8')

# footer date of the READMEs (the README title carries no version number) and version in the skill's own handoff
vf.write_text(new + '\n')
for fn in ('README.md', 'README.de.md'):
    f = root / fn
    if f.exists():
        t = f.read_text(encoding='utf-8')
        d = datetime.date.fromisoformat(today); human = d.strftime('%d.%m.%Y') if fn.endswith('.de.md') else today
        t = re.sub(r'((?:KI-generiert, Urheber- und Lizenzrechte ohne Gewähr|AI-generated, no guarantee for copyright and licence rights), )[\d.-]+\n*\Z', rf'\g<1>{human}\n\n', t)   # date of the footer line = release date
        f.write_text(t, encoding='utf-8')
h = sk / 'session-handoff.md'
if h.exists():
    t = h.read_text(encoding='utf-8')
    t = re.sub(r'(# Skill session handoff – [\w-]+ )v[\d.]+', rf'\g<1>v{new}', t, count=1)
    t = re.sub(r'\*\*Date:\*\* [\d-]+ · \*\*Skill version:\*\* [\d.]+', f'**Date:** {today} · **Skill version:** {new}', t, count=1)
    h.write_text(t, encoding='utf-8')
if root != sk:
    for fn in ('CHANGELOG.md', 'LICENSE'):
        if (root / fn).exists(): shutil.copy(root / fn, sk / fn)
    for fn in ('README.md', 'README.de.md'):
        # the repo header image (docs/img/...) does not exist inside the skill: drop it, including the blank line after it
        if (root / fn).exists():
            t = re.sub(r'^<p[^>]*>[^\n]*src(?:set)?="docs/img/[^\n]*\n\n?', '', (root / fn).read_text(encoding='utf-8'), flags=re.M)
            (sk / fn).write_text(t, encoding='utf-8')

target = out / f'{name}.skill'
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(sk.rglob('*')):
        if f.is_file() and '__pycache__' not in f.parts:
            z.write(f, pathlib.Path(name) / f.relative_to(sk))
(out / 'RELEASE_NOTES.md').write_text('\n'.join(bullets) + '\n', encoding='utf-8')
print(f'version {cur} -> {new}\n{target}\n{out / "RELEASE_NOTES.md"}')
print(f'\ngit add -A\ngit commit -m "Release {new}"\ngit tag v{new}\ngit push origin main --tags')
