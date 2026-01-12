# Troubleshooting

Lösungen für häufige Probleme mit L8teStudy.

---

## 🔐 Login & Authentifizierung

### "Ungültige Zugangsdaten"

**Problem**: Login schlägt fehl.

**Lösungen**:
1. **Klassencode prüfen**: Ist der Code korrekt?
2. **Benutzername prüfen**: Groß-/Kleinschreibung beachten
3. **Passwort prüfen**: Caps Lock aktiviert?
4. **Admin fragen**: Wurde der Benutzer erstellt?

**Als Admin prüfen**:
```bash
# Super Admin erstellen falls vergessen
python create_admin.py admin NeuesPasswort superadmin
```

---

### "CSRF Token Missing or Invalid"

**Problem**: Formular-Submission schlägt fehl.

**Ursachen**:
- Session abgelaufen
- Cookies blockiert
- Reverse Proxy-Problem

**Lösungen**:

1. **Seite neu laden**: `F5` oder `Ctrl+R`

2. **Cookies aktivieren**: Browser-Einstellungen prüfen

3. **Reverse Proxy**: In `.env` hinzufügen:
```env
WTF_CSRF_SSL_STRICT=False
```

4. **Session-Cookie prüfen**: Developer Tools → Application → Cookies

---

### Session läuft ständig ab

**Problem**: Benutzer wird immer wieder ausgeloggt.

**Lösungen**:

1. **Browser-Cookies**: Cookies von Drittanbietern erlauben

2. **Session-Lifetime erhöhen** (`app/__init__.py`):
```python
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 30  # 30 Tage
```

3. **"Angemeldet bleiben"**: Feature in Login-Seite aktivieren

---

## 💾 Datenbank

### "Database is locked"

**Problem**: SQLite kann nicht mit vielen gleichzeitigen Schreibzugriffen umgehen.

**Lösungen**:

1. **Gunicorn Workers reduzieren**:
```bash
gunicorn -w 2 -b 0.0.0.0:5000 run:app
```

2. **Auf PostgreSQL wechseln**:
```env
DATABASE_URL=postgresql://user:password@localhost/l8testudy
```

3. **Timeout erhöhen** (`app/__init__.py`):
```python
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
    'connect_args': {'timeout': 30}
}
```

---

### "No such table"

**Problem**: Datenbank-Tabelle fehlt.

**Lösungen**:

1. **Datenbank neu erstellen**:
```bash
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

2. **Migration ausführen**:
```bash
flask db upgrade
```

3. **Datenbank löschen und neu erstellen** (ACHTUNG: Datenverlust!):
```bash
rm instance/l8testudy.db
python run.py  # Erstellt DB automatisch
```

---

### Migration schlägt fehl

**Problem**: `flask db upgrade` funktioniert nicht.

**Lösungen**:

1. **Backup wiederherstellen**:
```bash
cp instance/l8testudy.db.backup instance/l8testudy.db
```

2. **Migration zurücksetzen**:
```bash
flask db downgrade
flask db upgrade
```

3. **Migrations-Ordner löschen** (Neustart):
```bash
rm -rf migrations/
flask db init
flask db migrate -m "Initial migration"
flask db upgrade
```

---

## 📁 Datei-Uploads

### Bilder werden nicht angezeigt

**Problem**: Hochgeladene Bilder sind nicht sichtbar.

**Lösungen**:

1. **Upload-Ordner prüfen**:
```bash
ls -la instance/uploads/
```

2. **Berechtigungen setzen**:
```bash
chmod 755 instance/uploads/
```

3. **Docker**: Volume korrekt gemountet?
```yaml
volumes:
  - l8testudy-data:/app/instance
```

4. **Pfad in `.env` prüfen**:
```env
UPLOAD_FOLDER=instance/uploads
```

---

### "File too large"

**Problem**: Datei-Upload schlägt fehl.

**Lösungen**:

1. **Max Upload Size erhöhen** (`app/__init__.py`):
```python
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16 MB
```

2. **Nginx**: Upload-Limit erhöhen:
```nginx
client_max_body_size 16M;
```

3. **Datei komprimieren**: Vor dem Upload verkleinern

---

## 🔔 Push-Benachrichtigungen

### Push funktioniert nicht

**Problem**: Keine Benachrichtigungen erhalten.

**Lösungen**:

1. **HTTPS erforderlich**: Push funktioniert nur über HTTPS (außer localhost)

2. **Browser-Berechtigung**: Wurde die Berechtigung erteilt?
   - Chrome: `chrome://settings/content/notifications`
   - Firefox: `about:preferences#privacy`

3. **Service Worker prüfen**:
   - Developer Tools → Application → Service Workers
   - Sollte "activated and running" sein

4. **Subscription prüfen**:
```javascript
// In Browser-Console
navigator.serviceWorker.ready.then(reg => {
  reg.pushManager.getSubscription().then(sub => {
    console.log(sub);
  });
});
```

5. **Scheduler läuft?**: Logs prüfen für "Notification Scheduler Started"

---

### "Push subscription failed"

**Problem**: Abonnement schlägt fehl.

**Lösungen**:

1. **VAPID-Keys generieren**:
```python
from pywebpush import webpush
print(webpush.generate_vapid_keys())
```

2. **Service Worker neu registrieren**:
   - Developer Tools → Application → Service Workers
   - "Unregister" → Seite neu laden

3. **Browser-Cache leeren**: `Ctrl+Shift+Delete`

---

## 🕐 WebUntis

### Stundenplan lädt nicht

**Problem**: WebUntis-Integration funktioniert nicht.

**Lösungen**:

1. **Zugangsdaten prüfen**:
   - In WebUntis-Portal testen
   - Server ohne `https://` (z.B. `mese.webuntis.com`)
   - Schulname korrekt?

2. **Firewall**: Ausgehende Verbindungen zu WebUntis erlauben

3. **Logs prüfen**:
```bash
# Lokale Installation
python run.py  # Fehler im Terminal

# Docker
docker-compose logs -f
```

4. **Passwort neu eingeben**: Wegen Verschlüsselung

---

### "Invalid credentials" (WebUntis)

**Problem**: WebUntis-Login schlägt fehl.

**Lösungen**:

1. **Zugangsdaten testen**: Direkt auf WebUntis-Website einloggen

2. **Klassenname**: Exakt wie in WebUntis (z.B. "10a" nicht "10A")

3. **Passwort-Sonderzeichen**: Manche Zeichen können Probleme machen

4. **Neu konfigurieren**: Zugangsdaten komplett neu eingeben

---

## 🌐 Netzwerk & Server

### "Address already in use"

**Problem**: Port ist bereits belegt.

**Lösungen**:

1. **Anderen Port verwenden**:
```bash
python run.py --port 5001
gunicorn -b 0.0.0.0:5001 run:app
```

2. **Prozess beenden**:
```bash
# Linux/Mac
lsof -ti:5000 | xargs kill -9

# Windows
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

---

### "Connection refused"

**Problem**: Server nicht erreichbar.

**Lösungen**:

1. **Server läuft?**: Prozess prüfen

2. **Firewall**: Port 5000 öffnen

3. **Bind-Adresse**: `0.0.0.0` statt `127.0.0.1`
```bash
gunicorn -b 0.0.0.0:5000 run:app
```

4. **Docker**: Port-Mapping prüfen
```yaml
ports:
  - "5000:5000"
```

---

### Langsame Performance

**Problem**: App reagiert langsam.

**Lösungen**:

1. **Gunicorn Workers erhöhen**:
```bash
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

2. **PostgreSQL statt SQLite**: Für größere Installationen

3. **Caching aktivieren**: Redis für Sessions

4. **Logs prüfen**: Langsame Queries identifizieren

5. **Server-Ressourcen**: RAM und CPU prüfen

---

## 🐳 Docker

### Container startet nicht

**Problem**: `docker-compose up` schlägt fehl.

**Lösungen**:

1. **Logs prüfen**:
```bash
docker-compose logs
```

2. **Image neu bauen**:
```bash
docker-compose build --no-cache
docker-compose up -d
```

3. **Volumes löschen** (ACHTUNG: Datenverlust!):
```bash
docker-compose down -v
docker-compose up -d
```

4. **Berechtigungen**: Docker-Daemon läuft?

---

### Volume-Daten gehen verloren

**Problem**: Nach Container-Neustart sind Daten weg.

**Lösungen**:

1. **Named Volume verwenden**:
```yaml
volumes:
  - l8testudy-data:/app/instance
```

2. **Volume prüfen**:
```bash
docker volume ls
docker volume inspect l8testudy-data
```

3. **Backup erstellen**:
```bash
docker run --rm -v l8testudy-data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data
```

---

## 🔧 Allgemeine Probleme

### "ModuleNotFoundError"

**Problem**: Python-Modul nicht gefunden.

**Lösungen**:

1. **Dependencies installieren**:
```bash
pip install -r requirements.txt
```

2. **Virtuelle Umgebung aktiviert?**:
```bash
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. **Python-Version**: Mindestens 3.8 erforderlich
```bash
python --version
```

---

### App lädt nicht / Weißer Bildschirm

**Problem**: Frontend zeigt nichts an.

**Lösungen**:

1. **Browser-Console**: `F12` → Console → Fehler prüfen

2. **JavaScript-Fehler**: Meist in `index.html`

3. **Cache leeren**: `Ctrl+Shift+Delete`

4. **Service Worker**: Deaktivieren und neu laden

5. **Kompatibilität**: Modernen Browser verwenden

---

### Übersetzungen fehlen

**Problem**: Texte werden als Keys angezeigt (z.B. "task_title").

**Lösungen**:

1. **translations.js prüfen**: Datei vorhanden?

2. **Sprache wechseln**: Einstellungen → Sprache

3. **Cache leeren**: Browser-Cache löschen

4. **Key hinzufügen** (`static/translations.js`):
```javascript
de: {
  task_title: "Aufgabe"
}
```

---

## 🆘 Weitere Hilfe

### Debug-Modus aktivieren

```env
FLASK_ENV=development
FLASK_DEBUG=1
```

**Dann**: Detaillierte Fehlermeldungen im Browser

**WARNUNG**: Niemals in Produktion verwenden!

---

### Logs sammeln

**Lokale Installation**:
```bash
python run.py > app.log 2>&1
```

**Docker**:
```bash
docker-compose logs > docker.log
```

**Gunicorn**:
```bash
gunicorn --log-file=gunicorn.log --log-level=debug run:app
```

---

### Datenbank-Backup erstellen

**Vor Troubleshooting immer Backup erstellen!**

```bash
# SQLite
cp instance/l8testudy.db instance/l8testudy.db.backup

# Oder über App
# Admin → Superadmin Dashboard → Backup & Restore → Export
```

---

### Support kontaktieren

Wenn nichts hilft:

1. **GitHub Issue erstellen**: Mit Logs und Fehlermeldungen
2. **Admin kontaktieren**: Bei Installation-spezifischen Problemen
3. **Dokumentation prüfen**: [Wiki](Home) durchsuchen

---

## 📚 Verwandte Seiten

- **[Installation](Installation)** - Neuinstallation
- **[Konfiguration](Konfiguration)** - Einstellungen prüfen
- **[Upgrade-Guide](Upgrade-Guide)** - Update-Probleme
- **[Sicherheit](Sicherheit)** - Sicherheitsprobleme

---

**Problem gelöst?** 🎉 Zurück zur [Startseite](Home) →
