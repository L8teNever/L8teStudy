# L8teStudy v2.0.0

**L8teStudy** ist eine moderne, webbasierte Lernplattform für Schulklassen mit umfassenden Funktionen für Aufgabenverwaltung, Terminplanung, Notenverwaltung und Stundenplan-Integration.

---

## 📋 Inhaltsverzeichnis

- [Überblick](#überblick)
- [Features](#features)
- [Technologie-Stack](#technologie-stack)
- [Installation](#installation)
  - [Voraussetzungen](#voraussetzungen)
  - [Lokale Installation](#lokale-installation)
  - [Docker Installation](#docker-installation)
- [Konfiguration](#konfiguration)
- [Verwendung](#verwendung)
  - [Erster Start](#erster-start)
  - [Benutzerrollen](#benutzerrollen)
  - [Hauptfunktionen](#hauptfunktionen)
- [Architektur](#architektur)
  - [Projektstruktur](#projektstruktur)
  - [Datenbank-Schema](#datenbank-schema)
  - [API-Endpunkte](#api-endpunkte)
- [Sicherheit](#sicherheit)
- [WebUntis Integration](#webuntis-integration)
- [Push-Benachrichtigungen](#push-benachrichtigungen)
- [Entwicklung](#entwicklung)
- [Deployment](#deployment)
- [Troubleshooting](#troubleshooting)
- [Changelog](#changelog)
- [Lizenz](#lizenz)

---

## 🎯 Überblick

L8teStudy ist eine vollständige Schulmanagement-Lösung, die es Schülern und Lehrern ermöglicht:
- Hausaufgaben und Klausuren zu verwalten
- Termine zu planen und zu teilen
- Noten zu tracken und Durchschnitte zu berechnen
- Stundenpläne von WebUntis zu importieren
- In Echtzeit über Aufgaben zu chatten
- Push-Benachrichtigungen zu erhalten

Die Anwendung ist als Progressive Web App (PWA) konzipiert und kann auf allen Geräten installiert werden.

---

## ✨ Features

### 📚 Aufgabenverwaltung
- Erstellen, Bearbeiten und Löschen von Aufgaben
- Fälligkeitsdaten und Fachzuordnung
- Bildanhänge für Aufgaben
- Aufgaben-Chat für Diskussionen
- Klassenübergreifendes Teilen von Aufgaben
- Individuelle Erledigungsstatus pro Benutzer

### 📅 Terminplanung
- Kalenderansicht (Monat/Liste)
- Ereignisse mit Fachzuordnung
- Geteilte Termine zwischen Klassen
- Erinnerungen für anstehende Termine

### 📊 Notenverwaltung
- Noten mit Gewichtung erfassen
- Automatische Durchschnittsberechnung
- Fachspezifische und Gesamtdurchschnitte
- Notenverlauf visualisieren

### 🕐 Stundenplan (WebUntis)
- Automatischer Import von WebUntis
- Anzeige von Vertretungen und Ausfällen
- Fachvorschläge basierend auf aktuellem Unterricht
- Automatischer Fächerimport

### 💬 Chat & Kommunikation
- Aufgaben-spezifische Chats
- Bild- und Dateianhänge
- Ungelesene Nachrichten-Zähler
- Echtzeit-Updates

### 🔔 Benachrichtigungen
- Browser Push-Benachrichtigungen
- Tägliche Erinnerungen (konfigurierbar)
- Benachrichtigungen für neue Aufgaben/Termine
- Chat-Benachrichtigungen

### 👥 Benutzerverwaltung
- Drei Benutzerrollen: Student, Admin, Super Admin
- Klassenbasierte Organisation
- Erzwungener Passwortwechsel für neue Benutzer
- Passwort-Komplexitätsprüfung

### 🎨 Benutzeroberfläche
- Responsive Design für alle Geräte
- Dark Mode
- Mehrsprachigkeit (DE, EN, FR, ES, IT, TR)
- Progressive Web App (installierbar)
- Tutorial für neue Benutzer

### 🔒 Sicherheit
- CSRF-Schutz
- Content Security Policy (CSP)
- Rate Limiting
- HTTPS-Erzwingung in Produktion
- Verschlüsselte WebUntis-Passwörter
- Sichere Session-Verwaltung

### 📦 Backup & Restore
- Vollständiger Datenbank-Export (JSON)
- Datenbank-Import/Wiederherstellung
- Audit-Log für alle Aktionen

---

## 🛠 Technologie-Stack

### Backend
- **Flask** - Python Web Framework
- **SQLAlchemy** - ORM für Datenbankzugriff
- **Flask-Login** - Benutzer-Session-Management
- **Flask-Migrate** - Datenbank-Migrationen
- **Gunicorn** - WSGI HTTP Server
- **APScheduler** - Hintergrund-Jobs für Benachrichtigungen

### Frontend
- **Vanilla JavaScript** - Keine Framework-Abhängigkeiten
- **HTML5 & CSS3** - Moderne Web-Standards
- **Service Worker** - Offline-Funktionalität & PWA

### Sicherheit
- **Flask-WTF** - CSRF-Schutz
- **Flask-Talisman** - Security Headers & CSP
- **Flask-Limiter** - Rate Limiting
- **Werkzeug** - Passwort-Hashing
- **Cryptography** - Fernet-Verschlüsselung für WebUntis

### Integrationen
- **WebUntis** - Stundenplan-Integration
- **PyWebPush** - Web Push-Benachrichtigungen

### Datenbank
- **SQLite** - Standarddatenbank (entwicklungsfreundlich)
- Unterstützt auch PostgreSQL/MySQL via SQLAlchemy

---

## 📥 Installation

### Voraussetzungen

- **Python 3.8+**
- **pip** (Python Package Manager)
- **Git** (optional, für Versionsverwaltung)
- **Docker & Docker Compose** (optional, für Container-Deployment)

### Lokale Installation

1. **Repository klonen oder herunterladen**
```bash
git clone <repository-url>
cd L8teStudy-4
```

2. **Virtuelle Umgebung erstellen (empfohlen)**
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

3. **Abhängigkeiten installieren**
```bash
pip install -r requirements.txt
```

4. **Umgebungsvariablen konfigurieren** (optional)
Erstelle eine `.env` Datei im Projektverzeichnis:
```env
SECRET_KEY=dein-geheimer-schluessel-hier
DATABASE_URL=sqlite:///instance/l8testudy.db
FLASK_ENV=development
UNTIS_FERNET_KEY=dein-fernet-key-hier
```

5. **Datenbank initialisieren**
```bash
flask db upgrade
# oder
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

6. **Super Admin erstellen**
```bash
python create_admin.py admin IhrSicheresPasswort superadmin
```

7. **Anwendung starten**
```bash
# Entwicklungsserver
python run.py

# Produktionsserver (Gunicorn)
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

Die Anwendung ist nun unter `http://localhost:5000` erreichbar.

### Docker Installation

1. **Docker Compose verwenden**

Es gibt mehrere Docker Compose Konfigurationen:
- `docker-compose.yml` - Basis-Konfiguration
- `docker-compose.local.yml` - Lokales Build
- `docker-compose.github.yml` - GitHub Container Registry
- `docker-compose.dockerhub.yml` - Docker Hub

2. **Container starten**
```bash
# Lokales Build
docker-compose -f docker-compose.local.yml up -d

# Oder mit GitHub Registry
docker-compose -f docker-compose.github.yml up -d
```

3. **Super Admin im Container erstellen**
```bash
docker exec -it l8testudy python create_admin.py admin IhrPasswort superadmin
```

4. **Logs anzeigen**
```bash
docker-compose logs -f
```

---

## ⚙️ Konfiguration

### Umgebungsvariablen

| Variable | Beschreibung | Standard |
|----------|--------------|----------|
| `SECRET_KEY` | Flask Secret Key für Sessions | `dev-secret-key-change-in-prod` |
| `DATABASE_URL` | Datenbank-Verbindungsstring | `sqlite:///l8testudy.db` |
| `FLASK_ENV` | Umgebung (development/production) | `development` |
| `UNTIS_FERNET_KEY` | Verschlüsselungsschlüssel für WebUntis | Auto-generiert |
| `UPLOAD_FOLDER` | Verzeichnis für Uploads | `instance/uploads` |

### Sicherheitseinstellungen

In Produktion (`FLASK_ENV=production`):
- HTTPS wird erzwungen
- Secure Cookies aktiviert
- HSTS (HTTP Strict Transport Security) aktiviert
- Strikte CSP-Richtlinien

### WebUntis Konfiguration

WebUntis-Zugangsdaten werden pro Klasse in der Admin-Oberfläche konfiguriert:
1. Als Admin einloggen
2. Admin Center → Klassen-Einstellungen
3. WebUntis-Daten eingeben (Server, Schule, Benutzername, Passwort, Klassenname)

---

## 📖 Verwendung

### Erster Start

1. **Super Admin Login**
   - Navigiere zu `http://localhost:5000`
   - Logge dich mit dem erstellten Super Admin ein

2. **Klasse erstellen**
   - Gehe zu "Admin" → "Superadmin Dashboard"
   - Klicke auf "Klassen verwalten"
   - Erstelle eine neue Klasse mit Namen und Code

3. **Benutzer erstellen**
   - In den Klassen-Einstellungen → "Benutzer verwalten"
   - Erstelle Schüler und Admins
   - Teile den Login-Link oder Klassencode

4. **Fächer einrichten**
   - "Fächer verwalten" in den Klassen-Einstellungen
   - Manuell hinzufügen oder von WebUntis importieren

### Benutzerrollen

#### 👤 Student
- Aufgaben und Termine ansehen/erstellen
- Eigene Noten verwalten
- Chat-Teilnahme
- Stundenplan ansehen

#### 👨‍💼 Admin
- Alle Student-Rechte
- Benutzerverwaltung der eigenen Klasse
- Klassen-Einstellungen bearbeiten
- Fächerverwaltung
- Audit-Log einsehen

#### 👑 Super Admin
- Alle Admin-Rechte
- Klassenübergreifende Verwaltung
- Globale Fächer erstellen
- Klassen erstellen/löschen
- System-weite Einstellungen
- Backup & Restore

### Hauptfunktionen

#### Aufgaben erstellen
1. Navigiere zu "Aufgaben"
2. Klicke auf das "+" Symbol
3. Fülle Titel, Fach, Datum und Beschreibung aus
4. Optional: Bilder anhängen
5. Optional: Als "Geteilt" markieren für klassenübergreifende Sichtbarkeit
6. Speichern

#### Termine erstellen
1. Navigiere zu "Plan"
2. Klicke auf das "+" Symbol
3. Fülle die Termindetails aus
4. Speichern

#### Noten eintragen
1. Navigiere zu "Noten"
2. Klicke auf das "+" Symbol
3. Wähle Fach, Note, Gewichtung
4. Optional: Titel und Beschreibung
5. Speichern

#### Chat verwenden
1. Öffne eine Aufgabe
2. Klicke auf das Chat-Symbol
3. Schreibe Nachrichten oder lade Bilder hoch
4. Andere Benutzer sehen die Nachrichten in Echtzeit

---

## 🏗 Architektur

### Projektstruktur

```
L8teStudy-4/
├── app/
│   ├── __init__.py          # Flask App Factory
│   ├── models.py            # SQLAlchemy Modelle
│   ├── routes.py            # API & View Routes
│   └── notifications.py     # Push-Benachrichtigungen & Scheduler
├── static/
│   ├── icon-192.png         # PWA Icon
│   ├── icon-512.png         # PWA Icon
│   ├── manifest.json        # PWA Manifest
│   ├── sw.js               # Service Worker
│   └── translations.js      # i18n Übersetzungen
├── templates/
│   ├── index.html          # Haupt-SPA
│   ├── login.html          # Login-Seite
│   ├── setup.html          # Ersteinrichtung
│   └── legal.html          # Impressum/Datenschutz
├── instance/               # Instanz-spezifische Daten
│   ├── l8testudy.db       # SQLite Datenbank
│   └── uploads/           # Hochgeladene Dateien
├── migrations/            # Alembic Migrationen
├── create_admin.py        # CLI Tool für Admin-Erstellung
├── requirements.txt       # Python Dependencies
├── run.py                # Entwicklungsserver Einstiegspunkt
├── Dockerfile            # Docker Image Definition
├── docker-compose.yml    # Docker Compose Konfiguration
├── entrypoint.sh         # Docker Entrypoint Script
└── README.md             # Diese Datei
```

### Datenbank-Schema

#### Haupttabellen

**SchoolClass** - Schulklassen
- `id`, `name`, `code`, `created_at`, `chat_enabled`

**User** - Benutzer
- `id`, `username`, `password_hash`, `role`, `class_id`
- `dark_mode`, `language`, `needs_password_change`, `has_seen_tutorial`

**Task** - Aufgaben
- `id`, `user_id`, `class_id`, `subject_id`, `is_shared`
- `title`, `subject`, `due_date`, `description`, `is_done`, `deleted_at`

**Event** - Termine
- `id`, `user_id`, `class_id`, `subject_id`, `is_shared`
- `title`, `date`, `description`, `deleted_at`

**Grade** - Noten
- `id`, `user_id`, `subject`, `value`, `weight`, `title`, `date`, `description`

**Subject** - Fächer
- `id`, `name`
- Many-to-Many Beziehung zu SchoolClass via `subject_classes`

**TaskMessage** - Chat-Nachrichten
- `id`, `task_id`, `user_id`, `content`, `message_type`
- `file_url`, `file_name`, `created_at`, `parent_id`

**NotificationSetting** - Benachrichtigungseinstellungen
- `id`, `user_id`, `notify_new_task`, `notify_new_event`, `notify_chat_message`
- `reminder_homework`, `reminder_exam`, `last_homework_reminder_at`, `last_exam_reminder_at`

**PushSubscription** - Push-Abonnements
- `id`, `user_id`, `endpoint`, `auth_key`, `p256dh_key`, `created_at`

**UntisCredential** - WebUntis Zugangsdaten
- `id`, `class_id`, `server`, `school`, `username`, `password`, `untis_class_name`

**AuditLog** - Aktivitätsprotokoll
- `id`, `user_id`, `class_id`, `action`, `timestamp`

### API-Endpunkte

#### Authentifizierung
- `POST /auth/login` - Benutzer-Login
- `GET /auth/logout` - Benutzer-Logout
- `POST /api/change-password` - Passwort ändern

#### Aufgaben
- `GET /api/tasks` - Alle Aufgaben abrufen
- `POST /api/tasks` - Neue Aufgabe erstellen
- `PUT /api/tasks/<id>` - Aufgabe bearbeiten
- `DELETE /api/tasks/<id>` - Aufgabe löschen
- `POST /api/tasks/<id>/toggle` - Erledigungsstatus umschalten

#### Termine
- `GET /api/events` - Alle Termine abrufen
- `POST /api/events` - Neuen Termin erstellen
- `PUT /api/events/<id>` - Termin bearbeiten
- `DELETE /api/events/<id>` - Termin löschen

#### Noten
- `GET /api/grades` - Alle Noten abrufen
- `POST /api/grades` - Neue Note erstellen
- `PUT /api/grades/<id>` - Note bearbeiten
- `DELETE /api/grades/<id>` - Note löschen

#### Fächer
- `GET /api/subjects` - Alle Fächer abrufen
- `POST /api/subjects` - Neues Fach erstellen
- `DELETE /api/subjects/<id>` - Fach löschen
- `POST /api/subjects/import-untis` - Fächer von WebUntis importieren

#### Chat
- `GET /api/tasks/<id>/messages` - Chat-Nachrichten abrufen
- `POST /api/tasks/<id>/messages` - Nachricht senden
- `POST /api/tasks/<id>/mark-read` - Chat als gelesen markieren
- `GET /api/tasks/unread-counts` - Ungelesene Nachrichten zählen

#### WebUntis
- `GET /api/untis/timetable` - Stundenplan abrufen
- `POST /api/untis/credentials` - Zugangsdaten speichern
- `GET /api/untis/credentials` - Zugangsdaten abrufen

#### Admin
- `GET /api/users` - Benutzer abrufen (Admin)
- `POST /api/users` - Benutzer erstellen (Admin)
- `DELETE /api/users/<id>` - Benutzer löschen (Admin)
- `GET /api/classes` - Klassen abrufen (Super Admin)
- `POST /api/classes` - Klasse erstellen (Super Admin)
- `PUT /api/classes/<id>` - Klasse bearbeiten (Admin)
- `DELETE /api/classes/<id>` - Klasse löschen (Super Admin)

#### Benachrichtigungen
- `POST /api/push/subscribe` - Push-Benachrichtigungen abonnieren
- `POST /api/push/unsubscribe` - Push-Benachrichtigungen abbestellen
- `GET /api/notification-settings` - Einstellungen abrufen
- `POST /api/notification-settings` - Einstellungen speichern
- `POST /api/push/test` - Test-Benachrichtigung senden

#### Backup
- `GET /api/backup/export` - Datenbank exportieren (Super Admin)
- `POST /api/backup/import` - Datenbank importieren (Super Admin)

---

## 🔒 Sicherheit

### Implementierte Sicherheitsmaßnahmen

1. **Authentifizierung & Autorisierung**
   - Passwort-Hashing mit Werkzeug (PBKDF2)
   - Session-basierte Authentifizierung
   - Rollenbasierte Zugriffskontrolle (RBAC)
   - Erzwungener Passwortwechsel für neue Benutzer

2. **CSRF-Schutz**
   - Flask-WTF CSRF-Tokens
   - SameSite Cookies (Strict)
   - Exemption für API-Endpunkte (Session-basiert)

3. **Content Security Policy**
   - Strikte CSP-Header
   - Nur selbst-gehostete Ressourcen
   - Kein Inline-JavaScript (außer in Templates)
   - Frame-Ancestors: none (Clickjacking-Schutz)

4. **HTTPS & Transport Security**
   - HTTPS-Erzwingung in Produktion
   - HSTS mit 1-Jahr Max-Age
   - Secure & HttpOnly Cookies

5. **Rate Limiting**
   - Flask-Limiter für API-Endpunkte
   - Schutz vor Brute-Force-Angriffen

6. **Datenverschlüsselung**
   - WebUntis-Passwörter mit Fernet verschlüsselt
   - Sichere Schlüsselverwaltung

7. **Weitere Maßnahmen**
   - X-Content-Type-Options: nosniff
   - X-Frame-Options: DENY
   - Referrer-Policy: strict-origin-when-cross-origin
   - Permissions-Policy für Browser-Features
   - Audit-Log für alle Aktionen

### Best Practices

- **Passwörter**: Mindestens 7 Zeichen, Groß-/Kleinbuchstaben, Zahlen
- **Secret Key**: Verwende einen starken, zufälligen Secret Key in Produktion
- **HTTPS**: Betreibe die Anwendung immer hinter HTTPS in Produktion
- **Updates**: Halte Dependencies aktuell (`pip list --outdated`)
- **Backups**: Erstelle regelmäßige Backups der Datenbank

---

## 📱 WebUntis Integration

### Einrichtung

1. **Zugangsdaten konfigurieren** (als Admin)
   - Admin Center → Klassen-Einstellungen
   - Scrolle zu "WebUntis Integration"
   - Fülle aus:
     - Server (z.B. `mese.webuntis.com`)
     - Schule (z.B. `gymnasium-beispiel`)
     - Benutzername (WebUntis-Login)
     - Passwort (wird verschlüsselt gespeichert)
     - Klassenname (z.B. `10a`)

2. **Stundenplan abrufen**
   - Navigiere zu "Stundenplan"
   - Der Plan wird automatisch geladen
   - Zeigt aktuelle Woche mit Vertretungen/Ausfällen

3. **Fächer importieren**
   - Fächer verwalten → "Von WebUntis importieren"
   - Alle Fächer aus dem Stundenplan werden importiert

### Features

- **Automatische Fachvorschläge**: Beim Erstellen von Aufgaben wird das aktuelle/letzte Fach vorgeschlagen
- **Vertretungsplan**: Vertretungen und Ausfälle werden farblich markiert
- **Wochenansicht**: Übersichtliche Darstellung der aktuellen Woche
- **Offline-Modus**: Letzter Stundenplan wird gecacht

---

## 🔔 Push-Benachrichtigungen

### Aktivierung

1. **Browser-Berechtigung erteilen**
   - Einstellungen → Benachrichtigungen
   - "Push erlauben" klicken
   - Browser-Popup bestätigen

2. **Benachrichtigungstypen konfigurieren**
   - Neue Aufgaben (von anderen)
   - Neue Termine (von anderen)
   - Neue Chat-Nachrichten
   - Tägliche Erinnerungen (mit Zeitauswahl)

### Unterstützte Browser

- Chrome/Edge (Desktop & Mobile)
- Firefox (Desktop & Mobile)
- Safari (macOS 16.4+, iOS 16.4+)
- Opera

### Funktionsweise

- **Service Worker**: Empfängt Benachrichtigungen im Hintergrund
- **PyWebPush**: Server-seitige Push-Implementierung
- **VAPID**: Sichere Authentifizierung ohne externe Dienste
- **Scheduler**: APScheduler prüft alle 45 Sekunden auf neue Ereignisse

---

## 👨‍💻 Entwicklung

### Entwicklungsumgebung einrichten

```bash
# Virtuelle Umgebung
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Dependencies installieren
pip install -r requirements.txt

# Entwicklungsserver starten
python run.py
```

### Code-Struktur

- **app/__init__.py**: Flask App Factory, Konfiguration, Extensions
- **app/models.py**: SQLAlchemy Datenmodelle
- **app/routes.py**: Alle API-Endpunkte und Views
- **app/notifications.py**: Push-Benachrichtigungen und Scheduler-Jobs
- **templates/index.html**: Haupt-SPA (Single Page Application)
- **static/translations.js**: Mehrsprachigkeit

### Datenbank-Migrationen

```bash
# Migration erstellen
flask db migrate -m "Beschreibung der Änderung"

# Migration anwenden
flask db upgrade

# Migration rückgängig machen
flask db downgrade
```

### Debugging

- **Flask Debug Mode**: Setze `FLASK_ENV=development`
- **Browser DevTools**: Nutze Console, Network, Application Tabs
- **Logs**: Gunicorn/Flask Logs in Terminal oder Docker Logs

### Testing

Die Anwendung enthält ein umfassendes Test-Script:
```bash
python test_everything.py
```

Dieses testet:
- Alle API-Endpunkte
- Authentifizierung
- CRUD-Operationen
- Berechtigungen
- Datenintegrität

---

## 🚀 Deployment

### Produktions-Checkliste

- [ ] `FLASK_ENV=production` setzen
- [ ] Starken `SECRET_KEY` generieren
- [ ] `UNTIS_FERNET_KEY` setzen (32 Bytes, base64)
- [ ] HTTPS konfigurieren (Reverse Proxy)
- [ ] Datenbank-Backups einrichten
- [ ] Firewall-Regeln konfigurieren
- [ ] Monitoring einrichten
- [ ] Log-Rotation konfigurieren

### Docker Deployment

1. **Image bauen**
```bash
docker build -t l8testudy:2.0.0 .
```

2. **Container starten**
```bash
docker run -d \
  -p 5000:5000 \
  -v l8testudy-data:/app/instance \
  -e SECRET_KEY=your-secret-key \
  -e FLASK_ENV=production \
  --name l8testudy \
  l8testudy:2.0.0
```

3. **Mit Reverse Proxy (Nginx)**
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

### Skalierung

- **Gunicorn Workers**: Anzahl der Worker = (2 × CPU-Kerne) + 1
- **Datenbank**: Für hohe Last PostgreSQL statt SQLite verwenden
- **Load Balancing**: Mehrere Gunicorn-Instanzen hinter Nginx
- **Caching**: Redis für Session-Storage und Caching

---

## 🔧 Troubleshooting

### Häufige Probleme

#### "CSRF Token Missing or Invalid"
- **Ursache**: CSRF-Token fehlt oder ist abgelaufen
- **Lösung**: 
  - Seite neu laden
  - Cookies aktivieren
  - Bei Reverse Proxy: `WTF_CSRF_SSL_STRICT=False` setzen

#### "Database is locked"
- **Ursache**: SQLite kann nicht mit vielen gleichzeitigen Schreibzugriffen umgehen
- **Lösung**: 
  - Auf PostgreSQL/MySQL wechseln
  - Gunicorn Workers reduzieren

#### Push-Benachrichtigungen funktionieren nicht
- **Ursache**: Browser-Berechtigung fehlt oder Service Worker nicht registriert
- **Lösung**:
  - Browser-Berechtigungen prüfen
  - HTTPS verwenden (erforderlich für Push)
  - Service Worker in DevTools → Application prüfen

#### WebUntis-Stundenplan lädt nicht
- **Ursache**: Falsche Zugangsdaten oder Server nicht erreichbar
- **Lösung**:
  - Zugangsdaten in WebUntis-Portal testen
  - Server-URL prüfen (ohne `https://`)
  - Firewall-Regeln prüfen

#### Bilder werden nicht angezeigt
- **Ursache**: Upload-Ordner fehlt oder Berechtigungen falsch
- **Lösung**:
  - `instance/uploads` Ordner erstellen
  - Schreibrechte für Webserver-User setzen
  - In Docker: Volume korrekt gemountet?

### Logs prüfen

**Lokale Installation:**
```bash
# Flask Entwicklungsserver
# Logs direkt in Terminal

# Gunicorn
gunicorn --log-level debug run:app
```

**Docker:**
```bash
# Container Logs
docker logs l8testudy

# Live Logs
docker logs -f l8testudy
```

### Debug-Modus aktivieren

```python
# In run.py oder .env
FLASK_ENV=development
FLASK_DEBUG=1
```

**Achtung**: Debug-Modus NIEMALS in Produktion verwenden!

---

## 📝 Changelog

### Version 2.0.0 (2026-01-12)

#### 🎉 Neue Features
- Vollständige WebUntis-Integration mit Stundenplan-Import
- Aufgaben-Chat-System mit Bild- und Dateianhängen
- Push-Benachrichtigungen mit konfigurierbaren Erinnerungen
- Klassenübergreifendes Teilen von Aufgaben und Terminen
- Tutorial für neue Benutzer
- Mehrsprachigkeit (6 Sprachen)
- Progressive Web App (PWA) mit Offline-Support

#### 🔒 Sicherheit
- Verschlüsselte WebUntis-Passwörter (Fernet)
- Erweiterte Content Security Policy
- HSTS in Produktion
- Rate Limiting für API-Endpunkte
- Audit-Log für alle Aktionen

#### 🏗 Architektur
- Rollenbasiertes System (Student, Admin, Super Admin)
- Klassenbasierte Organisation
- Many-to-Many Beziehung für Fächer
- Individuelle Aufgaben-Erledigungsstatus
- Soft-Delete für Aufgaben und Termine

#### 🐛 Bugfixes
- CSRF-Probleme hinter Reverse Proxies behoben
- Datenbank-Migrationen stabilisiert
- Session-Handling verbessert
- Upload-Pfade korrigiert

#### 🗑️ Entfernt
- Legacy-Migrationsskripte (in App-Initialisierung integriert)
- Backup-Dateien und temporäre Fixes
- Nicht verwendete Docker-Compose-Varianten

---

## 📄 Lizenz

Dieses Projekt ist proprietär. Alle Rechte vorbehalten.

Für Lizenzanfragen kontaktieren Sie bitte den Projektinhaber.

---

## 🙏 Danksagungen

- **Flask** Community für das exzellente Framework
- **WebUntis** für die API-Dokumentation
- Alle Tester und Early Adopters

---

## 📧 Kontakt & Support

Bei Fragen, Problemen oder Feature-Requests:
- Erstelle ein Issue im Repository
- Kontaktiere den Administrator
- Nutze die "Bug melden" Funktion in der App

---

**L8teStudy v2.0.0** - Moderne Lernplattform für Schulen 🎓
