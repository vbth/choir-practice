#!/usr/bin/env python3
"""Third-party rights check: every component the skill bundles or installs must be named in THIRD_PARTY_NOTICES.md.

Usage: check_third_party.py [--brief]

Reads three sources and compares them with THIRD_PARTY_NOTICES.md (next to the scripts folder):
  bundled   files in assets/ (fonts, EU label SVGs) and, in the repository, the website fonts and label copies in docs/
  run time  pip packages of requirements-stable.txt and apt packages of setup.sh (installed after the skill is installed)
Exit 1 when a component is missing from the notices; entries marked "to check" are listed as a warning (exit 0).
It checks that the notices are complete, not that the licences are right: it gives no legal advice.
"""
import glob, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__)); SKILL = os.path.dirname(HERE); REPO = os.path.dirname(SKILL)
NOTICES = os.path.join(SKILL, 'THIRD_PARTY_NOTICES.md')
brief = '--brief' in sys.argv
text = open(NOTICES, encoding='utf-8').read() if os.path.exists(NOTICES) else ''
low = text.lower()

# name in the notices that identifies each component (the pip or apt name is often not the one used in prose)
ALIAS = {'verovio': 'verovio', 'cairosvg': 'cairosvg', 'lxml': 'lxml', 'pypdf': 'pypdf', 'mido': 'mido', 'reportlab': 'reportlab',
         'pillow': 'pillow', 'numpy': 'numpy', 'scipy': 'scipy',
         'fluidsynth': 'fluidsynth', 'fluid-soundfont-gm': 'fluidr3', 'ffmpeg': 'ffmpeg', 'poppler-utils': 'poppler',
         'fonts-dejavu-core': 'dejavu', 'musescore-general-soundfont': 'musescore general'}

pip = [l.split('#')[0].strip().partition('==')[0] for l in open(os.path.join(HERE, 'requirements-stable.txt'), encoding='utf-8')]
pip = [p for p in pip if p]
apt = re.findall(r'need\+=\(([^)]+)\)', open(os.path.join(HERE, 'setup.sh'), encoding='utf-8').read())
bundled = sorted(os.path.relpath(f, SKILL) for pat in ('assets/fonts/*', 'assets/*.svg', 'assets/eu-labels/*.svg') for f in glob.glob(os.path.join(SKILL, pat)))
repo_only = sorted(os.path.relpath(f, REPO) for pat in ('docs/fonts/*', 'docs/img/ai-*.svg', 'docs/img/github-*.svg') for f in glob.glob(os.path.join(REPO, pat)))

missing = []
def need(kind, name, token):
    if token.lower() not in low: missing.append(f'{kind}: {name} (looked for "{token}")')

for p in pip: need('run time (pip)', p, ALIAS.get(p, p))
for a in apt: need('run time (apt)', a, ALIAS.get(a, a))
for f in bundled:
    need('bundled', f, 'assets/fonts/' if f.startswith('assets/fonts/') else 'assets/eu-labels/' if f.startswith('assets/eu-labels/') else os.path.basename(f))
for f in repo_only:
    need('repository only', f, 'docs/fonts/' if f.startswith('docs/fonts/') else os.path.basename(f))

todo = [l for l in text.splitlines() if '**to check**' in l and l.startswith('|')]
if not brief:
    print(f'bundled in the skill ({len(bundled)} files): ' + ', '.join(bundled))
    print(f'repository only, not in the .skill ({len(repo_only)} files): ' + (', '.join(repo_only) or 'none (not run inside the repository)'))
    print(f'installed at run time: pip {", ".join(pip)}; apt {", ".join(apt)}')
for m in missing: print('MISSING in THIRD_PARTY_NOTICES.md –', m)
for l in todo: print('to check –', l.split('|')[1].strip())
print('third party: ' + ('MISSING ' + str(len(missing)) if missing else 'ok') + (f', {len(todo)} entries marked "to check"' if todo else ''))
sys.exit(1 if missing else 0)
