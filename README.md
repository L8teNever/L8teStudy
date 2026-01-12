# L8teStudy v2.0.0

**L8teStudy** ist eine moderne, webbasierte Lernplattform für Schulklassen mit umfassenden Funktionen für Aufgabenverwaltung, Terminplanung, Notenverwaltung und Stundenplan-Integration.

![Version](https://img.shields.io/badge/version-2.0.0-blue)
![Python](https://img.shields.io/badge/python-3.8+-green)
![License](https://img.shields.io/badge/license-proprietary-red)

---

## 🚀 Quick Start

### Lokale Installation

```bash
# 1. Repository klonen
git clone <repository-url>
cd L8teStudy-4

# 2. Dependencies installieren
pip install -r requirements.txt

# 3. Super Admin erstellen
python create_admin.py admin IhrPasswort superadmin

# 4. Starten
python run.py
```

Die App läuft jetzt auf `http://localhost:5000`

### Docker Installation

```bash
# Container starten
docker-compose up -d

# Super Admin erstellen
docker exec -it l8testudy python create_admin.py admin IhrPasswort superadmin
```

---

## ✨ Features

- 📚 **Aufgabenverwaltung** - Hausaufgaben mit Bildern, Chat und Teilen
- 📅 **Terminplanung** - Kalender mit Erinnerungen
- 📊 **Notenverwaltung** - Automatische Durchschnittsberechnung
- 🕐 **WebUntis Integration** - Stundenplan-Import
- 💬 **Chat-System** - Aufgaben-spezifische Diskussionen
- 🔔 **Push-Benachrichtigungen** - Browser-Benachrichtigungen
- 👥 **Benutzerverwaltung** - Rollen: Student, Admin, Super Admin
- 🎨 **Modern & Responsive** - PWA mit Dark Mode
- 🌍 **Mehrsprachig** - DE, EN, FR, ES, IT, TR
- 🔒 **Sicher** - CSRF, CSP, HSTS, Rate Limiting

---

## 📚 Dokumentation

Die vollständige Dokumentation findest du im **[Wiki](../../wiki)**:

### Erste Schritte
- **[Installation](../../wiki/Installation)** - Detaillierte Installationsanleitung
- **[Konfiguration](../../wiki/Konfiguration)** - Umgebungsvariablen & Einstellungen
- **[Erste Schritte](../../wiki/Erste-Schritte)** - Tutorial für neue Benutzer

### Features & Verwendung
- **[Aufgaben & Termine](../../wiki/Aufgaben-und-Termine)** - Verwaltung von Aufgaben und Terminen
- **[Noten](../../wiki/Noten)** - Notenverwaltung und Durchschnitte
- **[WebUntis Integration](../../wiki/WebUntis-Integration)** - Stundenplan-Import
- **[Chat-System](../../wiki/Chat-System)** - Aufgaben-Chat verwenden
- **[Push-Benachrichtigungen](../../wiki/Push-Benachrichtigungen)** - Benachrichtigungen einrichten

### Administration
- **[Benutzerrollen](../../wiki/Benutzerrollen)** - Student, Admin, Super Admin
- **[Benutzerverwaltung](../../wiki/Benutzerverwaltung)** - Benutzer erstellen und verwalten
- **[Klassenverwaltung](../../wiki/Klassenverwaltung)** - Klassen einrichten
- **[Backup & Restore](../../wiki/Backup-und-Restore)** - Daten sichern

### Entwicklung
- **[Architektur](../../wiki/Architektur)** - Projektstruktur und Technologien
- **[API-Dokumentation](../../wiki/API-Dokumentation)** - Alle Endpunkte
- **[Datenbank-Schema](../../wiki/Datenbank-Schema)** - Modelle und Beziehungen
- **[Entwicklung](../../wiki/Entwicklung)** - Entwicklungsumgebung einrichten

### Deployment & Wartung
- **[Deployment](../../wiki/Deployment)** - Produktions-Deployment
- **[Sicherheit](../../wiki/Sicherheit)** - Sicherheits-Best-Practices
- **[Troubleshooting](../../wiki/Troubleshooting)** - Häufige Probleme lösen
- **[Upgrade-Guide](../../wiki/Upgrade-Guide)** - Von v1.x auf v2.0.0 upgraden

---

## 🛠 Technologie-Stack

- **Backend**: Flask, SQLAlchemy, Gunicorn
- **Frontend**: Vanilla JavaScript, HTML5, CSS3
- **Datenbank**: SQLite (PostgreSQL/MySQL unterstützt)
- **Sicherheit**: Flask-WTF, Flask-Talisman, Flask-Limiter
- **Integrationen**: WebUntis, PyWebPush

---

## 📋 Systemanforderungen

- Python 3.8+
- 500 MB freier Speicherplatz
- Moderne Browser (Chrome, Firefox, Safari, Edge)
- Optional: Docker & Docker Compose

---

## 🔧 Konfiguration

Erstelle eine `.env` Datei:

```env
SECRET_KEY=dein-geheimer-schluessel
DATABASE_URL=sqlite:///instance/l8testudy.db
FLASK_ENV=production
UNTIS_FERNET_KEY=dein-32-byte-base64-key
```

Mehr Details: **[Konfiguration Wiki](../../wiki/Konfiguration)**

---

## 📝 Changelog

Siehe [CHANGELOG.md](CHANGELOG.md) für alle Änderungen.

**Version 2.0.0** - Erste vollständige Production-Release
- WebUntis Integration
- Chat-System
- Push-Benachrichtigungen
- Klassenübergreifendes Teilen
- Und vieles mehr...

---

## 🆘 Support

- **Dokumentation**: [Wiki](../../wiki)
- **Probleme**: [Issues](../../issues)
- **Changelog**: [CHANGELOG.md](CHANGELOG.md)
- **Upgrade**: [UPGRADE.md](UPGRADE.md)

---

## 📄 Lizenz

Dieses Projekt ist proprietär. Alle Rechte vorbehalten.

---

**L8teStudy v2.0.0** - Moderne Lernplattform für Schulen 🎓
