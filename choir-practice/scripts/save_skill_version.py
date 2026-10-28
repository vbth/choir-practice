#!/usr/bin/env python3
"""Bump the skill version, append a changelog entry and build a versioned .skill file.

Usage: save_skill_version.py SKILL_DIR --out OUT_DIR --bump patch|minor|major --note "text" [--note "text" ...] [--handoff FILE]
Prints the path of the created file. Does not change the user's account skill.
"""
import argparse, datetime, pathlib, zipfile

ap = argparse.ArgumentParser()
ap.add_argument('skill_dir'); ap.add_argument('--out', required=True)
ap.add_argument('--bump', choices=['patch', 'minor', 'major'], default='patch')
ap.add_argument('--note', action='append', default=[])
ap.add_argument('--handoff', help='handoff file; copied into the version folder as session-handoff.md')
a = ap.parse_args()
d = pathlib.Path(a.skill_dir).resolve(); out = pathlib.Path(a.out); out.mkdir(parents=True, exist_ok=True)
vf = d / 'VERSION'
cur = vf.read_text().strip() if vf.exists() else '1.0.0'
M, m, p = map(int, cur.split('.'))
M, m, p = {'major': (M + 1, 0, 0), 'minor': (M, m + 1, 0), 'patch': (M, m, p + 1)}[a.bump]
new = f'{M}.{m}.{p}'; today = datetime.date.today().isoformat()
vf.write_text(new + '\n')
cl = d / 'CHANGELOG.md'
old = cl.read_text() if cl.exists() else '# Changelog\n'
entry = f'\n## {new} – {today}\n' + ''.join(f'- {n}\n' for n in (a.note or ['(no note)']))
head, _, rest = old.partition('\n')
cl.write_text(head + '\n' + entry + rest)
name = d.name
if a.handoff:
    import shutil; shutil.copy(a.handoff, d / 'session-handoff.md')  # travels inside the .skill and into every package
# constant file name (so uploading replaces the skill); version and date live in the folder name
folder = out / f'{name}_v{new}_{today}'; folder.mkdir(parents=True, exist_ok=True)
target = folder / f'{name}.skill'
with zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED) as z:
    for f in sorted(d.rglob('*')):
        if f.is_file() and '__pycache__' not in f.parts:
            z.write(f, pathlib.Path(name) / f.relative_to(d))
import shutil
if a.handoff: shutil.copy(a.handoff, folder / 'session-handoff.md')
if (d / 'README.md').exists(): shutil.copy(d / 'README.md', folder / 'README.md')
print(target)
