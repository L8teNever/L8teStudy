# Installation

Diese Anleitung zeigt dir, wie du L8teStudy installierst.

---

## 📋 Voraussetzungen

### Systemanforderungen
- **Python**: Version 3.8 oder höher
- **Speicherplatz**: Mindestens 500 MB frei
- **RAM**: Mindestens 512 MB
- **Browser**: Chrome, Firefox, Safari oder Edge (aktuell)

### Optional
- **Docker**: Für Container-Deployment
- **Git**: Für Versionsverwaltung
- **PostgreSQL/MySQL**: Für größere Installationen (statt SQLite)

---

## 🚀 Methode 1: Lokale Installation

### Schritt 1: Repository klonen

```bash
git clone <repository-url>
cd L8teStudy-4
```

Oder: ZIP-Datei herunterladen und entpacken.

### Schritt 2: Virtuelle Umgebung erstellen (empfohlen)

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Schritt 3: Dependencies installieren

```bash
pip install -r requirements.txt
```

### Schritt 4: Umgebungsvariablen konfigurieren (optional)

Erstelle eine `.env` Datei im Projektverzeichnis:

```env
SECRET_KEY=dein-sehr-geheimer-schluessel-hier
DATABASE_URL=sqlite:///instance/l8testudy.db
FLASK_ENV=development
UNTIS_FERNET_KEY=dein-32-byte-base64-key
```

**SECRET_KEY generieren:**
```python
import secrets
print(secrets.token_hex(32))
```

**UNTIS_FERNET_KEY generieren:**
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

### Schritt 5: Datenbank initialisieren

Die Datenbank wird automatisch beim ersten Start erstellt.

Optional manuell:
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### Schritt 6: Super Admin erstellen

```bash
python create_admin.py admin IhrSicheresPasswort superadmin
```

**Wichtig**: Wähle ein sicheres Passwort!

### Schritt 7: Anwendung starten

**Entwicklungsserver:**
```bash
python run.py
```

**Produktionsserver (Gunicorn):**
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Schritt 8: Zugriff

Öffne deinen Browser und gehe zu:
- Lokal: `http://localhost:5000`
- Netzwerk: `http://<deine-ip>:5000`

Logge dich mit dem erstellten Super Admin ein.

---

## 🐳 Methode 2: Docker Installation

### Schritt 1: Repository klonen

```bash
git clone <repository-url>
cd L8teStudy-4
```

### Schritt 2: Umgebungsvariablen setzen

Bearbeite `docker-compose.yml` oder erstelle eine `.env` Datei:

```env
SECRET_KEY=dein-sehr-geheimer-schluessel
FLASK_ENV=production
UNTIS_FERNET_KEY=dein-32-byte-base64-key
```

### Schritt 3: Container starten

```bash
docker-compose up -d
```

### Schritt 4: Super Admin erstellen

```bash
docker exec -it l8testudy python create_admin.py admin IhrPasswort superadmin
```

### Schritt 5: Logs prüfen

```bash
docker-compose logs -f
```

### Schritt 6: Zugriff

Öffne `http://localhost:5000` im Browser.

---

## 🔧 Post-Installation

### 1. Erste Klasse erstellen

1. Als Super Admin einloggen
2. **Admin** → **Superadmin Dashboard**
3. **Klassen verwalten** → **Neue Klasse**
4. Name und Code eingeben
5. Speichern

### 2. Benutzer erstellen

1. **Admin** → **Admin Center** → **Benutzerverwaltung**
2. Benutzername, Passwort und Rolle eingeben
3. **Erstellen**
4. Login-Link teilen oder Klassencode mitteilen

### 3. Fächer einrichten

**Option A: Manuell**
1. **Admin Center** → **Fächer verwalten**
2. Fachname eingeben
3. **Hinzufügen**

**Option B: Von WebUntis importieren**
1. WebUntis-Zugangsdaten konfigurieren (siehe [WebUntis Integration](WebUntis-Integration))
2. **Fächer verwalten** → **Von WebUntis importieren**

### 4. WebUntis konfigurieren (optional)

Siehe [WebUntis Integration](WebUntis-Integration) für Details.

---

## 🔒 Sicherheit nach Installation

### Produktionsumgebung

1. **HTTPS aktivieren**: Nutze einen Reverse Proxy (Nginx, Apache)
2. **Firewall konfigurieren**: Nur notwendige Ports öffnen
3. **Starkes SECRET_KEY**: Niemals den Default-Wert verwenden
4. **FLASK_ENV=production**: Unbedingt in Produktion setzen
5. **Regelmäßige Backups**: Siehe [Backup und Restore](Backup-und-Restore)

### Empfohlene Nginx-Konfiguration

```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🔄 Updates installieren

### Lokale Installation

```bash
# Code aktualisieren
git pull origin main

# Dependencies aktualisieren
pip install -r requirements.txt --upgrade

# Datenbank migrieren (falls nötig)
flask db upgrade

# Neu starten
python run.py
```

### Docker Installation

```bash
# Container stoppen
docker-compose down

# Code aktualisieren
git pull origin main

# Image neu bauen
docker-compose build

# Container starten
docker-compose up -d
```

---

## 🐛 Troubleshooting

### "ModuleNotFoundError"
**Problem**: Python-Modul nicht gefunden.

**Lösung**:
```bash
pip install -r requirements.txt
```

### "Address already in use"
**Problem**: Port 5000 ist bereits belegt.

**Lösung**:
```bash
# Anderen Port verwenden
python run.py --port 5001
# Oder
gunicorn -w 4 -b 0.0.0.0:5001 run:app
```

### "Database is locked"
**Problem**: SQLite kann nicht mit vielen gleichzeitigen Zugriffen umgehen.

**Lösung**:
- Gunicorn Workers reduzieren: `-w 2`
- Oder auf PostgreSQL wechseln

### Weitere Probleme?
Siehe [Troubleshooting](Troubleshooting) für mehr Lösungen.

---

## 📚 Nächste Schritte

- **[Konfiguration](Konfiguration)** - Erweiterte Einstellungen
- **[Erste Schritte](Erste-Schritte)** - Tutorial für neue Benutzer
- **[Klassenverwaltung](Klassenverwaltung)** - Klassen einrichten
- **[Benutzerverwaltung](Benutzerverwaltung)** - Benutzer verwalten

---

**Installation abgeschlossen!** 🎉 Weiter zu [Konfiguration](Konfiguration) →
