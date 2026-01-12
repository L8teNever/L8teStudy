# Entwicklung

Anleitung für Entwickler zur Einrichtung der Entwicklungsumgebung.

---

## 🛠 Entwicklungsumgebung einrichten

### Voraussetzungen

- Python 3.8+
- Git
- Code-Editor (VS Code, PyCharm, etc.)

### Setup

```bash
# Repository klonen
git clone <repo-url>
cd L8teStudy-4

# Virtuelle Umgebung
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

# Dependencies
pip install -r requirements.txt

# Datenbank erstellen
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"

# Admin erstellen
python create_admin.py admin test superadmin

# Entwicklungsserver
python run.py
```

---

## 🔧 Konfiguration

### .env für Entwicklung

```env
SECRET_KEY=dev-secret-key-only-for-testing
DATABASE_URL=sqlite:///instance/l8testudy_dev.db
FLASK_ENV=development
FLASK_DEBUG=1
```

---

## 📝 Code-Struktur

Siehe [Architektur](Architektur) für Details.

**Wichtigste Dateien**:
- `app/__init__.py` - App Factory
- `app/models.py` - Datenmodelle
- `app/routes.py` - API-Endpunkte
- `templates/index.html` - Frontend SPA

---

## 🔄 Datenbank-Migrationen

```bash
# Migration erstellen
flask db migrate -m "Beschreibung"

# Migration anwenden
flask db upgrade

# Migration rückgängig
flask db downgrade
```

---

## 🧪 Testing

```bash
# Alle Tests
python test_everything.py

# Einzelne Funktionen testen
python -m pytest tests/
```

---

## 📚 Weitere Ressourcen

- [Architektur](Architektur)
- [API-Dokumentation](API-Dokumentation)
- [Datenbank-Schema](Datenbank-Schema)

---
