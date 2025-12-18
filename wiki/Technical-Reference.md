# ⚙️ Technische Referenz

Für Entwickler und Neugierige: Hier wird erklärt, wie L8teStudy "unter der Haube" funktioniert.

## 🏗️ Projektstruktur
```text
L8teStudy/
├── app/                # Backend-Logik (Flask)
│   ├── routes.py       # API-Endpunkte & Seiten-Routing
│   ├── models.py       # Datenbank-Modelle (SQLAlchemy)
│   └── static/         # Backend-spezifische statische Dateien
├── static/             # Frontend-Assets
│   ├── sw.js           # Service Worker (PWA-Logik)
│   └── uploads/        # Hochgeladene Bilder
├── templates/          # HTML-Templates (Jinja2)
├── run.py              # Start-Script
└── Dockerfile          # Container-Konfiguration
```

---

## 🔢 Automatisches Versionierungssystem
L8teStudy nutzt ein intelligentes System, um die Version im Account-Hub aktuell zu halten.

### Wie es funktioniert:
In `app/__init__.py` wird die Funktion `inject_version` aufgerufen:
1.  **Git-Check**: Die App fragt `git rev-list --count HEAD` ab. Das Ergebnis ist die Anzahl der Commits.
2.  **Format**: Die Version wird als `1.1.<Commit-Anzahl>` formatiert.
3.  **Fallback**: Falls kein `.git`-Ordner existiert (z.B. in einem produktiven Docker-Container), sucht die App nach einer `version.txt` im Hauptverzeichnis. Findet sie diese auch nicht, wird standardmäßig `1.1.0` angezeigt.

---

## 🛠️ Technologie-Stack
- **Flask**: Leichtgewichtiges Web-Framework für Python.
- **Flask-SQLAlchemy**: ORM zur einfachen Datenbank-Interaktion.
- **Flask-WTF & CSRFProtect**: Schutz vor Cross-Site Request Forgery.
- **Flask-Talisman**: Setzt Sicherheits-Header (CSP, HSTS).
- **Lucide Icons**: Schicke, konsistente SVG-Icons im Frontend.
- **Pure JavaScript**: Keine schweren Bibliotheken wie React oder Vue – für maximale Geschwindigkeit und Kompatibilität.

---

## 🔒 Sicherheit
- **Passwort-Hashing**: Alle Passwörter werden mit `pbkdf2:sha256` verschlüsselt in der Datenbank gespeichert – niemals im Klartext.
- **CSRF-Token**: Jede POST-Anfrage im Frontend wird durch ein fälschungssicheres Token abgesichert.
- **Rate-Limiting**: Das System schützt sich selbst vor Brute-Force-Angriffen durch `Flask-Limiter`.
