# Architektur

Technische Übersicht über die Architektur von L8teStudy.

---

## 📁 Projektstruktur

```
L8teStudy-4/
├── app/                      # Hauptanwendung
│   ├── __init__.py          # Flask App Factory & Konfiguration
│   ├── models.py            # SQLAlchemy Datenmodelle
│   ├── routes.py            # API-Endpunkte & Views
│   └── notifications.py     # Push-Benachrichtigungen & Scheduler
│
├── static/                   # Statische Dateien
│   ├── icon-192.png         # PWA Icon (klein)
│   ├── icon-512.png         # PWA Icon (groß)
│   ├── manifest.json        # PWA Manifest
│   ├── sw.js               # Service Worker
│   └── translations.js      # Mehrsprachigkeit (i18n)
│
├── templates/               # HTML-Templates
│   ├── index.html          # Haupt-SPA (Single Page Application)
│   ├── login.html          # Login-Seite
│   ├── setup.html          # Ersteinrichtung
│   └── legal.html          # Impressum/Datenschutz
│
├── instance/               # Instanz-spezifische Daten (nicht im Git)
│   ├── l8testudy.db       # SQLite Datenbank
│   └── uploads/           # Hochgeladene Dateien
│
├── migrations/            # Alembic Datenbank-Migrationen
│   ├── versions/         # Migration-Scripts
│   └── alembic.ini       # Alembic-Konfiguration
│
├── wiki/                  # GitHub Wiki (Dokumentation)
│
├── create_admin.py       # CLI-Tool für Admin-Erstellung
├── test_everything.py    # Umfassende Test-Suite
├── run.py               # Entwicklungsserver Einstiegspunkt
├── requirements.txt     # Python Dependencies
├── Dockerfile          # Docker Image Definition
├── docker-compose.yml  # Docker Compose Konfiguration
├── entrypoint.sh       # Docker Entrypoint Script
├── .gitignore         # Git Ignore-Regeln
├── README.md          # Projekt-Übersicht
├── CHANGELOG.md       # Versionshistorie
├── UPGRADE.md         # Upgrade-Anleitung
└── version.txt        # Aktuelle Version

```

---

## 🏗 Architektur-Übersicht

### Schichtenmodell

```
┌─────────────────────────────────────┐
│         Frontend (Browser)          │
│  HTML5 + CSS3 + Vanilla JavaScript  │
│         Service Worker (PWA)        │
└─────────────────────────────────────┘
                  ↕ HTTP/HTTPS
┌─────────────────────────────────────┐
│      Flask Application (Python)     │
│  ┌───────────────────────────────┐  │
│  │   Routes (API + Views)        │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │   Business Logic              │  │
│  └───────────────────────────────┘  │
│  ┌───────────────────────────────┐  │
│  │   Models (SQLAlchemy ORM)     │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
                  ↕ SQL
┌─────────────────────────────────────┐
│     Datenbank (SQLite/PostgreSQL)   │
└─────────────────────────────────────┘
```

---

## 🔧 Technologie-Stack

### Backend

**Flask** (Python Web Framework)
- Routing & Request Handling
- Template Rendering
- Session Management

**SQLAlchemy** (ORM)
- Datenbank-Abstraktion
- Modell-Definitionen
- Query-Builder

**Flask-Login**
- Benutzer-Session-Management
- Login/Logout-Funktionalität
- `@login_required` Decorator

**Flask-Migrate** (Alembic)
- Datenbank-Migrationen
- Schema-Versionierung

**Gunicorn** (WSGI Server)
- Produktions-HTTP-Server
- Multi-Worker-Support
- Load Balancing

**APScheduler**
- Hintergrund-Jobs
- Benachrichtigungs-Scheduler
- Cron-ähnliche Tasks

### Frontend

**Vanilla JavaScript**
- Keine Framework-Abhängigkeiten
- Direkte DOM-Manipulation
- Fetch API für AJAX

**HTML5 & CSS3**
- Semantisches HTML
- Responsive Design
- CSS Grid & Flexbox

**Service Worker**
- Offline-Funktionalität
- Push-Benachrichtigungen
- Cache-Management

### Sicherheit

**Flask-WTF**
- CSRF-Schutz
- Form-Validierung
- Secure Token-Generierung

**Flask-Talisman**
- Security Headers
- Content Security Policy (CSP)
- HTTPS-Erzwingung
- HSTS

**Flask-Limiter**
- Rate Limiting
- Brute-Force-Schutz
- IP-basierte Limits

**Werkzeug**
- Passwort-Hashing (PBKDF2)
- Sichere Passwort-Verifikation

**Cryptography (Fernet)**
- Symmetrische Verschlüsselung
- WebUntis-Passwörter

### Integrationen

**WebUntis API**
- Stundenplan-Import
- Vertretungsplan
- Fächer-Synchronisation

**PyWebPush**
- Web Push-Benachrichtigungen
- VAPID-Authentifizierung
- Payload-Verschlüsselung

### Datenbank

**SQLite** (Standard)
- Dateibasiert
- Keine Konfiguration nötig
- Ideal für kleine/mittlere Installationen

**PostgreSQL** (Optional)
- Für größere Installationen
- Bessere Concurrent-Performance
- Erweiterte Features

---

## 🔄 Request-Flow

### Typischer API-Request

```
1. Browser sendet Request
   ↓
2. Gunicorn empfängt Request
   ↓
3. Flask-Limiter prüft Rate Limit
   ↓
4. Flask-Talisman prüft Security Headers
   ↓
5. Flask-Login prüft Authentifizierung
   ↓
6. Route-Handler verarbeitet Request
   ↓
7. Business Logic wird ausgeführt
   ↓
8. SQLAlchemy führt DB-Queries aus
   ↓
9. Response wird generiert
   ↓
10. Security Headers werden hinzugefügt
   ↓
11. Response wird an Browser gesendet
```

---

## 🗄 Datenbank-Architektur

### Entity-Relationship-Diagramm (vereinfacht)

```
┌─────────────┐       ┌─────────────┐
│ SchoolClass │───┐   │    User     │
└─────────────┘   │   └─────────────┘
       │          │          │
       │          └──────────┤
       │                     │
       │          ┌──────────┴──────────┐
       │          │                     │
       ├──────────┤                     │
       │          │                     │
┌──────▼──────┐   │   ┌─────────┐   ┌──▼──────┐
│   Subject   │   └───│  Task   │   │  Grade  │
└─────────────┘       └─────────┘   └─────────┘
       │                     │
       │              ┌──────┴──────┐
       │              │             │
       │       ┌──────▼──────┐  ┌──▼──────────┐
       │       │ TaskMessage │  │ TaskImage   │
       │       └─────────────┘  └─────────────┘
       │
┌──────▼──────┐
│    Event    │
└─────────────┘
```

Siehe [Datenbank-Schema](Datenbank-Schema) für Details.

---

## 🔐 Sicherheits-Architektur

### Defense in Depth

**Schicht 1: Netzwerk**
- Firewall
- HTTPS (TLS/SSL)
- Reverse Proxy (Nginx/Apache)

**Schicht 2: Application**
- CSRF-Schutz (Flask-WTF)
- CSP (Content Security Policy)
- HSTS (HTTP Strict Transport Security)
- Rate Limiting

**Schicht 3: Authentifizierung**
- Session-basiert (Flask-Login)
- Passwort-Hashing (PBKDF2)
- Secure Cookies (HttpOnly, Secure, SameSite)

**Schicht 4: Autorisierung**
- Rollenbasierte Zugriffskontrolle (RBAC)
- Klassenbasierte Isolation
- Ressourcen-Level-Checks

**Schicht 5: Daten**
- Verschlüsselte Passwörter (WebUntis)
- Sichere Datei-Uploads
- SQL-Injection-Schutz (SQLAlchemy)

---

## 📱 Progressive Web App (PWA)

### PWA-Komponenten

**Manifest** (`static/manifest.json`)
- App-Metadaten
- Icons
- Display-Modus
- Theme-Farben

**Service Worker** (`static/sw.js`)
- Offline-Funktionalität
- Cache-Strategie
- Push-Benachrichtigungen
- Background Sync

**Installierbarkeit**
- Add to Home Screen
- Standalone-Modus
- App-ähnliches Erlebnis

---

## 🔔 Benachrichtigungs-Architektur

### Push-Benachrichtigungs-Flow

```
1. Benutzer aktiviert Push in Browser
   ↓
2. Browser generiert Push-Subscription
   ↓
3. Subscription wird an Server gesendet
   ↓
4. Server speichert Subscription in DB
   ↓
5. APScheduler prüft alle 45 Sekunden
   ↓
6. Neue Ereignisse werden erkannt
   ↓
7. PyWebPush sendet Benachrichtigung
   ↓
8. Service Worker empfängt Push
   ↓
9. Browser zeigt Benachrichtigung an
```

---

## 🔄 Datenfluss

### Aufgabe erstellen

```
Frontend (index.html)
  ↓ FormData mit Bildern
routes.py: POST /api/tasks
  ↓ Validierung
  ↓ Datei-Upload (instance/uploads/)
  ↓ SQLAlchemy ORM
models.py: Task, TaskImage
  ↓ SQL INSERT
Datenbank (l8testudy.db)
  ↓ Commit
  ↓ Benachrichtigung triggern
notifications.py: check_reminders()
  ↓ PyWebPush
Browser: Push-Benachrichtigung
```

---

## 🧩 Modularität

### App Factory Pattern

```python
# app/__init__.py
def create_app():
    app = Flask(__name__)
    
    # Extensions initialisieren
    db.init_app(app)
    login_manager.init_app(app)
    csrf.init_app(app)
    
    # Blueprints registrieren
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(api_bp)
    
    return app
```

**Vorteile**:
- Testbarkeit
- Mehrere App-Instanzen
- Konfigurierbarkeit

---

## 📊 Performance-Optimierungen

### Datenbank

- **Lazy Loading**: Relationships werden nur bei Bedarf geladen
- **Eager Loading**: Kritische Relationships werden vorab geladen
- **Indizes**: Auf häufig abgefragten Spalten
- **Connection Pooling**: Wiederverwendung von DB-Verbindungen

### Frontend

- **Lazy Loading**: Bilder werden nur bei Sichtbarkeit geladen
- **Caching**: Service Worker cached statische Ressourcen
- **Minification**: CSS/JS werden minimiert (Produktion)
- **Compression**: Gzip/Brotli auf Server-Ebene

### Backend

- **Gunicorn Workers**: Parallele Request-Verarbeitung
- **APScheduler**: Asynchrone Hintergrund-Jobs
- **Session-Optimierung**: Effiziente Session-Speicherung

---

## 🔧 Erweiterbarkeit

### Neue Features hinzufügen

1. **Modell erstellen** (`app/models.py`)
2. **Migration generieren** (`flask db migrate`)
3. **API-Endpunkt** (`app/routes.py`)
4. **Frontend-Integration** (`templates/index.html`)
5. **Übersetzungen** (`static/translations.js`)

### Plugin-System

Zukünftige Erweiterung möglich durch:
- Blueprint-basierte Plugins
- Hook-System für Events
- Konfigurierbare Extensions

---

## 📚 Weitere Ressourcen

- **[Datenbank-Schema](Datenbank-Schema)** - Detaillierte Modell-Dokumentation
- **[API-Dokumentation](API-Dokumentation)** - Alle Endpunkte
- **[Entwicklung](Entwicklung)** - Entwicklungsumgebung
- **[Sicherheit](Sicherheit)** - Security Best Practices

---

**Architektur-Dokumentation komplett!** 🏗️
