#!/usr/bin/env python3
"""Build the delivery folder (the layout the user receives) from the finished work package.

  python3 make_layout.py PKG score.json OUTDIR --workdir WORK --source original.pdf [--docs docs.json] [--date YYYY-MM-DD]

Delivery layout (names from i18n "delivery"; every folder is numbered without gaps, at most 3 folder levels,
no file stored twice except guide/score/tutti, which make each voice folder complete on its own):

  <date>_Chor_Uebungen_<Title>/     (the ZIP of the same name holds the numbered folders directly, no extra top folder)
    1_Noten/         1_Noten_<T>_Scan.pdf  2_Noten_<T>.pdf  3/4_MusicXML (Chor, Klavier)  5_MIDI_<T>/<voice>_MIDI_<T>/ + Tutti_MIDI_<T>/
    2_Ueben/         1_Uebersicht_Overview.pdf  2_Anleitung_Guide.pdf  <abbr>_Ueben_<T>/   1_<abbr>_Anleitung_<T>.pdf  2_<abbr>_Noten_<T>.pdf (same full score everywhere)
                                    3_<abbr>_Audio_Chorklang_<T>/  4_<abbr>_Audio_Klavierklang_<T>/   stages 1-6, 6 = tutti
    3_Dokumentation/ README, Pruefprotokoll, Korrekturprotokoll, Session-Handoff
    4_Werkzeuge/     1_Projektdaten_<T>/ (score.json, docs.json, mixes.json, layout.json)  2_SKILL_<name>_v<x>/ (the scripts live in the skill only)

Audio file names: <stage>_<voice>_<Title>_<Chor|Klavier>_<content>.mp3 (a number is always followed by an underscore). All MP3s get ID3 tags
(title "<Title> – <n> <name>", album "<Title> <Voice>, <Chorklang|Klavierklang>", track n/6, artist = composer). Self-check at the end (exit 1 on failure).
"""
import os, sys, re, json, glob, shutil, zipfile, argparse, subprocess
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import load_i18n, safe, today_iso, log_check, TRANS, ACCENT, md_footer, rl_footer, register_plex
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm
from pypdf import PdfReader

TITLE_FOR_FOOTER = ['']   # piece title for the footer (set in main)
NAME_OK = re.compile(r'^[A-Za-z0-9][A-Za-z0-9_]*(\.[A-Za-z0-9]+)?$')   # no hyphen in any name
ORDER = ['solo_slow', 'solo', 'accomp_slow', 'accomp', 'choir', 'tutti']   # index + 1 = stage number (same in every folder)


def hy(s):
    """Share-safe name: transliterate, every run of non-alphanumerics becomes one hyphen."""
    s = ''.join(TRANS.get(c, c) for c in s)
    return re.sub(r'[^A-Za-z0-9]+', '-', s).strip('-')


def abbr_of(v):
    if v.get('abbr'): return hy(v['abbr']).replace('-', '')
    name = ''.join(TRANS.get(c, c) for c in v['name'])
    letters = re.findall(r'[A-Za-z]', name); digits = ''.join(re.findall(r'\d', name))
    return (letters[0].upper() if letters else v['id']) + digits


def tag_copy(src, dst, title, album, artist, track, total, comment='', cover=None):
    cmd = ['ffmpeg', '-y', '-v', 'error', '-i', src] + (['-i', cover] if cover else []) + ['-map', '0:a'] + (['-map', '1:v', '-disposition:v', 'attached_pic', '-metadata:s:v', 'title=Cover', '-metadata:s:v', 'comment=Cover (front)'] if cover else []) + ['-c', 'copy', '-map_metadata', '-1', '-id3v2_version', '3',
           '-metadata', f'title={title}', '-metadata', f'album={album}', '-metadata', f'track={track}/{total}']
    if artist: cmd += ['-metadata', f'artist={artist}']
    if comment: cmd += ['-metadata', f'comment={comment}', '-metadata', f'copyright={comment}', '-metadata', f'date={today_iso()[:4]}']
    subprocess.run(cmd + [dst], check=True)


def guide_pdf(path, heading, intro, rows, extra, lang, date):
    """Guide (one A4 page): Swiss design – IBM Plex Sans, flush left on a 20 mm margin, 100 % black, no rules or fills."""
    register_plex()
    K = colors.black
    H1 = ParagraphStyle('h1', fontName='PlexB', fontSize=24, leading=28, spaceAfter=4, textColor=K)
    B = ParagraphStyle('b', fontName='PlexR', fontSize=12, leading=17, textColor=K)
    C = ParagraphStyle('c', fontName='PlexR', fontSize=11.5, leading=15.5, textColor=K)
    CB = ParagraphStyle('cb', parent=C, fontName='PlexB')
    def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
    fl = [Paragraph(esc(heading), H1), Paragraph(esc(intro), B), Spacer(1, 12)]   # generic: only the heading, no piece title
    CH = ParagraphStyle('ch', parent=CB, textColor=colors.HexColor(ACCENT))
    data = [[Paragraph(esc(c), CH) for c in rows[0]]] + [[Paragraph(esc(r[0]), CB), Paragraph(esc(r[1]), C), Paragraph(esc(r[2]), C)] for r in rows[1:]]
    t = Table(data, colWidths=[14 * mm, 66 * mm, 90 * mm], repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.black), ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor(ACCENT)),
                           ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 5), ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                           ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 6)]))
    fl.append(t); fl.append(Spacer(1, 12))
    for e in extra: fl += [Paragraph(esc(e), B), Spacer(1, 6)]
    def cb(c, d):
        c.saveState(); rl_footer(c, d.leftMargin + 6, A4[0] - d.rightMargin - 6, 12 * mm, B.fontSize, None, TITLE_FOR_FOOTER[0], lang, date)   # guides are one page: no page number; c.restoreState()
    SimpleDocTemplate(path, pagesize=A4, leftMargin=20 * mm - 6, rightMargin=20 * mm - 6, topMargin=20 * mm, bottomMargin=22 * mm,
                      title=heading).build(fl, onFirstPage=cb, onLaterPages=cb)


def language_leaks(root, d03, d02, DL, lang, i18, spec, A, mp3tags_full):
    """The package speaks one language: list words of any other language pack that occur in file/folder names, PDF texts and metadata,
    Markdown files and MP3 tags. Allowed: words of the active pack, the piece content (score.json, docs.json) and the skill's own name."""
    from common import I18N_DIR
    tok = lambda t: re.findall(r'[A-Za-z\u00c4\u00d6\u00dc\u00e4\u00f6\u00fc\u00df]{4,}', t)
    norm = lambda w: w.lower().replace('\u00e4', 'ae').replace('\u00f6', 'oe').replace('\u00fc', 'ue').replace('\u00df', 'ss')
    def strings(o, skip=('protocol_notes', 'lang', 'language_name')):
        if isinstance(o, str): yield o
        elif isinstance(o, list):
            for x in o: yield from strings(x, skip)
        elif isinstance(o, dict):
            for k, v in o.items():
                if k not in skip: yield from strings(v, skip)
    vocab = lambda pack: {norm(w) for t in strings(pack) for w in tok(t)}
    own = vocab(i18)
    allowed = set(own)
    for src in (A.spec, A.docs):
        if src and os.path.exists(src): allowed |= {norm(w) for w in tok(open(src, encoding='utf-8').read())}
    allowed |= {norm(w) for w in tok(i18.get('skill_name', ''))}
    allowed |= {'setup'}   # name of the skill's own script setup.sh, quoted in the session handoff
    allowed |= {norm(w) for w in tok(os.path.basename(A.source))}
    allowed |= {norm(w) for w in tok(open(os.path.join(A.workdir, 'checks.jsonl'), encoding='utf-8').read())} if os.path.exists(os.path.join(A.workdir, 'checks.jsonl')) else set()
    foreign = {}
    for f in sorted(glob.glob(os.path.join(I18N_DIR, '*.json'))):
        code = os.path.splitext(os.path.basename(f))[0]
        if code != lang:
            for w in vocab(json.load(open(f, encoding='utf-8'))) - allowed: foreign.setdefault(w, code)
    from pypdf import PdfReader
    out = []
    def scan(where, text):
        readme = os.path.basename(where).split(' ')[0].split('_')[1:2] == [DL['readme']]   # the README of a non-English package is bilingual by design: its English half is allowed
        bad = sorted({w for w in map(norm, tok(text)) if w in foreign and not (readme and lang != 'en' and foreign[w] == 'en')})
        if bad: out.append(f'language leak ({", ".join(f"{w} [{foreign[w]}]" for w in bad[:6])}) in {where}')
    tools = os.path.join(root, DL['tools']) + os.sep
    for r_, ds, fs in os.walk(root):
        if (r_ + os.sep).startswith(tools): continue
        for n_ in ds + fs:
            if r_ == root and n_ == DL['tools']: continue
            scan('name ' + os.path.relpath(os.path.join(r_, n_), root), os.path.splitext(n_)[0].replace('_', ' '))
        for n_ in fs:
            p = os.path.join(r_, n_); rel = os.path.relpath(p, root)
            if n_.endswith('.pdf') and not n_.endswith(f'_{DL["scan"]}.pdf'):
                is_score = f'_{DL["score"]}_' in n_ or n_.startswith(f'2_{DL["partitur"]}') or f'_{DL["partitur"]}_' in n_
                pr = ['-f', '1', '-l', '1'] if is_score else []   # the score: cover page only (the music pages carry the lyrics)
                scan(rel, subprocess.run(['pdftotext'] + pr + [p, '-'], capture_output=True, text=True).stdout)
                md = PdfReader(p).metadata or {}; scan(rel + ' (metadata)', ' '.join(str(v) for v in md.values()))
            elif n_.endswith('.md'): scan(rel, re.sub(r'<!--.*?-->', ' ', open(p, encoding='utf-8').read(), flags=re.S))   # comments are notes for authors (token names)
    for rel, t in mp3tags_full.items(): scan(rel + ' (MP3 tags)', t)
    return out


def md5(p):
    import hashlib
    h = hashlib.md5()
    with open(p, 'rb') as f:
        for b in iter(lambda: f.read(1 << 20), b''): h.update(b)
    return h.hexdigest()


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('pkg'); ap.add_argument('spec'); ap.add_argument('outdir')
    ap.add_argument('--workdir', required=True); ap.add_argument('--source', required=True); ap.add_argument('--docs'); ap.add_argument('--date')
    A = ap.parse_args(); pkg = A.pkg; HERE = os.path.dirname(os.path.abspath(__file__))
    spec = json.load(open(A.spec, encoding='utf-8')); lang = spec.get('language', 'en'); i18 = load_i18n(lang)
    fo, snd, stg, SH, DL = i18['folders'], i18['sounds'], i18['stages'], i18['share'], i18['delivery']
    meta = spec['meta']; title = meta['title']; T = safe(title); date = A.date or today_iso(); artist = meta.get('composer') or ''
    voices = spec['voices']; melody = spec.get('melody'); ab = {v['id']: abbr_of(v) for v in voices}
    if len(set(ab.values())) != len(ab): sys.exit(f'voice abbreviations collide {ab} – set "abbr" for each voice in score.json')
    it, W, G, D, FN = dict(SH['items']), SH['what'], SH['guide'], SH['director_guide'], DL['fname']
    fails = []
    for k_, fn_ in FN.items():   # one vocabulary: the display name of a file is its file-name part with spaces (single source = delivery.fname)
        disp = fn_.replace('_', ' '); disp = disp[0].upper() + disp[1:]
        if it.get(k_) != disp: fails.append(f'display name "{it.get(k_)}" differs from file-name part "{fn_}" (share.items.{k_} must be "{disp}")')
        it[k_] = disp
    tips = [t.format(choir_dir=DL['choir_dir'], piano_dir=DL['piano_dir']) for t in G['tips']]
    TITLE_FOR_FOOTER[0] = title; total = len(ORDER); AI_TAG = i18['ai_tag']; AI_META = i18['ai_meta']   # exact nomenclature, see SKILL.md "AI labelling"
    root = os.path.join(A.outdir, f'{date}_{DL["package"]}_{T}'); shutil.rmtree(root, ignore_errors=True)
    d02, d03, d04, d05 = (os.path.join(root, DL[k]) for k in ('scores', 'practice', 'docs', 'tools'))   # 1_Noten, 2_Ueben, 3_Dokumentation, 4_Werkzeuge
    for d in (d02, d03, d04, d05): os.makedirs(d)
    item_key = lambda k, vid: {'accomp_slow': 'accomp_mel_slow', 'accomp': 'accomp_mel'}.get(k, k) if vid == melody else k
    def label(k, vid): return FN[item_key(k, vid)]
    def raw(sound, k, v):
        """Raw work-package file (mp3, mid) of stage k for voice v in the given sound key ('choir' | 'piano')."""
        if k == 'tutti':
            b = os.path.join(pkg, fo['tutti'], snd[sound], f'{T}_{i18["files"]["tutti"]}_{snd[sound]}'); return b + '.mp3', b + '.mid'
        st, slow = {'solo_slow': ('solo', 1), 'solo': ('solo', 0), 'accomp_slow': ('accomp', 1), 'accomp': ('accomp', 0), 'choir': ('choir', 0)}[k]
        base = f'{T}_{stg[st]}_{safe(v["name"])}_{snd[sound]}'; d = os.path.join(pkg, fo['practice'], snd[sound], stg[st])
        if slow: d = os.path.join(d, i18['slow']); base += f'_{i18["slow"]}'
        return os.path.join(d, 'MP3', base + '.mp3'), os.path.join(d, 'MIDI', base + '.mid')
    def guide_rows(vid):
        rows = [[G['col_no'], G['col_file'], G['col_what']]]
        for n, k in enumerate(ORDER, start=1): rows.append([str(n), it[item_key(k, vid)], W[item_key(k, vid)]])
        return rows
    lay = json.load(open(next(iter(glob.glob(os.path.join(pkg, fo['scores'], '*.layout.json')) + glob.glob(os.path.join(pkg, fo['tools'], 'layout.json')))), encoding='utf-8'))
    final_xml = os.path.join(A.workdir, 'final.musicxml')
    score_pdf = next(f for f in glob.glob(os.path.join(pkg, fo['scores'], '*.pdf')) if not f.endswith('_check.pdf'))

    # album art: one cover per piece, derived from key, mode, tempo and metre; legibility is checked on the pixels (make_cover.py)
    import make_cover
    COVER = os.path.join(A.workdir, 'cover.jpg'); cover_ok, cover_note = make_cover.make(spec, final_xml, COVER, A.workdir)
    if not cover_ok: print('WARNING: album art legibility check failed: ' + cover_note)
    # 2_Ueben: one complete folder per voice
    for idx, v in enumerate(voices):
        vid = v['id']; a = ab[vid]; vdir = os.path.join(d03, f'{a}_{DL["voice_dir"]}_{T}'); os.makedirs(vdir)
        guide_pdf(os.path.join(vdir, f'1_{a}_{DL["guide"]}.pdf'), G['sub'].format(voice=v['name']), G['intro'], guide_rows(vid), tips, lang, date)
        shutil.copy(score_pdf, os.path.join(vdir, f'2_{a}_{DL["score"]}_{T}.pdf'))   # the same full score in every voice folder
        for n_dir, sound, word in ((3, 'choir', DL['choir_dir']), (4, 'piano', DL['piano_dir'])):
            adir = os.path.join(vdir, f'{n_dir}_{a}_{DL["audio"]}_{word}_{T}'); os.makedirs(adir)
            for n, k in enumerate(ORDER, start=1):
                mp3, _ = raw(sound, k, v)
                if not os.path.exists(mp3): sys.exit('missing source audio: ' + os.path.relpath(mp3, pkg))
                tag_copy(mp3, os.path.join(adir, f'{n}_{a}_{T}_{snd[sound]}_{label(k, vid)}.mp3'), f'{title} – {n} {label(k, vid).replace("_", " ")}', f'{title} {v["name"]}, {word.replace("_", " ")}', artist, n, total, AI_META, COVER)
    # 1_Noten: scan, AI score, MusicXML, MIDI
    shutil.copy(A.source, os.path.join(d02, f'1_{DL["partitur"]}_{T}_{DL["scan"]}.pdf')); shutil.copy(score_pdf, os.path.join(d02, f'2_{DL["partitur"]}_{T}.pdf'))
    n = 3
    for sound in ('choir', 'piano'):
        f = os.path.join(pkg, fo['scores'], f'{T}_{snd[sound]}.musicxml')
        if os.path.exists(f): shutil.copy(f, os.path.join(d02, f'{n}_{DL["musicxml"]}_{T}_{snd[sound]}.musicxml')); n += 1
    mdir = os.path.join(d02, f'{n}_{DL["midi"]}_{T}'); os.makedirs(mdir)
    for v in voices:
        vd = os.path.join(mdir, f'{ab[v["id"]]}_{DL["midi"]}_{T}'); os.makedirs(vd)
        for k_, k in enumerate(ORDER[:-1], start=1):
            for sound in ('choir', 'piano'):
                _, mid = raw(sound, k, v)
                if not os.path.exists(mid): sys.exit('missing MIDI: ' + os.path.relpath(mid, pkg))
                shutil.copy(mid, os.path.join(vd, f'{k_}_{ab[v["id"]]}_{T}_{snd[sound]}_{label(k, v["id"])}.mid'))
    td = os.path.join(mdir, f'{DL["tutti"]}_{DL["midi"]}_{T}'); os.makedirs(td)
    for sound in ('choir', 'piano'): shutil.copy(raw(sound, 'tutti', None)[1], os.path.join(td, f'{T}_{DL["tutti"]}_{snd[sound]}.mid'))
    # 2_Ueben (top level): overview and director guide
    a0 = ab[voices[0]['id']]
    extra = [D['intro'], D['naming'].format(example=f'1_{a0}_{D["title_word"]}_{snd["choir"]}_{label("solo_slow", voices[0]["id"])}.mp3'),
             D['abbr_h'] + ': ' + ', '.join(f'{ab[v["id"]]} = {v["name"]}' for v in voices), D['tutti_note']]
    if melody in ab: extra.insert(2, D['melody_note'].format(abbr=ab[melody]))
    guide_pdf(os.path.join(d03, f'2_{DL["guide"]}.pdf'), D['sub'], D['table_h'], guide_rows(None), extra, lang, date)
    ov = glob.glob(os.path.join(pkg, fo['practice'], '*.pdf'))
    if ov: shutil.copy(ov[0], os.path.join(d03, f'1_{DL["overview"]}.pdf'))
    # 3_Dokumentation
    docs = [('README', DL['readme']), (i18['files']['protocol'], i18['files']['protocol']), (i18['files_more']['corrections'], i18['files_more']['corrections'])]
    n = 1
    for src_name, new in docs:
        for ext in ('pdf', 'md'):
            f = os.path.join(pkg, f'{safe(src_name)}.{ext}')
            if os.path.exists(f): shutil.copy(f, os.path.join(d04, f'{n}_{safe(new)}_{T}.{ext}'))
        n += 1
    handoff_dst = os.path.join(d04, f'{n}_{DL["handoff"]}_{T}.md')
    # 4_Werkzeuge
    pd = os.path.join(d05, f'1_{DL["data"]}_{T}'); os.makedirs(pd)
    shutil.copy(A.spec, os.path.join(pd, 'score.json'))
    if A.docs: shutil.copy(A.docs, os.path.join(pd, 'docs.json'))
    for f in (os.path.join(pkg, 'mixes.json'), os.path.join(pkg, fo['tools'], 'mixes.json')):
        if os.path.exists(f): shutil.copy(f, os.path.join(pd, 'mixes.json')); break
    lj = glob.glob(os.path.join(pkg, fo['scores'], '*.layout.json')) + glob.glob(os.path.join(pkg, fo['tools'], 'layout.json'))
    if lj: shutil.copy(lj[0], os.path.join(pd, 'layout.json'))
    sk = os.path.dirname(HERE); name = os.path.basename(sk)
    ver = open(os.path.join(sk, 'VERSION')).read().strip() if os.path.exists(os.path.join(sk, 'VERSION')) else 'unversioned'
    nu = name.replace('-', '_')   # the skill's own name is kebab-case; names in the package use underscores only
    sd = os.path.join(d05, f'2_{DL["skill"]}_{nu}_v{ver}'); os.makedirs(sd)
    for f in ('README.md', 'session-handoff.md'):
        if os.path.exists(os.path.join(sk, f)): shutil.copy(os.path.join(sk, f), os.path.join(sd, f.replace('-', '_')))
    with zipfile.ZipFile(os.path.join(sd, f'{nu}.skill'), 'w', zipfile.ZIP_DEFLATED) as z:
        for f in sorted(glob.glob(os.path.join(sk, '**', '*'), recursive=True)):
            if os.path.isfile(f) and '__pycache__' not in f: z.write(f, os.path.join(name, os.path.relpath(f, sk)))
    # session handoff: facts are filled in from the build, never typed by hand (tokens {{date}} {{package}} {{skill_version}} {{folders}} {{score_layout}})
    hsrc = os.path.join(pkg, 'session_handoff.md')
    if os.path.exists(hsrc):
        fac = {'date': date, 'package': os.path.basename(root), 'skill_version': ver, 'folders': ', '.join(sorted(os.listdir(root))),
               'project_data': f"{DL['tools']}/1_{DL['data']}_{T}",
               'score_layout': i18['delivery']['score_layout'].format(pages=lay.get('pages'), systems=lay.get('systems_per_page'), scale=lay.get('scale'), space=lay.get('staff_space_mm'))}
        ht = open(hsrc, encoding='utf-8').read()
        for k_, v_ in fac.items(): ht = ht.replace('{{' + k_ + '}}', str(v_))
        ht = re.sub(r'\n*<!--.*?-->\n*', '\n\n', ht, flags=re.S)   # author hints of the template do not belong in the package
        open(handoff_dst, 'w', encoding='utf-8').write(ht)
    # AI nomenclature in the metadata of every produced file (checked in the self-check below):
    #   PDF   Title=<title> Author/Creator/Producer/Keywords="KI-generiert" Subject="KI-generiert. Urheber- und Lizenzrechte beachten. Nutzung auf eigene Gefahr."
    #   MP3   comment + copyright="KI-generiert. Urheber- und Lizenzrechte beachten. Nutzung auf eigene Gefahr." (title/album/track/artist/date as usual)
    #   XML   encoding-description + rights="KI-generiert. Urheber- und Lizenzrechte beachten. Nutzung auf eigene Gefahr.", encoding-date
    #   MIDI  copyright + text meta event at tick 0
    from pypdf import PdfWriter
    import mido
    DT = i18['doc_titles']; kinds = {DL['partitur']: DT['partitur'], DL['score']: DT['score'], DL['guide']: DT['guide'], DL['overview']: DT['overview'],
                                    DL['readme']: DT['readme'], safe(i18['files']['protocol']): DT['protocol'], safe(i18['files_more']['corrections']): DT['corrections']}
    vname = {ab[v['id']]: v['name'] for v in voices}
    def pdf_title(fname):
        """PDF Title = "<title> – Noten[ <voice>]" for the score, "<document>[ <voice>]" for every other PDF: each PDF has its own title (checked below)."""
        stem = os.path.splitext(fname)[0].split('_', 1)[1] if '_' in fname else fname   # drop the number
        parts = stem.split('_'); voice = vname.get(parts[0]) if parts and parts[0] in vname else None
        kind = next((kinds[k_] for k_ in sorted(kinds, key=len, reverse=True) if f'_{k_}_' in f'_{stem}_'), None)   # names may contain underscores (Check_Log)
        if not kind: return title
        return (f'{title} – {kind}' if kind in (DT['score'], DT['partitur']) else kind) + (f' {voice}' if voice else '')   # only the score carries the piece title; all other PDFs are generic
    for r_, ds, fs in os.walk(root):
        if os.sep + 'scripts' in r_ + os.sep: continue
        for f in fs:
            p = os.path.join(r_, f)
            if f.endswith('.pdf') and not f.endswith(f'_{DL["scan"]}.pdf') and '.skill' not in f:   # the supplied scan stays untouched
                w = PdfWriter(clone_from=p)
                w.add_metadata({'/Title': pdf_title(f), '/Author': AI_TAG, '/Creator': AI_TAG, '/Producer': AI_TAG, '/Subject': AI_META, '/Keywords': AI_TAG})
                with open(p, 'wb') as fh: w.write(fh)
            elif f.endswith('.musicxml'):
                x = open(p, encoding='utf-8').read()
                x = re.sub(r'\s*<encoding-date>.*?</encoding-date>|\s*<encoding-description>.*?</encoding-description>|\s*<rights>.*?</rights>', '', x, flags=re.S)
                x = x.replace('</software>', '</software>\n      <encoding-date>' + date + '</encoding-date>\n      <encoding-description>' + AI_META + '</encoding-description>', 1)
                x = x.replace('<encoding>', '<rights>' + AI_META + '</rights>\n    <encoding>', 1)
                x = re.sub(r'<software>.*?</software>', f'<software>{name} {ver}</software>', x, flags=re.S); open(p, 'w', encoding='utf-8').write(x)
            elif f.endswith('.mid'):
                m = mido.MidiFile(p); m.tracks[0][:0] = [mido.MetaMessage('copyright', text=AI_META, time=0), mido.MetaMessage('text', text=AI_META, time=0)]; m.save(p)
    # self-check
    seen = {}; mp3tags = {}; mp3tags_full = {}
    for r_, ds, fs in os.walk(root):
        if os.sep + 'scripts' in r_ + os.sep: continue
        for nme in ds + fs:
            if '-' in nme: fails.append(f'hyphen in name (use _): {os.path.relpath(os.path.join(r_, nme), root)}')
    for r_, ds, fs in os.walk(root):
        depth = 0 if r_ == root else len(os.path.relpath(r_, root).split(os.sep))
        if depth > 3: fails.append(f'folder deeper than 3 levels: {os.path.relpath(r_, root)}')
        nums = set()
        for nme in ds + fs:
            m = re.match(r'^(\d+)[_-]', nme)
            if m: nums.add(int(m.group(1)))
            if re.match(r'^\d+-', nme): fails.append(f'number must be followed by underscore: {os.path.relpath(os.path.join(r_, nme), root)}')
        if nums and nums != set(range(1, max(nums) + 1)) and nums != set(range(1, max(nums) + 1)) | {0}:
            if r_ == root or not all(n_ == 0 for n_ in nums): fails.append(f'numbering has gaps in {os.path.relpath(r_, root)}: {sorted(nums)}')
        for f in fs:
            p = os.path.join(r_, f)
            if f == 'score.json' or '/scripts/' in p or '.skill' in f or f.endswith(('.py', '.sh', '.json', '.md')): continue
            if not NAME_OK.match(f): fails.append(f'file name not safe: {os.path.relpath(p, root)}')
            if f.endswith('.pdf') and DL["guide"] in f:
                if len(PdfReader(p).pages) != 1: fails.append(f'guide not one page: {os.path.relpath(p, root)}')
            if f.endswith('.mp3'):
                r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format_tags=title,album,track,artist:stream=codec_type', '-of', 'json', p], capture_output=True, text=True)
                if 'video' not in [s_.get('codec_type') for s_ in json.loads(r.stdout or '{}').get('streams', [])]: fails.append(f'MP3 without album art: {os.path.relpath(p, root)}')
                tags = {k.lower(): v for k, v in json.loads(r.stdout or '{}').get('format', {}).get('tags', {}).items()}
                if not all(tags.get(k) for k in ('title', 'album', 'track')): fails.append(f'MP3 tags missing: {os.path.relpath(p, root)}')
                mp3tags[os.path.relpath(p, root)] = (tags.get('album'), tags.get('title'))
                mp3tags_full[os.path.relpath(p, root)] = ' '.join(str(v) for v in tags.values())
            if f.endswith(('.pdf', '.musicxml', '.mid')) and not p.startswith(d03): seen.setdefault(md5(p), []).append(os.path.relpath(p, root))
    for r_, ds, fs in os.walk(root):   # AI nomenclature in the metadata of every produced file
        if os.sep + 'scripts' in r_ + os.sep: continue
        for f in fs:
            p = os.path.join(r_, f); rel = os.path.relpath(p, root); bad = None
            if f.endswith('.pdf') and not f.endswith(f'_{DL["scan"]}.pdf'):
                md = PdfReader(p).metadata or {}
                if md.get('/Author') != AI_TAG or md.get('/Subject') != AI_META or md.get('/Keywords') != AI_TAG or md.get('/Title') != pdf_title(f): bad = 'PDF metadata'
            elif f.endswith('.mp3'):
                tg = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format_tags', '-of', 'json', p], capture_output=True, text=True).stdout or '{}').get('format', {}).get('tags', {})
                tg = {k.lower(): v for k, v in tg.items()}
                if tg.get('comment') != AI_META or tg.get('copyright') != AI_META: bad = 'MP3 comment/copyright'
            elif f.endswith('.musicxml'):
                x = open(p, encoding='utf-8').read()
                if f'<encoding-description>{AI_META}</encoding-description>' not in x or f'<rights>{AI_META}</rights>' not in x: bad = 'MusicXML description/rights'
                elif f'<software>{name} {ver}</software>' not in x: bad = 'MusicXML software without skill version'
                elif not all(f'({i18["cover"][k_]})' in x for k_ in ('lyricist', 'composer') if meta.get({'lyricist': 'lyricist', 'composer': 'composer'}[k_])): bad = 'MusicXML credits without role labels (Name (Text), Name (Musik))'
            elif f.endswith('.mid'):
                ms = [(e.type, getattr(e, 'text', '')) for e in mido.MidiFile(p).tracks[0] if e.is_meta]
                if ('copyright', AI_META) not in ms or ('text', AI_META) not in ms: bad = 'MIDI copyright/text'
            elif f.endswith('.md') and rel.startswith(DL['docs']) and DL['handoff'] not in f:
                if not open(p, encoding='utf-8').read().endswith('\n\n' + md_footer(lang, title, date) + '\n\n'): bad = 'footer line in Markdown (blank line before and after, date, comma, AI note)'
            if bad: fails.append(f'AI nomenclature missing ({bad}): {rel}')
    for h, ps in seen.items():
        if len(ps) > 1: fails.append('identical files stored twice: ' + ', '.join(ps))
    # --- consistency rules (SKILL.md "Consistency rules"): the same fact is written the same way everywhere
    tops = sorted(os.listdir(root)); allpdf = []
    for r_, ds, fs in os.walk(root):
        for f in fs:
            if f.endswith('.pdf') and not f.endswith(f'_{DL["scan"]}.pdf') and not f.endswith('.skill'): allpdf.append(os.path.join(r_, f))
    ttl = {}
    for p in allpdf: ttl.setdefault((PdfReader(p).metadata or {}).get('/Title'), []).append(os.path.relpath(p, root))
    for t_, ps in ttl.items():
        if len(ps) > 1: fails.append(f'PDF title "{t_}" is not unique (every PDF needs its own title): ' + ', '.join(ps))
    albums = {}
    for rel, (alb, tit) in mp3tags.items(): albums.setdefault((alb, tit), []).append(rel)
    for k_, ps in albums.items():
        if len(ps) > 1: fails.append(f'MP3 album+title not unique {k_} (choir and piano version must be distinguishable): ' + ', '.join(ps[:3]))
    for r_, ds, fs in os.walk(root):   # nouns capitalised the way the language does it (de: Chor, Klavier, Melodie, Stimme …)
        if os.sep + 'scripts' in r_ + os.sep: continue
        if os.path.relpath(r_, root).startswith(DL['tools']): continue   # tools folder: the skill keeps its own identifier
        for nme in ds + fs:
            for seg in os.path.splitext(nme)[0].split('_'):
                if seg.lower() in {w.lower() for w in i18['capitalised_nouns']} and seg not in i18['capitalised_nouns']: fails.append(f'noun not capitalised in name ({seg}): {os.path.relpath(os.path.join(r_, nme), root)}')
    def text_of(p):
        if p.endswith('.pdf'): return re.sub(r'\s+', ' ', subprocess.run(['pdftotext', '-layout', p, '-'], capture_output=True, text=True).stdout)
        return re.sub(r'\s+', ' ', open(p, encoding='utf-8').read())
    docs_txt = {os.path.relpath(p, root): text_of(p) for p in allpdf if not os.path.basename(p).startswith(f'2_{DL["partitur"]}') and f'_{DL["score"]}_' not in os.path.basename(p)}
    for p in glob.glob(os.path.join(d04, '*.md')): docs_txt[os.path.relpath(p, root)] = text_of(p)
    for rel, tx in docs_txt.items():
        for tok in set(re.findall(r'(?<![\d-])\b\d_(?:' + '|'.join(re.escape(DL[k_].split('_', 1)[1]) for k_ in ('scores', 'practice', 'docs', 'tools')) + r')\b', tx)):
            if tok not in tops: fails.append(f'text mentions a folder that does not exist ({tok}): {rel}')
        if re.search(r'mscz|MuseScore(?![_ ]General)', tx): fails.append(f'text mentions MuseScore files (removed): {rel}')
        if rel.startswith(DL['docs']) and DL['handoff'] not in rel:   # shared documents are neutral: no "you"/"du"
            if re.search(r'\b(du|dir|dich|dein\w*|euch|euer|eure\w*|you|your|yours)\b', re.sub(r'„[^“]*“|"[^"]*"|“[^”]*”', ' ', tx), re.I): fails.append(f'shared document addresses the reader (du/you): {rel}')
        if '{{' in tx: fails.append(f'unfilled token in {rel}')
    for rel, tx in docs_txt.items():   # one vocabulary in the guides (the same names as file names and MP3 titles)
        base = os.path.basename(rel)
        vid_ = next((v['id'] for v in voices if base == f'1_{ab[v["id"]]}_{DL["guide"]}.pdf'), None)
        if vid_ or (rel.startswith(DL['practice']) and base == f'2_{DL["guide"]}.pdf'):
            for k_ in ORDER:
                if it[item_key(k_, vid_)] not in tx: fails.append(f'guide lacks the name "{it[item_key(k_, vid_)]}": {rel}')
    hp = glob.glob(os.path.join(d04, f'*{DL["handoff"]}*.md'))
    if hp:
        ht = open(hp[0], encoding='utf-8').read()
        for need_ in (os.path.basename(root), ver, date, *tops):
            if need_ not in ht: fails.append(f'session handoff does not mention "{need_}" (use the {{{{tokens}}}} of the template)')
    else: fails.append('session handoff missing in the documentation folder')
    prot = glob.glob(os.path.join(d04, f'*{safe(i18["files"]["protocol"])}*.md'))
    if prot:
        rows_ = [l.split('|')[1:5] for l in open(prot[0], encoding='utf-8').read().splitlines() if l.startswith('| ') and not l.startswith('| Phase') and not l.startswith('|---')]
        keys_ = [tuple(x.strip() for x in (r if r[1].strip() in ('question_asked', 'answer_received') else r[:2])) for r in rows_]
        if len(keys_) != len(set(keys_)): fails.append('check log has duplicate rows (only the latest run of every check belongs in it)')
        if not any(r[1].strip() == 'audio_check' for r in rows_): fails.append('audio test missing in the check log (run audio_check.py, Phase 6)')
    rd = glob.glob(os.path.join(d04, f'*{DL["readme"]}*.md'))
    if rd:
        rt = open(rd[0], encoding='utf-8').read()
        if i18['readme']['rights_h'] not in rt: fails.append('README has no rights section')
        rt_ = spec.get('rights') or {}
        if rt_.get('status') not in ('public_domain', 'licensed', 'own', 'unclear'): fails.append('score.json has no "rights" status (public_domain | licensed | own | unclear)')
        if rt_.get('use') not in ('rehearsal', 'commercial'): fails.append('score.json rights.use missing (rehearsal | commercial)')
        if rt_.get('use') == 'commercial' and (rt_.get('status') == 'unclear' or (rt_.get('status') == 'licensed' and not rt_.get('reference'))):
            print('WARNING: commercial use with open rights (status unclear or licence reference missing) - the README carries a clear warning; clear the rights before any commercial use; commercial use of the skill itself needs its own licence (LICENSE)')
    for v in voices:
        vdir = os.path.join(d03, f'{ab[v["id"]]}_{DL["voice_dir"]}_{T}')
        cnt = sum(len(fs) for _, _, fs in os.walk(vdir))
        for r_, ds_, fs_ in os.walk(vdir):
            for nme in ds_ + fs_:
                if not re.match(r'^\d+_' + re.escape(ab[v['id']]) + '_', nme): fails.append(f'voice abbreviation missing after number: {os.path.relpath(os.path.join(r_, nme), root)}')
        if cnt != 2 + 2 * total: fails.append(f'{os.path.basename(vdir)}: {cnt} files, expected {2 + 2 * total}')
    # --- language guarantee: nothing of another language pack in names, PDFs, texts, MP3 tags (piece content is allowed)
    import check_templates; fails += check_templates.problems()   # language packs and handoff templates have the same structure
    fails += language_leaks(root, d03, d02, DL, lang, i18, spec, A, mp3tags_full)
    for f in fails: print('  FAIL', f)
    nfiles = sum(len(fs) for _, _, fs in os.walk(root))
    print(f'delivery folder {root}: {nfiles} files')
    log_check(A.workdir, 6, 'delivery_layout', 'fail' if fails else 'pass',
              '; '.join(fails[:5]) if fails else f'{len(voices)} voice folders (2 PDFs + {2 * total} MP3 each), numbering without gaps, max 3 levels, no stored duplicates, MP3 tags, guides 1 page, names, metadata, terms, handoff, rights')
    sys.exit(1 if fails else 0)


if __name__ == '__main__':
    main()
