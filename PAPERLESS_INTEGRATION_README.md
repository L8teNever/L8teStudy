# Paperless-NGX Integration für L8teStudy

## Überblick

L8teStudy ist jetzt vollständig mit **Paperless-NGX** integriert! Paperless-NGX ist ein selbst-gehostetes Dokumenten-Management-System mit OCR, automatischem Tagging und Volltextsuche.

### Vorteile gegenüber Google Drive

✅ **Selbst-gehostet** - Volle Kontrolle über deine Daten  
✅ **OCR eingebaut** - Automatische Texterkennung aus gescannten Dokumenten  
✅ **Volltextsuche** - Durchsuche den Inhalt aller Dokumente  
✅ **Automatisches Tagging** - Intelligente Organisation deiner Dateien  
✅ **DSGVO-konform** - Keine Daten verlassen dein Netzwerk  
✅ **Keine OAuth-Komplexität** - Einfache Token-basierte Authentifizierung  
✅ **Korrespondenten & Dokumenttypen** - Professionelle Dokumentenverwaltung  

## Features

### 📄 Dokumenten-Management
- **Upload**: Lade Dokumente direkt über L8teStudy zu Paperless hoch
- **Download**: Lade Original- oder OCR-verarbeitete Versionen herunter
- **Preview**: Zeige Thumbnails aller Dokumente an
- **Metadaten**: Bearbeite Titel, Tags, Korrespondenten und Dokumenttypen

### 🔍 Suche & Filter
- **Volltextsuche**: Durchsuche den OCR-erkannten Text in allen Dokumenten
- **Tag-Filter**: Filtere nach einem oder mehreren Tags
- **Korrespondenten-Filter**: Zeige nur Dokumente von bestimmten Absendern
- **Dokumenttyp-Filter**: Organisiere nach Dokumenttypen (Rechnung, Brief, etc.)

### 🏷️ Tags & Organisation
- **Tags erstellen**: Erstelle eigene Tags direkt aus L8teStudy
- **Farbcodierung**: Jeder Tag hat eine eigene Farbe
- **Automatisches Tagging**: Paperless kann Dokumente automatisch taggen

### 🔄 Synchronisation
- **Auto-Sync**: Automatische Synchronisation mit Paperless
- **Manueller Sync**: Sync-Button für sofortige Aktualisierung
- **Caching**: Lokales Caching für schnellere Ladezeiten

### 🎓 Schul-Integration
- **Fächer-Mapping**: Ordne Dokumente automatisch Schulfächern zu
- **Klassen-Konfiguration**: Verschiedene Paperless-Instanzen pro Klasse möglich
- **Berechtigungen**: Admins können globale Konfiguration verwalten

## Setup

### 1. Paperless-NGX installieren

#### Option A: Docker (empfohlen)

```bash
# Docker Compose für Paperless-NGX
version: "3.4"
services:
  paperless:
    image: ghcr.io/paperless-ngx/paperless-ngx:latest
    restart: unless-stopped
    ports:
      - "8000:8000"
    volumes:
      - paperless_data:/usr/src/paperless/data
      - paperless_media:/usr/src/paperless/media
      - ./consume:/usr/src/paperless/consume
      - ./export:/usr/src/paperless/export
    environment:
      PAPERLESS_REDIS: redis://redis:6379
      PAPERLESS_DBHOST: db
      PAPERLESS_DBNAME: paperless
      PAPERLESS_DBUSER: paperless
      PAPERLESS_DBPASS: paperless
      PAPERLESS_SECRET_KEY: change-me-to-something-secure
      PAPERLESS_URL: https://paperless.example.com
      PAPERLESS_OCR_LANGUAGE: deu+eng  # Deutsch + Englisch
      PAPERLESS_TIME_ZONE: Europe/Berlin
      
  redis:
    image: redis:7
    restart: unless-stopped
    
  db:
    image: postgres:15
    restart: unless-stopped
    environment:
      POSTGRES_DB: paperless
      POSTGRES_USER: paperless
      POSTGRES_PASSWORD: paperless
    volumes:
      - pgdata:/var/lib/postgresql/data

volumes:
  paperless_data:
  paperless_media:
  pgdata:
```

Starte Paperless:
```bash
docker-compose up -d
```

#### Option B: Native Installation

Siehe [Paperless-NGX Dokumentation](https://docs.paperless-ngx.com/setup/)

### 2. Paperless-NGX konfigurieren

1. Öffne Paperless in deinem Browser: `http://localhost:8000`
2. Erstelle einen Admin-Account
3. Gehe zu **Einstellungen** → **API Tokens**
4. Klicke auf **Token erstellen**
5. Kopiere den generierten Token (wird nur einmal angezeigt!)

### 3. L8teStudy mit Paperless verbinden

#### Als Super Admin (Global):

1. Öffne L8teStudy
2. Gehe zur **Dokumente**-Seite
3. Klicke auf **⚙️ Einstellungen**
4. Wähle **Global** als Scope (für alle Klassen)
5. Gib deine Paperless-URL ein (z.B. `http://localhost:8000`)
6. Füge den API-Token ein
7. Klicke auf **Verbindung testen**
8. Bei Erfolg: **Speichern**

#### Als Klassen-Admin (Pro Klasse):

1. Öffne L8teStudy
2. Gehe zur **Dokumente**-Seite
3. Klicke auf **⚙️ Einstellungen**
4. Wähle **Klasse** als Scope
5. Gib deine Paperless-URL ein
6. Füge den API-Token ein
7. **Speichern**

#### Als Benutzer (Persönlich):

1. Öffne L8teStudy
2. Gehe zur **Dokumente**-Seite
3. Klicke auf **⚙️ Einstellungen**
4. Wähle **Benutzer** als Scope
5. Gib deine persönliche Paperless-URL ein
6. Füge den API-Token ein
7. **Speichern**

## Verwendung

### Dokumente hochladen

1. Klicke auf **+ Hochladen**
2. Wähle eine oder mehrere Dateien aus
3. Optional: Gib einen Titel ein
4. Optional: Wähle Tags, Korrespondent und Dokumenttyp
5. Klicke auf **Hochladen**

Paperless wird automatisch:
- OCR durchführen (Text aus Bildern/PDFs extrahieren)
- Das Dokument indexieren für Volltextsuche
- Automatische Tags hinzufügen (falls konfiguriert)
- Metadaten extrahieren (Datum, etc.)

### Dokumente suchen

**Volltextsuche:**
```
Rechnung 2024
```

**Tag-Filter:**
- Wähle einen oder mehrere Tags aus dem Dropdown

**Erweiterte Suche in Paperless:**
- `tag:schule` - Alle Dokumente mit Tag "schule"
- `correspondent:lehrer` - Alle Dokumente von "lehrer"
- `created:[2024-01-01 to 2024-12-31]` - Zeitraum
- `title:mathe` - Im Titel

### Dokumente organisieren

**Tags hinzufügen:**
1. Klicke auf ein Dokument
2. Klicke auf **Bearbeiten**
3. Wähle Tags aus oder erstelle neue
4. **Speichern**

**Korrespondent zuweisen:**
1. Dokument öffnen
2. **Bearbeiten**
3. Korrespondent auswählen (z.B. "Schule", "Lehrer", etc.)
4. **Speichern**

## API Endpoints

L8teStudy stellt folgende Paperless-Endpoints bereit:

### Konfiguration
- `GET /api/paperless/config` - Aktuelle Konfiguration abrufen
- `POST /api/paperless/config` - Konfiguration speichern
- `POST /api/paperless/config/test` - Verbindung testen

### Dokumente
- `GET /api/paperless/documents` - Liste aller Dokumente
- `GET /api/paperless/documents/<id>` - Einzelnes Dokument
- `GET /api/paperless/documents/<id>/download` - Dokument herunterladen
- `GET /api/paperless/documents/<id>/preview` - Thumbnail
- `POST /api/paperless/documents/upload` - Dokument hochladen
- `PATCH /api/paperless/documents/<id>` - Metadaten aktualisieren
- `DELETE /api/paperless/documents/<id>` - Dokument löschen

### Tags
- `GET /api/paperless/tags` - Alle Tags
- `POST /api/paperless/tags` - Tag erstellen

### Korrespondenten
- `GET /api/paperless/correspondents` - Alle Korrespondenten
- `POST /api/paperless/correspondents` - Korrespondent erstellen

### Dokumenttypen
- `GET /api/paperless/document-types` - Alle Dokumenttypen

### Suche
- `GET /api/paperless/search?q=<query>` - Volltextsuche

### Sync
- `POST /api/paperless/sync` - Manueller Sync

## Sicherheit

### API Token Verschlüsselung
- Alle API Tokens werden verschlüsselt in der Datenbank gespeichert
- Verwendet Fernet-Verschlüsselung (AES)
- Gleiches Verschlüsselungssystem wie für WebUntis-Passwörter

### HTTPS
- Paperless sollte immer über HTTPS erreichbar sein
- L8teStudy prüft SSL-Zertifikate

### Berechtigungen
- **Super Admin**: Kann globale Konfiguration verwalten
- **Klassen-Admin**: Kann Klassen-Konfiguration verwalten
- **Benutzer**: Kann eigene Konfiguration verwalten

## Troubleshooting

### "Connection failed" Fehler

**Problem:** Verbindung zu Paperless schlägt fehl

**Lösung:**
1. Prüfe, ob Paperless läuft: `docker ps` oder öffne die URL im Browser
2. Prüfe die URL (mit oder ohne trailing slash)
3. Prüfe den API Token (neu generieren falls nötig)
4. Prüfe Firewall-Regeln
5. Bei Docker: Prüfe Netzwerk-Konfiguration

### "Invalid token" Fehler

**Problem:** API Token wird nicht akzeptiert

**Lösung:**
1. Generiere einen neuen Token in Paperless
2. Kopiere den Token komplett (keine Leerzeichen)
3. Speichere in L8teStudy

### Dokumente werden nicht angezeigt

**Problem:** Hochgeladene Dokumente erscheinen nicht

**Lösung:**
1. Klicke auf **Sync** Button
2. Warte 30 Sekunden (OCR braucht Zeit)
3. Aktualisiere die Seite
4. Prüfe in Paperless, ob das Dokument dort ist

### OCR funktioniert nicht

**Problem:** Text wird nicht erkannt

**Lösung:**
1. Prüfe Paperless-Logs: `docker logs paperless`
2. Prüfe OCR-Sprache in Paperless-Config: `PAPERLESS_OCR_LANGUAGE`
3. Für deutsche Dokumente: `deu` oder `deu+eng`
4. Installiere Tesseract-Sprachpakete falls nötig

## Migration von Google Drive

### Automatische Migration

Die alte Google Drive Integration wurde komplett entfernt. Wenn du vorher Drive genutzt hast:

1. **Daten sichern**: Exportiere wichtige Dateien aus Google Drive
2. **Zu Paperless hochladen**: 
   - Manuell über L8teStudy Upload
   - Oder: Bulk-Upload über Paperless Consume-Ordner
3. **Tags zuweisen**: Organisiere die Dokumente mit Tags

### Bulk-Upload über Paperless

Für viele Dateien auf einmal:

```bash
# Kopiere Dateien in den Consume-Ordner
cp /pfad/zu/dateien/* /pfad/zu/paperless/consume/

# Paperless verarbeitet sie automatisch
# Fortschritt in Paperless UI unter "Tasks" sichtbar
```

## Best Practices

### 📋 Naming Convention
- Verwende aussagekräftige Titel
- Format: `[Fach] Thema - Datum`
- Beispiel: `[Mathe] Arbeitsblatt Integrale - 2024-01-15`

### 🏷️ Tagging-System
- **Fächer**: `mathe`, `deutsch`, `englisch`, etc.
- **Typ**: `arbeitsblatt`, `klausur`, `mitschrift`, `hausaufgabe`
- **Status**: `todo`, `erledigt`, `wichtig`
- **Semester**: `ws2024`, `ss2025`

### 📁 Korrespondenten
- Lehrer-Namen
- Schulname
- Externe Institutionen

### 📝 Dokumenttypen
- Arbeitsblatt
- Klausur
- Mitschrift
- Hausaufgabe
- Zeugnis
- Bescheinigung

## Erweiterte Features

### Automatisches Tagging in Paperless

Konfiguriere Regeln in Paperless:

1. Gehe zu **Einstellungen** → **Workflows** → **Matching**
2. Erstelle Regel, z.B.:
   - **Wenn Titel enthält** "Mathe" → **Tag hinzufügen** "mathe"
   - **Wenn Korrespondent ist** "Schule" → **Dokumenttyp** "Schulunterlagen"

### OCR-Optimierung

Für beste OCR-Ergebnisse:

```yaml
# In docker-compose.yml
environment:
  PAPERLESS_OCR_LANGUAGE: deu+eng
  PAPERLESS_OCR_MODE: skip_noarchive  # Nur wenn nötig
  PAPERLESS_OCR_CLEAN: clean  # Bessere Texterkennung
  PAPERLESS_OCR_DESKEW: true  # Schräge Scans korrigieren
```

### Backup

Sichere deine Paperless-Daten regelmäßig:

```bash
# Backup erstellen
docker exec paperless document_exporter /export

# Oder mit docker-compose
docker-compose exec paperless document_exporter /export
```

## Support

Bei Problemen:

1. **L8teStudy Issues**: [GitHub Issues](https://github.com/yourusername/L8teStudy/issues)
2. **Paperless-NGX Docs**: [docs.paperless-ngx.com](https://docs.paperless-ngx.com)
3. **Paperless-NGX Community**: [r/paperless](https://reddit.com/r/paperless)

## Changelog

### Version 2.0.0 - Paperless Integration

- ✅ Google Drive Integration entfernt
- ✅ Paperless-NGX Integration hinzugefügt
- ✅ OCR-Volltextsuche
- ✅ Tag-System
- ✅ Korrespondenten-Verwaltung
- ✅ Dokumenttypen
- ✅ Auto-Sync
- ✅ Upload/Download über L8teStudy
- ✅ Preview-Thumbnails

## Lizenz

L8teStudy ist Open Source Software. Paperless-NGX ist ebenfalls Open Source (GPL-3.0).
