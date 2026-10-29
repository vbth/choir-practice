#!/usr/bin/env python3
"""Template parity: the language packs are the templates of every generated document, so they must have the same structure.

  python3 check_templates.py            -> exit 1 and a list of problems

* every language pack in assets/i18n has the same keys and the same {placeholders} per text as en.json
* every language has a session handoff template in assets/templates (session_handoff.<lang>.md) with the same {{tokens}} and the same
  number of sections as the English one
* footer rules (see common.py): the AI note texts have no middle dot, the label files exist, and the READMEs (skill folder and repo root)
  end with a blank line, md_project(), a blank line, md_footer() and a blank line in their language
Used by make_layout.py (self-check) and runnable on its own."""
import os, re, sys, json, glob

HERE = os.path.dirname(os.path.abspath(__file__)); ASSETS = os.path.join(HERE, '..', 'assets')
SKIP = ('protocol_notes', 'capitalised_nouns')   # language-specific by nature (regex translations, nouns of that language)

def walk(o, path=''):
    if isinstance(o, dict):
        for k, v in o.items():
            if k in SKIP and not path: continue
            yield from walk(v, f'{path}.{k}' if path else k)
    elif isinstance(o, list): yield path + '[]', o
    else: yield path, o

def ph(o):
    txt = ' '.join(map(str, o)) if isinstance(o, list) else str(o)
    return set(re.findall(r'\{[a-z_]+\}', txt))

def problems():
    out = []; packs = {os.path.splitext(os.path.basename(f))[0]: json.load(open(f, encoding='utf-8')) for f in glob.glob(os.path.join(ASSETS, 'i18n', '*.json'))}
    ref = dict(walk(packs['en']))
    for code, pack in sorted(packs.items()):
        if code == 'en': continue
        cur = dict(walk(pack))
        for k in sorted(set(ref) - set(cur)): out.append(f'language pack {code}: key missing: {k}')
        for k in sorted(set(cur) - set(ref)): out.append(f'language pack {code}: key not in en.json: {k}')
        for k in sorted(set(ref) & set(cur)):
            if ph(ref[k]) != ph(cur[k]): out.append(f'language pack {code}: placeholders differ at {k}: {sorted(ph(ref[k]))} vs {sorted(ph(cur[k]))}')
    tdir = os.path.join(ASSETS, 'templates'); tok = lambda t: set(re.findall(r'\{\{[a-z_]+\}\}', t)); sec = lambda t: len(re.findall(r'^## ', t, re.M))
    en = open(os.path.join(tdir, 'session_handoff.en.md'), encoding='utf-8').read()
    for code in packs:
        f = os.path.join(tdir, f'session_handoff.{code}.md')
        if not os.path.exists(f): out.append(f'session handoff template missing for language {code}: {os.path.relpath(f, ASSETS)}'); continue
        t = open(f, encoding='utf-8').read()
        if tok(t) != tok(en): out.append(f'handoff template {code}: tokens differ from en ({sorted(tok(t) ^ tok(en))})')
        if sec(t) != sec(en): out.append(f'handoff template {code}: {sec(t)} sections, en has {sec(en)}')
    sk = open(os.path.join(tdir, 'skill_handoff.en.md'), encoding='utf-8').read()
    if '## 5. Third-party rights check' not in sk: out.append('skill_handoff.en.md: section "5. Third-party rights check" missing (mandatory)')
    out += footer_problems(packs)
    return out

def footer_problems(packs):
    sys.path.insert(0, HERE); from common import md_footer, md_project, MD_LABEL
    out = []
    for code, pack in packs.items():
        for k in ('ai_meta', 'ai_note', 'ai_note_info'):
            if '\u00b7' in pack.get(k, ''): out.append(f'language pack {code}: {k} contains a middle dot')
    for f in ('eu-ai-basic.svg', 'eu-ai-generated.svg', 'eu-ai-modified.svg'):
        if not os.path.exists(os.path.join(ASSETS, f)): out.append(f'footer label missing: assets/{f}')
    skill = os.path.join(HERE, '..'); repo = os.path.join(skill, '..')
    if os.path.isdir(os.path.join(repo, 'docs', 'img')):
        for f in ('ai-basic.svg', 'ai-basic-dark.svg'):
            if not os.path.exists(os.path.join(repo, 'docs', 'img', f)): out.append(f'footer label for Markdown missing: docs/img/{f} (linked from {MD_LABEL})')
    for d in (skill, repo):
        for fn, lang in (('README.md', 'en'), ('README.de.md', 'de')):
            p = os.path.join(d, fn)
            if not os.path.exists(p): continue
            t = open(p, encoding='utf-8').read(); m = re.search(r'\n\n([^\n]+)\n\n\Z', t); date = re.search(r'(\d{4}-\d{2}-\d{2})\n\n\Z', t)
            iso = None if not date else date.group(1)
            if not m or not iso or m.group(1) != md_footer(lang, '', iso):
                out.append(f'{os.path.relpath(p, repo)}: last line is not the footer (blank line, common.md_footer("{lang}"))')
            elif not t.rstrip('\n').endswith(md_project(lang) + '\n\n' + m.group(1)):
                out.append(f'{os.path.relpath(p, repo)}: the line above the footer is not the project line (common.md_project("{lang}"))')
    return out

if __name__ == '__main__':
    p = problems()
    for x in p: print('  FAIL', x)
    print('templates: ' + ('FAIL' if p else 'ok')); sys.exit(1 if p else 0)
