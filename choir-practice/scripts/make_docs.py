#!/usr/bin/env python3
"""Create the documentation of a package (Markdown + PDF):
  README.md / README.pdf          bilingual: user language first, then English (English users: English only)
  <Check_Log>.md / .pdf           all automatic/manual checks from WORK/checks.jsonl (user language)
  <Correction_Log>.md / .pdf      every deviation, correction, interpretation, uncertain spot (user language)

  python3 make_docs.py score.json docs.json outdir --workdir WORK [--mixes mixes.json] [--layout layout.json]

docs.json (written by Claude, see references/score-spec.md "docs.json"):
  {"source_file": "...pdf",
   "meta_sources": [{"field": "composer", "value": "...", "url": "https://...", "approved": true}],
   "texts": {"<lang>": {"notes": ["..."], "open": ["..."]}, "en": {...}},
   "corrections": [{"bar": 5, "voice": "A", "kind": "pitch", "source": "...", "result": "...",
                    "reason": {"<lang>": "...", "en": "..."}, "status": "corrected|as_in_source|interpretation|uncertain"}]}
"""
import json, os, sys, argparse, re
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import has_rights, load_i18n, read_checks, safe, log_check, ACCENT, md_block, rl_footer, register_plex
from reportlab.lib.pagesizes import A4, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import mm

register_plex()   # Swiss design: IBM Plex Sans, flush left, 100 % black, no rules, no fills
K = colors.black
B = ParagraphStyle('b', fontName='PlexR', fontSize=10.5, leading=15, textColor=K)
S = ParagraphStyle('s', parent=B, fontSize=9.5, leading=13)
SB = ParagraphStyle('sb', parent=S, fontName='PlexB')
H1 = ParagraphStyle('h1', fontName='PlexB', fontSize=24, leading=28, spaceAfter=14, textColor=K)
H2 = ParagraphStyle('h2', fontName='PlexB', fontSize=12, leading=16, spaceBefore=14, spaceAfter=4, textColor=K)
SH = ParagraphStyle('sh', parent=SB, textColor=colors.HexColor(ACCENT))   # table heads in the highlight colour
MARGIN = 20 * mm - 6   # minus the 6 pt frame padding: text starts exactly at 20 mm

def esc(s): return str(s).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
def P(t, st=B): return Paragraph(t, st)

def table(rows, widths):
    t = Table([[P(esc(c), SH if i == 0 else S) for c in r] for i, r in enumerate(rows)], colWidths=widths, repeatRows=1, hAlign='LEFT')
    t.setStyle(TableStyle([('GRID', (0, 0), (-1, -1), 0.5, colors.black), ('LINEBELOW', (0, 0), (-1, 0), 1.5, colors.HexColor(ACCENT)),
                           ('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LEFTPADDING', (0, 0), (-1, -1), 5), ('RIGHTPADDING', (0, 0), (-1, -1), 5),
                           ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 5)]))
    return t

def md_table(rows):
    out = ['| ' + ' | '.join(rows[0]) + ' |', '|' + '---|' * len(rows[0])]
    out += ['| ' + ' | '.join(str(c).replace('|', '/') for c in r) + ' |' for r in rows[1:]]
    return '\n'.join(out)

def footer_cb(lang, title, numbered=True):
    """Footer of every page: EU label, AI note and date flush left, page number flush right (no page number on a one-page PDF) – body size (see common.rl_footer)."""
    def cb(c, d):
        c.saveState(); rl_footer(c, d.leftMargin + 6, d.pagesize[0] - d.rightMargin - 6, 12 * mm, B.fontSize, d.page if numbered else None, title, lang); c.restoreState()
    return cb

def build_pdf(path, flow, lang, footer_title, **kw):
    """A PDF of one page carries no page number: build with numbers, count the pages, rebuild without if it is a single page."""
    from pypdf import PdfReader
    for numbered in (True, False):
        cb = footer_cb(lang, footer_title, numbered)
        SimpleDocTemplate(path, **kw).build(list(flow), onFirstPage=cb, onLaterPages=cb)
        if len(PdfReader(path).pages) > 1: break   # several pages: keep the numbers; one page: second pass without number

def readme_section(lang, spec, docs, mixes, layout):
    i = load_i18n(lang); R = i['readme']; RM = i['readme_more']; meta = spec.get('meta', {})
    title = meta.get('title', ''); md = []; fl = []
    md.append(f"# {R['title'].format(title=title)}\n"); fl.append(P(esc(R['title'].format(title=title)), H1))
    md.append(f"**{R['poc']}**\n"); fl += [Spacer(1, 4), P(esc(R['poc']))]
    intro = R['intro'].format(source=docs.get('source_file', ''))
    if i.get('skill_name'): intro += ' ' + i.get('made_with', 'Made with {name}.').format(name=i['skill_name'])
    md.append(intro + '\n'); fl += [Spacer(1, 4), P(esc(intro))]
    # work details with sources / approval
    rows = [RM['meta_cols']]
    src = {m['field']: m for m in docs.get('meta_sources', [])}
    for f in ('title', 'subtitle', 'lyricist', 'composer', 'arranger'):
        if meta.get(f):
            s = src.get(f, {}); st = R['confirmed'] if s.get('approved') else (R['unconfirmed'] if s else '')
            rows.append([RM['fields'][f], meta[f], s.get('url', ''), st])
    md.append(f"## {R['meta_h']}\n\n" + md_table(rows) + '\n'); fl += [P(R['meta_h'], H2), table(rows, [30 * mm, 50 * mm, 62 * mm, 28 * mm])]
    dl = load_i18n(spec.get('language', 'en'))['delivery']   # folder names are those of the package, in both README halves
    rows = [[R['col_folder'], R['col_content'], R['col_use']],
            [dl['scores']] + R['f_scores'], [dl['practice']] + R['f_practice'],
            [dl['docs']] + R['f_docs'], [dl['tools']] + R['f_tools']]
    pv = RM['per_voice'].format(practice=dl['practice'])
    mrows = [rows[0]] + [[f'[{r[0]}](../{r[0]}/)'] + r[1:] for r in rows[1:]]   # Markdown only: folder names link to the sibling folders of the package
    md.append(f"## {R['folders_h']}\n\n" + md_table(mrows) + '\n\n' + pv + '\n')
    fl += [P(R['folders_h'], H2), table(rows, [36 * mm, 74 * mm, 60 * mm]), Spacer(1, 3), P(esc(pv), S)]
    if mixes:
        L = mixes['levels']; st = i['stages']
        nm = lambda k: re.sub(r'^\d+_', '', st[k]).replace('_', ' ')   # stage name without folder number
        no = R['stage_nos']
        rows = [[R['col_no'], R['col_stage'], R['col_mix'], R['col_purpose']],
                [no['solo'], nm('solo')] + R['s_solo'], [no['accomp'], nm('accomp'), R['s_accomp'][0].format(mel=L['melody'], acc=L['accomp']), R['s_accomp'][1]],
                [no['choir'], nm('choir'), R['s_choir'][0].format(near=L['near'], second=L['second'], far=L['far']), R['s_choir'][1]],
                [no['tutti'], i['files']['tutti']] + R['s_tutti']]
        md.append(f"## {R['stages_h']}\n\n" + md_table(rows) + '\n'); fl += [P(R['stages_h'], H2), table(rows, [14 * mm, 32 * mm, 78 * mm, 46 * mm])]
        t = mixes['tempo']; beat = i.get('beats', {}).get(t['beat'], t['beat'])
        tempo_txt = (f"{t.get('text')}, " if t.get('text') else '') + f"{beat} = {t['bpm']}"
        items = [x.format(soundfont=mixes['soundfont'], lufs=mixes['lufs'], tempo=tempo_txt, slow_pct=t.get('slow_pct', 75), slow=i['slow']) for x in R['sound_items']]
        if os.path.basename(mixes['soundfont']).startswith('GeneralUser'): items.append(R['sound_generaluser'])
        md.append(f"## {R['sound_h']}\n\n" + '\n'.join('- ' + x for x in items) + '\n'); fl += [P(R['sound_h'], H2)] + [P('• ' + esc(x)) for x in items]
    if layout:
        sc = R.get('score_line', 'A4, {pages} pages × {spp} systems, staff space {mm} mm').format(pages=layout['pages'], spp=layout['systems_per_page'], mm=(str(layout['staff_space_mm']) if lang == 'en' else str(layout['staff_space_mm']).replace('.', ',')))
        md.append(f"## {R['score_h']}\n\n- {sc}\n"); fl += [P(R['score_h'], H2), P('• ' + esc(sc))]
    rt = spec.get('rights') or {}
    if has_rights(spec):   # nothing is written about rights if the user gave no information and the source prints none
        rlines = [R['rights_base']] + ([R['rights_status'][rt['status']]] if rt.get('status') in R['rights_status'] else [])
        if rt.get('reference'): rlines.append(R['rights_ref'].format(reference=rt['reference']))
        if rt.get('note'): rlines.append(R['rights_note'].format(note=rt['note']))
        if rt.get('notice'): rlines.append(R['rights_notice'].format(notice=rt['notice']))
        md.append(f"## {R['rights_h']}\n\n" + '\n\n'.join(rlines) + '\n'); fl += [P(R['rights_h'], H2)] + [P(esc(x)) for x in rlines]
    md.append(f"## {R['ai_h']}\n\n{R['ai_text']}\n"); fl += [P(R['ai_h'], H2), P(esc(R['ai_text']))]
    tx = docs.get('texts', {}).get(lang, {})
    for key, head in (('notes', R['notes_h']), ('open', R['open_h'])):
        items = tx.get(key) or []
        if items:
            md.append(f"## {head}\n\n" + '\n'.join('- ' + x for x in items) + '\n'); fl += [P(head, H2)] + [P('• ' + esc(x)) for x in items]
    urls = [m['url'] for m in docs.get('meta_sources', []) if m.get('url')]
    if urls:
        md.append(f"## {R['sources_h']}\n\n" + '\n'.join(f'- <{u}>' for u in dict.fromkeys(urls)) + '\n')
        fl += [P(R['sources_h'], H2)] + [P('• ' + esc(u), S) for u in dict.fromkeys(urls)]
    return '\n'.join(md), fl

def main():
    ap = argparse.ArgumentParser(); ap.add_argument('spec'); ap.add_argument('docs'); ap.add_argument('outdir')
    ap.add_argument('--workdir', required=True); ap.add_argument('--mixes'); ap.add_argument('--layout')
    A = ap.parse_args(); os.makedirs(A.outdir, exist_ok=True)
    spec = json.load(open(A.spec, encoding='utf-8')); docs = json.load(open(A.docs, encoding='utf-8'))
    mixes = json.load(open(A.mixes, encoding='utf-8')) if A.mixes else None
    layout = json.load(open(A.layout, encoding='utf-8')) if A.layout else None
    lang = spec.get('language', 'en'); i = load_i18n(lang); title = spec.get('meta', {}).get('title', '')
    # README (bilingual)
    langs = [lang] + ([] if lang == 'en' else ['en'])
    md_all, fl_all = [], []
    for k, L in enumerate(langs):
        md, fl = readme_section(L, spec, docs, mixes, layout)
        md_all.append(md); fl_all += fl
        if k < len(langs) - 1: fl_all.append(PageBreak()); md_all.append('\n---\n')
    open(os.path.join(A.outdir, 'README.md'), 'w', encoding='utf-8').write('\n'.join(md_all).rstrip() + f'\n\n{md_block(lang, title)}\n\n')
    build_pdf(os.path.join(A.outdir, 'README.pdf'), fl_all, lang, title, pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN,
              bottomMargin=22 * mm, title='README')
    # log this step first, so the check log below already shows the current run
    _corr = docs.get('corrections', []); _unc = sum(1 for c in _corr if c.get('status') == 'uncertain')
    log_check(A.workdir, 6, 'make_docs', 'warn' if _unc else 'pass', f'{len(_corr)} correction-log entries, {_unc} uncertain')
    if (spec.get('rights') or {}).get('status') in ('public_domain', 'licensed', 'own'): log_check(A.workdir, 6, 'rights', 'pass', f"status {spec['rights']['status']}")   # no rights information: no log row either
    # Check log
    Pr = i['protocol']; ph = i['phases']; checks = read_checks(A.workdir)
    rows = [[Pr['col_phase'], Pr['col_check'], Pr['col_result'], Pr['col_note']]]
    latest = {}
    for c in checks:
        if c['check'] in ('package', 'share_folders'): continue   # the ZIP check cannot be inside the ZIP; share_folders is a retired check of earlier skill versions
        key = (c['phase'], c['check'], c['note']) if c['check'] in ('question_asked', 'answer_received') else (c['phase'], c['check'])   # one row per check (latest run), one per stop for the questions
        latest[key] = c
    def note_(t):
        for pat, rep in i.get('protocol_notes', []):
            if re.match(pat, t): return re.sub(r'(?<=\d)\.(?=\d)', ',', re.sub(pat, rep, t)) if lang == 'de' else re.sub(pat, rep, t)   # decimal comma in German
        return t
    for key_, c in sorted(latest.items(), key=lambda kv: (kv[0][0], list(latest).index(kv[0]))):
        phase_, chk_ = key_[0], key_[1]
        rows.append([f"{phase_} {ph.get(str(phase_), '')}", chk_, Pr.get(c['result'], c['result']), note_(c['note'])])
    name = safe(i['files']['protocol'])
    md = (f"# {Pr['title'].format(title=title)}\n\n{i['protocol_intro']}\n\n" + md_table(rows)).rstrip() + f"\n\n{md_block(lang, title)}\n\n"
    open(os.path.join(A.outdir, f'{name}.md'), 'w', encoding='utf-8').write(md)
    build_pdf(os.path.join(A.outdir, f'{name}.pdf'),
              [P(esc(Pr['title'].format(title=title)), H1), P(esc(i['protocol_intro']), S), Spacer(1, 6), table(rows, [36 * mm, 38 * mm, 28 * mm, 155 * mm])],
              lang, title, pagesize=landscape(A4), leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN, bottomMargin=22 * mm, title=Pr['title'])
    # Correction log
    C = i['corr']; corr = docs.get('corrections', [])
    rows = [C['cols']]
    for k, c in enumerate(corr, 1):
        reason = c.get('reason', {}); reason = reason.get(lang) or reason.get('en', '') if isinstance(reason, dict) else reason
        rows.append([str(k), str(c.get('bar', '')), c.get('voice', ''), C['kinds'].get(c.get('kind'), c.get('kind', '')), c.get('source', ''),
                     c.get('result', ''), reason, C['status'].get(c.get('status'), c.get('status', ''))])
    cname = safe(i['files_more']['corrections'])
    md = (f"# {C['title'].format(title=title)}\n\n{C['intro']}\n\n" + (md_table(rows) if corr else C['none'])).rstrip() + f"\n\n{md_block(lang, title)}\n\n"
    open(os.path.join(A.outdir, f'{cname}.md'), 'w', encoding='utf-8').write(md)
    body = [P(esc(C['title'].format(title=title)), H1), P(esc(C['intro']), S), Spacer(1, 6)]
    body.append(table(rows, [9 * mm, 13 * mm, 18 * mm, 22 * mm, 44 * mm, 44 * mm, 72 * mm, 35 * mm]) if corr else P(esc(C['none'])))
    build_pdf(os.path.join(A.outdir, f'{cname}.pdf'), body, lang, title, pagesize=landscape(A4), leftMargin=MARGIN, rightMargin=MARGIN, topMargin=MARGIN,
              bottomMargin=22 * mm, title=C['title'])
    unc = sum(1 for c in corr if c.get('status') == 'uncertain')
    print(f'README.md/.pdf, {name}.md/.pdf, {cname}.md/.pdf written to {A.outdir} | corrections: {len(corr)} (uncertain: {unc})')


if __name__ == '__main__':
    main()
