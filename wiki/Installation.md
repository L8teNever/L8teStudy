# 🚀 Installation & Setup

L8teStudy kann auf verschiedene Arten betrieben werden. Hier findest du die detaillierte Anleitung für jede Methode.

## 🐍 1. Lokale Installation (Python)

Diese Methode eignet sich am besten für die Entwicklung oder wenn du die App direkt auf deinem PC nutzen möchtest.

### Voraussetzungen
- Python 3.9 oder höher
- Git (optional, für automatische Versionierung empfohlen)

### Schritte
1.  **Repository klonen**:
    ```bash
    git clone https://github.com/L8teNever/L8teStudy.git
    cd L8teStudy
    ```
2.  **Virtuelle Umgebung erstellen**:
    ```bash
    python -m venv venv
    ```
3.  **Umgebung aktivieren**:
    - *Windows*: `.\venv\Scripts\activate`
    - *Mac/Linux*: `source venv/bin/activate`
4.  **Abhängigkeiten installieren**:
    ```bash
    pip install -r requirements.txt
    ```
5.  **App starten**:
    ```bash
    python run.py
    ```
    Die App ist nun unter `http://localhost:5000` erreichbar.

---

## 🐳 2. Setup mit Docker

Docker ist die empfohlene Methode für den dauerhaften Betrieb (z.B. auf einem NAS oder Homeserver).

### Mit Docker Compose
1.  Stelle sicher, dass `docker-compose.yml` vorhanden ist.
2.  Starte den Container:
    ```bash
    docker-compose up -d --build
    ```

### Umgebungsvariablen (.env)
Du kannst das Verhalten der App über Umgebungsvariablen steuern:
| Variable | Beschreibung | Standard |
| :--- | :--- | :--- |
| `SECRET_KEY` | Schlüssel für verschlüsselte Sessions | `dev-secret-key` |
| `DATABASE_URL` | Verbindung zur Datenbank | `sqlite:///instance/l8testudy.db` |
| `FLASK_ENV` | Modus (production/development) | `development` |

---

## 🏗️ 3. Deployment auf Homeservern (Portainer/Dockge)

Wenn du Tools wie Portainer oder Dockge nutzt, kannst du L8teStudy direkt von GitHub bauen lassen. Nutze dazu die `docker-compose.github.yml`:

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
      - SECRET_KEY=dein_geheimer_schlüssel
    restart: always
```

---

## 🔐 Erster Login
Nach der Installation ist die Datenbank leer. Du musst einen Administrator-Account erstellen, um dich einloggen zu können:

**Lokal:**
```bash
python create_admin.py DeinNutzername DeinPasswort
```

**In Docker:**
```bash
docker exec -it l8testudy python create_admin.py DeinNutzername DeinPasswort
```
