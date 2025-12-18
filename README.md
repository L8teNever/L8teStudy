# 📋 L8teStudy

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

### Option 2: Docker

Voraussetzung: Docker Desktop ist installiert und läuft.

1.  **Container starten**:
    ```powershell
    docker-compose up -d --build
    ```
2.  Öffne [http://localhost:5000](http://localhost:5000) im Browser.

## 🔐 Login

Das System ist geschlossen. Standard-Login:

*   **Benutzername**: `admin`
*   **Passwort**: `secret`

> **Hinweis**: Neue Benutzer können über das Skript `create_admin.py` erstellt werden:
> `python create_admin.py wunschname wunschpasswort`

## 📱 Als App installieren

1.  Öffne die Seite auf deinem Smartphone oder Tablet (Chromium-Browser empfohlen für Android, Safari für iOS).
2.  Wähle im Menü "Zum Startbildschirm hinzufügen" oder "Installieren".
