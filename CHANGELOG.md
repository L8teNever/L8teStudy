# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/lang/de/).


## [1.2.0] - 2026-01-28

### 🎉 Hinzugefügt

- **Lernkarten (Flashcards)**: Vollständiges System zum Erstellen und Lernen von Lernkarten.
  - **Decks**: Erstellen von persönlichen Stapeln und Zugriff auf öffentliche Stapel.
  - **Lernmodus**: Interaktiver Lernmodus mit SM-2 Algorithmus (Spaced Repetition).
  - **Kartenverwaltung**: Einfaches Hinzufügen und Löschen von Karten.
  - **Fortschrittsverfolgung**: Intelligente Wiedervorlage basierend auf Lernerfolg (Nochmal, Schwer, Gut, Einfach).

## [2.0.4] - 2026-01-16

### 🎉 Hinzugefügt

- **Gewichtungs-Eingabefeld für Noten**: Beim Erstellen oder Bearbeiten von Noten kann jetzt die Gewichtung (z.B. 1.0 = 100%, 0.5 = 50%, 2.0 = 200%) angegeben werden
- **Gewichtete Durchschnittsberechnung**: Der Notendurchschnitt wird jetzt korrekt gewichtet berechnet basierend auf den individuellen Gewichtungen
- **Gewichts-Anzeige**: Das Gewicht wird in der Notenliste und in der Details-Ansicht angezeigt

### 🔄 Geändert

- **Backend**: `update_grade()` Route akzeptiert jetzt das `weight` Feld
- **Frontend**: Formular für Noten enthält jetzt ein Gewichtungs-Eingabefeld mit Standardwert 1.0

## [2.0.0] - 2026-01-12

### 🎉 Hinzugefügt

#### Hauptfunktionen
- **WebUntis Integration**: Vollständige Integration mit automatischem Stundenplan-Import
- **Aufgaben-Chat-System**: Echtzeit-Chat für jede Aufgabe mit Bild- und Dateianhängen
- **Push-Benachrichtigungen**: Browser-Push mit konfigurierbaren Erinnerungen
- **Klassenübergreifendes Teilen**: Aufgaben und Termine können zwischen Klassen geteilt werden
- **Tutorial-System**: Interaktives Tutorial für neue Benutzer
- **Mehrsprachigkeit**: Unterstützung für 6 Sprachen (DE, EN, FR, ES, IT, TR)
- **Progressive Web App**: Installierbar auf allen Geräten mit Offline-Support

#### Benutzerverwaltung
- **Rollenbasiertes System**: Drei Rollen (Student, Admin, Super Admin)
- **Klassenbasierte Organisation**: Benutzer sind Klassen zugeordnet
- **Erzwungener Passwortwechsel**: Neue Benutzer müssen ihr Passwort ändern
- **Passwort-Komplexitätsprüfung**: Mindestanforderungen für sichere Passwörter

#### Aufgaben & Termine
- **Individuelle Erledigungsstatus**: Jeder Benutzer kann Aufgaben unabhängig als erledigt markieren
- **Soft-Delete**: Gelöschte Aufgaben/Termine werden archiviert statt permanent gelöscht
- **Bildanhänge**: Mehrere Bilder pro Aufgabe
- **Fachzuordnung**: Aufgaben und Termine können Fächern zugeordnet werden
- **Automatische Fachvorschläge**: Basierend auf aktuellem WebUntis-Unterricht

#### Noten
- **Gewichtete Noten**: Unterschiedliche Gewichtung für verschiedene Notentypen
- **Automatische Durchschnittsberechnung**: Fachspezifisch und gesamt
- **Notenverlauf**: Chronologische Übersicht aller Noten

#### Admin-Funktionen
- **Super Admin Dashboard**: Globale Systemübersicht und Statistiken
- **Klassenverwaltung**: Klassen erstellen, bearbeiten, löschen
- **Globale Fächer**: Fächer können klassenübergreifend definiert werden
- **Audit-Log**: Vollständiges Protokoll aller Benutzeraktionen
- **Backup & Restore**: Datenbank-Export und -Import als JSON

### 🔒 Sicherheit

- **Verschlüsselte WebUntis-Passwörter**: Fernet-Verschlüsselung für gespeicherte Passwörter
- **Content Security Policy**: Strikte CSP-Header zur Verhinderung von XSS
- **HSTS**: HTTP Strict Transport Security in Produktion
- **Rate Limiting**: Schutz vor Brute-Force-Angriffen
- **CSRF-Schutz**: Erweitert für Reverse-Proxy-Umgebungen
- **Sichere Session-Verwaltung**: HttpOnly, Secure, SameSite Cookies
- **Audit-Logging**: Alle sicherheitsrelevanten Aktionen werden protokolliert

### 🏗 Architektur

- **Rollenbasierte Zugriffskontrolle (RBAC)**: Granulare Berechtigungen
- **Many-to-Many Beziehungen**: Fächer können mehreren Klassen zugeordnet werden
- **Junction Tables**: Optimierte Datenbankstruktur für Beziehungen
- **Service Worker**: Offline-Funktionalität und Push-Benachrichtigungen
- **APScheduler**: Hintergrund-Jobs für automatische Benachrichtigungen
- **Flask-Migrate**: Automatische Datenbank-Migrationen

### 🐛 Behoben

- **CSRF-Probleme**: Fehler hinter Reverse Proxies (Nginx, Dockge) behoben
- **Datenbank-Migrationen**: Stabilisiert und in App-Initialisierung integriert
- **Session-Handling**: Verbesserte Session-Verwaltung und Cookie-Sicherheit
- **Upload-Pfade**: Korrekte Pfadauflösung für Datei-Uploads
- **WebUntis-Fehlerbehandlung**: Robustere Fehlerbehandlung bei API-Fehlern
- **Chat-Nachrichten**: Korrekte Sortierung und Anzeige von Nachrichten
- **Push-Benachrichtigungen**: Zuverlässigere Zustellung und Fehlerbehandlung

### 🗑️ Entfernt

- **Legacy-Migrationsskripte**: 
  - `migrate_db.py` (in App-Initialisierung integriert)
  - `migrate_subjects.py` (in App-Initialisierung integriert)
  - `migrate_uploads.py` (nicht mehr benötigt)
  - `fix_schema.py` (durch Flask-Migrate ersetzt)
- **Backup-Dateien**:
  - `static/translations.js.backup` (nicht mehr benötigt)
  - `SAVE_FUNCTIONS_FIX.js` (Fix wurde integriert)
- **Docker-Compose-Varianten**:
  - `docker-compose.local.yml` (konsolidiert)
  - `docker-compose.github.yml` (konsolidiert)
  - `docker-compose.dockerhub.yml` (konsolidiert)
- **Alte Spalten**: `is_admin`, `is_super_admin` (ersetzt durch `role`)

### 🔄 Geändert

- **Versionierung**: Von 1.1.x auf 2.0.0 (Major Release)
- **Datenbank-Schema**: Optimiert für bessere Performance und Skalierbarkeit
- **API-Struktur**: Konsistentere Endpunkt-Benennung
- **Fehlerbehandlung**: Verbesserte Fehlermeldungen und Logging
- **Dokumentation**: Vollständige README.md mit allen Details

### 📚 Dokumentation

- **README.md**: Umfassende Dokumentation mit:
  - Detaillierte Feature-Beschreibungen
  - Installations- und Konfigurationsanleitungen
  - API-Dokumentation
  - Sicherheits-Best-Practices
  - Troubleshooting-Guide
  - Deployment-Anleitungen
- **CHANGELOG.md**: Diese Datei für Versionsverwaltung
- **Code-Kommentare**: Verbesserte Inline-Dokumentation

### 🔧 Technische Details

#### Abhängigkeiten
- Flask 3.x
- SQLAlchemy 2.x
- Flask-Login 0.6.x
- Flask-Migrate 4.x
- WebUntis API Client
- Cryptography (Fernet)
- PyWebPush
- APScheduler

#### Datenbank-Änderungen
- Neue Tabellen: `TaskMessage`, `TaskChatRead`, `UntisCredential`, `GlobalSetting`
- Neue Spalten: `role`, `parent_id`, `notify_chat_message`, `chat_enabled`
- Junction Table: `subject_classes` für Many-to-Many Beziehungen
- Indizes für bessere Query-Performance

#### API-Änderungen
- Neue Endpunkte: `/api/tasks/<id>/messages`, `/api/untis/*`, `/api/backup/*`
- Erweiterte Endpunkte: `/api/tasks`, `/api/events` mit Sharing-Support
- Verbesserte Fehler-Responses mit detaillierten Meldungen

---

## [1.1.x] - 2025-2026

### Entwicklungsversionen
- Kontinuierliche Verbesserungen und Bugfixes
- Experimentelle Features
- Interne Releases

---

## Versionsschema

**MAJOR.MINOR.PATCH** (Semantic Versioning)

- **MAJOR**: Inkompatible API-Änderungen
- **MINOR**: Neue Funktionen (abwärtskompatibel)
- **PATCH**: Bugfixes (abwärtskompatibel)

---

## Upgrade-Hinweise

### Von 1.1.x auf 2.0.0

1. **Backup erstellen**: Vor dem Update unbedingt ein Backup der Datenbank erstellen
2. **Umgebungsvariablen prüfen**: `UNTIS_FERNET_KEY` sollte gesetzt sein
3. **Datenbank-Migration**: Wird automatisch beim Start durchgeführt
4. **Benutzerrollen**: Alte `is_admin`/`is_super_admin` werden automatisch migriert
5. **WebUntis**: Zugangsdaten müssen neu eingegeben werden (werden verschlüsselt)
6. **Push-Benachrichtigungen**: Benutzer müssen sich neu anmelden

### Breaking Changes

- **API**: Einige Endpunkte haben neue Response-Formate
- **Datenbank**: Schema-Änderungen (automatisch migriert)
- **Konfiguration**: Neue Umgebungsvariablen erforderlich
- **Docker**: Neue Volume-Struktur für persistente Daten

---

## Support

Bei Problemen oder Fragen:
- Siehe [README.md](README.md) für Troubleshooting
- Erstelle ein Issue im Repository
- Kontaktiere den Administrator

---

**L8teStudy** - Moderne Lernplattform für Schulen 🎓
