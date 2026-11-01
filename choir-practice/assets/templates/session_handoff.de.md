# Sitzungsübergabe: <Titel> – Chor-Übungspaket

**Datum:** {{date}} · **Erstellt mit:** Skill choir-practice {{skill_version}} · **Sprache der Unterhaltung:** <Sprache>

## 0. Anweisungen für den nächsten Chat
Du setzt die Arbeit an einem fertigen Chor-Übungspaket fort. **Führe zuerst `bash <Skill-Ordner>/scripts/setup.sh` aus und warte, bis jedes Werkzeug „ok“ meldet** (frische Umgebungen haben keine Audio- und Notationswerkzeuge). Lese dann diese Datei vollständig. Verwende die Werte aus Abschnitt 4 genau so. Öffne Entscheidungen aus Abschnitt 3 nicht erneut, außer es wird ausdrücklich verlangt. Antworte zuerst mit höchstens 5 Zeilen: Stück, Stand, offene Punkte (Abschnitt 6), nächster Schritt – und warte dann.

## 1. Stück
- Titel / Untertitel:
- Musik / Bearbeitung / Text (+ Bestätigungsstatus und Quellenlinks):
- Besetzung, Stimmen und Schlüssel:
- Tonart, Taktart (Wechsel), Auftakt, Taktanzahl, Strophen- und Refrainstruktur:

## 2. Vorlage
- Gelieferte Datei, Art (Scan / Export), Qualität, Seitenzahl:
- Besonderheiten (stimmenspezifische Textzeilen, gepunktete Bögen, Wiederholungen, Begleitung):

## 3. Entscheidungen
| Entscheidung | Grund / bestätigt von |
|---|---|
| Melodiestimme | |
| Aufstellung (links → rechts) | |
| Tempo (Bezeichnung, bpm, Schlag) | |
| Notenlayout | {{score_layout}} |
| Rechte (Status, Referenz) | |

## 4. Genaue Daten
- Paket: {{package}} (Datum {{date}}); oberste Ordner: {{folders}}
- Anzahl Dateien, Stimmen-ZIP-Dateien:
- Audio-Einstellungen: Stufen und Pegel, Soundfont, Lautheit, Tempo der langsamen Fassung in %:

## 5. Korrekturen und Prüfungen
- Anzahl der Einträge im Korrekturprotokoll je Status (korrigiert / wie in der Vorlage / Interpretation / unsicher) und die wichtigen:
- Bestandene Schranken (Einrichtung, Sichtung, Werkdaten, Erfassung, Korrekturlesen ×2, Notensatz, Audio, Verifikation, Paket):

## 6. Offene Punkte
- <unsichere Stellen, unbestätigte Werkdaten, nicht Geprüftes (Audio nur technisch geprüft, Klang nicht beurteilt)>

<!-- Fakten, die der Bau kennt, stehen als Platzhalter in doppelten geschweiften Klammern (date, package, skill_version, folders, score_layout, project_data); make_layout.py füllt sie. Nie von Hand eintippen. -->

## 7. So änderst du etwas
Bearbeite `{{project_data}}/score.json` (Projektdatenordner des Pakets; Format: references/score-spec.md), führe dann alles ab build_score.py (Phase 3) bis package.py (Phase 7) mit denselben Sprach- und Datumsregeln erneut aus; trage für jede Änderung einen Eintrag ins Korrekturprotokoll ein.
