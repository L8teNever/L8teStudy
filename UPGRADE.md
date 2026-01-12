# Upgrade auf v2.0.0

Dieser Guide hilft dir beim Upgrade von L8teStudy 1.x auf 2.0.0.

## ⚠️ Wichtig: Vor dem Upgrade

### 1. Backup erstellen

**WICHTIG**: Erstelle unbedingt ein Backup deiner Datenbank!

```bash
# Als Super Admin in der App einloggen
# Admin → Superadmin Dashboard → Backup & Restore
# "Daten exportieren" klicken und JSON-Datei speichern

# Oder manuell:
cp instance/l8testudy.db instance/l8testudy.db.backup
```

### 2. Systemanforderungen prüfen

- Python 3.8 oder höher
- Genügend Speicherplatz (mindestens 500 MB frei)
- Backup der aktuellen Installation

## 🚀 Upgrade-Schritte

### Lokale Installation

1. **Code aktualisieren**
```bash
git pull origin main
# Oder: Neue Version herunterladen und entpacken
```

2. **Dependencies aktualisieren**
```bash
pip install -r requirements.txt --upgrade
```

3. **Datenbank migrieren**
```bash
# Die Migration erfolgt automatisch beim nächsten Start
# Oder manuell:
flask db upgrade
```

4. **Umgebungsvariablen prüfen**

Erstelle/aktualisiere deine `.env` Datei:
```env
SECRET_KEY=dein-geheimer-schluessel
DATABASE_URL=sqlite:///instance/l8testudy.db
FLASK_ENV=production
UNTIS_FERNET_KEY=dein-32-byte-base64-key
```

**UNTIS_FERNET_KEY generieren** (falls nicht vorhanden):
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

5. **Anwendung neu starten**
```bash
# Entwicklung
python run.py

# Produktion
gunicorn -w 4 -b 0.0.0.0:5000 run:app
```

### Docker Installation

1. **Container stoppen**
```bash
docker-compose down
```

2. **Backup erstellen**
```bash
# Volume sichern
docker run --rm -v l8testudy-data:/data -v $(pwd):/backup alpine tar czf /backup/l8testudy-backup.tar.gz /data
```

3. **Neue Version pullen**
```bash
git pull origin main
# Oder: docker-compose.yml aktualisieren
```

4. **Image neu bauen**
```bash
docker-compose build
```

5. **Container starten**
```bash
docker-compose up -d
```

6. **Logs prüfen**
```bash
docker-compose logs -f
```

## 🔄 Automatische Migrationen

Beim ersten Start von v2.0.0 werden folgende Migrationen automatisch durchgeführt:

1. **Benutzerrollen**: `is_admin` und `is_super_admin` → `role`
2. **Neue Tabellen**: `TaskMessage`, `TaskChatRead`, `UntisCredential`, `GlobalSetting`
3. **Neue Spalten**: `chat_enabled`, `parent_id`, `notify_chat_message`
4. **Junction Table**: `subject_classes` für Many-to-Many Beziehungen

## ⚙️ Nach dem Upgrade

### 1. WebUntis neu konfigurieren

Da Passwörter jetzt verschlüsselt werden, müssen WebUntis-Zugangsdaten neu eingegeben werden:

1. Als Admin einloggen
2. Admin Center → Klassen-Einstellungen
3. WebUntis-Daten neu eingeben

### 2. Push-Benachrichtigungen neu aktivieren

Benutzer müssen sich für Push-Benachrichtigungen neu anmelden:

1. Einstellungen → Benachrichtigungen
2. "Push erlauben" klicken
3. Browser-Berechtigung erteilen

### 3. Tutorial für neue Benutzer

Neue Benutzer sehen beim ersten Login ein Tutorial. Bestehende Benutzer können es in den Einstellungen zurücksetzen.

## 🐛 Troubleshooting

### "Database is locked"

**Problem**: SQLite kann nicht mit vielen gleichzeitigen Schreibzugriffen umgehen.

**Lösung**:
```bash
# Gunicorn Workers reduzieren
gunicorn -w 2 -b 0.0.0.0:5000 run:app

# Oder auf PostgreSQL wechseln
```

### "CSRF Token Missing"

**Problem**: CSRF-Token fehlt oder ist ungültig.

**Lösung**:
```env
# In .env hinzufügen
WTF_CSRF_SSL_STRICT=False
```

### "Migration failed"

**Problem**: Datenbank-Migration ist fehlgeschlagen.

**Lösung**:
```bash
# Backup wiederherstellen
cp instance/l8testudy.db.backup instance/l8testudy.db

# Oder: Datenbank neu erstellen (ACHTUNG: Datenverlust!)
rm instance/l8testudy.db
python -c "from app import create_app, db; app = create_app(); app.app_context().push(); db.create_all()"
```

### WebUntis funktioniert nicht

**Problem**: Stundenplan lädt nicht.

**Lösung**:
1. Zugangsdaten in WebUntis-Portal testen
2. Server-URL prüfen (ohne `https://`)
3. Firewall-Regeln prüfen
4. Logs prüfen: `docker-compose logs -f` oder Terminal-Output

## 📊 Neue Features nutzen

### Aufgaben-Chat

1. Aufgabe öffnen
2. Chat-Symbol klicken
3. Nachrichten schreiben oder Bilder hochladen

### Klassenübergreifendes Teilen

1. Aufgabe/Termin erstellen
2. "Geteilt" aktivieren
3. Alle Klassen mit dem Fach sehen den Inhalt

### Backup & Restore

1. Als Super Admin einloggen
2. Superadmin Dashboard → Backup & Restore
3. "Daten exportieren" für Backup
4. "Daten importieren" für Restore (ACHTUNG: Überschreibt alles!)

## 🔙 Rollback

Falls Probleme auftreten, kannst du zur vorherigen Version zurückkehren:

### Lokale Installation

```bash
# Backup wiederherstellen
cp instance/l8testudy.db.backup instance/l8testudy.db

# Alte Version auschecken
git checkout v1.1.170  # Oder deine letzte Version

# Dependencies neu installieren
pip install -r requirements.txt

# Starten
python run.py
```

### Docker Installation

```bash
# Container stoppen
docker-compose down

# Backup wiederherstellen
docker run --rm -v l8testudy-data:/data -v $(pwd):/backup alpine tar xzf /backup/l8testudy-backup.tar.gz -C /

# Alte Version verwenden
git checkout v1.1.170
docker-compose build
docker-compose up -d
```

## 📞 Support

Bei Problemen:
- Siehe [README.md](README.md) → Troubleshooting
- Siehe [CHANGELOG.md](CHANGELOG.md) für alle Änderungen
- Erstelle ein Issue im Repository
- Kontaktiere den Administrator

## ✅ Upgrade-Checkliste

- [ ] Backup erstellt
- [ ] Systemanforderungen geprüft
- [ ] Code aktualisiert
- [ ] Dependencies aktualisiert
- [ ] Umgebungsvariablen konfiguriert
- [ ] Anwendung neu gestartet
- [ ] Logs geprüft (keine Fehler)
- [ ] Login funktioniert
- [ ] WebUntis neu konfiguriert
- [ ] Push-Benachrichtigungen getestet
- [ ] Alle Hauptfunktionen getestet

---

**Viel Erfolg mit L8teStudy v2.0.0!** 🎉
