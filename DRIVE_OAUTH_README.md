# Google Drive OAuth Integration - README

## Übersicht

Die L8teStudy App nutzt jetzt **Google Drive OAuth 2.0** für die Integration mit Google Drive. Admins können Ordner auswählen, die allen Nutzern angezeigt werden, und die App nutzt die Google Drive API für Live-Zugriff und Suche.

## Änderungen gegenüber der vorherigen Version

### Entfernt
- ❌ Paperless-NGX Integration komplett entfernt
- ❌ Service Account basierte Drive-Integration entfernt
- ❌ Lokale Datei-Verschlüsselung und Caching entfernt

### Neu hinzugefügt
- ✅ Google Drive OAuth 2.0 Authentication
- ✅ Admin-Interface zur Ordnerauswahl
- ✅ Live-Zugriff auf Drive-Dateien über API
- ✅ Google Drive Search API Integration (Name + Inhalt)
- ✅ Subject-Mapping für Drive-Ordner

## Setup-Anleitung

### 1. Google Cloud Console Setup

1. Gehe zu [Google Cloud Console](https://console.cloud.google.com/)
2. Erstelle ein neues Projekt oder wähle ein bestehendes
3. Aktiviere die **Google Drive API**:
   - APIs & Services → Library → "Google Drive API" suchen → Aktivieren

4. Erstelle OAuth 2.0 Credentials:
   - APIs & Services → Credentials → "+ CREATE CREDENTIALS" → "OAuth client ID"
   - Application type: **Web application**
   - Name: `L8teStudy Drive Integration`
   - Authorized redirect URIs:
     ```
     http://localhost:5000/api/drive/auth/callback
     https://your-domain.com/api/drive/auth/callback
     ```
   - Klicke "CREATE"
   - **Wichtig**: Notiere dir die **Client ID** und **Client Secret**

### 2. Umgebungsvariablen konfigurieren

Erstelle/bearbeite die `.env` Datei:

```bash
# Google Drive OAuth Integration
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
DRIVE_ENCRYPTION_KEY=qv6aHbyp1j1xHpLVE87DIax+x/4YvD54rlh3SbZGTjg=

# Andere Konfigurationen...
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///instance/l8testudy.db
```

**Hinweis**: Der `DRIVE_ENCRYPTION_KEY` wird für die Verschlüsselung der OAuth-Tokens in der Datenbank verwendet.

### 3. Docker Compose Setup

Die `docker-compose.yml` ist bereits aktualisiert. Stelle sicher, dass deine `.env` Datei die richtigen Werte enthält:

```yaml
environment:
  GOOGLE_CLIENT_ID: ${GOOGLE_CLIENT_ID}
  GOOGLE_CLIENT_SECRET: ${GOOGLE_CLIENT_SECRET}
  DRIVE_ENCRYPTION_KEY: ${DRIVE_ENCRYPTION_KEY}
```

### 4. Installation

```bash
# Dependencies installieren
pip install -r requirements.txt

# Oder mit Docker
docker-compose up -d --build
```

### 5. Datenbank Migration

```bash
# Lokale Entwicklung
flask db upgrade

# Docker
docker exec l8testudy flask db upgrade
```

## Verwendung

### Als Super Admin

#### 1. Google Drive verbinden

1. Gehe zu **Einstellungen** → **Drive Integration**
2. Klicke auf **"Mit Google Drive verbinden"**
3. Ein Popup öffnet sich für die Google OAuth-Anmeldung
4. Melde dich mit dem Google-Account an, der Zugriff auf die Drive-Dateien hat
5. Erlaube die benötigten Berechtigungen (Read-only Zugriff)
6. Das Popup schließt sich automatisch nach erfolgreicher Authentifizierung

#### 2. Ordner auswählen

1. Nach erfolgreicher Verbindung kannst du Ordner auswählen
2. Klicke auf **"Ordner hinzufügen"**
3. Navigiere durch deine Drive-Struktur
4. Wähle einen Ordner aus
5. Optional: Weise dem Ordner ein Fach (Subject) zu
6. Optional: Aktiviere "Unterordner einbeziehen"
7. Klicke auf **"Hinzufügen"**

#### 3. Ordner verwalten

- **Bearbeiten**: Ändere Subject-Zuordnung oder Unterordner-Einstellung
- **Deaktivieren**: Blende einen Ordner temporär aus
- **Löschen**: Entferne einen Ordner komplett aus der Anzeige

### Als Schüler/Nutzer

1. Gehe zur **Drive-Ansicht** im Hauptmenü
2. Alle von Admins freigegebenen Dateien werden angezeigt
3. **Suche**: Nutze die Suchfunktion, um nach Dateinamen oder Inhalten zu suchen
4. **Filter**: Filtere nach Fach (Subject)
5. **Öffnen**: Klicke auf eine Datei, um sie in Google Drive zu öffnen

## API Endpoints

### Authentication

- `GET /api/drive/auth/status` - Prüfe Auth-Status
- `GET /api/drive/auth/start` - Starte OAuth-Flow
- `GET /api/drive/auth/callback` - OAuth Callback
- `POST /api/drive/auth/revoke` - Trenne Verbindung

### Folder Management (Admin only)

- `GET /api/drive/browse?parent_id=<id>` - Browse Drive-Ordner
- `GET /api/drive/folders` - Liste ausgewählte Ordner
- `POST /api/drive/folders` - Füge Ordner hinzu
- `PUT /api/drive/folders/<id>` - Aktualisiere Ordner
- `DELETE /api/drive/folders/<id>` - Entferne Ordner

### File Access

- `GET /api/drive/files` - Liste alle Dateien aus ausgewählten Ordnern
- `GET /api/drive/search?q=<query>` - Suche Dateien (Name + Inhalt)
- `GET /api/drive/file/<file_id>` - Hole Datei-Metadaten

## Sicherheit

### OAuth Token Verschlüsselung

Alle OAuth-Tokens (Access Token, Refresh Token) werden verschlüsselt in der Datenbank gespeichert. Die Verschlüsselung nutzt den `DRIVE_ENCRYPTION_KEY`.

### Berechtigungen

- **Super Admin**: Kann OAuth verbinden/trennen und Ordner verwalten
- **Admin**: Kann Ordner verwalten (aber nicht OAuth verbinden/trennen)
- **Schüler**: Können nur Dateien ansehen und suchen

### Google Drive Berechtigungen

Die App benötigt folgende OAuth Scopes:
- `https://www.googleapis.com/auth/drive.readonly` - Dateien lesen
- `https://www.googleapis.com/auth/drive.metadata.readonly` - Metadaten lesen

**Wichtig**: Die App hat **nur Lesezugriff** auf Drive. Sie kann keine Dateien ändern oder löschen.

## Troubleshooting

### "Not authenticated" Fehler

**Lösung**: 
1. Gehe zu Einstellungen → Drive Integration
2. Klicke auf "Mit Google Drive verbinden"
3. Führe den OAuth-Flow erneut durch

### OAuth Popup wird blockiert

**Lösung**: 
1. Erlaube Popups für deine L8teStudy Domain
2. Versuche es erneut

### "Invalid redirect URI" Fehler

**Lösung**: 
1. Gehe zur Google Cloud Console
2. Überprüfe die Redirect URIs in den OAuth Credentials
3. Stelle sicher, dass die URI exakt mit deiner Domain übereinstimmt

### Token abgelaufen

Die App erneuert Access Tokens automatisch mit dem Refresh Token. Falls dies fehlschlägt:
1. Trenne die Verbindung (Revoke)
2. Verbinde erneut

## Datenschutz

- Die App speichert **keine Dateiinhalte** lokal
- Alle Zugriffe erfolgen live über die Google Drive API
- OAuth-Tokens werden verschlüsselt gespeichert
- Nur Metadaten (Ordner-IDs, Namen) werden in der Datenbank gespeichert

## Migration von alter Drive-Integration

Falls du die alte Service Account basierte Integration genutzt hast:

1. **Backup**: Erstelle ein Backup deiner Datenbank
2. **Migration**: Die Migration entfernt automatisch alte Drive-Tabellen
3. **Neu einrichten**: Folge der Setup-Anleitung oben
4. **Ordner neu auswählen**: Wähle die gewünschten Ordner erneut aus

## Support

Bei Problemen:
1. Prüfe die Logs: `docker logs l8testudy`
2. Überprüfe die Umgebungsvariablen
3. Stelle sicher, dass die Google Drive API aktiviert ist
4. Prüfe die OAuth Redirect URIs

## Changelog

### Version 2.1.0 (2026-01-23)

- ✅ Paperless-NGX Integration entfernt
- ✅ Google Drive OAuth 2.0 Integration hinzugefügt
- ✅ Admin Ordnerauswahl implementiert
- ✅ Live Drive API Integration
- ✅ Google Drive Search (Name + Inhalt)
- ✅ Subject-Mapping für Drive-Ordner
