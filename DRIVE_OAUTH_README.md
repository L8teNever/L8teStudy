# Google Drive OAuth Integration - README

## Übersicht

Die L8teStudy App nutzt **Google Drive OAuth 2.0** für direkten Zugriff auf Google Drive. Nach der OAuth-Anmeldung werden **automatisch ALLE Dateien** vom verbundenen Google Account angezeigt.

## ✨ Hauptmerkmale

- ✅ **Automatische Anzeige aller Drive-Dateien** - Keine manuelle Ordnerauswahl nötig
- ✅ **Live-Zugriff** über Google Drive API
- ✅ **Erweiterte Suche** - Suche nach Dateinamen UND Inhalten
- ✅ **Pagination** - Effiziente Anzeige auch bei vielen Dateien
- ✅ **Direkter Zugriff** - Dateien öffnen sich direkt in Google Drive

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

Die `docker-compose.yml` ist bereits konfiguriert:

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

### Als Super Admin - Einmalige Einrichtung

1. Gehe zu **Einstellungen** → **Drive Integration**
2. Klicke auf **"Mit Google Drive verbinden"**
3. Ein Popup öffnet sich für die Google OAuth-Anmeldung
4. Melde dich mit dem Google-Account an, dessen Drive-Dateien angezeigt werden sollen
5. Erlaube die benötigten Berechtigungen (Read-only Zugriff)
6. Das Popup schließt sich automatisch nach erfolgreicher Authentifizierung
7. **Fertig!** Alle Dateien vom verbundenen Google Account sind jetzt verfügbar

### Als Schüler/Nutzer

1. Gehe zur **Drive-Ansicht** im Hauptmenü
2. **Alle Dateien** vom verbundenen Google Account werden angezeigt
3. **Suche**: Nutze die Suchfunktion, um nach Dateinamen oder Inhalten zu suchen
4. **Öffnen**: Klicke auf eine Datei, um sie in Google Drive zu öffnen
5. **Mehr laden**: Scrolle nach unten, um weitere Dateien zu laden (Pagination)

## API Endpoints

### Authentication

- `GET /api/drive/auth/status` - Prüfe Auth-Status
- `GET /api/drive/auth/start` - Starte OAuth-Flow
- `GET /api/drive/auth/callback` - OAuth Callback
- `POST /api/drive/auth/revoke` - Trenne Verbindung

### File Access

- `GET /api/drive/files?pageToken=<token>` - Liste alle Dateien (mit Pagination)
- `GET /api/drive/search?q=<query>` - Suche Dateien (Name + Inhalt)
- `GET /api/drive/file/<file_id>` - Hole Datei-Metadaten

### Folder Management (Optional, für zukünftige Erweiterungen)

- `GET /api/drive/browse?parent_id=<id>` - Browse Drive-Ordner
- `GET /api/drive/folders` - Liste ausgewählte Ordner
- `POST /api/drive/folders` - Füge Ordner hinzu
- `PUT /api/drive/folders/<id>` - Aktualisiere Ordner
- `DELETE /api/drive/folders/<id>` - Entferne Ordner

## Sicherheit

### OAuth Token Verschlüsselung

Alle OAuth-Tokens (Access Token, Refresh Token) werden verschlüsselt in der Datenbank gespeichert. Die Verschlüsselung nutzt den `DRIVE_ENCRYPTION_KEY`.

### Berechtigungen

- **Super Admin**: Kann OAuth verbinden/trennen
- **Alle Nutzer**: Können Dateien ansehen, suchen und öffnen

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

### Zu viele Dateien / Langsames Laden

Die App nutzt Pagination (100 Dateien pro Seite). Bei sehr vielen Dateien:
- Nutze die Suchfunktion, um spezifische Dateien zu finden
- Die neuesten Dateien werden zuerst angezeigt

## Datenschutz

- Die App speichert **keine Dateiinhalte** lokal
- Alle Zugriffe erfolgen live über die Google Drive API
- OAuth-Tokens werden verschlüsselt gespeichert
- Nur Metadaten werden temporär im Browser gecacht

## Welcher Google Account?

Die App zeigt die Dateien des Google Accounts an, mit dem der OAuth-Flow durchgeführt wurde. Dies ist typischerweise:
- Ein Lehrer-Account mit Zugriff auf Unterrichtsmaterialien
- Ein Schul-Account mit geteilten Ressourcen
- Ein dedizierter Account nur für L8teStudy

**Tipp**: Erstelle einen separaten Google Account speziell für L8teStudy und teile die relevanten Ordner mit diesem Account.

## FAQ

### Können Schüler eigene Dateien hochladen?

Nein, die App hat nur Lesezugriff. Schüler können Dateien ansehen und öffnen, aber nicht hochladen oder ändern.

### Werden gelöschte Dateien angezeigt?

Nein, Dateien im Papierkorb werden automatisch ausgeblendet.

### Werden Google Docs/Sheets/Slides unterstützt?

Ja! Alle Google Workspace Dateitypen werden angezeigt und können direkt in Google Drive geöffnet werden.

### Kann ich mehrere Google Accounts verbinden?

Aktuell wird nur ein Google Account gleichzeitig unterstützt. Um den Account zu wechseln:
1. Trenne die aktuelle Verbindung
2. Verbinde mit einem anderen Account

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
- ✅ **Automatische Anzeige aller Drive-Dateien**
- ✅ Live Drive API Integration
- ✅ Google Drive Search (Name + Inhalt)
- ✅ Pagination Support
