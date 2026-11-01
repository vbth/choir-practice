#!/usr/bin/env python3
"""Builds the example package of the website ("Alle meine Entchen" / "All My Ducklings", 2/4) with the skill's own pipeline (phases 3 to 7).

  python3 site/build_example.py LANG WORKROOT [--date YYYY-MM-DD] [--from-phase N] [--soundfont NAME]

Inputs live in site/example/: score.<lang>.json (the piece), docs.<lang>.json (notes, sources), handoff.<lang>.md (session handoff of the piece).
Writes WORKROOT/<lang>/work (project data), WORKROOT/<lang>/pkg (work package) and WORKROOT/<lang>/out (delivery folder and the ONE ZIP).
--from-phase 6 keeps the existing audio (score, overview, documents, package are rebuilt). Needs the skill's tools (scripts/setup.sh)."""
import argparse, glob, json, os, shutil, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); SK = os.path.join(HERE, '..', 'choir-practice'); S = os.path.join(SK, 'scripts')
sys.path.insert(0, S)
from common import load_i18n, safe

def run(*a):
    print('$', ' '.join(os.path.relpath(x) if os.path.exists(x) else x for x in map(str, a)), flush=True)
    subprocess.run([sys.executable, *map(str, a)], check=True)

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('lang'); ap.add_argument('root'); ap.add_argument('--date', default='2026-10-28'); ap.add_argument('--from-phase', type=int, default=3); ap.add_argument('--soundfont', help='passed to make_audio.py (musescore or generaluser); default: make_audio decides')
    A = ap.parse_args(); L = A.lang; base = os.path.abspath(os.path.join(A.root, L)); W, P, O = (os.path.join(base, x) for x in ('work', 'pkg', 'out'))
    spec = json.load(open(os.path.join(HERE, 'example', f'score.{L}.json'), encoding='utf-8')); slug = safe(spec['meta']['title']); i18 = load_i18n(L); fo = i18['folders']
    if A.from_phase <= 3:
        for d in (W, P, O): shutil.rmtree(d, ignore_errors=True)
    for d in (W, P, O): os.makedirs(d, exist_ok=True)
    score, docs = os.path.join(W, 'score.json'), os.path.join(W, 'docs.json')
    shutil.copy(os.path.join(HERE, 'example', f'score.{L}.json'), score); shutil.copy(os.path.join(HERE, 'example', f'docs.{L}.json'), docs)
    sc = os.path.join(P, fo['scores']); os.makedirs(sc, exist_ok=True); pdf = os.path.join(sc, f'{slug}_{i18["files"]["score"]}.pdf')
    run(os.path.join(S, 'build_score.py'), score, os.path.join(W, 'score.musicxml'), '--workdir', W)
    run(os.path.join(S, 'check_music.py'), score, '--workdir', W)
    run(os.path.join(S, 'render_score.py'), os.path.join(W, 'score.musicxml'), pdf, '--lang', L, '--date', A.date, '--spec', score, '--preview-dir', os.path.join(W, 'prev'),
        '--write-xml', os.path.join(W, 'final.musicxml'), '--workdir', W)
    run(os.path.join(S, 'make_scores.py'), os.path.join(W, 'final.musicxml'), sc, '--slug', slug, '--lang', L, '--workdir', W)
    if A.from_phase <= 5:
        run(os.path.join(S, 'make_audio.py'), os.path.join(W, 'final.musicxml'), score, P, '--slug', slug, '--slow-pct', '80', '--workdir', W,
            *(['--soundfont', A.soundfont] if A.soundfont else []))
        run(os.path.join(S, 'audio_check.py'), P, score, '--workdir', W)
    run(os.path.join(S, 'make_overview.py'), os.path.join(P, 'mixes.json'), score, os.path.join(P, fo['practice'], f'{slug}_{i18["files"]["overview"]}.pdf'), '--png', os.path.join(W, 'overview.png'), '--workdir', W)
    shutil.copy(os.path.join(HERE, 'example', f'handoff.{L}.md'), os.path.join(P, 'session_handoff.md'))
    lay = glob.glob(os.path.join(sc, '*.layout.json'))[0]
    docs_cmd = [os.path.join(S, 'make_docs.py'), score, docs, P, '--workdir', W, '--mixes', os.path.join(P, 'mixes.json'), '--layout', lay]
    run(*docs_cmd); run(os.path.join(S, 'verify.py'), P, score, '--workdir', W); run(*docs_cmd)
    run(os.path.join(S, 'package.py'), P, score, '--source', pdf, '--workdir', W, '--docs', docs, '--date', A.date, '--out', O)
    print('done:', glob.glob(os.path.join(O, '*.zip')))

if __name__ == '__main__':
    main()
