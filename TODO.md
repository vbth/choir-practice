# To-Do

Arbeitsliste für Website, READMEs und Skill. Die IDs (O1 bis O26) entsprechen `choir-practice/session-handoff.md`, Abschnitt 4. Stand: 29.10.2026, Draft-PR [#4](https://github.com/vbth/choir-practice/pull/4).

## A. Entscheidung von dir nötig

| ID | Frage | Optionen |
|---|---|---|
| O11 | Prüfzeilen im Ablauf, Schritte 6 bis 9: „Fehlerfrei?“ (6) und „Alles sauber?“ (7) überschneiden sich, 8 und 9 unklar | Wortlaut je Schritt festlegen oder Zeilen streichen |
| O20 | Ersatz für „Lizenzen für Noten müssen eingehalten werden.“ | 1. „Ob die Noten verarbeitet und weitergegeben werden dürfen, richtet sich nach ihrer Lizenz.“ 2. „Die Lizenzbedingungen der Noten bleiben maßgeblich, der Skill ersetzt keine Erlaubnis.“ 3. „Wer Noten hochlädt, muss deren Lizenz einhalten.“ |
| O24 | `LICENSE` zu `LICENSE.md` umbenennen? | Ja: lesbar auf GitHub, aber `release.py`, `checks.yml`, READMEs, Website nachziehen. Nein: bleibt Rohtext |
| – | Schritt 12 im Ablauf: War „Tipp herunterladen“ gemeint als „ZIP herunterladen“? | Bestätigen |
| – | Bildunterschriften im Modul 2 („Nur die eigene Stimme, in der Mitte“) an die neue Einleitung („Jeweils eine Stimme …“) angleichen? | Ja / nein |

## B. Bereit zur Umsetzung

| ID | Aufgabe |
|---|---|
| O32 | Englische Fassung des Hinweises bestätigen: aktuell „AI-generated, no guarantee for copyright and licence rights“. Alternativen: „AI-generated, copyright and licence rights without warranty“ oder „AI-generated, copyright and licence rights without guarantee“. Änderung an einer Stelle: `ai_note`, `ai_note_info`, `ai_meta` in `en.json`, dazu die Texte in README, SKILL.md und `site/build_site.py` |
| O4 | Handtuch in `site/header/header-src.svg` (Gruppe `towel`): schwarzen Bogen und roten Punkt entfernen. Danach alle Assets für Website und README neu bauen: `site/header/build.sh` (`docs/img/header.png`), `site/make_previews.py`, `site/build_site.py` |
| O25 | Markdown-Dateien im Paket: die grau hinterlegten Datei- und Ordnerverweise zusätzlich verlinken (Datei im Paket oder im Repo) |

## C. Später

| ID | Aufgabe |
|---|---|
| O26 | Rechte-Review gemeinsam (offen sind die fünf Einträge „to check“ in `THIRD_PARTY_NOTICES.md`): jede Komponente (Schriften, EU-Label, Verovio, Leland, Soundfonts, Pakete, Website-Assets) durchgehen. Pro Komponente festlegen, wo dokumentiert wird und ob öffentlich. Prüfen, ob `THIRD_PARTY_NOTICES.md` einen eindeutigeren Namen braucht. Technische Prüfung gegen die Lizenztexte, keine Rechtsberatung |
| O35 | Website-Footer „privates Projekt“: „nichtkommerziell“ ergänzen? Zusammen mit O26 klären, ob die Seite ein Impressum und eine Datenschutzerklärung braucht (Hosting auf GitHub Pages). Die Selbstbezeichnung allein entscheidet das nicht |
| O1 | Repo-Umzug nach `vbth/choir-practice-material`: `common.MD_LABEL`, `GH` und `SITE` in `site/build_site.py`, README-Links anpassen |
| O2 | Website-Reihenfolge: Beispiel zuerst, dann Paket, Üben, Loslegen, Ablauf, Rechte, Lizenz |
| O3 | Kopfhörer-Grafik: Melodiestimme auf Höhe der eigenen Stimme zeichnen, Unterschrift „Kopfhörer, aus deiner Sicht“ |

## D. Am Gerät testen

- Modul 2: Klick auf eine Stimme startet die Aufnahme von vorn (nur im Code geprüft, nicht mit echter Audiowiedergabe).
- Modul 2: Schallwellen erscheinen beim Abspielen und verschwinden bei Pause.

## E. Erledigt in PR 4

O5 Logo-Link auf Hauptseiten-URL · O6 mobiler Abstand Headline zu Headerbild · O7 Statistik „2 Fassungen“ · O8 Call to Action im Ablauf · O9 Schritt 2 „Stopp A“ · O10 Ablauf-Texte (Schritte 2, 3, 10, 11, 12) · O12 Modul-2-Einleitung · O13 Kopfhörerblock und Bildunterschrift zentriert · O14 Neustart bei Stimmwechsel · O15 Schallwellen · O16 Buchstaben mittig und größer · O17 Tutti-Abstand · O18 Button ohne MB · O19 Rechtetext Modul 4 · O21 Drittanbieter-Lizenzen im Modul 6 verlinkt · O27 „Lizenzen“ (Mehrzahl) in Menü und Modul 6 · O28 Footer-Link auf das Repo · O29 Drittanbieter-Prüfschritt (Skript `check_third_party.py`, `setup.sh`, SKILL.md, `release.py`, CI, Pflichtabschnitt 5 im Skill-Handoff) · O30 `THIRD_PARTY_NOTICES.md` vervollständigt · O34 Einheitliches „AI“-Icon auch im Albumcover und im Website-Footer (Header-Bild behält „AI GENERATED“) · O33 ISO-Datum überall, Website-Footer nur mit Jahr (aus dem Release-Datum) · O31 komplettes offizielles EU-Label-Set (12 SVG) im Bundle, Dark-Mode-Kopien aus den offiziellen weißen Dateien · O23 Hinweis „KI-generiert, Urheber- und Lizenzrechte ohne Gewähr“ überall festgeschrieben · O22 Label „AI“ in PDFs, Markdown und Beispielvorschauen (rundes offizielles Icon; Albumcover, Header-Bild und Website-Footer behalten „AI GENERATED“)
