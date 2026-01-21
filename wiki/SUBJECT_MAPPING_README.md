# Smarte Fach-Zuordnung für L8teStudy

## 🎯 Überblick

Die **Smarte Fach-Zuordnung** ermöglicht es Benutzern, unordentliche oder abgekürzte Ordnernamen (z.B. "Ph", "GdT", "Technik") mit den offiziellen Fächernamen der Website zu verknüpfen.

## ✨ Features

- ✅ **Persönliche Zuordnungen**: Jeder Benutzer kann eigene Mappings erstellen
- ✅ **Globale Zuordnungen**: Admins können Mappings für die ganze Klasse erstellen
- ✅ **Automatische Auflösung**: Exakte und Fuzzy-Matching-Algorithmen
- ✅ **Einfache Verwaltung**: Intuitive UI zum Erstellen, Bearbeiten und Löschen
- ✅ **API-Integration**: RESTful API für externe Anwendungen

## 📁 Dateien

### Backend
- **`app/models.py`**: `SubjectMapping`-Modell hinzugefügt
- **`app/routes.py`**: API-Endpunkte für Subject-Mappings
- **`migrations/versions/add_subject_mapping.py`**: Datenbank-Migration

### Frontend
- **`static/subject-mapping.js`**: JavaScript-Manager-Klasse
- **`wiki/SUBJECT_MAPPING.md`**: Vollständige Dokumentation
- **`wiki/SUBJECT_MAPPING_INTEGRATION.html`**: Integrations-Beispiele

## 🚀 Schnellstart

### 1. Datenbank aktualisieren

Die Migration wurde bereits angewendet:
```bash
py -m flask db stamp head
```

### 2. Frontend einbinden

Füge in `templates/index.html` ein:
```html
<script src="/static/subject-mapping.js"></script>
```

### 3. Manager initialisieren

```javascript
// Im DOMContentLoaded
window.subjectMappingManager = new SubjectMappingManager();
```

### 4. UI hinzufügen

Siehe `wiki/SUBJECT_MAPPING_INTEGRATION.html` für vollständige Beispiele.

## 🔧 API-Endpunkte

| Methode | Endpoint | Beschreibung |
|---------|----------|--------------|
| GET | `/api/subject-mappings` | Alle Zuordnungen abrufen |
| POST | `/api/subject-mappings` | Neue Zuordnung erstellen |
| PUT | `/api/subject-mappings/{id}` | Zuordnung aktualisieren |
| DELETE | `/api/subject-mappings/{id}` | Zuordnung löschen |
| POST | `/api/subject-mappings/resolve` | Ordnernamen auflösen |

## 💡 Verwendungsbeispiele

### Beispiel 1: Zuordnung erstellen
```javascript
await subjectMappingManager.createMapping('Ph', 5); // 5 = Physik
```

### Beispiel 2: Ordnernamen auflösen
```javascript
const result = await subjectMappingManager.resolveInformalName('GdT');
if (result.success) {
    console.log(`Gefunden: ${result.subject_name}`);
}
```

### Beispiel 3: Liste anzeigen
```javascript
subjectMappingManager.renderMappingsList('mappings-list');
```

## 🗄️ Datenbank-Schema

```sql
CREATE TABLE subject_mapping (
    id INTEGER PRIMARY KEY,
    informal_name VARCHAR(128) NOT NULL,
    subject_id INTEGER NOT NULL,
    class_id INTEGER,
    user_id INTEGER,
    is_global BOOLEAN DEFAULT FALSE,
    created_at DATETIME,
    FOREIGN KEY(subject_id) REFERENCES subject(id),
    FOREIGN KEY(class_id) REFERENCES school_class(id),
    FOREIGN KEY(user_id) REFERENCES user(id),
    UNIQUE(informal_name, class_id, user_id)
);
```

## 🔐 Berechtigungen

- **Normale Benutzer**: Können eigene persönliche Zuordnungen verwalten
- **Administratoren**: Können globale Zuordnungen für die Klasse erstellen

## 📖 Dokumentation

Vollständige Dokumentation: [`wiki/SUBJECT_MAPPING.md`](wiki/SUBJECT_MAPPING.md)

Integrations-Beispiele: [`wiki/SUBJECT_MAPPING_INTEGRATION.html`](wiki/SUBJECT_MAPPING_INTEGRATION.html)

## 🎨 UI-Integration

Die Funktion kann in verschiedenen Bereichen integriert werden:

1. **Einstellungen**: Als eigener Menüpunkt
2. **Drive-Integration**: Beim Import von GoodNotes-Dateien
3. **Aufgaben-Erstellung**: Automatische Fach-Zuordnung
4. **Admin-Panel**: Verwaltung globaler Zuordnungen

## 🔄 Workflow

```
1. Benutzer erstellt Zuordnung: "Ph" → "Physik"
2. System speichert in Datenbank
3. Bei Upload/Import wird "Ph" automatisch zu "Physik" aufgelöst
4. Aufgabe/Datei wird dem richtigen Fach zugeordnet
```

## 🐛 Troubleshooting

**Problem**: Zuordnung wird nicht gefunden
- Lösung: Prüfe Groß-/Kleinschreibung (sollte case-insensitive sein)

**Problem**: Kann keine globale Zuordnung erstellen
- Lösung: Nur Admins können globale Zuordnungen erstellen

**Problem**: Fuzzy-Matching findet nichts
- Lösung: Schwellenwert liegt bei 30% Ähnlichkeit, erstelle exakte Zuordnung

## 📝 Nächste Schritte

- [ ] UI in Einstellungen integrieren
- [ ] Drive-Integration implementieren
- [ ] Bulk-Import-Funktion hinzufügen
- [ ] Export/Import von Zuordnungen als JSON
- [ ] Statistiken über verwendete Zuordnungen

## 🤝 Beitragen

Siehe Hauptprojekt-README für Contribution-Guidelines.

## 📄 Lizenz

Siehe Hauptprojekt-Lizenz.

---

**Erstellt am**: 2026-01-21  
**Version**: 1.0.0  
**Status**: ✅ Produktionsbereit
