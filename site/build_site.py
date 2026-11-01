#!/usr/bin/env python3
"""Builds docs/de/index.html (de), docs/en/index.html (en), css/site.css, js/site.js for the landing page.
Level data comes from the skill itself (make_audio.stages), so the headphone graphic cannot drift from the audio."""
import re, os, sys, json, hashlib
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'choir-practice', 'scripts'))
import make_audio as M
OUT = os.path.join(HERE, '..', 'docs')
GH = 'https://github.com/vbth/choir-practice'
PROFILE = 'https://github.com/vbth'
SITE = 'https://choir-practice-skill.pages.dev/'
GHICON = '<svg class="ghi" viewBox="0 0 16 16" width="22" height="22" aria-hidden="true" focusable="false"><path fill="currentColor" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"/></svg>'

def ext(html):
    """External links open in a new tab."""
    return re.sub(r'<a ([^>]*href="https?://[^"]*"[^>]*)>', lambda m: '<a ' + m.group(1) + ' target="_blank" rel="noopener noreferrer">', html)
NB_BLOCKS = re.compile(r'<(p|li|h1|h2|h3|h4|figcaption|dd|dt|summary|label)(\s[^>]*)?>(.*?)</\1>', re.S)
NB_FOOTER = re.compile(r'(<footer>.*?</footer>)', re.S)

def _glue(inner):
    """Joins the last two words of an element (or of each line before a <br>) with a non-breaking space, so a line never ends with one word alone."""
    if '<button' in inner or '<svg' in inner: return inner
    out = []
    for seg in re.split(r'(<br\s*/?>)', inner):
        if seg.startswith('<br'): out.append(seg); continue
        toks = re.split(r'(<[^>]+>)', seg)
        for i in range(len(toks) - 1, -1, -1):
            if toks[i].startswith('<') or ' ' not in toks[i]: continue
            k = toks[i].rindex(' ')
            if k == len(toks[i]) - 1 and not toks[i].strip(): k = len(toks[i]) - 1
            if not ''.join(t for t in toks[:i] if not t.startswith('<')) + toks[i][:k]: break   # nothing before the space: leave it
            toks[i] = toks[i][:k] + '&nbsp;' + toks[i][k + 1:]; break
        out.append(''.join(toks))
    return ''.join(out)

def nobreak(html):
    """Build rule: no line of the page ends with a single word. The last space of every text block (and of every line before a <br>) becomes
    a non-breaking space; the footer lines too. Applied to the body only. Texts set by the page script do the same (nb() in site.js)."""
    head, sep, body = html.partition('<body')
    body = NB_BLOCKS.sub(lambda m: f'<{m.group(1)}{m.group(2) or ""}>{_glue(m.group(3))}</{m.group(1)}>', body)
    body = NB_FOOTER.sub(lambda m: re.sub(r'<span>((?:(?!<span).)*?)</span>', lambda n: '<span>' + _glue(n.group(1)) + '</span>', m.group(1)), body)
    return head + sep + body

IMG_REF = re.compile(r'(\bimg/([A-Za-z0-9_.-]+\.(?:png|jpg|svg)))(?=["\s,])')

def bust(html):
    """Cache busting: every image reference of the page (src, srcset, preload, og:image) gets ?v=<hash of the file>, so a changed image
    (new footer in the example pages, new header) is fetched again instead of served from the browser or CDN cache."""
    def one(m):
        f = os.path.join(OUT, 'img', m.group(2))
        if not os.path.exists(f): return m.group(0)
        return m.group(1) + '?v=' + hashlib.sha1(open(f, 'rb').read()).hexdigest()[:8]
    return IMG_REF.sub(one, html)

REL = GH + '/releases/download/v1.0.0/'   # example ZIPs: assets of the release v1.0.0
ZIPS = [('Deutsch: Alle meine Entchen', 'Chor_Uebungen_Alle_meine_Entchen.zip'), ('English: All My Ducklings', 'Choir_Practice_All_My_Ducklings.zip')]   # make_previews.py renders both
ZIP_OF = {'de': ZIPS[0][1], 'en': ZIPS[1][1]}   # each page links only the package of its own language
VERSION = open(os.path.join(HERE, '..', 'choir-practice', 'VERSION'), encoding='utf-8').read().strip()
YEAR = re.search(r'\*\*Date:\*\* (\d{4})', open(os.path.join(HERE, '..', 'choir-practice', 'session-handoff.md'), encoding='utf-8').read()).group(1)   # year of the last release (release.py rewrites the date there), shown in the footer

SEAT = ['S', 'A', 'T', 'B']
ST = M.stages(SEAT, 'S')
spread = {v: round(-0.5 + k / 3, 2) for k, v in enumerate(SEAT)}
ST['tutti'] = {own: [[v, spread[v], M.LV['tutti'], 'own'] for v in SEAT] for own in SEAT}

T = {
 'de': {
  'html': 'de', 'name': 'Choir Practice Skill', 'title': 'Choir Practice Skill – Deine Chorstimme. Deine Noten. Überall lesen, hören und singen.', 'other': ('../en/', 'EN'), 'self_prefix': '../', 'assets': '../',
  'desc': 'Dokumentation eines agentischen KI-Musik-Workflows und -Skills entwickelt für und mit Claude Code als privates Code-Experiment. Es ist nur ein „Proof of Concept“. Aus Chornoten entsteht ein „KI-geprüftes“ ZIP, in dem sich für jede Stimme 10 Aufnahmen zum Üben befinden.',
  'ids': {'start': 'start', 'ablauf': 'ablauf', 'ueben': 'ueben', 'paket': 'beispiel', 'rechte': 'rechte-und-ki', 'lizenz': 'lizenzen'},
  'menu': [('start', 'Start'), ('ablauf', 'Ablauf'), ('ueben', 'Üben'), ('paket', 'Beispiel'), ('rechte', 'Rechte & KI'), ('lizenz', 'Lizenzen')],
  'menu_label': 'Menü', 'skip': 'Zum Inhalt', 'theme_to_dark': 'Zum dunklen Modus wechseln', 'theme_to_light': 'Zum hellen Modus wechseln',
  'h1': 'Deine Chorstimme. Deine Noten. Überall lesen, hören und singen.',
  'lead': 'Dokumentation eines agentischen KI-Musik-Workflows und -Skills entwickelt für und mit Claude Code als privates Code-Experiment. Es ist nur ein „Proof of Concept“. Aus Chornoten entsteht ein „KI-\u2060geprüftes“ ZIP, in dem sich für jede Stimme 10 Aufnahmen zum Üben befinden.',
  'cta': 'Beispiel ansehen',
  'ai': 'KI-generiert. Nutzung auf eigene Verantwortung.', 'foot_note': 'choir-practice – KI-Musik-Workflow/-Skill für Claude.', 'foot_site': 'Startseite',
  'facts': [('4', 'Stufen je Stimme'), ('2', 'Klänge: Chor und Klavier'), ('2', 'Fassungen: normal und langsam'), ('42', 'Aufnahmen im Beispiel')],
  'inh_h': 'Inhalte', 'paket_h': 'Beispiel', 'paket_p': 'Im ZIP liegen vier Ordner. Die Stimmen-ZIPs in 2_Ueben sind fertig zum Weitergeben, ihr Inhalt steht zuletzt. Einen Ordner anklicken.',
  'tree': [
   ('1_Noten', 'Noten (PDF), MusicXML und MIDI.', [
    '1_Noten_<Titel>_Scan.pdf', '2_Noten_<Titel>.pdf', '3_MusicXML_<Titel>_Chor.musicxml', '4_MusicXML_<Titel>_Klavier.musicxml',
    '5_MIDI_<Titel>/', '  S_MIDI_<Titel>/  (je Stimme: S, A, T, B)', '    1 bis 5_S_<Titel>_Chor_und_Klavier_*.mid  (zehn Dateien)', '  Tutti_MIDI_<Titel>/', '    <Titel>_Tutti_Chor.mid', '    <Titel>_Tutti_Klavier.mid']),
   ('2_Ueben', 'Übersicht, Anleitung und je Stimme eine fertige ZIP-Datei.', [
    '1_Uebersicht.pdf', '2_Anleitung.pdf', 'S_Ueben_<Titel>.zip', 'A_Ueben_<Titel>.zip', 'T_Ueben_<Titel>.zip', 'B_Ueben_<Titel>.zip']),
   ('3_Dokumentation', 'README, Prüfprotokoll, Korrekturprotokoll und Session-Handoff.', [
    '1_README_<Titel>.md und .pdf', '2_Pruefprotokoll_<Titel>.md und .pdf', '3_Korrekturprotokoll_<Titel>.md und .pdf', '4_Session_Handoff_<Titel>.md']),
   ('4_Werkzeuge', 'Projektdaten und der Skill selbst, zum Weiterarbeiten.', [
    '1_Projektdaten_<Titel>/', '  score.json', '  docs.json', '  layout.json', '  mixes.json',
    '2_SKILL_choir_practice_v<Version>/', '  choir_practice.skill', '  README.md', '  session_handoff.md']),
   ('S_Ueben_<Titel>.zip', 'Inhalt jeder Stimmen-ZIP (hier Sopran): alles, was eine Stimme braucht.', [
    '1_S_Anleitung.pdf', '2_S_Noten_<Titel>.pdf', '3_S_Audio_Chorklang_<Titel>/', '  1 bis 6_S_<Titel>_Chor_*.mp3  (allein, mit Klavier, jeweils langsam und normal; eigene Stimme lauter; alle gleich laut)',
    '4_S_Audio_Klavierklang_<Titel>/', '  1 bis 6_S_<Titel>_Klavier_*.mp3  (dieselben sechs)']),
  ],
  'ablauf_h': 'Ablauf', 'ablauf_p': 'Zwölf Schritte, zwei Stopps mit Rückfragen. Unten einen Schritt anklicken, hier erscheinen die Details.',
  'who_claude': 'Claude', 'who_you': 'Nutzer',
  'steps': [
   ('Aufruf', 'you', 'Skill in Claude starten, noch ohne Noten.', ''),
   ('Stopp A', 'both', 'Angaben über die Rechte.', 'Alles bereit?'),
   ('Noten anhängen', 'you', 'Als PDF oder Foto.', ''),
   ('Sichtung', 'claude', 'Claude liest die Seiten und prüft die Qualität.', 'Alles verstanden?'),
   ('Stopp B', 'you', 'Titel, Stimmen und Tempo bestätigen.', ''),
   ('Notenerfassung', 'claude', 'Claude überträgt die Noten.', 'Alle Takte und Stimmen erfasst?'),
   ('Korrekturlesen', 'claude', 'Claude vergleicht das Ergebnis zweimal mit der Vorlage: erst Töne, dann Text.', 'Töne und Text wie in der Vorlage? Sonst zurück zu Schritt 6.'),
   ('Endgültiger Notensatz', 'claude', 'Claude setzt die Noten sauber, mit Titelblatt.', 'Gut lesbar?'),
   ('Audio', 'claude', 'Claude erzeugt für jede Stimme die Audio-Dateien zum Üben.', 'Passt jede Stimme zu den Noten?'),
   ('Paket', 'claude', 'Claude schreibt die Anleitungen und packt alles zusammen.', 'Alle Inhalte vorhanden?'),
   ('Abschluss', 'both', 'Claude macht Verbesserungsvorschläge. Die Entscheidung über die Umsetzung liegt beim Nutzer.', ''),
   ('Herunterladen', 'you', 'ZIP herunterladen und die Audiodateien der einzelnen Stimmen an den Chor weitergeben.', ''),
  ],
  'ueben_h': 'Üben', 'ueben_p': 'Jede Stimme bekommt ihren eigenen Mix. Jeweils eine Stimme liegt in der Mitte, die anderen sind nach der Chorsitzordnung im Stereobild verteilt. Du wählst Stimme, Stufe, Klang und Tempo. Der Kopfhörer zeigt die Verteilung, und du hörst genau diesen Mix. Beim Erzeugen der Dateien wählst du den Klang: MuseScore General oder GeneralUser GS. Mit Kopfhörern klingt es am besten. Die Aufnahmen sind mechanisch exakt, ohne Interpretation.',
  'gate_lbl': 'Prüfung am Ende', 'voice_label': 'Stimme', 'stage_label': 'Stufe',
  'voices': {'S': 'Sopran', 'A': 'Alt', 'T': 'Tenor', 'B': 'Bass'},
  'stages': {'solo': 'Allein', 'accomp': 'Mit Begleitung', 'choir': 'Im Chor', 'tutti': 'Tutti'},
  'sound_label': 'Klang', 'sounds': {'choir': 'Chor', 'piano': 'Klavier'}, 'tempo_label': 'Tempo', 'tempos': {'normal': 'Normal', 'slow': 'Langsam'}, 'sound_names': {'choir': 'Chorklang', 'piano': 'Klavierklang'}, 'slow_name': 'langsam',
  'stage_txt': {
   'solo': 'Nur die gewählte Stimme, in der Mitte.',
   'accomp': 'Die gewählte Stimme, die Melodie leiser, dazu die Klavierbegleitung aller Stimmen.',
   'choir': 'Die anderen Stimmen sitzen wie im Chor: Nachbarn links und rechts etwas leiser, weiter entfernte noch leiser.',
   'tutti': 'Alle Stimmen gleich laut.'}, 'own_lbl': 'Gesang', 'acc_lbl': 'Klavier',
  'dl_p': 'Das Ergebnis: Aufnahmen zum Üben für jede Stimme, Anleitungen und Protokolle.', 'dl_btn': 'Download', 'dl_ttl': 'Alle meine Entchen', 'dl_meta': 'ZIP · ca. 36 MB · Noten, Aufnahmen, Anleitungen',
  'tutti_all': 'Tutti, alle Stimmen', 'pl_title': 'Alle meine Entchen', 'pl_play': 'Wiedergabe', 'pl_pause': 'Pause', 'pl_loop': 'Wiederholen', 'pl_vol': 'Lautstärke', 'pl_mute': 'Stumm', 'pl_seek': 'Position',
  'pl_cover': 'Albumcover des Beispielpakets', 'mx_h': 'Mixer', 'mx_tempo': 'Tempo', 'mx_all': 'Gesamt', 'mx_p': 'Stimmen und Klavier einzeln ein- und ausschalten (antippen oder -klicken) und in der Lautstärke regeln, während es läuft.', 'mx_acc': 'Klavier', 'mx_on': 'an / aus',
  'rechte_h': 'Rechte & KI',
  'rechte_items': [
   ('Rechte', 'Bevor Noten verarbeitet werden, fragt der Skill nach den Rechten. Diese Angaben werden danach in der README-Datei vermerkt. Ob die Noten verarbeitet und weitergegeben werden dürfen, richtet sich nach dem Urheber- und Lizenzrecht, unter dem sie stehen.'),
   ('KI-Kennzeichnung', 'Alles, was der Skill erzeugt, ist als KI-Inhalt gekennzeichnet, sowohl mit dem EU-Label für KI-generierte Inhalte als auch im Text und in den Metadaten der Dokumente.'),
  ],
  'lic_h': 'Lizenzen', 'lic_link': 'PolyForm Noncommercial License 1.0.0', 'lic_p': ', frei für nichtkommerzielle Nutzung.',
  'duck': '„Sonntagmorgen, er übt mal wieder für seinen Chor\n… und ich darf es ausbaden!“', 'duck_by': 'Ente eines Tenors',
  'lic_third_link': 'Komponenten von Drittanbietern', 'foot_profile': 'GitHub-Repository vbth/choir-practice', 'private': 'privates Projekt', 'og_alt': 'Ein Mann mit Kopfhörern steht in einer alten Badewanne und singt vom Notenblatt, neben ihm schwimmt eine Quietscheente, rote Noten schweben im Raum',
  'alt_cover': 'Deckblatt des Beispielpakets', 'alt_page1': 'Erste Notenseite des Beispielpakets', 'alt_page2': 'Zweite Notenseite des Beispielpakets', 'alt_ai': 'EU-Label AI',
  'ai_label': 'AI', 'top': 'Nach oben',
 },
 'en': {
  'html': 'en', 'name': 'Choir Practice Skill', 'title': 'Choir Practice Skill – Your voice. Your sheet music. Read, listen, and sing anywhere.', 'other': ('../de/', 'DE'), 'self_prefix': '../', 'assets': '../',
  'desc': 'Documentation of an agentic AI music workflow and skill developed for and with Claude Code as a private code experiment. It is only a “proof of concept”. A choir score goes in, and an “AI-checked” ZIP comes out with 10 practice recordings for every voice.',
  'ids': {'start': 'start', 'ablauf': 'workflow', 'ueben': 'practice', 'paket': 'example', 'rechte': 'rights-and-ai', 'lizenz': 'licences'},
  'menu': [('start', 'Start'), ('ablauf', 'Workflow'), ('ueben', 'Practice'), ('paket', 'Example'), ('rechte', 'Rights & AI'), ('lizenz', 'Licences')],
  'menu_label': 'Menu', 'skip': 'Skip to content', 'theme_to_dark': 'Switch to dark mode', 'theme_to_light': 'Switch to light mode',
  'h1': 'Your voice. Your sheet music. Read, listen, and sing anywhere.',
  'lead': 'Documentation of an agentic AI music workflow and skill developed for and with Claude Code as a private code experiment. It is only a “proof of concept”. A choir score goes in, and an “AI-checked” ZIP comes out with 10 practice recordings for every voice.',
  'cta': 'See the example',
  'ai': 'AI-generated. Use at your own risk.', 'foot_note': 'choir-practice – AI music workflow/skill for Claude.', 'foot_site': 'Home page',
  'facts': [('4', 'stages per voice'), ('2', 'sounds: choir and piano'), ('2', 'versions: normal and slow'), ('42', 'recordings in the example')],
  'inh_h': 'Contents', 'paket_h': 'Example', 'paket_p': 'The ZIP holds four folders. The voice ZIPs in 2_Practice are ready to hand out, their contents are listed last. Click a folder.',
  'tree': [
   ('1_Scores', 'Score (PDF), MusicXML and MIDI.', [
    '1_Score_<Title>_Scan.pdf', '2_Score_<Title>.pdf', '3_MusicXML_<Title>_Choir.musicxml', '4_MusicXML_<Title>_Piano.musicxml',
    '5_MIDI_<Title>/', '  S_MIDI_<Title>/  (one per voice: S, A, T, B)', '    1 to 5_S_<Title>_Choir_and_Piano_*.mid  (ten files)', '  Tutti_MIDI_<Title>/', '    <Title>_Tutti_Choir.mid', '    <Title>_Tutti_Piano.mid']),
   ('2_Practice', 'Overview, guide and one ready ZIP per voice.', [
    '1_Overview.pdf', '2_Guide.pdf', 'S_Practice_<Title>.zip', 'A_Practice_<Title>.zip', 'T_Practice_<Title>.zip', 'B_Practice_<Title>.zip']),
   ('3_Documentation', 'README, check log, correction log and session handoff.', [
    '1_README_<Title>.md and .pdf', '2_Check_Log_<Title>.md and .pdf', '3_Correction_Log_<Title>.md and .pdf', '4_Session_Handoff_<Title>.md']),
   ('4_Tools', 'Project data and the skill itself, for further work.', [
    '1_Project_Data_<Title>/', '  score.json', '  docs.json', '  layout.json', '  mixes.json',
    '2_SKILL_choir_practice_v<Version>/', '  choir_practice.skill', '  README.md', '  session_handoff.md']),
   ('S_Practice_<Title>.zip', 'Contents of every voice ZIP (soprano shown): everything one voice needs.', [
    '1_S_Guide.pdf', '2_S_Score_<Title>.pdf', '3_S_Audio_Choir_Sound_<Title>/', '  1 to 6_S_<Title>_Choir_*.mp3  (solo, with piano, each slow and normal; own voice louder; all voices equal)',
    '4_S_Audio_Piano_Sound_<Title>/', '  1 to 6_S_<Title>_Piano_*.mp3  (the same six)']),
  ],
  'ablauf_h': 'Workflow', 'ablauf_p': 'Twelve steps, two stops with questions for you. Click a step below, its details appear here.',
  'who_claude': 'Claude', 'who_you': 'You',
  'steps': [
   ('Call', 'you', 'Start the skill in Claude, still without a score.', ''),
   ('Stop A', 'both', 'Details on the rights.', 'All set?'),
   ('Attach score', 'you', 'As PDF or photo.', ''),
   ('Survey', 'claude', 'Claude reads the pages and checks the quality.', 'Everything understood?'),
   ('Stop B', 'you', 'Confirm title, voices and tempo.', ''),
   ('Transcription', 'claude', 'Claude transcribes the score.', 'All bars and voices captured?'),
   ('Proofreading', 'claude', 'Claude compares the result twice with your original: notes first, then lyrics.', 'Notes and lyrics as in your original? Otherwise back to step 6.'),
   ('Final engraving', 'claude', 'Claude sets the score cleanly, with a title page.', 'Easy to read?'),
   ('Audio', 'claude', 'Claude creates the practice recordings for every voice.', 'Does every voice match the score?'),
   ('Package', 'claude', 'Claude writes the guides and packs everything together.', 'All contents there?'),
   ('Closing', 'both', 'Claude suggests improvements. You decide how they are implemented.', ''),
   ('Download', 'you', 'Download the ZIP and pass the audio files of the individual voices on to the choir.', ''),
  ],
  'ueben_h': 'Practice', 'ueben_p': 'Every voice gets its own mix. In each mix one voice sits in the middle, the others are spread across the stereo image like the choir stands. You pick a voice, a stage, a sound and a tempo. The headphones show the distribution, and you hear exactly that mix. When the files are created you choose the sound: MuseScore General or GeneralUser GS. It sounds best on headphones. The recordings are mechanically exact, without interpretation.',
  'gate_lbl': 'Check at the end', 'voice_label': 'Voice', 'stage_label': 'Stage',
  'voices': {'S': 'Soprano', 'A': 'Alto', 'T': 'Tenor', 'B': 'Bass'},
  'stages': {'solo': 'Solo', 'accomp': 'With accompaniment', 'choir': 'In the choir', 'tutti': 'Tutti'},
  'sound_label': 'Sound', 'sounds': {'choir': 'Choir', 'piano': 'Piano'}, 'tempo_label': 'Tempo', 'tempos': {'normal': 'Normal', 'slow': 'Slow'}, 'sound_names': {'choir': 'choir sound', 'piano': 'piano sound'}, 'slow_name': 'slow',
  'stage_txt': {
   'solo': 'Only the selected voice, in the middle.',
   'accomp': 'The selected voice, the melody quieter, plus the piano accompaniment of all voices.',
   'choir': 'The other voices sit as in the choir: neighbours left and right a little quieter, voices further away quieter still.',
   'tutti': 'All voices equally loud.'}, 'own_lbl': 'Singing', 'acc_lbl': 'Piano',
  'dl_p': 'The result: practice recordings for every voice, guides and logs.', 'dl_btn': 'Download', 'dl_ttl': 'All My Ducklings', 'dl_meta': 'ZIP · ca. 36 MB · Scores, recordings, guides',
  'tutti_all': 'Tutti, all voices', 'pl_title': 'All My Ducklings', 'pl_play': 'Play', 'pl_pause': 'Pause', 'pl_loop': 'Repeat', 'pl_vol': 'Volume', 'pl_mute': 'Mute', 'pl_seek': 'Position',
  'pl_cover': 'Album cover of the example pack', 'mx_h': 'Mixer', 'mx_tempo': 'Tempo', 'mx_all': 'Master', 'mx_p': 'Switch each voice and the piano on and off (tap or click) and set its level while it plays.', 'mx_acc': 'Piano', 'mx_on': 'on / off',
  'rechte_h': 'Rights & AI',
  'rechte_items': [
   ('Rights', 'Before scores are processed, the skill asks about the rights. These details are then recorded in the README file. Whether the scores may be processed and passed on depends on the copyright and licence law they are subject to.'),
   ('AI labelling', 'Everything the skill creates is labelled as AI content, both with the EU label for AI-generated content and in the text and metadata of the documents.'),
  ],
  'lic_h': 'Licences', 'lic_link': 'PolyForm Noncommercial License 1.0.0', 'lic_p': ', free for non-commercial use.',
  'duck': '“Sunday morning, he’s rehearsing for his choir\n… and I’m the one who has to face the music.”', 'duck_by': 'A tenor’s duck',
  'lic_third_link': 'Third-party components', 'foot_profile': 'GitHub repository vbth/choir-practice', 'private': 'private project', 'og_alt': 'A man with headphones stands in an old bathtub and sings from a sheet of music, a rubber duck floats beside him, red notes drift through the room',
  'alt_cover': 'Title page of the example pack', 'alt_page1': 'First score page of the example pack', 'alt_page2': 'Second score page of the example pack', 'alt_ai': 'EU label AI',
  'ai_label': 'AI', 'top': 'Back to top',
 },
}

def asset_version():
    """Short hash of CSS and JS: appended to their URLs, so browsers and the Pages cache fetch changed files at once."""
    return hashlib.sha1((CSS + JS).encode('utf-8')).hexdigest()[:8]

def esc(s): return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')

def playlist(t):
    """Every recording of the example pack: per voice 2 sounds x (solo, with accompaniment: normal + slow; in the choir), plus tutti in both sounds."""
    def b(label, voice, stage, snd, tempo):
        v = f' data-voice="{voice}"' if voice else ''
        return f'<li><button type="button"{v} data-stage="{stage}" data-sound="{snd}" data-tempo="{tempo}" aria-pressed="false">{esc(label)}</button></li>'
    out = []
    for v, vn in t['voices'].items():
        it = []
        for snd, sn in t['sound_names'].items():
            for st in ('solo', 'accomp', 'choir'):
                for slow in ((False, True) if st != 'choir' else (False,)):
                    it.append(b(f"{t['stages'][st]}, {sn}" + (f", {t['slow_name']}" if slow else ''), v, st, snd, 'slow' if slow else 'normal'))
        out.append(f'<details data-voice="{v}"><summary>{esc(vn)}</summary><ul class="trk">{"".join(it)}</ul></details>')
    it = [b(f"{t['stages']['tutti']}, {sn}", None, 'tutti', snd, 'normal') for snd, sn in t['sound_names'].items()]
    out.append(f'<details data-tutti="1"><summary>{esc(t["tutti_all"])}</summary><ul class="trk">{"".join(it)}</ul></details>')
    return ''.join(out)

FAN_W = (160, 240, 320, 480, 720)   # widths written by make_previews.py: 160 and 240 CSS px at 1x, 2x, 3x

def fan_img(A, L, name, cls, alt):
    """Score page of the fan: one file per device pixel density (srcset), so the staff lines stay sharp."""
    srcset = ', '.join(f'{A}img/example-{name}-{L}-{w}.png {w}w' for w in FAN_W)
    return f'<img class="{cls}" src="{A}img/example-{name}-{L}-480.png" srcset="{srcset}" sizes="(max-width:520px) 160px, 240px" alt="{esc(alt)}" width="240" height="339" loading="lazy">'

# Renders one language version of the landing page; texts come from the dict T, structure and markup live here
# tick marks at the snap points (10 %) of the mixer sliders; left = half a thumb + the free track length times the step
SNAP = '<span class="tk" aria-hidden="true">' + ''.join(f'<i style="left:calc(var(--th)/2 + (100% - var(--th)) * {i / 10:g})"></i>' for i in range(1, 10)) + '</span>'

def page(L):
    t = T[L]; A = t['assets']
    I = t['ids']
    h1 = esc(t['h1']); k = h1.rfind('. ')                        # line break before the last sentence of the headline
    h1_html = h1[:k + 1] + '<br>' + h1[k + 2:] if k >= 0 else h1
    menu =''.join(f'<li><a href="#{I[a]}">{esc(n)}</a></li>' for a, n in t['menu'])
    facts = ''.join(f'<div><dt>{esc(a)}</dt><dd>{esc(b)}</dd></div>' for a, b in t['facts'])
    tree = ''.join(
        f'<div class="folder"><button type="button" aria-expanded="false" aria-controls="f{i}"><span class="fn">{esc(n)}</span><span class="fd">{esc(d)}</span></button>'
        f'<ul id="f{i}" hidden>' + ''.join(f'<li class="mono" style="padding-left:{(len(c)-len(c.lstrip()))*7+10}px">{esc(c.strip())}</li>' for c in ch) + '</ul></div>'
        for i, (n, d, ch) in enumerate(t['tree']))
    steps = ''.join(f'<li><button type="button" data-step="{i}" aria-pressed="false"><span class="n">{i+1}</span><span class="s">{esc(s[0])}</span></button></li>' for i, s in enumerate(t['steps']))
    rights = ''.join(f'<article><h3>{esc(h)}</h3><p>{esc(p)}</p></article>' for h, p in t['rechte_items'])
    METER = '<span class="mxmeter" data-meter="{}" aria-hidden="true">' + '<i></i>' * 16 + '</span>'
    mxmaster = f'<div class="mxr mxm"><span class="mxmlb">{esc(t["mx_all"])}</span>{METER.format("master")}<span class="mxf"><input type="range" id="mxmaster" class="mxv" min="0" max="100" step="10" value="100"aria-label="{esc(t["mx_all"])}">{SNAP}</span><span id="mxmp" class="mxp2 mono">100&nbsp;%</span></div>'
    mixrows = ''.join(
        f'<div class="mxr"><button type="button" class="mxb" data-stem="{k}" data-pan="{pan}" aria-pressed="true" title="{esc(t["mx_on"])}">{esc(n)}</button>'
        f'{METER.format(k)}<span class="mxf"><input type="range" class="mxv" min="0" max="100" step="10" value="100" aria-label="{esc(n)}">{SNAP}</span><span class="mxp2 mono">100&nbsp;%</span></div>'
        for k, n, pan in [(v.lower(), vn, round(-0.6 + 1.2 * i / 3, 2)) for i, (v, vn) in enumerate(t['voices'].items())] + [('acc', t['mx_acc'], 0)])
    mxtempos = '<input type="range" id="mxtempo" class="mxtrack" min="80" max="100" step="10" value="100" aria-label="' + esc(t['mx_tempo']) + '"><div class="mxtk"><span>80&nbsp;%</span><span>90&nbsp;%</span><span>100&nbsp;%</span></div>'
    voices = ''.join(f'<button type="button" data-voice="{v}" aria-pressed="false">{esc(n)}</button>' for v, n in t['voices'].items())
    stages = ''.join(f'<button type="button" data-stage="{k}" aria-pressed="false">{esc(n)}</button>' for k, n in t['stages'].items())
    sounds = ''.join(f'<button type="button" data-sound="{k}" aria-pressed="false">{esc(n)}</button>' for k, n in t['sounds'].items())
    tempos = ''.join(f'<button type="button" data-tempo="{k}" aria-pressed="false">{esc(n)}</button>' for k, n in t['tempos'].items())
    ai = open(os.path.join(OUT, 'img', 'ai-basic.svg'), encoding='utf-8').read()
    ai = ai[ai.index('<svg'):].replace('role="img"', 'role="img" class="ailabel" focusable="false"', 1)
    data = {'lang': L, 'seat': SEAT, 'mix': ST, 'voices': t['voices'], 'stages': t['stages'], 'stage_txt': t['stage_txt'], 'steps': t['steps'],
            'who': {'you': t['who_you'], 'claude': t['who_claude'], 'both': t['who_claude'] + ' + ' + t['who_you']}, 'own': t['own_lbl'], 'acc': t['acc_lbl'], 'gate': t['gate_lbl'],
            'sound_names': t['sound_names'], 'slow_name': t['slow_name'], 'slow': M.SLOW_PCT / 100, 'theme_to_dark': t['theme_to_dark'], 'theme_to_light': t['theme_to_light']}
    other_href, other_lbl = t['other']
    ld = {'@context': 'https://schema.org', '@type': 'SoftwareApplication', 'name': t['name'],
          'description': t['desc'], 'url': SITE + L + '/', 'inLanguage': L, 'softwareVersion': VERSION,
          'applicationCategory': 'MultimediaApplication', 'operatingSystem': 'Claude (skill)', 'image': {'@type': 'ImageObject', 'url': SITE + 'img/og.png', 'width': 2400, 'height': 1260, 'caption': t['og_alt']},
          'license': 'https://polyformproject.org/licenses/noncommercial/1.0.0', 'codeRepository': GH,
          'author': {'@type': 'Person', 'name': 'vbth', 'url': PROFILE},
          'offers': {'@type': 'Offer', 'price': '0', 'priceCurrency': 'EUR'}}
    ld_json = json.dumps(ld, ensure_ascii=False, indent=1).replace('</', '<\\/')
    return f'''<!doctype html>
<html lang="{t['html']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(t['title'])}</title>
<meta name="description" content="{esc(t['desc'])}">
<meta name="color-scheme" content="light dark">
<link rel="canonical" href="{SITE}{L}/">
<link rel="alternate" hreflang="de" href="{SITE}de/">
<link rel="alternate" hreflang="en" href="{SITE}en/">
<link rel="alternate" hreflang="x-default" href="{SITE}">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(t['name'])}">
<meta property="og:title" content="{esc(t['title'])}">
<meta property="og:description" content="{esc(t['desc'])}">
<meta property="og:url" content="{SITE}{L}/">
<meta property="og:locale" content="{'de_DE' if L=='de' else 'en_US'}">
<meta property="og:locale:alternate" content="{'en_US' if L=='de' else 'de_DE'}">
<meta property="og:image" content="{SITE}img/og.png">
<meta property="og:image:type" content="image/png">
<meta property="og:image:width" content="2400">
<meta property="og:image:height" content="1260">
<meta property="og:image:alt" content="{esc(t['og_alt'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{esc(t['title'])}">
<meta name="twitter:description" content="{esc(t['desc'])}">
<meta name="twitter:image" content="{SITE}img/og.png">
<meta name="twitter:image:alt" content="{esc(t['og_alt'])}">
<link rel="icon" href="{A}img/favicon.svg" type="image/svg+xml">
<link rel="icon" href="{A}favicon.ico" sizes="32x32">
<link rel="icon" href="{A}img/favicon-192.png" sizes="192x192" type="image/png">
<link rel="apple-touch-icon" href="{A}img/favicon-180.png">
<link rel="preload" href="{A}img/header.png" as="image" type="image/png" media="(prefers-color-scheme: light)">
<link rel="preload" href="{A}img/header-dark.png" as="image" type="image/png" media="(prefers-color-scheme: dark)">
<script>try{{var t=localStorage.getItem("theme");if(t==="light"||t==="dark")document.documentElement.setAttribute("data-theme",t)}}catch(e){{}}</script>
<link rel="stylesheet" href="{A}css/site.css?v={asset_version()}">
<script type="application/ld+json">
{ld_json}
</script>
</head>
<body>
<a class="skip" href="#start">{esc(t['skip'])}</a>
<header class="bar">
 <a class="brand" href="{SITE}{L}/" aria-label="{esc(t['name'])}"><img src="{A}img/logo.png" alt="" width="46" height="46"><span class="bt"><span class="bn">{esc(t['name'].rpartition(' ')[0])}</span> {esc(t['name'].rpartition(' ')[2])}</span></a>
 <button class="theme" type="button" aria-label="{esc(t['theme_to_dark'])}"><svg class="moon" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path d="M20 14.6A8.6 8.6 0 0 1 9.4 4 8.6 8.6 0 1 0 20 14.6z"/></svg><svg class="sun" viewBox="0 0 24 24" aria-hidden="true" focusable="false"><circle cx="12" cy="12" r="4"/><path d="M12 2.5v2.5M12 19v2.5M2.5 12H5M19 12h2.5M5.3 5.3l1.8 1.8M16.9 16.9l1.8 1.8M5.3 18.7l1.8-1.8M16.9 7.1l1.8-1.8"/></svg></button>
 <a class="lang" href="{other_href}" hreflang="{'en' if L=='de' else 'de'}" lang="{'en' if L=='de' else 'de'}">{other_lbl}</a>
 <button class="burger" type="button" aria-expanded="false" aria-controls="nav">{esc(t['menu_label'])}</button>
 <nav id="nav" aria-label="{esc(t['menu_label'])}"><ul>{menu}<li class="navlang"><a href="{other_href}" hreflang="{'en' if L=='de' else 'de'}" lang="{'en' if L=='de' else 'de'}">{'English' if L=='de' else 'Deutsch'}</a></li></ul></nav>
</header>
<main>
<figure class="banner"><picture><source media="(prefers-color-scheme: dark)" srcset="{A}img/header-dark.png"><img src="{A}img/header.png" alt="{esc(t['og_alt'])}. {esc(t['duck'].replace(chr(10), ' '))} — {esc(t['duck_by'])}" width="1280" height="640" fetchpriority="high" decoding="async"></picture>
<figcaption class="duck">{esc(t['duck']).replace(chr(10), ' <br class="dbr">')}<span class="by">— {esc(t['duck_by'])}</span></figcaption></figure>
<section id="start" class="hero">
 <h1>{h1_html}</h1>
 <p class="lead">{'<br><br>'.join(esc(x) for x in t['lead'].split(chr(10) * 2))}</p>
 <p class="cta"><a href="#{I['paket']}">{esc(t['cta'])}</a></p>
 <dl class="facts">{facts}</dl>
</section>
<section id="{I['ablauf']}"><h2><span class="num">01</span>{esc(t['ablauf_h'])}</h2>
 <p class="intro">{esc(t['ablauf_p'])}</p>
 <div id="stepbox" class="panel" aria-live="polite"></div>
 <ol class="chain">{steps}</ol>
</section>
<section id="{I['ueben']}"><h2><span class="num">02</span>{esc(t['ueben_h'])}</h2>
 <p class="intro">{esc(t['ueben_p'])}</p>
 <div class="listen" id="player" data-audio="{A}audio/" data-play="{esc(t['pl_play'])}" data-pause="{esc(t['pl_pause'])}">
  <div class="pbox">
   <img class="art" src="{A}img/cover-{L}.jpg" alt="{esc(t['pl_cover'])}" width="600" height="600" loading="lazy">
   <div class="pl">
    <p class="pt">{esc(t['pl_title'])}</p><p class="ps" id="plname" aria-live="polite"></p>
    <div class="pc"><button type="button" class="pbtn" aria-label="{esc(t['pl_play'])}"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path class="picon" data-c d="M7 4l13 8-13 8z" fill="currentColor"/></svg></button>
     <input type="range" id="plseek" min="0" max="1000" value="0" aria-label="{esc(t['pl_seek'])}"><span id="pltime" class="mono">0:00</span></div>
    <div class="pc pv"><button type="button" class="vbtn mute" aria-pressed="false" aria-label="{esc(t['pl_mute'])}"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path d="M3 9v6h4l5 4V5L7 9H3z" fill="currentColor"/><path class="w" d="M15.5 8.5a5 5 0 010 7M18 6a8.5 8.5 0 010 12" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/><path class="x" d="M15 9l6 6M21 9l-6 6" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"/></svg></button><input type="range" class="vol" min="0" max="100" value="50" aria-label="{esc(t['pl_vol'])}"><span class="mono vp">50&nbsp;%</span></div>
   </div>
  </div>
  <div class="groups">{playlist(t)}</div>
  <audio id="plaudio" preload="none"></audio>
 </div>
 <div class="mixer">
  <figure><svg id="hp" viewBox="-32 -53 704 419" role="img"></svg>
  <figcaption id="hpcap" aria-live="polite"></figcaption></figure>
  <div class="ctl"><span class="lbl" id="vlbl">{esc(t['voice_label'])}</span><div class="seg" id="voices" role="group" aria-labelledby="vlbl">{voices}</div></div>
  <div class="ctl"><span class="lbl" id="slbl">{esc(t['stage_label'])}</span><div class="seg" id="stages" role="group" aria-labelledby="slbl">{stages}</div></div>
  <div class="ctl2">
   <div class="ctl"><span class="lbl" id="klbl">{esc(t['sound_label'])}</span><div class="seg" id="sounds" role="group" aria-labelledby="klbl">{sounds}</div></div>
   <div class="ctl" id="tempoctl"><span class="lbl" id="tlbl">{esc(t['tempo_label'])}</span><div class="seg" id="tempos" role="group" aria-labelledby="tlbl">{tempos}</div></div>
  </div>
  <div class="nowplay"><button type="button" class="pbtn" aria-label="{esc(t['pl_play'])}"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path class="picon" data-c d="M7 4l13 8-13 8z" fill="currentColor"/></svg></button><p class="ps" id="hpname" aria-live="polite"></p></div>
 </div>
 <div class="mix" id="mix" data-audio="{A}audio/mix/" role="group" aria-labelledby="mxh">
  <p class="mxh" id="mxh">{esc(t['mx_h'])}</p><p class="mxp">{esc(t['mx_p'])}</p>
  <div class="pc"><button type="button" class="mxplay" id="mxplay" aria-label="{esc(t['pl_play'])}"><svg viewBox="0 0 24 24" width="22" height="22" aria-hidden="true"><path id="mxicon" d="M7 4l13 8-13 8z" fill="currentColor"/></svg></button>
   <input type="range" id="mxseek" min="0" max="1000" value="0" aria-label="{esc(t['pl_seek'])}"><span id="mxtime" class="mono">0:00</span></div>
<div class="mxbank">{mxmaster}{mixrows}</div>
  <div class="ctl mxt"><span class="lbl" id="mxtl">{esc(t['mx_tempo'])}</span><div id="mxtempos">{mxtempos}</div></div>
  </div>
</section>
<section id="{I['paket']}"><h2><span class="num">03</span>{esc(t['paket_h'])}</h2>
 <div class="exrow">
  <figure class="fan"><div class="pages">
   {fan_img(A, L, 'cover', 'p0', t['alt_cover'])}
   {fan_img(A, L, 'page-2', 'p2', t['alt_page2'])}
   {fan_img(A, L, 'page-1', 'p1', t['alt_page1'])}
  </div></figure>
  <div class="dl"><p class="ttl">{esc(t['dl_ttl'])}</p><p>{esc(t['dl_p'])}</p><p class="meta">{esc(t['dl_meta'])}</p><p class="dlb"><a href="{REL}{ZIP_OF[L]}" download>{esc(t['dl_btn'])}</a></p></div>
 </div>
 <h3 class="sub">{esc(t['inh_h'])}</h3>
 <p class="intro">{esc(t['paket_p'])}</p>
 <div class="tree">{tree}</div>
</section>
<section id="{I['rechte']}"><h2><span class="num">04</span>{esc(t['rechte_h'])}</h2>
 <div class="cols">{rights}</div>
</section>
<section id="{I['lizenz']}"><h2><span class="num">05</span>{esc(t['lic_h'])}</h2>
 <p class="intro wide"><a href="{GH}/blob/main/LICENSE.md">{esc(t['lic_link'])}</a>{esc(t['lic_p'])} <a href="{GH}/blob/main/choir-practice/THIRD_PARTY_NOTICES.md">{esc(t['lic_third_link'])}</a>.</p>
</section>
</main>
<footer><p class="fnote"><span class="fl">{GHICON}</span><span>{esc(t['foot_note']).replace('-Skill', '-&#8288;Skill')}</span></p><p class="fnote"><span class="fl">{ai}</span><span>{YEAR} {esc(t['ai'])}</span></p></footer>
<script>window.PAGE={json.dumps(data, ensure_ascii=False)};</script>
<script src="{A}js/site.js?v={asset_version()}"></script>
</body>
</html>
'''

CSS = r'''@font-face{font-family:"IBM Plex Sans";font-weight:400;font-style:normal;font-display:swap;src:url(../fonts/IBMPlexSans-Regular.woff2) format("woff2")}
@font-face{font-family:"IBM Plex Sans";font-weight:700;font-style:normal;font-display:swap;src:url(../fonts/IBMPlexSans-Bold.woff2) format("woff2")}
@font-face{font-family:"IBM Plex Sans Condensed";font-weight:400;font-style:normal;font-display:swap;src:url(../fonts/IBMPlexSansCondensed-Regular.woff2) format("woff2")}
:root{--bg:#fff;--fg:#000;--mute:#000;--link:#d9251d;--line:#000;--gut:32px;--max:1152px;--fs:17px;--fs-s:15px;--fs-m:22px;--edge:max(var(--gut),calc((100% - var(--max))/2 + var(--gut)))}
/* type scale: all running text 17 (lead, descriptions, notes too); one smaller size 15 for labels, captions, controls and the footer; one larger size 22 (h3, quote, folder names); h1, h2 and the key figures are display sizes. Bold only for headings (also the folder names), titles, numerals and the active menu item. No grey. */
@media (prefers-color-scheme:dark){:root:not([data-theme=light]){--bg:#000;--fg:#fff;--mute:#fff;--line:#fff}}
:root[data-theme=dark]{--bg:#000;--fg:#fff;--mute:#fff;--line:#fff;color-scheme:dark}:root[data-theme=light]{color-scheme:light}
*{box-sizing:border-box}
html{scroll-behavior:smooth;scroll-padding-top:var(--barh,76px)}
p,li,figcaption{text-wrap:pretty}
body{margin:0;background:var(--bg);color:var(--fg);font:400 var(--fs)/1.55 "IBM Plex Sans",Helvetica,Arial,sans-serif;-webkit-text-size-adjust:100%}
a{color:var(--link);text-decoration:none}a:hover{color:var(--fg)}
.mono{font-family:"IBM Plex Sans Condensed","IBM Plex Sans",sans-serif}
.skip{position:absolute;left:-999px}.skip:focus{left:16px;top:8px;background:var(--bg);padding:8px;z-index:20}
:focus-visible{outline:2px solid var(--fg);outline-offset:3px}
.bar{position:sticky;top:0;z-index:10;display:flex;align-items:center;gap:16px;padding:12px var(--edge);background:var(--bg);border-bottom:1.5px solid var(--line)}
.brand{display:flex;align-items:center;gap:12px;color:var(--fg);text-decoration:none;font-weight:700;font-size:var(--fs-m);letter-spacing:.02em}
.brand img{display:block;flex:none}.bn{white-space:nowrap}.bt{line-height:1.15}
.bar nav{margin-left:auto}.bar nav ul{display:flex;gap:0;list-style:none;margin:0;padding:0}
.bar nav a{display:block;padding:6px 9px;color:var(--fg);text-decoration:none;font-size:var(--fs-s);border-bottom:1.5px solid transparent}
.navlang{display:none}
.fl{display:flex;flex-wrap:wrap;align-items:center;gap:0}.fl a{display:flex;align-items:center;gap:8px;color:var(--fg);text-decoration:none}.fl .ghi{width:20px;height:20px}
.theme{order:98;display:flex;align-items:center;background:none;border:0;color:var(--fg);padding:6px;cursor:pointer;line-height:0}
.theme svg{width:22px;height:22px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round}.theme .sun{display:none}.theme.is-dark .sun{display:block}.theme.is-dark .moon{display:none}
.lang{order:99;color:var(--fg);text-decoration:none;padding:6px 9px;font-size:var(--fs-s)}
.burger{display:none;margin-left:auto;background:none;color:var(--fg);border:1.5px solid var(--line);padding:6px 12px;font:inherit;font-size:var(--fs-s)}
main{max-width:var(--max);margin:0 auto;padding:0 var(--gut)}
section{padding:64px 0 56px;border-top:1.5px solid var(--line)}
section.hero{border-top:0;padding-top:72px;padding-bottom:24px}
h1{font-size:clamp(34px,5.2vw,64px);line-height:1.05;letter-spacing:-.02em;margin:8px 0 28px;font-weight:700;text-wrap:balance}
h2{font-size:clamp(28px,4vw,44px);line-height:1.1;margin:0 0 20px;font-weight:700;display:flex;gap:20px;align-items:baseline}
h2 .num{font-weight:400;font-size:.5em;color:var(--link);min-width:2ch}
h3{margin:0 0 8px;font-size:var(--fs-m)}
.lead{margin:0 0 30px}
.input{margin:0 0 24px;color:var(--mute)}
.intro{max-width:44em;margin:0 0 28px}.intro.wide{max-width:none}
.cta{display:flex;flex-wrap:wrap;gap:12px 28px;margin:0 0 36px}
.facts{display:grid;grid-template-columns:repeat(4,1fr);gap:0;margin:0;border-top:1.5px solid var(--line)}
.facts div{padding:22px 12px 0 0}.facts dt{font-size:clamp(28px,4vw,44px);font-weight:700;line-height:1}.facts dd{margin:6px 0 0;color:var(--mute);font-size:var(--fs-s)}
.aitag{display:flex;align-items:center;gap:10px;margin:0}
.ailabel{height:1.6em;width:auto;flex:none}
@media (prefers-color-scheme:dark){:root:not([data-theme=light]) .ailabel{filter:invert(1)}}
:root[data-theme=dark] .ailabel{filter:invert(1)}
.tree{display:grid;grid-template-columns:repeat(2,1fr);gap:0 32px}
.folder{border-top:1.5px solid var(--line)}
.folder button{all:unset;box-sizing:border-box;display:block;width:100%;padding:14px 28px 14px 0;cursor:pointer;position:relative}
.folder button:focus-visible{outline:2px solid var(--fg);outline-offset:2px}
.folder button::after{content:"+";position:absolute;right:4px;top:12px;font-size:24px;line-height:1}
.folder button[aria-expanded=true]::after{content:"\2212"}
.folder .fn{display:block;font-weight:700;font-size:var(--fs-m)}.folder .fd{display:block;color:var(--mute);margin-top:2px}
.folder ul{list-style:none;margin:0 0 14px;padding:0 0 0 18px;border-left:1.5px solid var(--line)}.folder li{padding:2px 0;overflow-wrap:anywhere}.folder{min-width:0}.folder li{padding:2px 0 2px 10px}
.note{color:var(--mute);font-size:var(--fs-s);max-width:44em;margin:20px 0 0}
ul.note{padding-left:18px}
.chain{list-style:none;margin:0;padding:0;display:grid;grid-template-columns:repeat(6,1fr);gap:0;border-top:1.5px solid var(--line);border-left:1.5px solid var(--line)}
.chain button{all:unset;box-sizing:border-box;display:flex;flex-direction:column;gap:6px;width:100%;height:100%;min-height:92px;padding:10px;cursor:pointer;border-right:1.5px solid var(--line);border-bottom:1.5px solid var(--line);font-size:var(--fs-s);line-height:1.25}
.chain .n{font-size:var(--fs-m);font-weight:700}
.chain button[aria-pressed=true]{background:var(--fg);color:var(--bg)}
.chain button:focus-visible{outline:2px solid var(--fg);outline-offset:-4px}
.panel{margin:0 0 20px;border:1.5px solid var(--line);padding:18px 20px;min-height:96px}
.panel h3{display:flex;gap:12px;align-items:baseline}.panel .gate{margin:10px 0 0;color:var(--mute)}.panel .who{font-weight:400;font-size:var(--fs-s);color:var(--link);letter-spacing:.04em;text-transform:uppercase;font-family:"IBM Plex Sans Condensed",sans-serif}
.panel p{margin:0}
.banner{margin:72px 0 0}.banner img{display:block;width:100%;height:auto}
.banner .duck{max-width:26em;margin:18px auto 0;text-align:center;font-style:italic;font-size:var(--fs-m);line-height:1.4;text-wrap:balance}
.banner .duck .by{display:block;margin-top:6px;font-style:normal;font-size:var(--fs)}
@media (max-width:600px){.banner .duck{font-size:var(--fs);margin-top:14px}.banner .duck .dbr{display:none}.banner .duck .by{font-size:var(--fs-s)}}
.exrow{--pop:150px;--pw:250px;display:grid;grid-template-columns:calc(var(--pw)*1.8) minmax(0,1fr);gap:32px 56px;align-items:center;border:1.5px solid var(--line);padding:40px 48px;margin:calc(var(--pop) + 56px) 0 72px}   /* card; the fan pops out of its top edge by --pop, 56px stay free below the headline */
h3.sub{margin:0 0 8px;font-size:var(--fs-m)}
.dl p{margin:0 0 20px;max-width:30em}.dl .dlb{margin:0}.steps+.dlb{margin:24px 0 16px}.dlb a{display:inline-block;border:1.5px solid var(--line);padding:12px 20px;font-weight:400;color:var(--fg);text-decoration:none}.dlb a:hover,.dlb a:focus-visible{background:var(--fg);color:var(--bg)}
#hp .vb{cursor:pointer}@media (hover:hover){#hp .vb:hover circle{stroke:var(--link)}#hp .vb:hover text{fill:var(--link)}}   /* hover only where a pointer exists: on touch screens it would stay red after the tap */#hp .vb:focus-visible{outline:2px solid var(--fg);outline-offset:4px}
.fan{width:100%;margin:calc(var(--pop)*-1) 0 -10px}.fan .pages{position:relative;height:calc(var(--pw)*1.62)}.fan img{position:absolute;bottom:calc(var(--pw)*.13);left:50%;width:var(--pw);height:auto;background:#fff;border:1.5px solid var(--line);transform-origin:50% 100%}
.fan .p0{transform:translateX(-50%) rotate(-15deg)}.fan .p1{transform:translateX(-50%) rotate(0)}.fan .p2{transform:translateX(-50%) rotate(15deg)}

.dl .ttl{font-weight:700;font-size:var(--fs-m);margin:0 0 6px}.dl .meta{font-size:var(--fs-s);color:var(--mute);margin:0 0 20px}
.dlb a{padding:16px 22px}.dl{min-width:0}   /* desktop: the button is as wide as its text, no arrow */
@media (max-width:900px){.dlb a{display:block;text-align:center}.exrow{--pop:130px;--pw:200px;grid-template-columns:1fr;gap:8px;padding:24px 20px;margin-top:calc(var(--pop) + 44px)}.fan{width:min(100%,calc(var(--pw)*1.8));margin:calc(var(--pop)*-1) auto 0}}
@media (max-width:520px){.exrow{--pw:190px}}
.mixer{display:grid;gap:28px;max-width:760px;margin:56px auto 0}
.ctl2{display:flex;flex-wrap:wrap;gap:16px 32px}.ctl2 .ctl{flex:1 1 14em}.ctl2 .ctl[hidden]{display:none}
.ctl{display:flex;flex-direction:column;gap:6px;align-items:stretch}.lbl{font:400 var(--fs-s)/1.2 "IBM Plex Sans Condensed",sans-serif;color:var(--link);letter-spacing:.04em;text-transform:uppercase}
.seg{display:flex;flex-wrap:wrap}.seg button{flex:1 1 0;min-width:max-content;font:inherit;font-size:var(--fs-s);background:var(--bg);color:var(--fg);border:1.5px solid var(--line);margin:0 -1.5px -1.5px 0;padding:10px 16px;cursor:pointer}
.seg button:focus-visible{outline:2px solid var(--fg);outline-offset:-5px;position:relative}
.seg button[aria-pressed=true]{background:var(--fg);color:var(--bg)}
.mixer figure{margin:0}
.listen{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:24px 56px;align-items:start}
.pbox{display:grid;grid-template-columns:1fr;gap:20px;align-items:start;justify-self:start;width:100%;max-width:26em}
.listen .art{width:100%;height:auto;display:block;border:1.5px solid var(--line)}
@media (hover:hover){.pbtn:hover,.vbtn:hover{color:var(--link)}.vol:hover,#plseek:hover{accent-color:var(--link)}}
.pt{margin:0;font-weight:700}.ps{margin:2px 0 12px;color:var(--mute);font-size:var(--fs-s);min-height:1.55em}
.pc{display:flex;align-items:center;gap:14px}
.pbtn,.vbtn,.mxplay{flex:none;width:44px;height:44px;border:1.5px solid var(--line);background:var(--bg);color:var(--fg);display:grid;place-items:center;cursor:pointer;padding:0}
.pbtn:focus-visible,.vbtn:focus-visible,.mxplay:focus-visible,#plseek:focus-visible,.vol:focus-visible,.groups summary:focus-visible,.trk button:focus-visible{outline:2px solid var(--fg);outline-offset:2px}
#plseek{flex:1;min-width:0;accent-color:var(--fg);height:24px;cursor:pointer}
.vol{flex:1;min-width:0;accent-color:var(--fg);height:24px;cursor:pointer}.pv{margin-top:10px}
.mute .x{display:none}.mute[aria-pressed=true] .x{display:inline}.mute[aria-pressed=true] .w{display:none}
#pltime,.vp{flex:none;font-size:var(--fs-s);min-width:3.2em;text-align:right}
.nowplay{display:flex;align-items:center;gap:14px}.nowplay .ps{margin:0}
.mix{margin:32px 0 0;padding:20px 0 0;border-top:1.5px solid var(--line)}.mxh{margin:0;font-weight:700;font-size:var(--fs-m)}.mxp{margin:4px 0 14px;color:var(--mute);font-size:var(--fs-s)}
.mix #mxseek{flex:1;min-width:0;accent-color:var(--fg);height:24px;cursor:pointer}.mix #mxtime{flex:none;font-size:var(--fs-s);min-width:3.2em;text-align:right}
.mxr{display:flex;align-items:center;gap:14px;margin-top:10px;--th:16px}
.mxb{flex:none;width:6.5em;height:36px;border:1.5px solid var(--line);background:var(--bg);color:var(--fg);font:inherit;font-size:var(--fs-s);cursor:pointer;padding:0 6px}
.mxb[aria-pressed=true]{background:var(--fg);color:var(--bg)}
.mxplay{width:calc(6.5*var(--fs-s));height:36px}
.mxt{margin-top:18px}
.mxtrack{display:block;width:100%;accent-color:var(--fg);height:28px;margin:6px 0 0;cursor:pointer}
.mxtk{display:flex;justify-content:space-between;padding:0 10px;font-size:var(--fs-s);color:var(--mute)}
.mxtrack:focus-visible{outline:2px solid var(--fg);outline-offset:4px}
/* the mixer as a console: on wide screens the channels stand side by side with a level meter and a vertical fader; on phones they stay rows */
.mxbank{display:flex;flex-direction:column;margin-top:20px}   /* space between the play row and the channels */
.mxm{order:-1}
.mxmeter{display:none}
.mxmeter i{display:block;flex:1;border:1px solid var(--line)}
.mxmeter i.on{background:var(--fg)}
.mxmeter i:nth-child(n+14){border-color:var(--link)}.mxmeter i:nth-child(n+14).on{background:var(--link)}
.mxf{position:relative;flex:1 1 0;width:0;min-width:0;height:auto}
.mxf .mxv{position:static;width:100%;height:24px;margin:0;transform:none}
@media (min-width:760px){
 .mxbank{flex-direction:row;align-items:flex-start;gap:12px}
 .mxm{order:0}
 .mxr,.mxm{display:grid;grid-template-columns:14px 1fr;gap:10px;flex:1 1 0;min-width:0;margin-top:0;align-items:stretch}
 .mxb,.mxmlb{grid-column:1/-1;width:100%}
 .mxmeter{display:flex;flex-direction:column-reverse;gap:2px;grid-column:1;grid-row:2;width:14px;height:150px;align-self:center}
 .mxf{grid-column:2;grid-row:2;flex:none;width:auto;height:150px}
 .mxf .mxv{position:absolute;left:50%;top:50%;width:150px;height:28px;transform:translate(-50%,-50%) rotate(-90deg)}
 .mxf .tk{left:50%;top:50%;right:auto;bottom:auto;width:150px;height:28px;transform:translate(-50%,-50%) rotate(-90deg)}
 .mxr .mxp2,.mxm .mxp2{grid-column:1/-1;text-align:center;min-width:0}
 .mxm .mxmlb{width:100%}   /* as wide as the channels */
}
.mxmlb{flex:none;width:calc(6.5*var(--fs-s));height:36px;display:grid;place-items:center;box-sizing:border-box;border:1.5px solid var(--line);background:var(--fg);color:var(--bg);font-size:var(--fs-s);font-weight:700}   /* always on, so filled like a pressed voice */   /* same size as the voice buttons below */
.mxv{flex:1;min-width:0;height:24px;margin:0;cursor:pointer;-webkit-appearance:none;appearance:none;background:transparent}
.mxv::-webkit-slider-runnable-track{height:2px;background:var(--fg)}
.mxv::-webkit-slider-thumb{-webkit-appearance:none;width:var(--th);height:var(--th);margin-top:-7px;border:0;border-radius:50%;background:var(--fg)}
.mxv::-moz-range-track{height:2px;background:var(--fg)}
.mxv::-moz-range-thumb{width:var(--th);height:var(--th);border:0;border-radius:50%;background:var(--fg)}
.tk{position:absolute;inset:0;pointer-events:none}
.tk i{position:absolute;top:calc(50% - 4px);width:1px;height:8px;margin-left:-.5px;background:var(--fg)}
.mxr .mxp2{flex:none;font-size:var(--fs-s);min-width:3.2em;text-align:right}
.mxr.off .mxv,.mxr.off .mxp2{opacity:.4}
.mxb:focus-visible,.mxv:focus-visible,#mxseek:focus-visible{outline:2px solid var(--fg);outline-offset:2px}
@media (hover:hover){.mxb:hover,#mxplay:hover{color:var(--link)}.mxb[aria-pressed=true]:hover{background:var(--link);color:var(--bg);border-color:var(--link)}#mxseek:hover{accent-color:var(--link)}.mxv:hover::-webkit-slider-thumb,.mxv:hover::-moz-range-thumb{background:var(--link)}}
.groups details{border-top:1.5px solid var(--line)}.groups details:last-child{border-bottom:1.5px solid var(--line)}
.groups summary{list-style:none;cursor:pointer;padding:8px 28px 8px 0;position:relative}.groups summary::-webkit-details-marker{display:none}
.groups summary::after{content:"+";position:absolute;right:4px;top:4px;font-size:24px;line-height:1.3}.groups details[open] summary::after{content:"\2212"}
.trk{list-style:none;margin:0 0 10px;padding:0}
.trk button{all:unset;box-sizing:border-box;display:block;position:relative;width:100%;padding:5px 0;font-size:var(--fs-s);cursor:pointer}
.trk button[aria-pressed=true]::before{content:"";position:absolute;left:-18px;top:50%;transform:translateY(-50%);width:0;height:0;border-style:solid;border-width:5px 0 5px 9px;border-color:transparent transparent transparent var(--fg)}
@media (max-width:900px){.listen{grid-template-columns:1fr}}
#hp{width:100%;height:auto;display:block;max-width:760px;color:var(--fg)}
#hp text{font-family:"IBM Plex Sans",sans-serif;fill:currentColor}
.mixer figcaption{max-width:44em;margin:6px auto 0;text-align:center}
#hp .wave{opacity:0}#hp.playing .wave{animation:wave 1.4s ease-out infinite}
@keyframes wave{0%{opacity:0}25%{opacity:1}100%{opacity:0}}
#hp.live.playing .wave{animation:none}   /* opacity then comes from the script (level of the recording) */
@media (prefers-reduced-motion:reduce){#hp.playing .wave{animation:none;opacity:1}}
.cols{display:grid;grid-template-columns:repeat(2,1fr);gap:0 32px}.cols article{border-top:1.5px solid var(--line);padding-top:16px}
.cols p{margin:0}
.steps{padding-left:1.4em;max-width:44em}.steps li{margin:0 0 10px}
footer .fnote{flex:0 0 100%;margin:0;display:flex;align-items:center;gap:10px}footer .fnote .fl{flex:none;display:flex;align-items:center;justify-content:center;width:1.6em;height:1.6em;color:var(--fg);text-decoration:none}footer .fnote .ghi{width:1.6em;height:1.6em}footer .fnote .ailabel{height:1.6em;width:1.6em}
footer{max-width:var(--max);margin:0 auto;padding:24px var(--gut) 48px;border-top:1.5px solid var(--line);display:flex;flex-wrap:wrap;gap:12px 32px;align-items:center;justify-content:space-between;font-size:var(--fs-s)}
@media (max-width:900px){.chain{grid-template-columns:repeat(3,1fr)}.cols{grid-template-columns:1fr;row-gap:16px}.tree{grid-template-columns:1fr}}
@media (max-width:760px){
 .facts{grid-template-columns:repeat(2,1fr)}section{padding:48px 0 40px}h2{gap:12px}
 /* same visible gap above the headline as between menu and header image (72 px; the headline box starts 13 px above its first ink) */
 section.hero{padding-top:59px}
}
@media (max-width:899px){
 .theme{margin-left:auto}.burger{display:block;order:100;margin-left:0}.bar>.lang{display:none}.navlang{display:block;border-top:1.5px solid var(--line);margin-top:4px}
 .bar nav{display:none;position:absolute;left:0;right:0;top:100%;background:var(--bg);border-bottom:1.5px solid var(--line);margin:0}
 .bar.open nav{display:block}.bar nav ul{flex-direction:column;gap:0;padding:8px var(--gut)}.bar nav a{padding:12px 0}
}
@media (max-width:420px){.chain{grid-template-columns:repeat(2,1fr)}}
@media (max-width:520px){.bar{gap:12px}.brand{font-size:var(--fs);gap:10px}.brand img{width:36px;height:36px}}
@media (prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
'''

JS = r'''(function(){
var D=window.PAGE,$=function(s,r){return (r||document).querySelector(s)},$$=function(s,r){return Array.prototype.slice.call((r||document).querySelectorAll(s))};
// menu
var bar=$('.bar'),bg=$('.burger');
bg.addEventListener('click',function(){var o=bar.classList.toggle('open');bg.setAttribute('aria-expanded',o)});
function barH(){document.documentElement.style.setProperty('--barh',bar.offsetHeight+'px')}
barH();window.addEventListener('resize',barH);window.addEventListener('load',barH);
// a menu click always scrolls to its section; layout shifts during the smooth scroll (late images, fonts) are corrected afterwards
$$('#nav a[href^="#"]').forEach(function(a){a.addEventListener('click',function(e){
 bar.classList.remove('open');bg.setAttribute('aria-expanded',false);
 var t=document.getElementById(a.getAttribute('href').slice(1));if(!t)return;e.preventDefault();
 function y(){return Math.max(0,Math.round(t.getBoundingClientRect().top+window.pageYOffset-bar.offsetHeight))}
 window.scrollTo({top:y(),behavior:'smooth'});
 try{history.replaceState(null,'',a.getAttribute('href'))}catch(x){}
 setTimeout(function(){if(Math.abs(window.pageYOffset-y())>2)window.scrollTo({top:y(),behavior:'auto'})},900)})});
if('IntersectionObserver' in window){
 var links={};$$('#nav a[href^="#"]').forEach(function(a){links[a.getAttribute('href').slice(1)]=a});
 var io=new IntersectionObserver(function(es){es.forEach(function(e){if(e.isIntersecting){$$('#nav a').forEach(function(a){a.removeAttribute('aria-current')});var a=links[e.target.id];if(a)a.setAttribute('aria-current','true')}})},{rootMargin:'-45% 0px -50% 0px'});
 $$('main section').forEach(function(s){io.observe(s)});
}
// hero: the sub head wraps at the width of the headline (measured from its lines); on phones it keeps the full width
function fitLead(){var h=$('.hero h1'),l=$('.hero .lead');if(!h||!l)return;l.style.maxWidth='';if(window.innerWidth<760)return;var r=document.createRange();r.selectNodeContents(h);var a=1e9,z=0;
 Array.prototype.forEach.call(r.getClientRects(),function(q){if(q.width>1){a=Math.min(a,q.left);z=Math.max(z,q.right)}});if(z>a)l.style.maxWidth=Math.ceil(z-a)+'px'}
fitLead();if(document.fonts&&document.fonts.ready)document.fonts.ready.then(fitLead);window.addEventListener('load',fitLead);
// light / dark switch: system setting by default, the choice is kept in localStorage
(function(){var root=document.documentElement,tb=$('.theme'),mq=window.matchMedia('(prefers-color-scheme: dark)');if(!tb)return;
function dark(){var t=root.getAttribute('data-theme');return t?t==='dark':mq.matches}
function apply(){var d=dark(),t=root.getAttribute('data-theme'),src=$('.banner picture source');tb.className='theme '+(d?'is-dark':'is-light');tb.setAttribute('aria-label',d?D.theme_to_light:D.theme_to_dark);
 if(src)src.media=t==='dark'?'all':t==='light'?'not all':'(prefers-color-scheme: dark)'}
tb.addEventListener('click',function(){var t=dark()?'light':'dark';root.setAttribute('data-theme',t);try{localStorage.setItem('theme',t)}catch(e){}apply()});
if(mq.addEventListener)mq.addEventListener('change',apply);apply()})();
// folder tree
$$('.folder button').forEach(function(b){b.addEventListener('click',function(){var o=b.getAttribute('aria-expanded')==='true';b.setAttribute('aria-expanded',!o);document.getElementById(b.getAttribute('aria-controls')).hidden=o})});
// workflow chain
function nb(t){var i=t.lastIndexOf(' ');return i>0?t.slice(0,i)+String.fromCharCode(160)+t.slice(i+1):t}   // last two words stay together
function showStep(i){
 $$('.chain button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-step')==i)});
 var s=D.steps[i],box=$('#stepbox');box.innerHTML='';
 var h=document.createElement('h3');h.innerHTML='<span>'+(i+1)+' – '+s[0]+'</span><span class="who">'+D.who[s[1]]+'</span>';
 var p=document.createElement('p');p.textContent=nb(s[2]);box.appendChild(h);box.appendChild(p);
 if(s[3]){var g=document.createElement('p');g.className='gate';g.textContent=nb(D.gate+': '+s[3]);box.appendChild(g)}
}
$$('.chain button').forEach(function(b){b.addEventListener('click',function(){showStep(+b.getAttribute('data-step'))})});
showStep(0);
// headphone mix
var NS='http://www.w3.org/2000/svg',svg=$('#hp'),cur={voice:'S',stage:'choir',sound:'choir',tempo:'normal'};
function el(n,a,t){var e=document.createElementNS(NS,n);for(var k in a)e.setAttribute(k,a[k]);if(t!=null)e.textContent=t;return e}
function rad(db){return Math.max(15,34+1.33*db)}
function mob0(W){return W<600}
function draw(){
 while(svg.lastChild)svg.removeChild(svg.lastChild);
 var sw=1.5,col='currentColor',x0=320,half=250,GAP=24,VW=656+2*GAP,W=svg.getBoundingClientRect().width||640,FS=Math.round(10*15*VW/W)/10,LS=mob0(W)?FS:Math.round(FS*15)/10;
 // over-ear headphones seen from the front, line art: steel frame, mesh canopy, telescopic arms, cups with cushions facing in, crown on the right cup
 var mob=mob0(W),oy=mob?200:230,ay=mob?338:312,py=mob?388:352;
 svg.setAttribute('viewBox',(-8-GAP)+' -53 '+VW+' '+(mob?453:419));
 function ln(d,w,dx){svg.appendChild(el('path',{d:d,fill:'none',stroke:col,'stroke-width':w||sw*2,'stroke-linecap':'round','stroke-linejoin':'round',transform:'translate('+(dx||0)+' 0)'}))}   // dx: shifts a cup outwards
 ln('M'+(47-GAP)+' 128 L'+(47-GAP)+' 120 A'+(273+GAP)+' 165 0 0 1 '+(593+GAP)+' 120 L'+(593+GAP)+' 128 L'+(581+GAP)+' 128 L'+(581+GAP)+' 120 A'+(261+GAP)+' 147 0 0 0 '+(59-GAP)+' 120 L'+(59-GAP)+' 128 Z');
 ln('M47 128 h12 v8 h-12 Z',sw*1.5,-GAP);ln('M581 128 h12 v8 h-12 Z',sw*1.5,GAP);
 ln('M30 160 C30 142 40 136 53 136 C66 136 76 142 76 160 L76 286 C76 304 66 310 53 310 C40 310 30 304 30 286 Z',null,-GAP);
 ln('M564 160 C564 142 574 136 587 136 C600 136 610 142 610 160 L610 286 C610 304 600 310 587 310 C574 310 564 304 564 286 Z',null,GAP);
 ln('M76 156 C88 156 92 164 92 174 L92 272 C92 282 88 290 76 290',sw*1.5,-GAP);
 ln('M564 156 C552 156 548 164 548 174 L548 272 C548 282 552 290 564 290',sw*1.5,GAP);
 // sound waves between cup and ear, travelling inwards, red; only visible while a recording plays (class 'playing' on the svg).
 // The circles never reach further out than x=121 (or 519 on the right); the whole headphones are GAP=24 units wider on each side, so the waves end at x=92 (or 548) and the gap to the circles is at least 29 units
 [0,1,2].forEach(function(i){var x=102+5*i,h=20+10*i,c=x+6;
  [[x-GAP,c-GAP],[640-x+GAP,640-c+GAP]].forEach(function(p){svg.appendChild(el('path',{'class':'wave',d:'M'+p[0]+' '+(223-h)+' Q'+p[1]+' 223 '+p[0]+' '+(223+h),fill:'none',stroke:'var(--link)','stroke-width':sw*1.7,'stroke-linecap':'round',style:'animation-delay:'+(i*0.25)+'s'}))})});
 var list=D.mix[cur.stage][cur.voice],own=[],acc=[];
 list.forEach(function(e){(e[3]==='acc'?acc:own).push(e)});
 function pos(e){return x0+e[1]*(cur.stage==='tutti'?270:190)}   // tutti: circles further apart
 own.forEach(function(e,i){var y=oy;
  var g=el('g',{'class':'vb',role:'button',tabindex:0,'aria-label':D.voices[e[0]],'aria-pressed':e[0]===cur.voice});var r=rad(e[2]);
  var pick=function(){if(e[0]===cur.voice&&!A.paused){A.pause();return}change(function(){cur.voice=e[0]},true)};   // the circles switch the voice, like the voice buttons; the circle of the voice that is playing stops the sound
  g.addEventListener('click',pick);g.addEventListener('keydown',function(ev){if(ev.key==='Enter'||ev.key===' '){ev.preventDefault();pick()}});
  g.appendChild(el('circle',{cx:pos(e),cy:y,r:r,fill:'none','pointer-events':'all',stroke:col,'stroke-width':e[0]===cur.voice&&e[2]===0?sw*3:sw*1.5}));
  g.appendChild(el('text',{x:pos(e),y:y,dy:'.35em','font-size':Math.min(LS,1.5*r),'text-anchor':'middle','font-weight':700},e[0]));   // dy: cap height centred in the circle
  g.appendChild(el('text',{x:pos(e),y:y+r+(mob?FS*0.95+3:16),'font-size':FS,'text-anchor':'middle'},e[2]+(mob&&i>0?'':' dB')));
  svg.appendChild(g);});
 acc.forEach(function(e){var y=ay,r=rad(e[2]);
  svg.appendChild(el('circle',{cx:pos(e),cy:y,r:r,fill:'none',stroke:col,'stroke-width':sw,'stroke-dasharray':'4 4'}));
  svg.appendChild(el('text',{x:pos(e),y:y,dy:'.35em','font-size':FS,'text-anchor':'middle'},e[0]));});
 if(acc.length){svg.appendChild(el('text',{x:x0,y:py,'font-size':FS,'text-anchor':'middle'},D.acc+' ('+acc[0][2]+' dB)'))}
 svg.setAttribute('aria-label',D.voices[cur.voice]+', '+D.stages[cur.stage]);   // no <title>: it would show a tooltip on hover
 $('#hpcap').textContent=nb(D.stage_txt[cur.stage]);
}
// one state (voice, stage, sound, tempo) drives the headphones, the buttons, the playlist and the audio
var pl=$('#player'),A=$('#plaudio'),sk=$('#plseek'),tm=$('#pltime'),base=pl.getAttribute('data-audio');
function slowOk(){return cur.stage==='solo'||cur.stage==='accomp'}
function isSlow(){return slowOk()&&cur.tempo==='slow'}
function file(){return cur.stage==='tutti'?'tutti_'+cur.sound:cur.voice.toLowerCase()+'_'+cur.stage+'_'+cur.sound+(isSlow()?'_slow':'')}
function label(){return (cur.stage==='tutti'?D.stages.tutti:D.voices[cur.voice]+', '+D.stages[cur.stage])+', '+D.sound_names[cur.sound]+(isSlow()?', '+D.slow_name:'')}
function f(t){t=Math.floor(t||0);return Math.floor(t/60)+':'+('0'+t%60).slice(-2)}
function ui(){var on=!A.paused;svg.classList.toggle('playing',on);$$('.picon').forEach(function(i){var c=i.hasAttribute('data-c');i.setAttribute('d',on?(c?'M6 4h4v16H6zM14 4h4v16h-4z':'M6.3 4.4Q8.2 4 10.1 4.5Q10.4 12 9.9 19.7Q8 20.2 6.1 19.6Q6.6 12 6.3 4.4ZM14.2 4.3Q16.1 4 18 4.6Q18.4 12 17.9 19.8Q16 20.1 14.1 19.7Q14.5 12 14.2 4.3Z'):(c?'M7 4l13 8-13 8z':'M7.2 4.6Q13.5 8.4 19.6 12.1Q13.3 15.9 7.4 19.6Q7.8 12 7.2 4.6Z'))});$$('.pbtn').forEach(function(b){b.setAttribute('aria-label',pl.getAttribute(on?'data-pause':'data-play'))})}
function sync(){
 draw();
 $$('#voices button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-voice')===cur.voice)});
 $$('#stages button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-stage')===cur.stage)});
 $$('#sounds button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-sound')===cur.sound)});
 $$('#tempos button').forEach(function(b){b.setAttribute('aria-pressed',b.getAttribute('data-tempo')===(slowOk()?cur.tempo:'normal'))});
 $('#tempoctl').hidden=!slowOk();
 var k=file();
 $$('.trk button').forEach(function(b){var st=b.getAttribute('data-stage'),vo=b.getAttribute('data-voice')||cur.voice,sl=b.getAttribute('data-tempo')==='slow';
  b.setAttribute('aria-pressed',st===cur.stage&&b.getAttribute('data-sound')===cur.sound&&(st==='tutti'||vo===cur.voice)&&sl===isSlow())});
 $$('.groups details').forEach(function(d){d.open=cur.stage==='tutti'?d.hasAttribute('data-tutti'):d.getAttribute('data-voice')===cur.voice});   // only the group of the chosen voice is open
 $('#plname').textContent=$('#hpname').textContent=label();
 var u=base+k+'.mp3';if(A.getAttribute('src')!==u)A.setAttribute('src',u);
}
// change the selection; keep the playing position (scaled when the tempo changes), or start the chosen recording when asked
function change(fn,restart){
 var was=!A.paused,t=A.currentTime||0,ps=isSlow();fn();var ns=isSlow();sync();
 if(restart){sk.value=0;tm.textContent='0:00';try{A.currentTime=0}catch(e){}A.play().catch(function(){});return}
 if(was){var sc=(ns?1/D.slow:1)/(ps?1/D.slow:1);A.addEventListener('loadedmetadata',function h(){A.removeEventListener('loadedmetadata',h);A.currentTime=Math.min(t*sc,Math.max(0,(A.duration||t*sc)-0.2))});A.play().catch(function(){})}
 else{sk.value=0;tm.textContent='0:00'}
}
$$('#voices button').forEach(function(b){b.addEventListener('click',function(){change(function(){cur.voice=b.getAttribute('data-voice')},true)})});
$$('#stages button').forEach(function(b){b.addEventListener('click',function(){change(function(){cur.stage=b.getAttribute('data-stage')},A.paused)})});
$$('#sounds button').forEach(function(b){b.addEventListener('click',function(){change(function(){cur.sound=b.getAttribute('data-sound')},A.paused)})});
$$('#tempos button').forEach(function(b){b.addEventListener('click',function(){change(function(){cur.tempo=b.getAttribute('data-tempo')},A.paused)})});
$$('.trk button').forEach(function(b){b.addEventListener('click',function(){change(function(){var v=b.getAttribute('data-voice');if(v)cur.voice=v;cur.stage=b.getAttribute('data-stage');cur.sound=b.getAttribute('data-sound');cur.tempo=b.getAttribute('data-tempo')},true)})});
$$('.pbtn').forEach(function(b){b.addEventListener('click',function(){if(A.paused){A.play().catch(function(){})}else{A.pause()}})});
// volume: the slider and the speaker button exist twice (remote on the header image, player); both follow one value (no effect on iPhones: the system volume rules there)
var vols=$$('.vol'),mutes=$$('.mute'),lastVol=.5;
function setVol(v){v=Math.max(0,Math.min(1,v));A.volume=v;$$('.vp').forEach(function(e){e.textContent=Math.round(v*100)+'\u00a0%'});vols.forEach(function(r){r.value=Math.round(v*100)});mutes.forEach(function(m){m.setAttribute('aria-pressed',v===0)})}
vols.forEach(function(r){r.addEventListener('input',function(){lastVol=+r.value/100||lastVol;setVol(+r.value/100)})});
mutes.forEach(function(m){m.addEventListener('click',function(){if(A.volume>0){lastVol=A.volume;setVol(0)}else setVol(lastVol||.5)})});
setVol(.5);   // starts at half volume
A.addEventListener('play',ui);A.addEventListener('pause',ui);
// sound waves pulse with the rhythm of the recording: Web Audio analyser on the audio element; every note onset (level jumps more than 2.5 dB above its slow average) switches the three arcs per side on, they then go off again from the outside in; while it sounds the inner arc stays on (always full red, no fading).
// Onset rate on the example recordings: 2 to 4 per second. Without Web Audio, with reduced motion or if the context cannot run, the fixed animation stays
var live=null;
function startLive(){
 if(live!==null||(window.matchMedia&&matchMedia('(prefers-reduced-motion:reduce)').matches))return;
 live=false;
 var AC=window.AudioContext||window.webkitAudioContext;if(!AC)return;
 try{
  var cx=new AC();
  var build=function(){
   if(cx.state!=='running'){try{cx.close()}catch(e){}return}   // an element routed into a suspended context would be silent
   var an=cx.createAnalyser();an.fftSize=1024;var sr=cx.createMediaElementSource(A);sr.connect(an);an.connect(cx.destination);
   live={cx:cx,an:an,buf:new Uint8Array(an.fftSize),slow:null,pulse:0,last:0,t:0,raf:0,on:[false,false,false]};svg.classList.add('live');if(!A.paused)loop()};
  if(cx.state==='running')build();else cx.resume().then(build,function(){})
 }catch(e){}
}
function stopLoop(){if(live&&live.raf){cancelAnimationFrame(live.raf);live.raf=0}if(live){live.on=[false,false,false];live.slow=null;live.pulse=0}$$('#hp .wave').forEach(function(w){w.style.opacity=''})}
function loop(now){
 if(!live||A.paused){stopLoop();return}
 now=now||performance.now();
 var b=live.buf,q=0,i;live.an.getByteTimeDomainData(b);for(i=0;i<b.length;i++){var x=(b[i]-128)/128;q+=x*x}
 var db=20*Math.log10(Math.sqrt(q/b.length)+1e-6),dt=Math.min(100,live.t?now-live.t:16);live.t=now;
 if(live.slow===null)live.slow=db;
 var flux=db-live.slow;   // jump above the slow average = note onset
 if(flux>2.5&&db>-45&&now-live.last>110){live.pulse=Math.min(1,0.55+flux/10);live.last=now}
 live.pulse*=Math.pow(0.92,dt*0.06);live.slow+=(1-Math.pow(0.95,dt*0.06))*(db-live.slow);   // per 60 Hz frame: pulse x0.92, average 5 %
 var v=Math.max(live.pulse,db>-25?0.35:0);   // inner arc stays on while it sounds
 for(i=0;i<3;i++){var th=0.25*(i+1);if(live.on[i]?v<th-0.04:v>th+0.04)live.on[i]=!live.on[i]}   // thresholds 0.25 / 0.5 / 0.75 with hysteresis against flicker
 for(i=1;i<3;i++)if(!live.on[i-1])live.on[i]=false;   // an outer arc is only on while the inner one is
 var ws=svg.querySelectorAll('.wave');for(i=0;i<ws.length;i++)ws[i].style.opacity=live.on[Math.floor(i/2)]?1:0;   // order of creation: both sides of arc 0, then arc 1, arc 2
 live.raf=requestAnimationFrame(loop)}
document.addEventListener('click',function(e){if(e.target.closest&&e.target.closest('button'))startLive()},true);   // created inside a click, so the context may run
A.addEventListener('play',function(){if(live&&!live.raf){if(live.cx.state==='suspended')live.cx.resume();loop()}});
A.addEventListener('pause',stopLoop);A.addEventListener('ended',stopLoop);
A.addEventListener('timeupdate',function(){if(A.duration)sk.value=Math.round(A.currentTime/A.duration*1000);tm.textContent=f(A.currentTime)});
A.addEventListener('loadedmetadata',function(){tm.textContent=f(A.currentTime)});
A.addEventListener('ended',function(){ui();sk.value=0});
sk.addEventListener('input',function(){if(A.duration)A.currentTime=sk.value/1000*A.duration});
sync();ui();
// mixer: the stems (4 voices, piano, starting notes) play together through Web Audio; every voice has an on/off button and its own level; the room reverb is added here.
// Tempo steps (60, 75, 90, 100 %) are separate sets of files, loaded when first chosen; switching keeps the position in proportion to the length of the set.
(function(){
var mx=$('#mix');if(!mx)return;
var AC=window.AudioContext||window.webkitAudioContext,base=mx.getAttribute('data-audio'),play=$('#mxplay'),ic=$('#mxicon'),seek=$('#mxseek'),time=$('#mxtime');
var names=['s','a','t','b','acc','intro'],cx=null,mgain=null,anal={},mloop=0,sets={},tp='100',gains={},srcs=[],t0=0,off=0,playing=false,raf=0,asked=0,mixOwns=false;
var PLAY='M7 4l13 8-13 8z',PAUSE='M6 4h4v16H6zM14 4h4v16h-4z';
function dur(){return sets[tp]?sets[tp].dur:0}
function fmt(t){t=Math.floor(t||0);return Math.floor(t/60)+':'+('0'+t%60).slice(-2)}
function rows(){return $$('.mxr:not(.mxm)',mx)}   // the master row is not a stem
function level(r){var b=$('.mxb',r),v=+$('.mxv',r).value/100;return b.getAttribute('aria-pressed')==='true'?v*v:0}   // squared: the slider follows the loudness we hear
function apply(){if(!cx)return;rows().forEach(function(r){var k=$('.mxb',r).getAttribute('data-stem');if(gains[k])gains[k].gain.setTargetAtTime(level(r),cx.currentTime,.02)})}
function setIcon(on){ic.setAttribute('d',on?PAUSE:PLAY);play.setAttribute('aria-label',on?pl.getAttribute('data-pause'):pl.getAttribute('data-play'))}
function ir(c){var rt=1.3,n=Math.floor(c.sampleRate*rt*1.2),b=c.createBuffer(2,n,c.sampleRate);   // synthetic room: decaying noise
 for(var ch=0;ch<2;ch++){var d=b.getChannelData(ch);for(var i=0;i<n;i++)d[i]=(Math.random()*2-1)*Math.exp(-6.9*(i/c.sampleRate)/rt)*.35}return b}
function setup(){
 cx=new AC();var master=cx.createGain(),lim=cx.createDynamicsCompressor();mgain=cx.createGain();var mv=$('#mxmaster');mgain.gain.value=mv?Math.pow(+mv.value/100,2):1;master.connect(mgain);lim.threshold.value=-6;lim.ratio.value=8;lim.attack.value=.003;lim.release.value=.15;
 var wet=cx.createGain(),cv=cx.createConvolver();wet.gain.value=.3;cv.buffer=ir(cx);mgain.connect(lim);mgain.connect(cv);cv.connect(wet);wet.connect(lim);lim.connect(cx.destination);
 names.forEach(function(k){var g=cx.createGain(),p=cx.createStereoPanner?cx.createStereoPanner():null,b=$('.mxb[data-stem="'+k+'"]',mx);g.gain.value=1;
  if(p){p.pan.value=b?+b.getAttribute('data-pan'):0;g.connect(p);p.connect(master)}else g.connect(master);gains[k]=g;anal[k]=cx.createAnalyser();anal[k].fftSize=512;g.connect(anal[k])});anal.master=cx.createAnalyser();anal.master.fftSize=512;mgain.connect(anal.master);
}
function load(t){
 if(sets[t])return Promise.resolve(sets[t]);
 return Promise.all(names.map(function(k){return fetch(base+t+'/'+k+'.mp3').then(function(r){return r.arrayBuffer()}).then(function(a){return new Promise(function(ok,no){cx.decodeAudioData(a,ok,no)})})})).then(function(l){
  var b={};names.forEach(function(k,i){b[k]=l[i]});b.dur=Math.max.apply(null,l.map(function(x){return x.duration}));sets[t]=b;return b});
}
// level meters: one per channel and one for the master, each behind its gain; 16 segments from -60 dB to 0 dB
function lamp(el,n){if(el._n===n)return;el._n=n;var c=el.children;for(var i=0;i<c.length;i++)c[i].className=i<n?'on':''}
function meterTick(){
 if(!playing){mloop=0;$$('.mxmeter',mx).forEach(function(m){lamp(m,0)});return}
 var buf=new Float32Array(512);
 $$('.mxmeter',mx).forEach(function(m){var an=anal[m.getAttribute('data-meter')];if(!an)return;an.getFloatTimeDomainData(buf);var q=0,i;for(i=0;i<buf.length;i++)q+=buf[i]*buf[i];var db=20*Math.log10(Math.sqrt(q/buf.length)+1e-9);lamp(m,Math.max(0,Math.min(16,Math.round((db+60)/60*16))))});
 mloop=requestAnimationFrame(meterTick);
}
function stopSrc(){srcs.forEach(function(s){try{s.onended=null;s.stop()}catch(e){}});srcs=[]}
function pos(){return playing?Math.max(0,Math.min(dur(),off+cx.currentTime-t0)):off}   // t0 lies slightly ahead, so the first frames would be negative
function tick(){var p=pos(),d=dur();seek.value=d?Math.round(p/d*1000):0;time.textContent=fmt(p);if(playing)raf=requestAnimationFrame(tick)}
function start(from){
 stopSrc();apply();var b=sets[tp];off=from;t0=cx.currentTime+.05;
 names.forEach(function(k){var s=cx.createBufferSource();s.buffer=b[k];s.connect(gains[k]);s.start(t0,from);srcs.push(s)});
 srcs[0].onended=function(){if(playing&&pos()>=dur()-.1)finish()};
 playing=true;setIcon(true);cancelAnimationFrame(raf);tick(); if(!mloop)mloop=requestAnimationFrame(meterTick);
}
function pause(){if(!playing)return;off=pos();playing=false;stopSrc();setIcon(false);cancelAnimationFrame(raf);tick()}
function finish(){playing=false;stopSrc();off=0;setIcon(false);cancelAnimationFrame(raf);tick()}
function mark(){var tr=$('#mxtempo');if(tr){tr.value=tp;tr.setAttribute('aria-valuetext',tp+' %')}}   // the slider snaps to 80, 90 and 100
function setTempo(t){
 if(t===tp)return;
 var p=pos(),old=dur(),was=playing;
 tp=t;mark();
 if(!cx){off=0;return}
 pause();
 load(t).then(function(){
  if(tp!==t)return;   // the visitor changed the step again meanwhile
  var nd=dur();off=old?Math.min(Math.max(0,nd-.1),p*nd/old):0;
  if(was&&!playing)start(off);else if(!playing){seek.value=nd?Math.round(off/nd*1000):0;time.textContent=fmt(off)}
 }).catch(function(){});
}
play.addEventListener('click',function(){
 if(!AC)return;if(playing){pause();return}
 if(!cx)setup();if(cx.state==='suspended')cx.resume();
 A.pause();mixOwns=true;   // only one thing plays at a time
 mx.setAttribute('aria-busy','true');
 load(tp).then(function(){mx.removeAttribute('aria-busy');A.pause();if(!playing)start(off>=dur()-.1?0:off)}).catch(function(){mx.removeAttribute('aria-busy')});
});
seek.addEventListener('input',function(){if(!sets[tp])return;var p=seek.value/1000*dur();if(playing)start(p);else{off=p;time.textContent=fmt(p)}});
rows().forEach(function(r){var b=$('.mxb',r),v=$('.mxv',r),pc=$('.mxp2',r);
 function upd(){pc.innerHTML=v.value+'&nbsp;%';r.classList.toggle('off',b.getAttribute('aria-pressed')!=='true');apply()}
 b.addEventListener('click',function(){b.setAttribute('aria-pressed',b.getAttribute('aria-pressed')!=='true');upd()});
 v.addEventListener('input',upd)});
var tr=$('#mxtempo');if(tr)tr.addEventListener('input',function(){setTempo(tr.value)});
var mv=$('#mxmaster'),mp=$('#mxmp');if(mv)mv.addEventListener('input',function(){var v=+mv.value/100;mp.innerHTML=mv.value+'&nbsp;%';if(mgain)mgain.gain.setTargetAtTime(v*v,cx.currentTime,.02)});   // master: scales every stem and the room together; the limiter at the output still catches peaks
// the two never play together: starting the mixer stops the recordings; the recordings only start again when the visitor asks for them
// (on iPhones the system may resume an interrupted audio element by itself when the mixer pauses: such a start without a click on the recordings is stopped)
document.addEventListener('click',function(e){var t=e.target;if(t.closest&&!t.closest('#mix')&&t.closest('button,#player'))asked=Date.now()},true);
A.addEventListener('play',function(){if(mixOwns&&Date.now()-asked>1500){A.pause();return}mixOwns=false;pause()});
document.addEventListener('visibilitychange',function(){if(!document.hidden&&playing)tick()});
})();
window.addEventListener('resize',function(){clearTimeout(window.__rz);window.__rz=setTimeout(function(){draw();fitLead()},150)});
})();
'''

def inline_label(src, viewbox, title, note):
    """Official EU label file (classes in <style>) -> one small SVG with the styles inlined and the viewBox cropped to the label; the shapes stay unchanged."""
    rules = {m.group(1): [kv.strip().split(':', 1) for kv in m.group(2).split(';') if kv.strip()] for m in re.finditer(r'\.(cls-\d+)\s*\{([^}]*)\}', src)}
    body = src[src.index('</defs>') + 7:src.rindex('</svg>')]
    body = re.sub(r'class="(cls-\d+)"', lambda m: ' '.join(f'{k.strip()}="{v.strip()}"' for k, v in rules[m.group(1)]), body)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<!-- {note} -->\n<svg xmlns="http://www.w3.org/2000/svg" viewBox="{viewbox}" role="img"><title>{title}</title>{body.strip()}</svg>\n'

def ai_labels():
    """EU label "AI" for the website footer and the Markdown footers (common.MD_LABEL): black = the skill asset, white for dark mode = the official white file
    of the set (assets/eu-labels/) with the same crop. The long label "AI GENERATED" stays only in the header image."""
    AS = os.path.join(HERE, '..', 'choir-practice', 'assets')
    name, black, white, title = 'ai-basic', 'eu-ai-basic.svg', 'LABEL_AI_white.svg', 'AI'
    src = open(os.path.join(AS, black), encoding='utf-8').read()
    open(os.path.join(OUT, 'img', name + '.svg'), 'w', encoding='utf-8').write(src)
    vb = re.search(r'viewBox="([^"]+)"', src).group(1)
    dark = inline_label(open(os.path.join(AS, 'eu-labels', white), encoding='utf-8').read(), vb, title,
                        f'EU label "{title}", white (dark mode): official file {white} of the EU icon set, viewBox cropped to the label, styles inlined, shapes unchanged')
    open(os.path.join(OUT, 'img', name + '-dark.svg'), 'w', encoding='utf-8').write(dark)
    gh = open(os.path.join(AS, 'github-mark.svg'), encoding='utf-8').read()   # GitHub mark (Octicons, MIT) for the Markdown footers
    open(os.path.join(OUT, 'img', 'github-mark.svg'), 'w', encoding='utf-8').write(gh)
    open(os.path.join(OUT, 'img', 'github-mark-dark.svg'), 'w', encoding='utf-8').write(gh.replace('#000000', '#ffffff'))

# Writes css, js, both pages, sitemap and robots into docs/; CI fails if the committed docs/ differ from this output
def main():
    os.makedirs(os.path.join(OUT, 'css'), exist_ok=True); os.makedirs(os.path.join(OUT, 'js'), exist_ok=True); os.makedirs(os.path.join(OUT, 'de'), exist_ok=True); os.makedirs(os.path.join(OUT, 'en'), exist_ok=True)
    ai_labels()
    open(os.path.join(OUT, 'css', 'site.css'), 'w', encoding='utf-8').write(CSS)
    open(os.path.join(OUT, 'js', 'site.js'), 'w', encoding='utf-8').write(JS)
    open(os.path.join(OUT, 'de', 'index.html'), 'w', encoding='utf-8').write(ext(bust(nobreak(page('de')))))
    open(os.path.join(OUT, 'en', 'index.html'), 'w', encoding='utf-8').write(ext(bust(nobreak(page('en')))))
    alt = ''.join(f'<xhtml:link rel="alternate" hreflang="{h}" href="{u}"/>' for h, u in (('de', SITE + 'de/'), ('en', SITE + 'en/'), ('x-default', SITE)))
    open(os.path.join(OUT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9" xmlns:xhtml="http://www.w3.org/1999/xhtml">\n'
        + ''.join(f'<url><loc>{u}</loc>{alt}</url>\n' for u in (SITE + 'de/', SITE + 'en/')) + '</urlset>\n')
    open(os.path.join(OUT, '_redirects'), 'w', encoding='utf-8').write('/ /en/ 302\n')   # Cloudflare Pages: Startseite leitet auf Englisch um
    print('site built')

if __name__ == '__main__': main()
