# 📋 L8teStudy v1.1.25

Eine minimalistische, offline-fähige Schul-Organisations-App im iOS-Design.

## 🌟 Features

*   **Offline-First**: Funktioniert auch ohne Internetverbindung (Lesemodus).
*   **Minimalistisches Design**: Angelehnt an modernste Apple iOS UI (Glassmorphism, Snappy Animations).
*   **Organisation**:
    *   **Dashboard**: Überblick über den Tag, nächste Termine und fällige Aufgaben.
    *   **Aufgaben**: Verwalten von Hausaufgaben (Offen/Erledigt).
    *   **Plan**: Kalender für Termine und Klausuren (Monats- und Listenansicht).
    *   **Noten**: Notenverwaltung mit Gewichtung und Durchschnittsberechnung.
*   **Technologie**: PWA (Progressive Web App) - installierbar auf Mobilgeräten.

## 🛠 Tech Stack

*   **Backend**: Python (Flask), SQLAlchemy, SQLite.
*   **Frontend**: Vanilla HTML5, CSS3, JavaScript (keine Frameworks).
*   **PWA**: Service Worker für Caching.

## 🚀 Installation & Start

### Option 1: Lokal (Python)

Voraussetzung: Python 3.9+ ist installiert.

1.  **Repository klonen** (oder Dateien herunterladen).
2.  **Virtuelle Umgebung erstellen & aktivieren**:
    ```powershell
    python -m venv venv
    .\venv\Scripts\activate
    ```
3.  **Abhängigkeiten installieren**:
    ```powershell
    pip install -r requirements.txt
    ```
4.  **App starten**:
    ```powershell
    python run.py
    ```
5.  Öffne [http://localhost:5000](http://localhost:5000) im Browser.

### Option 2: Docker (Manuell)

Voraussetzung: Docker Desktop ist installiert und läuft.

1.  **Repository klonen** und in den Ordner wechseln.
2.  **Container starten**:
    ```powershell
    docker-compose up -d --build
    ```
3.  Öffne [http://localhost:5000](http://localhost:5000) im Browser.

> **Daten-Sicherheit**: Deine Datenbank und hochgeladenen Bilder werden in den Ordnern `./instance` und `./static/uploads` auf deinem PC gespeichert. Sie gehen bei einem Update nicht verloren.

### Option 3: Deployment Tools (Dockge / Portainer) 🚀

Perfekt für Homeserver oder einfache Updates.

1.  Erstelle einen neuen Stack in Dockge oder Portainer.
2.  Kopiere den Inhalt der `docker-compose.github.yml` (siehe Repo) oder nutze diesen:
    ```yaml
    services:
      l8testudy:
        build: https://github.com/L8teNever/L8teStudy.git#main
        container_name: l8testudy
        ports:
          - "5000:5000"
        volumes:
          - ./data:/data
          - ./uploads:/app/static/uploads
        environment:
          - DATABASE_URL=sqlite:////data/l8testudy.db
          - SECRET_KEY=ein-sicheres-passwort-hier-einfuegen
        restart: always
    ```
3.  Starte den Stack. Der Container wird **direkt von GitHub** gebaut.
4.  Für Updates einfach im Tool auf "Update" / "Rebuild" klicken.

> **Automatische Datenbank-Initialisierung**: Die Datenbank und alle benötigten Tabellen werden beim ersten Start automatisch erstellt. Du musst nichts manuell einrichten!

> **Automatische Migration**: Bei Updates werden neue Datenbank-Tabellen automatisch hinzugefügt. Deine Daten bleiben erhalten!

> **Standard-Admin-Account**: Beim ersten Start wird automatisch ein Admin-Account erstellt:
> - **Benutzername**: `admin`
> - **Passwort**: `admin`
> - ⚠️ **WICHTIG**: Ändere dieses Passwort sofort nach dem ersten Login in den Einstellungen!

### 🔄 Nach einem Update

Wenn du nach einem Update Probleme hast (z.B. 400 Fehler):
1. Container neu starten - die Migration läuft automatisch
2. Falls das nicht hilft: Siehe [MIGRATION.md](MIGRATION.md) für detaillierte Anweisungen


## ⚙️ Konfiguration

Erstelle optional eine `.env` Datei (bei lokaler Nutzung) oder setze Umgebungsvariablen in Docker:

*   `SECRET_KEY`: Ein zufälliger Schlüssel zur Absicherung von Sessions (WICHTIG für Produktion!).
*   `DATABASE_URL`: Pfad zur Datenbank (Standard: SQLite).

## 🔐 Login

Das System ist geschlossen. Du musst erst einen Benutzer erstellen.

### Benutzer erstellen

**Option A: Lokal (Python)**
```powershell
python create_admin.py DeinName DeinPasswort
```

**Option B: Docker (laufender Container)**
```powershell
docker compose exec web python create_admin.py DeinName "DeinPasswort!"
```
*(Hinweis: Bei Sonderzeichen das Passwort in Anführungszeichen setzen!)*

**Option C: Dockge / Portainer**
Öffne die Konsole des Containers ("Exec" oder ">_") und tippe:
```bash
python create_admin.py DeinName DeinPasswort
```
> **Wichtig**: Wenn du die GitHub-Version nutzt, heißt der Service evtl. `l8testudy` statt `web`. 
> Befehl dann: `docker compose exec l8testudy python create_admin.py ...`

## 📱 Als App installieren

1.  Öffne die Seite auf deinem Smartphone oder Tablet (Chromium-Browser empfohlen für Android, Safari für iOS).
2.  Wähle im Menü "Zum Startbildschirm hinzufügen" oder "Installieren".
