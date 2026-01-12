# Konfiguration

Diese Seite beschreibt alle Konfigurationsoptionen für L8teStudy.

---

## 🔧 Umgebungsvariablen

L8teStudy verwendet Umgebungsvariablen für die Konfiguration. Diese können in einer `.env` Datei im Projektverzeichnis gesetzt werden.

### Erstellen der .env Datei

Erstelle eine Datei namens `.env` im Hauptverzeichnis:

```env
SECRET_KEY=dein-sehr-geheimer-schluessel
DATABASE_URL=sqlite:///instance/l8testudy.db
FLASK_ENV=production
UNTIS_FERNET_KEY=dein-32-byte-base64-key
UPLOAD_FOLDER=instance/uploads
```

---

## 📋 Verfügbare Variablen

### SECRET_KEY (Erforderlich)

**Beschreibung**: Geheimer Schlüssel für Session-Verschlüsselung und CSRF-Schutz.

**Standard**: `dev-secret-key-change-in-prod` (NICHT in Produktion verwenden!)

**Generieren**:
```python
import secrets
print(secrets.token_hex(32))
```

**Beispiel**:
```env
SECRET_KEY=a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6
```

**Wichtig**: 
- Mindestens 32 Zeichen
- Zufällig generiert
- Niemals im Code oder Repository speichern
- In Produktion IMMER ändern!

---

### DATABASE_URL

**Beschreibung**: Datenbank-Verbindungsstring.

**Standard**: `sqlite:///l8testudy.db`

**Beispiele**:

**SQLite** (Standard):
```env
DATABASE_URL=sqlite:///instance/l8testudy.db
```

**PostgreSQL**:
```env
DATABASE_URL=postgresql://user:password@localhost/l8testudy
```

**MySQL**:
```env
DATABASE_URL=mysql://user:password@localhost/l8testudy
```

**Hinweis**: SQLite ist für kleine bis mittlere Installationen ausreichend. Für größere Deployments empfehlen wir PostgreSQL.

---

### FLASK_ENV

**Beschreibung**: Umgebungsmodus (development/production).

**Standard**: `development`

**Werte**:
- `development`: Debug-Modus, Auto-Reload, detaillierte Fehler
- `production`: Optimiert, HTTPS-Erzwingung, sichere Cookies

**Beispiel**:
```env
FLASK_ENV=production
```

**Wichtig**: In Produktion IMMER `production` verwenden!

---

### UNTIS_FERNET_KEY

**Beschreibung**: Verschlüsselungsschlüssel für WebUntis-Passwörter.

**Standard**: Automatisch aus SECRET_KEY abgeleitet

**Generieren**:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

**Beispiel**:
```env
UNTIS_FERNET_KEY=abcdefghijklmnopqrstuvwxyz0123456789ABCD=
```

**Wichtig**: 
- Muss 32 Bytes sein (base64-kodiert)
- Einmal gesetzt, nicht mehr ändern (sonst können WebUntis-Passwörter nicht mehr entschlüsselt werden)

---

### UPLOAD_FOLDER

**Beschreibung**: Verzeichnis für hochgeladene Dateien (Bilder, etc.).

**Standard**: `instance/uploads`

**Beispiel**:
```env
UPLOAD_FOLDER=/var/www/l8testudy/uploads
```

**Hinweis**: 
- Verzeichnis muss existieren und schreibbar sein
- In Docker: Volume mounten für Persistenz

---

## 🐳 Docker-spezifische Konfiguration

### docker-compose.yml

```yaml
version: '3.8'

services:
  l8testudy:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - l8testudy-data:/app/instance
    environment:
      - SECRET_KEY=dein-geheimer-schluessel
      - FLASK_ENV=production
      - UNTIS_FERNET_KEY=dein-fernet-key
    restart: unless-stopped

volumes:
  l8testudy-data:
```

### Wichtige Docker-Einstellungen

**Volumes**: Persistente Daten
```yaml
volumes:
  - l8testudy-data:/app/instance  # Datenbank und Uploads
```

**Ports**: Zugriff von außen
```yaml
ports:
  - "5000:5000"  # Host:Container
```

**Restart-Policy**: Automatischer Neustart
```yaml
restart: unless-stopped
```

---

## 🔒 Sicherheitseinstellungen

### Produktions-Checkliste

- [ ] `FLASK_ENV=production` gesetzt
- [ ] Starker `SECRET_KEY` (mindestens 32 Zeichen)
- [ ] `UNTIS_FERNET_KEY` gesetzt
- [ ] HTTPS aktiviert (Reverse Proxy)
- [ ] Firewall konfiguriert
- [ ] Regelmäßige Backups eingerichtet

### Automatische Sicherheitsfeatures

In Produktion (`FLASK_ENV=production`) werden automatisch aktiviert:

- **HTTPS-Erzwingung**: Alle HTTP-Requests werden zu HTTPS umgeleitet
- **Secure Cookies**: Cookies nur über HTTPS
- **HSTS**: HTTP Strict Transport Security (1 Jahr)
- **Strikte CSP**: Content Security Policy
- **Session-Sicherheit**: HttpOnly, SameSite=Strict

---

## ⚙️ Erweiterte Einstellungen

### Gunicorn-Konfiguration

**Workers**: Anzahl paralleler Prozesse
```bash
gunicorn -w 4 run:app  # 4 Workers
```

**Empfehlung**: `(2 × CPU-Kerne) + 1`

**Bind-Adresse**: IP und Port
```bash
gunicorn -b 0.0.0.0:5000 run:app  # Alle Interfaces
gunicorn -b 127.0.0.1:5000 run:app  # Nur localhost
```

**Timeout**: Maximale Request-Dauer
```bash
gunicorn --timeout 120 run:app  # 120 Sekunden
```

### Datenbank-Optimierung

**SQLite**:
```python
# In app/__init__.py (bereits konfiguriert)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
```

**PostgreSQL** (für größere Installationen):
```env
DATABASE_URL=postgresql://user:password@localhost/l8testudy?pool_size=10&max_overflow=20
```

---

## 📊 Logging

### Log-Level setzen

**Entwicklung**:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

**Produktion**:
```python
import logging
logging.basicConfig(level=logging.WARNING)
```

### Logs in Datei schreiben

```python
import logging
logging.basicConfig(
    filename='l8testudy.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

---

## 🔄 Konfiguration ändern

### Laufende Anwendung

**Lokale Installation**:
1. `.env` Datei bearbeiten
2. Anwendung neu starten: `Ctrl+C` → `python run.py`

**Docker**:
1. `docker-compose.yml` oder `.env` bearbeiten
2. Container neu starten: `docker-compose restart`

### Ohne Neustart (nur bestimmte Einstellungen)

Einige Einstellungen können über die Admin-Oberfläche geändert werden:
- Klasseneinstellungen
- Benutzereinstellungen
- WebUntis-Zugangsdaten

---

## 🧪 Entwicklungs-Konfiguration

### Empfohlene .env für Entwicklung

```env
SECRET_KEY=dev-secret-key-only-for-testing
DATABASE_URL=sqlite:///instance/l8testudy_dev.db
FLASK_ENV=development
FLASK_DEBUG=1
```

### Debug-Modus aktivieren

```bash
export FLASK_DEBUG=1  # Linux/Mac
set FLASK_DEBUG=1     # Windows CMD
$env:FLASK_DEBUG=1    # Windows PowerShell

python run.py
```

**Features im Debug-Modus**:
- Auto-Reload bei Code-Änderungen
- Detaillierte Fehlerseiten
- Interaktiver Debugger
- Keine HTTPS-Erzwingung

**Warnung**: Debug-Modus NIEMALS in Produktion verwenden!

---

## 📚 Nächste Schritte

- **[Erste Schritte](Erste-Schritte)** - Tutorial für neue Benutzer
- **[Sicherheit](Sicherheit)** - Sicherheits-Best-Practices
- **[Deployment](Deployment)** - Produktions-Deployment
- **[Troubleshooting](Troubleshooting)** - Probleme lösen

---

**Konfiguration abgeschlossen!** 🎉
