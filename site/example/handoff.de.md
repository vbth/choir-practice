# Sitzungsübergabe: Alle meine Entchen – Chor-Übungspaket

**Datum:** {{date}} · **Erstellt mit:** Skill choir-practice {{skill_version}} · **Sprache der Unterhaltung:** Deutsch

## 0. Anweisungen für den nächsten Chat
Du setzt die Arbeit an einem fertigen Chor-Übungspaket fort. **Führe zuerst `bash <Skill-Ordner>/scripts/setup.sh` aus und warte, bis jedes Werkzeug „ok“ meldet** (frische Umgebungen haben keine Audio- und Notationswerkzeuge). Lese dann diese Datei vollständig. Verwende die Werte aus Abschnitt 4 genau so. Öffne Entscheidungen aus Abschnitt 3 nicht erneut, außer es wird ausdrücklich verlangt. Antworte zuerst mit höchstens 5 Zeilen: Stück, Stand, offene Punkte (Abschnitt 6), nächster Schritt – und warte dann.

## 1. Stück
- Titel: Alle meine Entchen
- Musik / Text: Unbekannt (Volkslied), gemeinfrei (Quelle: https://de.wikipedia.org/wiki/Alle_meine_Entchen, bestätigt). Der vierstimmige Satz ist neu gesetzt (Beispielpaket der Webseite).
- Besetzung: Sopran (Violinschlüssel), Alt (Violinschlüssel), Tenor (Violinschlüssel, eine Oktave tiefer), Bass (Bassschlüssel).
- C-Dur, 2/4, kein Auftakt, 20 Takte, eine Strophe, Schlussfermate.

## 2. Vorlage
- Keine Vorlage: Die Noten sind der Ausgangspunkt. Die Datei „Scan“ im Paket ist eine Kopie der gesetzten Noten.
- Besonderheiten: keine stimmenspezifischen Textzeilen, keine Wiederholungen.

## 3. Entscheidungen
| Entscheidung | Grund / bestätigt von |
|---|---|
| Melodiestimme | Sopran |
| Aufstellung (links → rechts) | S, A, T, B (Annahme, nicht bestätigt) |
| Tempo (Bezeichnung, bpm, Schlag) | Munter, 150 pro Viertel; langsame Fassung 80 % |
| Notenlayout | {{score_layout}} |
| Rechte (Status, Verwendungszweck, Referenz) | gemeinfrei, Üben im Chor, https://de.wikipedia.org/wiki/Alle_meine_Entchen |

## 4. Genaue Daten
- Paket: {{package}} (Datum {{date}}); oberste Ordner: {{folders}}
- Stimmen-ZIP-Dateien: vier (S, A, T, B), jede mit Anleitung, Noten und allen Übe-Dateien in Chor- und Klavierklang.
- Audio-Einstellungen: Stufen und Pegel, Soundfont und Lautheit stehen im Prüfprotokoll; langsame Fassung 80 %.

## 5. Korrekturen und Prüfungen
- Korrekturprotokoll: keine Einträge.
- Bestandene Schranken: siehe Prüfprotokoll.

## 6. Offene Punkte
- Die Audiodateien wurden nicht angehört, nur technisch geprüft; der Klang ist nicht beurteilt.
- Die Aufstellung S, A, T, B ist eine Annahme.

<!-- Fakten, die der Bau kennt, stehen als Platzhalter in doppelten geschweiften Klammern (date, package, skill_version, folders, score_layout, project_data); make_layout.py füllt sie. Nie von Hand eintippen. -->

## 7. So änderst du etwas
Bearbeite `{{project_data}}/score.json` (Projektdatenordner des Pakets; Format: references/score-spec.md), führe dann alles ab build_score.py (Phase 3) bis package.py (Phase 7) mit denselben Sprach- und Datumsregeln erneut aus; trage für jede Änderung einen Eintrag ins Korrekturprotokoll ein.
