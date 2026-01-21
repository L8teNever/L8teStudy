# Smarte Fach-Zuordnung - Dokumentation

## Übersicht

Die **Smarte Fach-Zuordnung** ermöglicht es Benutzern und Administratoren, unordentliche oder abgekürzte Ordnernamen (z.B. "Ph", "GdT", "Technik") mit den offiziellen Fächernamen der Website zu verknüpfen.

## Features

### 1. Zuordnungen erstellen
- **Persönliche Zuordnungen**: Jeder Benutzer kann eigene Zuordnungen erstellen
- **Globale Zuordnungen**: Administratoren können Zuordnungen für die ganze Klasse erstellen

### 2. Automatische Auflösung
- Exakte Übereinstimmung (case-insensitive)
- Fuzzy-Matching für ähnliche Namen
- Vorschläge bei unbekannten Namen

### 3. Verwaltung
- Zuordnungen anzeigen
- Zuordnungen bearbeiten (nur eigene)
- Zuordnungen löschen (nur eigene)

## API-Endpunkte

### GET /api/subject-mappings
Gibt alle Zuordnungen für den aktuellen Benutzer zurück (persönliche + globale).

**Response:**
```json
[
  {
    "id": 1,
    "informal_name": "Ph",
    "subject_id": 5,
    "subject_name": "Physik",
    "is_global": false,
    "is_own": true,
    "created_at": "2026-01-21T11:00:00"
  }
]
```

### POST /api/subject-mappings
Erstellt eine neue Zuordnung.

**Request:**
```json
{
  "informal_name": "GdT",
  "subject_id": 3,
  "is_global": false
}
```

**Response:**
```json
{
  "success": true,
  "id": 2,
  "informal_name": "GdT",
  "subject_id": 3,
  "subject_name": "Grundlagen der Technik",
  "is_global": false
}
```

### PUT /api/subject-mappings/{id}
Aktualisiert eine bestehende Zuordnung.

**Request:**
```json
{
  "informal_name": "Physik",
  "subject_id": 5
}
```

### DELETE /api/subject-mappings/{id}
Löscht eine Zuordnung.

### POST /api/subject-mappings/resolve
Löst einen informellen Namen zu einem offiziellen Fach auf.

**Request:**
```json
{
  "informal_name": "Ph"
}
```

**Response (Exakte Übereinstimmung):**
```json
{
  "success": true,
  "subject_id": 5,
  "subject_name": "Physik",
  "mapping_id": 1,
  "match_type": "exact"
}
```

**Response (Fuzzy Match):**
```json
{
  "success": true,
  "subject_id": 5,
  "subject_name": "Physik",
  "match_type": "fuzzy",
  "confidence": 0.75
}
```

**Response (Kein Match):**
```json
{
  "success": false,
  "message": "No matching subject found",
  "suggestions": [
    {"id": 1, "name": "Mathematik"},
    {"id": 2, "name": "Deutsch"}
  ]
}
```

## Frontend-Integration

### 1. JavaScript einbinden

Füge in `index.html` das Script ein:
```html
<script src="/static/subject-mapping.js"></script>
```

### 2. Manager initialisieren

```javascript
// Im DOMContentLoaded oder nach dem Laden der Seite
subjectMappingManager = new SubjectMappingManager();
```

### 3. UI-Komponenten hinzufügen

#### Zuordnungen-Liste anzeigen
```html
<div id="mappings-list"></div>
<script>
  subjectMappingManager.renderMappingsList('mappings-list');
</script>
```

#### Neue Zuordnung erstellen
```html
<!-- Sheet für Erstellung -->
<div class="sheet-overlay" id="createMappingSheetOverlay">
    <div class="sheet" id="createMappingSheet"></div>
</div>

<!-- Button zum Öffnen -->
<button onclick="subjectMappingManager.showCreateDialog()">
    Neue Zuordnung
</button>
```

#### Zuordnung bearbeiten
```html
<!-- Sheet für Bearbeitung -->
<div class="sheet-overlay" id="editMappingSheetOverlay">
    <div class="sheet" id="editMappingSheet"></div>
</div>
```

### 4. Ordnernamen auflösen

```javascript
// Beispiel: Ordnername zu Fach auflösen
const result = await subjectMappingManager.resolveInformalName('Ph');
if (result && result.success) {
    console.log(`Gefunden: ${result.subject_name} (ID: ${result.subject_id})`);
    console.log(`Match-Typ: ${result.match_type}`);
}
```

## Datenbank-Schema

### Tabelle: subject_mapping

| Spalte | Typ | Beschreibung |
|--------|-----|--------------|
| id | INTEGER | Primary Key |
| informal_name | VARCHAR(128) | Informeller/abgekürzter Name |
| subject_id | INTEGER | Foreign Key zu Subject |
| class_id | INTEGER | Foreign Key zu SchoolClass (NULL bei persönlichen Zuordnungen) |
| user_id | INTEGER | Foreign Key zu User (NULL bei globalen Zuordnungen) |
| is_global | BOOLEAN | True = für ganze Klasse, False = nur für Benutzer |
| created_at | DATETIME | Erstellungszeitpunkt |

**Unique Constraint:** `(informal_name, class_id, user_id)`

## Berechtigungen

- **Normale Benutzer:**
  - Können eigene persönliche Zuordnungen erstellen, bearbeiten und löschen
  - Können globale Zuordnungen sehen, aber nicht bearbeiten

- **Administratoren:**
  - Können globale Zuordnungen für die ganze Klasse erstellen
  - Können alle Zuordnungen sehen und verwalten

## Verwendungsbeispiele

### Beispiel 1: GoodNotes-Ordner zuordnen
Ein Schüler hat in GoodNotes einen Ordner "GdT" für "Grundlagen der Technik":
1. Öffnet die Zuordnungsverwaltung
2. Klickt auf "Neue Zuordnung"
3. Gibt "GdT" als Ordnernamen ein
4. Wählt "Grundlagen der Technik" aus der Liste
5. Speichert die Zuordnung

### Beispiel 2: Admin erstellt Klassen-Standard
Ein Admin möchte für die ganze Klasse festlegen, dass "Ph" = "Physik":
1. Öffnet die Zuordnungsverwaltung
2. Klickt auf "Neue Zuordnung"
3. Gibt "Ph" ein
4. Wählt "Physik"
5. Aktiviert "Global für Klasse"
6. Speichert

### Beispiel 3: Automatische Auflösung bei Upload
Wenn ein Schüler eine Datei aus dem Ordner "Technik" hochlädt:
```javascript
const result = await subjectMappingManager.resolveInformalName('Technik');
if (result.success) {
    // Verwende result.subject_id für die Aufgabe/Datei
    taskData.subject_id = result.subject_id;
}
```

## Migration

Die Datenbank-Migration wurde bereits erstellt:
- Datei: `migrations/versions/add_subject_mapping.py`
- Status: Angewendet mit `flask db stamp head`

## Nächste Schritte

1. **UI-Integration**: Füge eine neue Seite oder einen Tab in den Einstellungen hinzu
2. **Drive-Integration**: Nutze die Auflösung beim Import von GoodNotes-Dateien
3. **Bulk-Import**: Ermögliche das Importieren mehrerer Zuordnungen auf einmal
4. **Export/Import**: Zuordnungen als JSON exportieren/importieren

## Troubleshooting

### Problem: Zuordnung wird nicht gefunden
- Prüfe, ob die Zuordnung für den richtigen Benutzer/Klasse erstellt wurde
- Prüfe die Groß-/Kleinschreibung (sollte case-insensitive sein)

### Problem: Kann globale Zuordnung nicht erstellen
- Nur Administratoren können globale Zuordnungen erstellen
- Prüfe die Benutzerrolle

### Problem: Fuzzy-Matching findet nichts
- Der Schwellenwert liegt bei 0.3 (30% Ähnlichkeit)
- Versuche, eine exakte Zuordnung zu erstellen
