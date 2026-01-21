---
description: L8teStudy Drive Integration - Implementation Plan
---

# L8teStudy Drive Integration - Implementierungsplan

## Übersicht
Integration eines Google Drive Sync-Systems für automatisches Sammeln und Durchsuchen von GoodNotes-Notizen.

## Phase 1: Datenbank-Erweiterung

### 1.1 Neue Modelle erstellen
- **DriveFolder**: Verknüpfte Google Drive Ordner
  - `id`, `user_id`, `folder_id`, `folder_name`, `privacy_level` (public/private)
  - `sync_enabled`, `last_sync_at`, `created_at`
  
- **DriveFile**: Gespeicherte Dateien
  - `id`, `drive_folder_id`, `file_id`, `filename`, `encrypted_path`
  - `file_hash`, `file_size`, `mime_type`, `created_at`, `updated_at`
  
- **DriveFileContent**: OCR-extrahierter Text (FTS5)
  - `id`, `drive_file_id`, `content_text`, `ocr_completed_at`
  
- **SubjectMapping**: Alias-System für Fächer
  - `id`, `user_input`, `official_subject_id`, `user_id`, `auto_mapped`

### 1.2 Migration erstellen
```bash
flask db migrate -m "Add Drive Integration models"
flask db upgrade
```

## Phase 2: Backend-Entwicklung

### 2.1 Google Drive API Integration
- Service Account Setup
- OAuth2-Authentifizierung
- Drive API Client (`app/drive_client.py`)
  - `list_files()` - Dateien auflisten
  - `download_file()` - Datei herunterladen
  - `get_file_metadata()` - Metadaten abrufen

### 2.2 Verschlüsselungs-Service
- Erweitere `app/encryption.py` (bereits vorhanden!)
- `DriveEncryptionManager` Klasse
  - `encrypt_and_store_file()` - Datei verschlüsseln und speichern
  - `decrypt_file_to_memory()` - Datei im RAM entschlüsseln
  - `get_encrypted_file_path()` - Pfad zur verschlüsselten Datei

### 2.3 OCR-Service
- PDF-Text-Extraktion (`app/ocr_service.py`)
  - Library: `pdfplumber` oder `PyPDF2`
  - Fallback: `pytesseract` für gescannte PDFs
  - `extract_text_from_pdf()` - Text extrahieren
  - `index_text_for_search()` - Text in FTS5 indexieren

### 2.4 Background Worker
- APScheduler Integration (bereits vorhanden!)
- `app/drive_sync.py`
  - `sync_all_folders()` - Alle Ordner synchronisieren
  - `sync_folder(folder_id)` - Einzelnen Ordner synchronisieren
  - `process_new_file(file)` - Neue Datei verarbeiten
  - Scheduler: Alle 15 Minuten

### 2.5 Smarte Fach-Zuordnung
- `app/subject_mapper.py`
  - `map_folder_to_subject()` - Ordner zu Fach zuordnen
  - `suggest_subject()` - KI-basierte Vorschläge (optional)
  - Fuzzy-Matching für ähnliche Namen

### 2.6 Such-Service
- `app/drive_search.py`
  - SQLite FTS5 für Volltextsuche
  - `search_files(query, filters)` - Dateien durchsuchen
  - Filter: Fach, Benutzer, Datum
  - Ranking nach Relevanz

## Phase 3: API-Endpunkte

### 3.1 Drive-Verwaltung (`/api/drive/...`)
- `POST /api/drive/folders` - Ordner hinzufügen
- `GET /api/drive/folders` - Ordner auflisten
- `PATCH /api/drive/folders/<id>` - Ordner aktualisieren (Privacy-Level)
- `DELETE /api/drive/folders/<id>` - Ordner entfernen
- `POST /api/drive/folders/<id>/sync` - Manuellen Sync starten

### 3.2 Datei-Zugriff
- `GET /api/drive/files` - Dateien auflisten
- `GET /api/drive/files/<id>/download` - Datei herunterladen (entschlüsselt)
- `GET /api/drive/files/<id>/preview` - PDF-Vorschau

### 3.3 Suche
- `GET /api/drive/search?q=<query>&subject=<id>&user=<id>` - Suche
- `GET /api/drive/search/suggestions?q=<query>` - Autocomplete

### 3.4 Fach-Zuordnung
- `GET /api/drive/subject-mappings` - Zuordnungen abrufen
- `POST /api/drive/subject-mappings` - Zuordnung erstellen
- `PATCH /api/drive/subject-mappings/<id>` - Zuordnung ändern

## Phase 4: Frontend - Drive-Seite

### 4.1 Neue Seite erstellen
- `templates/drive.html` (oder in `index.html` integrieren)
- Route: `/drive` oder `/<class>/drive`

### 4.2 UI-Komponenten
- **Ordner-Liste**
  - Verknüpfte Ordner anzeigen
  - Privacy-Toggle (Öffentlich/Privat)
  - Sync-Status (Letzter Sync, Anzahl Dateien)
  - "Ordner hinzufügen" Button

- **Ordner hinzufügen Dialog**
  - Google Drive Ordner-ID eingeben
  - Oder: OAuth-Flow für Ordner-Auswahl
  - Privacy-Level auswählen

- **Sync-Status Dashboard**
  - Gesamtanzahl Dateien
  - Letzter Sync-Zeitpunkt
  - Sync-Fortschritt (bei laufendem Sync)
  - Fehler-Log

- **Such-Interface**
  - Suchleiste mit Autocomplete
  - Filter-Chips (Fach, Benutzer)
  - Suchergebnisse mit Vorschau
  - "Von: [Username]" Anzeige

- **Fach-Zuordnungs-Manager**
  - Liste aller Zuordnungen
  - Bearbeiten/Löschen
  - Neue Zuordnung erstellen

### 4.3 JavaScript-Logik
- `static/js/drive.js`
  - Ordner-Verwaltung
  - Such-Funktionalität
  - Datei-Download
  - Real-time Sync-Updates (WebSocket optional)

## Phase 5: Sicherheit & Datenschutz

### 5.1 Verschlüsselung
- ✅ AES-256-GCM bereits implementiert
- Verschlüsselungsschlüssel in `.env`
- Dateien in `instance/encrypted_files/` speichern

### 5.2 Zugriffskontrolle
- Nur Besitzer sieht private Ordner
- Öffentliche Ordner: Nur für Klassenmitglieder
- Admin-Rechte: Alle Dateien sehen (Audit)

### 5.3 Rate Limiting
- Sync-Anfragen: Max 1/Minute pro User
- Such-Anfragen: Max 30/Minute
- Download: Max 100/Stunde

### 5.4 Datenschutz
- DSGVO-konform
- Nutzer kann jederzeit alle Daten löschen
- Transparenz: Wer sieht was?

## Phase 6: Testing & Deployment

### 6.1 Tests
- Unit-Tests für alle Services
- Integration-Tests für API
- E2E-Tests für Frontend
- Performance-Tests (große Dateien)

### 6.2 Dokumentation
- Wiki-Seite: "Drive Integration"
- API-Dokumentation aktualisieren
- User-Guide erstellen

### 6.3 Deployment
- Dependencies aktualisieren (`requirements.txt`)
- Migrations ausführen
- Service Account konfigurieren
- Monitoring einrichten

## Abhängigkeiten (requirements.txt)

```
google-api-python-client
google-auth-httplib2
google-auth-oauthlib
pdfplumber
PyPDF2
pytesseract  # Optional, für OCR
pillow  # Für Bildverarbeitung
```

## Konfiguration (.env)

```env
# Google Drive API
GOOGLE_SERVICE_ACCOUNT_FILE=path/to/service-account.json
GOOGLE_DRIVE_SCOPES=https://www.googleapis.com/auth/drive.readonly

# Encryption
DRIVE_ENCRYPTION_KEY=<base64-encoded-key>

# Storage
ENCRYPTED_FILES_PATH=instance/encrypted_files
```

## Zeitplan

- **Woche 1**: Phase 1-2 (Backend-Grundlagen)
- **Woche 2**: Phase 3 (API-Endpunkte)
- **Woche 3**: Phase 4 (Frontend)
- **Woche 4**: Phase 5-6 (Sicherheit, Testing, Deployment)

## Nächste Schritte

1. Dependencies installieren
2. Datenbank-Modelle erstellen
3. Google Drive API einrichten
4. Basis-Sync implementieren
5. Frontend-Seite erstellen
