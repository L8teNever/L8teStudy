# 5. Technischer Stack

Vollständige Übersicht über die verwendeten Technologien in L8teStudy.

---

## 🎯 Übersicht

L8teStudy verwendet einen modernen, sicheren und skalierbaren Tech-Stack, der auf **Python** basiert und **Privatsphäre** sowie **Performance** priorisiert.

---

## 🐍 Backend-Technologien

### Core Framework

**Python 3.8+**
- Hauptprogrammiersprache
- Moderne Syntax und Features
- Große Bibliotheks-Ökosystem

**Flask 2.x** (Micro Web Framework)
- Leichtgewichtig und flexibel
- Routing & Request Handling
- Template Rendering (Jinja2)
- Session Management
- WSGI-kompatibel

### Datenbank & ORM

**SQLite** (Standard-Datenbank)
- Dateibasiert (`instance/l8testudy.db`)
- Keine separate Installation nötig
- Ideal für kleine/mittlere Installationen
- **FTS5 (Full-Text Search)** für Millisekunden-Suche
- Unterstützung für OCR-Textindizierung

**PostgreSQL** (Optional, für größere Installationen)
- Bessere Concurrent-Performance
- Erweiterte Features
- Skalierbarkeit

**SQLAlchemy** (ORM)
- Objekt-relationale Abbildung
- Datenbank-Abstraktion
- Query-Builder
- Relationship-Management
- Migration-Support

**Flask-Migrate** (Alembic)
- Datenbank-Schema-Versionierung
- Automatische Migration-Generierung
- Upgrade/Downgrade-Funktionalität

### Authentifizierung & Sicherheit

**Flask-Login**
- Session-basierte Authentifizierung
- User-Loader
- `@login_required` Decorator
- Remember-Me-Funktionalität

**Werkzeug Security**
- Passwort-Hashing (PBKDF2-SHA256)
- Sichere Passwort-Verifikation
- Salt-Generation

**Cryptography Library** (AES-256-GCM)
- **At-Rest-Verschlüsselung** für alle Dateien
- Symmetrische Verschlüsselung (Fernet)
- WebUntis-Passwort-Verschlüsselung
- **Live-Entschlüsselung** im RAM beim Öffnen
- Sichere Schlüsselverwaltung

**Flask-WTF**
- CSRF-Schutz (Cross-Site Request Forgery)
- Form-Validierung
- Secure Token-Generierung

**Flask-Talisman**
- Security Headers (CSP, HSTS, X-Frame-Options)
- Content Security Policy
- HTTPS-Erzwingung
- Clickjacking-Schutz

**Flask-Limiter**
- Rate Limiting
- Brute-Force-Schutz
- IP-basierte Request-Limits
- Flexible Limit-Konfiguration

### OCR & Dokumentenverarbeitung

**Tesseract OCR** (via pytesseract)
- Texterkennung aus handschriftlichen Notizen
- Multi-Language-Support (Deutsch, Englisch, etc.)
- PDF-Verarbeitung
- Bildoptimierung für bessere Erkennung

**PyPDF2 / PDFMiner**
- PDF-Text-Extraktion
- Metadaten-Auslesen
- PDF-Manipulation

**Pillow (PIL Fork)**
- Bildverarbeitung
- Format-Konvertierung
- Thumbnail-Generierung
- Bildoptimierung für OCR

### Cloud-Integration

**Google Drive API** (google-api-python-client)
- Automatischer Sync mit GoodNotes-Backup-Ordnern
- OAuth 2.0 Authentifizierung
- Datei-Upload/Download
- Change Detection (Webhooks)
- Ordner-Monitoring

**iCloud API** (Optional, via pyicloud)
- Alternative zu Google Drive
- Backup-Synchronisation

### Background Jobs & Scheduling

**APScheduler** (Advanced Python Scheduler)
- Hintergrund-Jobs
- Cron-ähnliche Tasks
- Benachrichtigungs-Scheduler
- Periodisches Scannen von Cloud-Ordnern
- OCR-Verarbeitung im Hintergrund

**Celery** (Optional, für größere Installationen)
- Verteilte Task-Queue
- Asynchrone Verarbeitung
- Worker-Pools

### Push-Benachrichtigungen

**PyWebPush**
- Web Push Protocol
- VAPID-Authentifizierung
- Payload-Verschlüsselung
- Browser-Push-Notifications

### HTTP Server

**Gunicorn** (WSGI Server)
- Produktions-HTTP-Server
- Multi-Worker-Support
- Load Balancing
- Graceful Restarts

**Nginx** (Reverse Proxy, empfohlen)
- SSL/TLS-Terminierung
- Static File Serving
- Load Balancing
- Caching

---

## 🌐 Frontend-Technologien

### Core Technologies

**HTML5**
- Semantisches Markup
- Accessibility (ARIA)
- Progressive Enhancement

**CSS3**
- Responsive Design
- CSS Grid & Flexbox
- Custom Properties (CSS Variables)
- Animations & Transitions
- Dark Mode Support

**Vanilla JavaScript (ES6+)**
- Keine Framework-Abhängigkeiten
- Direkte DOM-Manipulation
- Fetch API für AJAX
- Async/Await
- Module System

### Progressive Web App (PWA)

**Service Worker** (`static/sw.js`)
- Offline-Funktionalität
- Cache-First-Strategie
- Push-Benachrichtigungen
- Background Sync

**Web App Manifest** (`static/manifest.json`)
- App-Metadaten
- Icons (192x192, 512x512)
- Display-Modus (standalone)
- Theme-Farben
- Installierbarkeit

### Internationalisierung

**i18n System** (`static/translations.js`)
- Mehrsprachigkeit (Deutsch, Englisch)
- Client-seitige Übersetzungen
- Dynamischer Sprachwechsel

---

## 🔌 Externe Integrationen

### WebUntis API

**WebUntis Python Client**
- Stundenplan-Import
- Vertretungsplan
- Fächer-Synchronisation
- Lehrer-Informationen
- Raum-Informationen

### Cloud-Speicher

**Google Drive API**
- GoodNotes-Backup-Synchronisation
- Automatische Datei-Erkennung
- Change Notifications

**Dropbox API** (Optional)
- Alternative Cloud-Integration

---

## 🗄 Datenbank-Technologien

### SQLite Features

**FTS5 (Full-Text Search)**
- Volltextsuche in OCR-Texten
- Millisekunden-Suchgeschwindigkeit
- Ranking-Algorithmen
- Phrase-Suche

**JSON Support**
- JSON-Spalten für flexible Daten
- JSON-Queries

**Foreign Keys**
- Referenzielle Integrität
- Cascade-Operationen

### Datenbank-Schema

Siehe [Datenbank-Schema](Datenbank-Schema) für Details.

---

## 🔐 Sicherheits-Technologien

### Verschlüsselung

**AES-256-GCM** (via Cryptography Library)
- At-Rest-Verschlüsselung aller Dateien
- Authenticated Encryption
- Nonce-basierte Verschlüsselung
- Schlüsselableitung (PBKDF2)

**TLS/SSL**
- HTTPS-Verschlüsselung
- Let's Encrypt Integration
- Perfect Forward Secrecy

### Authentifizierung

**Session-basiert**
- Secure Cookies (HttpOnly, Secure, SameSite)
- Session-Timeout
- CSRF-Token

**Passwort-Hashing**
- PBKDF2-SHA256
- Salting
- Iterationen: 260,000+

---

## 🐳 DevOps & Deployment

### Containerisierung

**Docker**
- Dockerfile für App-Image
- Multi-Stage Builds
- Layer-Caching

**Docker Compose**
- Multi-Container-Setup
- Entwicklungsumgebung
- Produktions-Konfiguration

### Versionskontrolle

**Git**
- GitHub Repository
- Branch-Strategie
- Pull Requests

### CI/CD (Optional)

**GitHub Actions**
- Automatische Tests
- Deployment-Pipelines
- Code-Quality-Checks

---

## 🧪 Testing & Qualität

### Testing Frameworks

**pytest**
- Unit Tests
- Integration Tests
- Fixtures

**test_everything.py**
- Umfassende Test-Suite
- API-Tests
- Datenbank-Tests

### Code Quality

**pylint / flake8**
- Code-Linting
- Style-Checks
- Best Practices

**Black**
- Code-Formatting
- Konsistenter Stil

---

## 📦 Python-Dependencies

Vollständige Liste in `requirements.txt`:

```txt
Flask>=2.3.0
Flask-Login>=0.6.2
Flask-Migrate>=4.0.4
Flask-WTF>=1.1.1
Flask-Talisman>=1.0.0
Flask-Limiter>=3.3.1
SQLAlchemy>=2.0.0
gunicorn>=20.1.0
APScheduler>=3.10.1
pywebpush>=1.14.0
cryptography>=41.0.0
pytesseract>=0.3.10
Pillow>=10.0.0
PyPDF2>=3.0.0
google-api-python-client>=2.95.0
google-auth-httplib2>=0.1.0
google-auth-oauthlib>=1.0.0
requests>=2.31.0
python-dotenv>=1.0.0
```

---

## 🌟 Besondere Features

### Lokale Verarbeitung

**Keine Cloud-Abhängigkeit für Verarbeitung**
- OCR läuft lokal auf dem Server
- Verschlüsselung lokal
- Suche lokal
- Datenschutz-freundlich

### Intelligente Organisation

**Smarte Fach-Zuordnung**
- Automatische Erkennung von Fächern
- Mapping von Ordnernamen zu Fächern
- Konfigurierbare Zuordnungen

**Urheber-Transparenz**
- Jede Notiz zeigt den Ersteller
- "Gefunden in 'Mathe-Notizen' von Lena"
- Respekt für geistiges Eigentum

### Privatsphäre-Kontrolle

**Granulare Freigabe-Optionen**
- Pro Ordner entscheidbar
- "Nur für mich" / "Für die Klasse"
- Jederzeit änderbar

---

## 🔄 Datenfluss-Architektur

### GoodNotes → L8teStudy Flow

```
1. Schüler speichert Notizen in GoodNotes
   ↓
2. GoodNotes exportiert zu Google Drive
   ↓
3. Google Drive sendet Change Notification
   ↓
4. L8teStudy Background Worker erkennt neue Datei
   ↓
5. Datei wird heruntergeladen
   ↓
6. AES-256-GCM Verschlüsselung
   ↓
7. Speicherung auf Server (verschlüsselt)
   ↓
8. OCR-Verarbeitung (Tesseract)
   ↓
9. Text-Extraktion
   ↓
10. FTS5-Indizierung in SQLite
   ↓
11. Verfügbar für Suche
```

### Suchvorgang

```
1. Benutzer gibt Suchbegriff ein
   ↓
2. FTS5-Query auf SQLite
   ↓
3. Relevante Dokumente gefunden (< 100ms)
   ↓
4. Berechtigungsprüfung (Privatsphäre-Level)
   ↓
5. Ergebnisse mit Urheber-Info
   ↓
6. Benutzer klickt auf Ergebnis
   ↓
7. Live-Entschlüsselung im RAM
   ↓
8. PDF-Anzeige im Browser
   ↓
9. RAM wird geleert (keine Spuren)
```

---

## 📊 Performance-Spezifikationen

### Suchgeschwindigkeit

- **FTS5-Suche**: < 100ms für 10.000+ Dokumente
- **OCR-Verarbeitung**: ~5-10 Sekunden pro Seite
- **Verschlüsselung**: ~50-100 MB/s
- **Entschlüsselung**: ~50-100 MB/s

### Skalierbarkeit

- **SQLite**: Bis zu 10.000 Dokumente
- **PostgreSQL**: Unbegrenzt
- **Concurrent Users**: 50-100 (Gunicorn Workers)

---

## 🔮 Zukünftige Technologien (Roadmap)

### Geplante Erweiterungen

**Machine Learning**
- Automatische Fach-Erkennung (NLP)
- Handschrift-Verbesserung für OCR
- Intelligente Zusammenfassungen

**Real-Time Collaboration**
- WebSockets (Flask-SocketIO)
- Live-Editing
- Chat-Integration

**Mobile Apps**
- React Native / Flutter
- Native iOS/Android Apps
- Offline-Sync

**Advanced OCR**
- Handwriting Recognition (HTR)
- Mathematische Formeln (LaTeX)
- Diagramm-Erkennung

---

## 📚 Weitere Ressourcen

- **[Architektur](Architektur)** - Systemarchitektur-Übersicht
- **[Sicherheit](Sicherheit)** - Security Best Practices
- **[API-Dokumentation](API-Dokumentation)** - Alle Endpunkte
- **[Installation](Installation)** - Setup-Anleitung

---

**Technischer Stack komplett dokumentiert!** 🚀
