# Noten

Detaillierte Anleitung zur Notenverwaltung und Durchschnittsberechnung in L8teStudy.

---

## 📊 Noten verwalten

### Note eintragen

1. **Navigiere zu "Noten"**
2. **Klicke auf das "+" Symbol**
3. **Fülle das Formular aus**:

**Pflichtfelder**:
- **Fach**: z.B. "Mathematik"
- **Note**: Zahlenwert (z.B. 2.0, 1.5, 3.0)

**Optionale Felder**:
- **Gewichtung**: Standard 1.0 (siehe unten)
- **Titel**: z.B. "Klausur 1", "mündlich"
- **Datum**: Wann wurde die Note erteilt?
- **Beschreibung**: Zusätzliche Informationen

4. **Speichern**

---

### Note bearbeiten

1. **Klicke auf die Note** in der Liste
2. **Bearbeiten-Symbol** (Stift)
3. **Ändere die Felder**
4. **Speichern**

---

### Note löschen

1. **Klicke auf die Note**
2. **Papierkorb-Symbol**
3. **Bestätigen**

---

## ⚖️ Gewichtung

Die Gewichtung bestimmt, wie stark eine Note in den Durchschnitt einfließt.

### Gewichtungs-Beispiele

| Notenart | Empfohlene Gewichtung |
|----------|----------------------|
| Mündliche Note | 0.5 |
| Hausaufgabe | 0.5 |
| Test/Arbeit | 1.0 |
| Klausur | 2.0 |
| Abschlussprüfung | 3.0 |

### Wie funktioniert Gewichtung?

**Beispiel**:
- Klausur: Note 2.0, Gewichtung 2.0 → Zählt wie zwei Noten mit 2.0
- Mündlich: Note 1.0, Gewichtung 0.5 → Zählt wie eine halbe Note mit 1.0

**Berechnung**:
```
Durchschnitt = (Note1 × Gewichtung1 + Note2 × Gewichtung2 + ...) 
               / (Gewichtung1 + Gewichtung2 + ...)
```

**Konkretes Beispiel**:
- Klausur: 2.0 (Gewichtung 2.0)
- Mündlich: 1.0 (Gewichtung 0.5)
- Test: 3.0 (Gewichtung 1.0)

```
Durchschnitt = (2.0×2.0 + 1.0×0.5 + 3.0×1.0) / (2.0 + 0.5 + 1.0)
             = (4.0 + 0.5 + 3.0) / 3.5
             = 7.5 / 3.5
             = 2.14
```

---

## 📈 Durchschnitte

### Fach-Durchschnitt

Für jedes Fach wird automatisch der gewichtete Durchschnitt berechnet.

**Anzeige**:
- Neben dem Fachnamen
- Farbcodiert: Grün (gut), Gelb (mittel), Rot (schlecht)
- Aktualisiert sich automatisch bei neuen Noten

---

### Gesamtdurchschnitt

Der Gesamtdurchschnitt ist der Durchschnitt aller Fach-Durchschnitte.

**Berechnung**:
```
Gesamtdurchschnitt = (Fach1-Durchschnitt + Fach2-Durchschnitt + ...) / Anzahl Fächer
```

**Hinweis**: Jedes Fach zählt gleich, unabhängig von der Anzahl der Noten.

---

### Durchschnitt verbessern

**Tipps**:
1. **Regelmäßig eintragen**: Vergiss keine Noten
2. **Gewichtung beachten**: Konzentriere dich auf wichtige Noten
3. **Trends erkennen**: Sieh dir die Entwicklung an
4. **Ziele setzen**: Berechne, welche Note du brauchst

**Beispiel-Rechnung**:
"Welche Note brauche ich in der nächsten Klausur für einen 2.0-Durchschnitt?"

Aktuell:
- Klausur 1: 2.5 (Gewichtung 2.0)
- Mündlich: 1.5 (Gewichtung 0.5)

Ziel: 2.0

```
2.0 = (2.5×2.0 + 1.5×0.5 + X×2.0) / (2.0 + 0.5 + 2.0)
2.0 = (5.0 + 0.75 + 2X) / 4.5
9.0 = 5.75 + 2X
X = 1.625
```

Du brauchst eine 1.625 (oder besser) in der nächsten Klausur.

---

## 📊 Notenübersicht

### Nach Fach sortiert

**Ansicht**:
- Fächer als Kategorien
- Noten chronologisch unter jedem Fach
- Durchschnitt pro Fach

**Filtern**:
- Klicke auf ein Fach
- Nur Noten dieses Fachs werden angezeigt

---

### Chronologische Ansicht

**Alle Noten nach Datum**:
- Neueste zuerst
- Übersicht über alle Fächer
- Schneller Überblick

---

### Statistiken

**Auf der Noten-Seite**:
- **Anzahl Noten**: Gesamt und pro Fach
- **Beste Note**: Deine beste Note
- **Schlechteste Note**: Deine schlechteste Note
- **Trend**: Verbesserung oder Verschlechterung

---

## 🎯 Notenziele

### Ziel setzen

**Beispiele**:
- "Ich will in Mathe auf 2.0 kommen"
- "Ich will meinen Gesamtdurchschnitt auf 1.8 verbessern"
- "Ich will in allen Fächern besser als 3.0 sein"

**Tracking**:
- Notiere dein Ziel in der Beschreibung
- Prüfe regelmäßig den Fortschritt
- Passe deine Lernstrategie an

---

### Benötigte Note berechnen

**Formel**:
```
Benötigte Note = (Ziel × Summe Gewichtungen - Summe (Note × Gewichtung)) / Gewichtung neue Note
```

**Online-Rechner**: Nutze einen Notenrechner oder erstelle eine Excel-Tabelle

---

## 📱 Noten-Features

### Export

**Daten exportieren**:
1. **Admin** → **Superadmin Dashboard** (nur Super Admin)
2. **Backup & Restore**
3. **Daten exportieren**
4. JSON-Datei enthält alle Noten

**Hinweis**: Normale Benutzer können keine Noten exportieren. Frage deinen Admin.

---

### Privatsphäre

**Wichtig**: 
- Noten sind **privat**
- Nur du siehst deine Noten
- Admins sehen KEINE Noten von Schülern
- Auch Super Admins haben keinen Zugriff auf Noten

**Ausnahme**: Datenbank-Backups enthalten alle Daten (verschlüsselt).

---

## 💡 Tipps & Tricks

### Regelmäßig eintragen

**Warum**:
- Vergiss keine Noten
- Aktueller Durchschnitt
- Bessere Planung

**Wie**:
- Trage Noten sofort nach Erhalt ein
- Setze Erinnerungen
- Mache es zur Gewohnheit

---

### Gewichtung richtig nutzen

**Faustregel**:
- Mündlich/Hausaufgaben: 0.5
- Tests/Arbeiten: 1.0
- Klausuren: 2.0
- Wichtige Prüfungen: 3.0

**Anpassen**:
- Frage deinen Lehrer nach der Gewichtung
- Passe an dein Schulsystem an
- Sei konsistent

---

### Beschreibungen nutzen

**Was eintragen**:
- Thema der Klausur
- Warum diese Note?
- Was kann ich verbessern?
- Ziele für nächstes Mal

**Beispiel**:
```
Titel: Klausur 1
Note: 2.5
Beschreibung: Thema: Integralrechnung
              Fehler bei Aufgabe 3
              Nächstes Mal: Mehr Übungsaufgaben
```

---

### Notenverlauf analysieren

**Fragen**:
- Verbessere ich mich?
- In welchen Fächern bin ich stark/schwach?
- Wo brauche ich mehr Übung?
- Welche Notenarten fallen mir schwer?

**Aktion**:
- Fokussiere dich auf schwache Fächer
- Nutze Stärken aus
- Hole dir Hilfe bei Problemen

---

## 📚 Notensysteme

### Deutschland (1-6)

| Note | Bedeutung |
|------|-----------|
| 1.0 | Sehr gut |
| 2.0 | Gut |
| 3.0 | Befriedigend |
| 4.0 | Ausreichend |
| 5.0 | Mangelhaft |
| 6.0 | Ungenügend |

**Zwischennoten**: 1.5, 2.5, 3.5, etc.

---

### Schweiz (6-1)

| Note | Bedeutung |
|------|-----------|
| 6.0 | Sehr gut |
| 5.0 | Gut |
| 4.0 | Genügend |
| 3.0 | Ungenügend |
| 2.0 | Schlecht |
| 1.0 | Sehr schlecht |

**Hinweis**: L8teStudy unterstützt beide Systeme. Sei konsistent!

---

### Punkte-System (0-15)

Für Oberstufe/Abitur:

| Punkte | Note |
|--------|------|
| 15-13 | Sehr gut (1) |
| 12-10 | Gut (2) |
| 9-7 | Befriedigend (3) |
| 6-4 | Ausreichend (4) |
| 3-1 | Mangelhaft (5) |
| 0 | Ungenügend (6) |

**Tipp**: Trage Punkte direkt ein (z.B. 12.0) oder rechne in Noten um.

---

## 🆘 Häufige Probleme

### Durchschnitt stimmt nicht

**Lösungen**:
1. **Gewichtung prüfen**: Sind alle Gewichtungen korrekt?
2. **Alle Noten eingetragen**: Fehlt eine Note?
3. **Fach-Zuordnung**: Sind Noten dem richtigen Fach zugeordnet?
4. **Neu berechnen**: Seite neu laden

---

### Note kann nicht gelöscht werden

**Ursache**: Möglicherweise ein Browser-Problem

**Lösung**:
1. Seite neu laden
2. Anderen Browser versuchen
3. Cache leeren

---

### Noten werden nicht angezeigt

**Lösungen**:
1. **Filter prüfen**: Ist ein Fachfilter aktiv?
2. **Neu laden**: Seite aktualisieren
3. **Eingeloggt**: Bist du noch angemeldet?

---

## 📚 Weitere Ressourcen

- **[Erste Schritte](Erste-Schritte)** - Grundlagen
- **[Aufgaben und Termine](Aufgaben-und-Termine)** - Aufgabenverwaltung
- **[Troubleshooting](Troubleshooting)** - Probleme lösen

---

**Viel Erfolg bei deinen Noten!** 📊
