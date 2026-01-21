# 🚀 L8teStudy Drive Integration

## Übersicht

Die **Drive Integration** ist ein leistungsstarkes Feature für L8teStudy, das automatisch handschriftliche Notizen aus GoodNotes (via Google Drive Backup) einsammelt, verschlüsselt speichert und für die gesamte Klasse durchsuchbar macht.

![Architecture](../artifacts/drive_integration_architecture.png)

## ✨ Hauptfunktionen

### 🔄 Automatische Synchronisation
- **Background Worker**: Scannt Google Drive Ordner alle 15 Minuten
- **Change Detection**: SHA-256 Hash-basierte Erkennung von Änderungen
- **Einweg-System**: Nur Lesezugriff auf Google Drive

### 🔒 Sicherheit & Verschlüsselung
- **AES-256-GCM**: Militärische Verschlüsselung für alle Dateien
- **Live-Entschlüsselung**: Dateien werden nur im RAM entschlüsselt
- **Privacy-Level**: Jeder Ordner kann "Privat" oder "Öffentlich" sein
- **Metadaten-Authentifizierung**: AAD (Additional Authenticated Data)

### 🔍 Intelligente Suche
- **SQLite FTS5**: Blitzschnelle Volltextsuche
- **OCR-Integration**: Automatische Textextraktion aus PDFs
- **Filter**: Nach Fach, Benutzer, Datum
- **Snippet-Extraktion**: Relevante Textausschnitte mit Highlighting
- **Urheber-Transparenz**: "Gefunden in 'Mathe-Notizen' von Lena"

### 🎯 Smarte Fach-Zuordnung
- **Fuzzy-Matching**: Erkennt ähnliche Namen (Ph → Physik)
- **Alias-System**: Häufige Abkürzungen automatisch zuordnen
- **Manuelle Korrektur**: Admins und User können Zuordnungen anpassen

## 📦 Installation

### 1. Dependencies installieren

```bash
pip install -r requirements.txt
```

### 2. Google Service Account einrichten

1. **Google Cloud Console** öffnen: https://console.cloud.google.com
2. Neues Projekt erstellen: "L8teStudy Drive"
3. **Google Drive API** aktivieren
4. **Service Account** erstellen:
   - Navigation: IAM & Admin → Service Accounts
   - "Create Service Account"
   - Name: "L8teStudy Drive Sync"
   - Role: Keine (nur Drive-Zugriff)
5. **JSON-Key** herunterladen:
   - Service Account auswählen
   - Keys → Add Key → Create new key → JSON
   - Datei speichern als `service-account.json`

### 3. Konfiguration

#### Docker (Empfohlen)
Die Variablen werden direkt in der `docker-compose.yml` unter `environment` konfiguriert. 

#### Lokal (.env)
Falls du kein Docker nutzt, erstelle eine `.env` Datei:
```env
# Google Drive Integration (Alternative: In docker-compose.yml konfiguriert)
# GOOGLE_SERVICE_ACCOUNT_FILE=instance/service-account.json
# DRIVE_ENCRYPTION_KEY=qv6aHbyp1j1xHpLVE87DIax+x/4YvD54rlh3SbZGTjg=
# ENCRYPTED_FILES_PATH=instance/encrypted_files
```

### 4. Datenbank Migration

```bash
flask db migrate -m "Add Drive Integration models"
flask db upgrade
```

### 5. FTS5-Tabelle initialisieren

```python
from app import create_app
from app.drive_search import get_drive_search_service

app = create_app()
with app.app_context():
    search = get_drive_search_service()
    search.ensure_fts_table()
    print("FTS5 table created successfully!")
```

## 🎮 Verwendung

### Für Schüler: Ordner freigeben

1. **GoodNotes Backup** in Google Drive aktivieren
2. **Backup-Ordner** in Google Drive öffnen
3. **Ordner teilen** mit der Service Account Email:
   - Rechtsklick auf Ordner → "Teilen"
   - Service Account Email einfügen (z.B. `l8testudy-drive@project-id.iam.gserviceaccount.com`)
   - Berechtigung: **"Betrachter"** (Read-only)
4. **Ordner-ID** kopieren:
   - URL des Ordners: `https://drive.google.com/drive/folders/1234567890abcdef`
   - Ordner-ID: `1234567890abcdef`
5. **In L8teStudy** auf der Drive-Seite:
   - "Ordner hinzufügen" klicken
   - Ordner-ID einfügen
   - Privacy-Level wählen (Privat/Öffentlich)

### Für Entwickler: API-Nutzung

#### Ordner hinzufügen

```python
from app.drive_sync import get_drive_sync_service

sync_service = get_drive_sync_service()

# Ordner hinzufügen
folder = sync_service.add_folder(
    user_id=1,
    folder_id='1234567890abcdef',
    privacy_level='public'  # oder 'private'
)

print(f"Ordner '{folder.folder_name}' hinzugefügt!")
```

#### Manueller Sync

```python
# Einzelnen Ordner synchronisieren
stats = sync_service.sync_folder(folder.id)
print(f"Neue Dateien: {stats['new_files']}")
print(f"Aktualisierte Dateien: {stats['updated_files']}")

# Alle Ordner synchronisieren
all_stats = sync_service.sync_all_folders()
print(f"Synchronisierte Ordner: {all_stats['synced_folders']}")
```

#### Suche

```python
from app.drive_search import get_drive_search_service

search_service = get_drive_search_service(current_user_id=1)

# Einfache Suche
results = search_service.search(
    query='Photosynthese',
    limit=20
)

for result in results:
    print(f"{result['filename']} - von {result['username']}")
    print(f"Snippet: {result['snippet']}")

# Gefilterte Suche
results = search_service.search(
    query='Integral',
    subject_id=5,  # Mathematik
    user_id=3,     # Nur von User 3
    limit=10
)
```

#### Datei herunterladen

```python
from app.drive_encryption import get_drive_encryption_manager
from flask import send_file
import io

encryption_manager = get_drive_encryption_manager()

# Datei entschlüsseln (im RAM)
decrypted_bytes = encryption_manager.decrypt_file_to_memory(
    encrypted_path='/path/to/encrypted/file.enc',
    metadata={'file_id': '123'}
)

# Als Download bereitstellen
return send_file(
    io.BytesIO(decrypted_bytes),
    mimetype='application/pdf',
    as_attachment=True,
    download_name='notizen.pdf'
)
```

#### Fach-Zuordnung

```python
from app.subject_mapper import get_subject_mapper

mapper = get_subject_mapper(class_id=1, user_id=1)

# Automatische Zuordnung
subject = mapper.map_folder_to_subject('Ph', auto_create=True)
print(f"'Ph' wurde zugeordnet zu: {subject.name}")

# Vorschläge abrufen
suggestions = mapper.suggest_multiple('Mathe', limit=5)
for subject, score in suggestions:
    print(f"{subject.name} - Ähnlichkeit: {score:.2f}")

# Manuelle Zuordnung erstellen
mapping = mapper.create_mapping(
    informal_name='GdT',
    subject_id=10,  # Grundlagen der Technik
    is_global=True  # Für alle in der Klasse
)
```

## 🔧 APScheduler Integration

In `app/__init__.py` oder `app/scheduler.py`:

```python
from flask_apscheduler import APScheduler
from app.drive_sync import get_drive_sync_service

scheduler = APScheduler()

@scheduler.task('interval', id='drive_sync', minutes=15)
def sync_drive_folders():
    """Synchronisiert alle Drive-Ordner alle 15 Minuten"""
    with app.app_context():
        sync_service = get_drive_sync_service()
        stats = sync_service.sync_all_folders()
        
        app.logger.info(
            f"Drive Sync: {stats['synced_folders']} folders synced, "
            f"{stats['new_files']} new files, "
            f"{stats['updated_files']} updated files"
        )
        
        if stats['errors']:
            app.logger.error(f"Drive Sync errors: {stats['errors']}")

# Scheduler starten
scheduler.init_app(app)
scheduler.start()
```

## 📊 Datenbank-Schema

### DriveFolder
```sql
CREATE TABLE drive_folder (
    id INTEGER PRIMARY KEY,
    user_id INTEGER NOT NULL,
    folder_id VARCHAR(256) NOT NULL,
    folder_name VARCHAR(256) NOT NULL,
    privacy_level VARCHAR(20) DEFAULT 'private',
    sync_enabled BOOLEAN DEFAULT 1,
    last_sync_at DATETIME,
    sync_status VARCHAR(50) DEFAULT 'pending',
    sync_error TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES user(id),
    UNIQUE (user_id, folder_id)
);
```

### DriveFile
```sql
CREATE TABLE drive_file (
    id INTEGER PRIMARY KEY,
    drive_folder_id INTEGER NOT NULL,
    file_id VARCHAR(256) NOT NULL,
    filename VARCHAR(512) NOT NULL,
    encrypted_path VARCHAR(512) NOT NULL,
    file_hash VARCHAR(64) NOT NULL,
    file_size INTEGER NOT NULL,
    mime_type VARCHAR(128) NOT NULL,
    subject_id INTEGER,
    auto_mapped BOOLEAN DEFAULT 0,
    ocr_completed BOOLEAN DEFAULT 0,
    ocr_error TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (drive_folder_id) REFERENCES drive_folder(id),
    FOREIGN KEY (subject_id) REFERENCES subject(id),
    UNIQUE (drive_folder_id, file_id)
);
```

### DriveFileContent
```sql
CREATE TABLE drive_file_content (
    id INTEGER PRIMARY KEY,
    drive_file_id INTEGER NOT NULL UNIQUE,
    content_text TEXT NOT NULL,
    page_count INTEGER DEFAULT 0,
    ocr_completed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (drive_file_id) REFERENCES drive_file(id)
);

-- FTS5 Virtual Table
CREATE VIRTUAL TABLE drive_file_content_fts USING fts5(
    content_text,
    content='drive_file_content',
    content_rowid='id'
);
```

## 🔐 Sicherheitskonzept

### Verschlüsselung
- **Algorithmus**: AES-256-GCM (Authenticated Encryption)
- **Key Management**: Master Key in `.env`, pro Datei unique Nonce
- **AAD**: Metadaten (file_id, file_hash) als Additional Authenticated Data
- **Storage**: Verschlüsselte Dateien in `instance/encrypted_files/`

### Privacy-Level
- **Private**: Nur der Besitzer kann die Dateien sehen und durchsuchen
- **Public**: Alle Klassenmitglieder können die Dateien durchsuchen

### Zugriffskontrolle
- **Read-only**: Service Account hat nur Lesezugriff auf Google Drive
- **User-based**: Jeder Ordner gehört einem User
- **Class-based**: Öffentliche Ordner sind nur für Klassenmitglieder sichtbar

## 🎨 Frontend-Komponenten (TODO)

### Drive-Seite (`/drive`)
```html
<!-- Ordner-Liste -->
<div class="drive-folders">
    <div class="folder-card">
        <h3>GoodNotes Backup</h3>
        <div class="privacy-toggle">
            <label>
                <input type="checkbox" checked>
                Öffentlich für Klasse
            </label>
        </div>
        <div class="sync-status">
            <span class="badge success">Synchronisiert</span>
            <small>Vor 5 Minuten</small>
        </div>
        <div class="stats">
            <span>📄 42 Dateien</span>
            <span>📊 15 Fächer</span>
        </div>
    </div>
</div>

<!-- Suchleiste -->
<div class="drive-search">
    <input type="text" placeholder="Durchsuche alle Notizen...">
    <div class="filters">
        <button class="filter-chip">Mathematik</button>
        <button class="filter-chip">Von: Lena</button>
    </div>
</div>

<!-- Suchergebnisse -->
<div class="search-results">
    <div class="result-card">
        <h4>Analysis_Notizen.pdf</h4>
        <p class="snippet">...die <mark>Ableitung</mark> einer Funktion...</p>
        <div class="meta">
            <span>Von: <strong>Lena</strong></span>
            <span>Fach: Mathematik</span>
            <span>12 Seiten</span>
        </div>
        <button class="download-btn">Download</button>
    </div>
</div>
```

## 📈 Performance

### Optimierungen
- **FTS5**: Millisekunden-Suche auch bei tausenden Dateien
- **Lazy Loading**: Dateien werden nur bei Bedarf entschlüsselt
- **Chunked Processing**: Große PDFs werden in Chunks verarbeitet
- **Hash-basierte Change Detection**: Nur geänderte Dateien werden neu verarbeitet

### Limits
- **Max File Size**: 100 MB pro PDF (konfigurierbar)
- **Sync Interval**: 15 Minuten (konfigurierbar)
- **Search Results**: 50 pro Seite (konfigurierbar)

## 🐛 Troubleshooting

### "Service account file not found"
→ Prüfe `GOOGLE_SERVICE_ACCOUNT_FILE` in `.env`

### "Cannot access folder"
→ Stelle sicher, dass der Ordner mit dem Service Account geteilt wurde

### "OCR failed"
→ Prüfe ob `pdfplumber` und `PyPDF2` installiert sind

### "FTS5 not available"
→ SQLite muss mit FTS5-Support kompiliert sein (Standard ab SQLite 3.9.0)

## 📝 Lizenz

Proprietär - Teil von L8teStudy

---

**L8teStudy Drive Integration** - Automatische Notizen-Synchronisation für die Klasse 🎓
