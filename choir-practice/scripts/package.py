#!/usr/bin/env python3
"""Finish the work package: build the delivery folder and create the ONE delivery ZIP.

  python3 package.py PKG score.json --source original.pdf --workdir WORK [--docs docs.json] [--date YYYY-MM-DD] [--out DIR]

* PKG is the work package built in phases 5-7 (raw layout, checked by verify.py); it is not delivered as is.
* make_layout.py builds <package>_<Title>/ from it: 1 scores (+MusicXML, MIDI), 2 practice (overview,
  director guide, one complete ZIP per voice), 3 documentation, 4 tools (project data + the skill) – see its docstring.
* ONE delivery ZIP Chor_Uebungen_<Title>.zip holding the numbered folders directly (no extra top folder); CRC test; result logged.
"""
import os, sys, json, shutil, zipfile, argparse, glob, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import safe, today_iso, log_check, load_i18n

HERE = os.path.dirname(os.path.abspath(__file__))

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('pkg'); ap.add_argument('spec')
    ap.add_argument('--source', required=True); ap.add_argument('--workdir', required=True)
    ap.add_argument('--docs'); ap.add_argument('--date'); ap.add_argument('--out', help='folder for the delivery folder and ZIP (default: parent of PKG)')
    A = ap.parse_args(); spec = json.load(open(A.spec, encoding='utf-8'))
    slug = safe(spec['meta']['title']); date = A.date or today_iso(); pkg = A.pkg
    # remove scratch files of earlier phases so they never end up in the delivery
    for pat in ('**/*.png', '**/*_check.pdf', '**/__pycache__'):
        for f in glob.glob(os.path.join(pkg, pat), recursive=True):
            shutil.rmtree(f) if os.path.isdir(f) else os.remove(f)
    outdir = A.out or os.path.dirname(os.path.abspath(pkg)); os.makedirs(outdir, exist_ok=True)
    cmd = [sys.executable, os.path.join(HERE, 'make_layout.py'), pkg, A.spec, outdir, '--workdir', A.workdir, '--source', A.source, '--date', date]
    if A.docs: cmd += ['--docs', A.docs]
    mx = os.path.join(pkg, 'mixes.json'); lj = glob.glob(os.path.join(pkg, '*', '*.layout.json'))
    dcmd = [sys.executable, os.path.join(HERE, 'make_docs.py'), A.spec, A.docs, pkg, '--workdir', A.workdir] if A.docs else None
    if dcmd:
        if os.path.exists(mx): dcmd += ['--mixes', mx]
        if lj: dcmd += ['--layout', lj[0]]
        subprocess.run(dcmd, check=True)   # pass 0: documents and check log with everything logged so far (audio test, verify)
    # first pass builds the layout so the check log can include its results
    ok = subprocess.run(cmd).returncode == 0
    if ok:   # second pass: regenerate the check log (now with this run's delivery check) and build the delivery folder again
        if dcmd: subprocess.run(dcmd, check=True); ok = subprocess.run(cmd).returncode == 0
    top = f'{load_i18n(spec.get("language", "en"))["delivery"]["package"]}_{slug}'; folder = os.path.join(outdir, top); zpath = os.path.join(outdir, f'{top}.zip')   # no date in folder or ZIP name
    pkg_word = load_i18n(spec.get('language', 'en'))['delivery']['package']
    for old in glob.glob(os.path.join(outdir, f'*_{pkg_word}_{slug}.zip')): os.remove(old)   # no stray ZIPs of THIS piece from earlier runs (exact title, so 'Ave' never removes 'Ave_Maria')
    # every ZIP is verified with testzip() and a file count before the run counts as delivered
    bad, n = 'no delivery folder', 0
    vz_bad = []
    if ok and os.path.isdir(folder):
        dl = load_i18n(spec.get('language', 'en'))['delivery']; pdir = os.path.join(folder, dl['practice'])
        for vd in sorted(d for d in os.listdir(pdir) if os.path.isdir(os.path.join(pdir, d))):   # one ZIP per voice, the folder inside (unzips to a folder)
            src = os.path.join(pdir, vd); want = sum(len(fs) for _, _, fs in os.walk(src))
            with zipfile.ZipFile(src + '.zip', 'w', zipfile.ZIP_DEFLATED) as vz:
                for r_, _, fs in os.walk(src):
                    for f in sorted(fs): vz.write(os.path.join(r_, f), os.path.join(vd, os.path.relpath(os.path.join(r_, f), src)))
            with zipfile.ZipFile(src + '.zip') as vz:
                if vz.testzip() is not None or len([i for i in vz.infolist() if not i.is_dir()]) != want: vz_bad.append(vd)
            shutil.rmtree(src)
        print(f'voice ZIPs: {len([f for f in os.listdir(pdir) if f.endswith(".zip")])}, test={"OK" if not vz_bad else vz_bad}')
        with zipfile.ZipFile(zpath, 'w', zipfile.ZIP_DEFLATED) as z:
            for r_, _, fs in os.walk(folder):
                for f in sorted(fs): z.write(os.path.join(r_, f), os.path.relpath(os.path.join(r_, f), folder))
        with zipfile.ZipFile(zpath) as z: bad = z.testzip(); n = len(z.infolist())
        print(f'delivery ZIP {zpath}: {n} files, {os.path.getsize(zpath)/1e6:.1f} MB, test={"OK" if bad is None else bad}')
    results = [ok, bad is None, not vz_bad]
    log_check(A.workdir, 6, 'package', 'pass' if all(results) else 'fail', f'one ZIP ({top}), CRC test {"OK" if all(results) else "FAILED"}')
    if not all(results): sys.exit(1)

if __name__ == '__main__':
    main()
