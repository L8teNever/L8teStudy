# Changelog - Google Drive OAuth Integration

## Version 2.1.0 (2026-01-23)

### 🔄 Große Änderungen

#### Paperless-NGX Integration entfernt
- Alle Paperless-NGX Modelle, Routes und Frontend-Code entfernt
- Datenbank-Migration erstellt zum Entfernen der Paperless-Tabellen
- `paperless_client.py`, `paperless_routes.py`, `paperless_delete_route.py` gelöscht
- `static/paperless.js` und `static/paperless_settings_extended.js` gelöscht

#### Google Drive OAuth 2.0 Integration hinzugefügt

**Backend:**
- ✅ Neue Modelle:
  - `DriveOAuthToken`: Speichert verschlüsselte OAuth-Tokens
  - `DriveFolder`: Admin-ausgewählte Ordner mit Subject-Mapping
  
- ✅ Neuer Client (`app/drive_oauth_client.py`):
  - OAuth 2.0 Flow Implementation
  - Automatische Token-Erneuerung
  - Google Drive API Integration
  - Ordner-Navigation
  - Datei-Suche (Name + Inhalt)
  - Metadaten-Abruf

- ✅ Neue Routes (`app/drive_routes.py`):
  - `/api/drive/auth/*` - OAuth Authentication
  - `/api/drive/browse` - Drive-Ordner durchsuchen
  - `/api/drive/folders` - Ordnerverwaltung (CRUD)
  - `/api/drive/files` - Dateien aus ausgewählten Ordnern
  - `/api/drive/search` - Dateisuche mit Google Drive API

**Frontend:**
- ✅ Neues JavaScript (`static/drive.js`):
  - `DriveManager` Klasse für Drive-Verwaltung
  - OAuth Popup-Flow
  - Ordner-Browser für Admins
  - Datei-Anzeige und Suche
  - Datei-Icons und Formatierung

**Konfiguration:**
- ✅ `docker-compose.yml` aktualisiert:
  - `GOOGLE_CLIENT_ID` statt `GOOGLE_SERVICE_ACCOUNT_INFO`
  - `GOOGLE_CLIENT_SECRET` hinzugefügt
  - `ENCRYPTED_FILES_PATH` entfernt (nicht mehr benötigt)

- ✅ `.env.example` aktualisiert mit OAuth-Variablen

- ✅ `requirements.txt` aktualisiert:
  - `google-auth-oauthlib` hinzugefügt
  - `google-auth-httplib2` hinzugefügt
  - `google-api-python-client` hinzugefügt

**Datenbank:**
- ✅ Migration erstellt: `remove_paperless_add_drive_oauth.py`
  - Entfernt alle Paperless-Tabellen
  - Erstellt `drive_oauth_token` Tabelle
  - Aktualisiert `drive_folder` Tabelle

### 🎯 Neue Features

1. **OAuth 2.0 Authentication**
   - Sichere OAuth-Anmeldung mit Google
   - Automatische Token-Erneuerung
   - Verschlüsselte Token-Speicherung

2. **Admin Ordnerauswahl**
   - Admins können spezifische Drive-Ordner auswählen
   - Subject-Zuordnung für Ordner
   - Option für Unterordner-Einbeziehung
   - Ordner aktivieren/deaktivieren

3. **Live Drive API Integration**
   - Keine lokale Datei-Speicherung
   - Echtzeit-Zugriff auf Drive-Dateien
   - Automatische Metadaten-Aktualisierung

4. **Erweiterte Suche**
   - Suche nach Dateinamen
   - Volltextsuche in Dateiinhalten (Google Drive API)
   - Filterung nach Ordnern/Subjects

### 🔒 Sicherheit

- OAuth-Tokens werden mit Fernet verschlüsselt
- Nur Read-Only Zugriff auf Drive
- Berechtigungsprüfung auf allen Endpoints
- CSRF-Protection auf Drive-Routes

### 📝 Berechtigungen

- **Super Admin**: OAuth verbinden/trennen, Ordner verwalten
- **Admin**: Ordner verwalten
- **Schüler**: Dateien ansehen und suchen

### 🗑️ Entfernte Dateien

```
app/paperless_client.py
app/paperless_routes.py
app/paperless_delete_route.py
static/paperless.js
static/paperless_settings_extended.js
PAPERLESS_INTEGRATION_README.md
CHANGELOG_PAPERLESS.md
```

### ➕ Neue Dateien

```
app/drive_oauth_client.py
app/drive_routes.py
static/drive.js
migrations/versions/remove_paperless_add_drive_oauth.py
DRIVE_OAUTH_README.md
CHANGELOG_DRIVE_OAUTH.md (diese Datei)
```

### 🔧 Geänderte Dateien

```
app/__init__.py - OAuth Config, Drive Blueprint Registration
app/models.py - Paperless-Modelle entfernt, Drive OAuth Modelle hinzugefügt
app/routes.py - Paperless-Imports entfernt, Drive-Imports hinzugefügt
docker-compose.yml - OAuth Credentials statt Service Account
.env.example - OAuth Variablen
requirements.txt - Google OAuth Libraries
```

### ⚠️ Breaking Changes

1. **Paperless-NGX Integration komplett entfernt**
   - Alle Paperless-Daten werden bei der Migration gelöscht
   - Paperless-Konfigurationen müssen entfernt werden

2. **Service Account Drive-Integration entfernt**
   - Alte `GOOGLE_SERVICE_ACCOUNT_INFO` wird nicht mehr verwendet
   - Neue OAuth-Credentials erforderlich

3. **Lokales Datei-Caching entfernt**
   - `ENCRYPTED_FILES_PATH` wird nicht mehr benötigt
   - Keine lokalen verschlüsselten Dateien mehr

### 📋 Migration Checklist

Wenn du von einer älteren Version migrierst:

- [ ] Backup der Datenbank erstellen
- [ ] Google Cloud Console: OAuth Credentials erstellen
- [ ] `.env` Datei mit `GOOGLE_CLIENT_ID` und `GOOGLE_CLIENT_SECRET` aktualisieren
- [ ] `docker-compose.yml` aktualisieren (falls custom)
- [ ] Dependencies neu installieren: `pip install -r requirements.txt`
- [ ] Datenbank-Migration ausführen: `flask db upgrade`
- [ ] Als Super Admin: OAuth-Verbindung herstellen
- [ ] Gewünschte Drive-Ordner auswählen

### 🐛 Bekannte Probleme

Keine bekannten Probleme zum Release-Zeitpunkt.

### 📚 Dokumentation

Siehe `DRIVE_OAUTH_README.md` für:
- Detaillierte Setup-Anleitung
- API-Dokumentation
- Troubleshooting
- Sicherheitshinweise

### 🙏 Danke

Diese Integration wurde entwickelt, um eine einfachere und sicherere Drive-Integration mit OAuth 2.0 zu ermöglichen.

---

**Hinweis**: Diese Version ist nicht rückwärtskompatibel mit Paperless-NGX oder der alten Service Account basierten Drive-Integration.
