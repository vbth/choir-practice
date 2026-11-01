#!/usr/bin/env python3
"""Version consistency check for the build and release process.

Usage: check_version.py [--file PATH.skill] [--tag vX.Y.Z]

VERSION (next to the scripts folder) is the single source of truth. The check fails (exit 1) when
  - VERSION is not a plain X.Y.Z,
  - the newest dated section of CHANGELOG.md or the version in session-handoff.md differs from VERSION,
  - --file: the file is not named <skill>.skill, a version in its folder name (<skill>_vX.Y.Z_DATE/) differs
    from VERSION, or the VERSION packed inside the archive differs,
  - --tag: the git tag is not v<VERSION>.
"""
import argparse, os, re, sys, zipfile

SKILL = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NAME = os.path.basename(SKILL)
SEMVER = r'\d+\.\d+\.\d+'

ap = argparse.ArgumentParser()
ap.add_argument('--file', help='built .skill file to check')
ap.add_argument('--tag', help='git tag of the release, e.g. v1.1.0')
a = ap.parse_args()

def read(name):
    p = os.path.join(SKILL, name)
    return open(p, encoding='utf-8').read() if os.path.exists(p) else ''

errors = []
version = read('VERSION').strip()
if not re.fullmatch(SEMVER, version):
    raise SystemExit(f'VERSION is not X.Y.Z: {version!r}')

# newest dated changelog section ("## Unreleased" has no number and is skipped)
m = re.search(rf'^## ({SEMVER}) ', read('CHANGELOG.md'), re.M)
if not m: errors.append('CHANGELOG.md has no dated version section')
elif m.group(1) != version: errors.append(f'CHANGELOG.md newest section is {m.group(1)}, VERSION is {version}')

m = re.search(rf'^# Skill session handoff – \S+ v({SEMVER})', read('session-handoff.md'), re.M)
if m and m.group(1) != version: errors.append(f'session-handoff.md says v{m.group(1)}, VERSION is {version}')

if a.tag and a.tag != f'v{version}': errors.append(f'tag {a.tag} does not match VERSION {version}')

if a.file:
    path = os.path.abspath(a.file)
    if os.path.basename(path) != f'{NAME}.skill': errors.append(f'file name is {os.path.basename(path)}, expected {NAME}.skill')
    # save_skill_version.py puts version and date into the folder name; release.py uses a constant name and no folder
    fm = re.fullmatch(rf'{re.escape(NAME)}_v({SEMVER})_\d{{4}}-\d\d-\d\d', os.path.basename(os.path.dirname(path)))
    if fm and fm.group(1) != version: errors.append(f'folder name carries {fm.group(1)}, VERSION is {version}')
    try:
        with zipfile.ZipFile(path) as z:
            packed = z.read(f'{NAME}/VERSION').decode().strip()
        if packed != version: errors.append(f'VERSION inside the archive is {packed}, expected {version}')
    except (OSError, KeyError, zipfile.BadZipFile) as e:
        errors.append(f'cannot read {NAME}/VERSION from {a.file}: {e}')

if errors:
    sys.exit('Version check failed:\n  ' + '\n  '.join(errors))
print(f'version check ok: {version}')
