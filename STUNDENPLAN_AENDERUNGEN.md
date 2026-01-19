# Stundenplan Änderungsanzeige - Verbesserungen

## Übersicht
Die Stundenplan-Seite wurde erweitert, um **alle Arten von Änderungen** deutlich sichtbar zu machen:

## Neue Funktionen

### 1. **Neue Stunden** (Stunden, die vorher nicht im Plan waren)
- **Badge**: Orange "Neu" Badge
- **Visuell**: Orange linker Rand + leicht orange Hintergrund
- **Anwendung**: Wenn eine Vertretungsstunde hinzugefügt wird, ohne dass eine andere Stunde entfällt

### 2. **Raumänderungen** (nur der Raum hat sich geändert)
- **Badge**: Hellblau "Raum geändert"
- **Visuell**: Hellblauer linker Rand + leicht blauer Hintergrund
- **Anzeige**: 
  - Alter Raum durchgestrichen
  - Pfeil (→)
  - Neuer Raum in Akzentfarbe hervorgehoben

### 3. **Lehreränderungen** (nur der Lehrer hat sich geändert)
- **Badge**: Hellblau "Lehrer geändert"
- **Visuell**: Hellblauer linker Rand + leicht blauer Hintergrund
- **Anzeige**:
  - Alter Lehrer durchgestrichen
  - Pfeil (→)
  - Neuer Lehrer in Akzentfarbe hervorgehoben

### 4. **Raum & Lehrer Änderungen** (beides hat sich geändert)
- **Badge**: Hellblau "Raum & Lehrer geändert"
- **Visuell**: Hellblauer linker Rand
- **Anzeige**: Beide Änderungen werden mit Pfeilen angezeigt

### 5. **Vollständige Vertretungen** (Fach wurde ersetzt)
- **Badge**: Grün "Vertretung"
- **Visuell**: Grüner linker Rand
- **Anzeige**:
  - Altes Fach durchgestrichen → Neues Fach
  - Raum- und Lehreränderungen werden ebenfalls angezeigt

### 6. **Entfallene Stunden**
- **Badge**: Rot "Entfällt"
- **Visuell**: Reduzierte Opazität, roter Hintergrund
- Bleibt unverändert wie vorher

## Farbschema

| Änderungstyp | Farbe | Badge-Hintergrund | Rand |
|--------------|-------|-------------------|------|
| Neu | Orange | #FF9500 | 4px solid #FF9500 |
| Raum/Lehrer geändert | Hellblau | #5AC8FA | 4px solid #5AC8FA |
| Vertretung | Grün | #34c759 | 4px solid #34c759 |
| Entfällt | Rot | #FF3B30 | - |

## Technische Details

### CSS-Klassen hinzugefügt:
```css
.status-badge.new          /* Orange Badge für neue Stunden */
.status-badge.changed      /* Hellblau Badge für Raum/Lehrer-Änderungen */
.period-card.new-lesson    /* Styling für neue Stunden */
.period-card.room-change   /* Styling für Raum/Lehrer-Änderungen */
```

### JavaScript-Logik:
Die `renderTimetableList()` Funktion wurde erweitert um:
1. Vergleich von alten und neuen Lehrern (zusätzlich zu Fächern und Räumen)
2. Erkennung von Teiländerungen (nur Raum oder nur Lehrer)
3. Intelligente Badge-Auswahl basierend auf der Art der Änderung
4. Visuelle Hervorhebung geänderter Felder mit Pfeilen und Akzentfarbe

## Beispiele

**Szenario 1**: Eine neue 5. Stunde wurde hinzugefügt
- Zeigt: Orange "Neu" Badge, orange Rand

**Szenario 2**: Mathe findet im Raum 204 statt statt 201
- Zeigt: Hellblau "Raum geändert" Badge
- Anzeige: "201 → 204" (201 durchgestrichen, 204 hervorgehoben)

**Szenario 3**: Deutsch hat einen Vertretungslehrer
- Zeigt: Hellblau "Lehrer geändert" Badge
- Anzeige: "Müller → Schmidt" (Müller durchgestrichen, Schmidt hervorgehoben)

**Szenario 4**: Mathe wurde durch Sport ersetzt
- Zeigt: Grün "Vertretung" Badge
- Anzeige: "Mathe → Sport" mit allen Details
