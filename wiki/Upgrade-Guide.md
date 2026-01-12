# Upgrade-Guide

Anleitung zum Upgrade von L8teStudy v1.x auf v2.0.0.

---

## ⚠️ Vor dem Upgrade

### 1. Backup erstellen

**WICHTIG**: Erstelle unbedingt ein Backup!

```bash
# Datenbank kopieren
cp instance/l8testudy.db instance/l8testudy.db.backup

# Oder über App (Super Admin)
# Admin → Superadmin Dashboard → Backup & Restore → Export
```

---

## 🚀 Upgrade-Schritte

### Lokale Installation

```bash
# 1. Code aktualisieren
git pull origin main

# 2. Dependencies aktualisieren
pip install -r requirements.txt --upgrade

# 3. Datenbank migrieren (automatisch beim Start)
python run.py
```

### Docker

```bash
# 1. Container stoppen
docker-compose down

# 2. Backup erstellen
docker run --rm -v l8testudy-data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data

# 3. Code aktualisieren
git pull origin main

# 4. Image neu bauen
docker-compose build

# 5. Container starten
docker-compose up -d
```

---

## 🔄 Automatische Migrationen

Beim ersten Start von v2.0.0:

1. **Benutzerrollen**: `is_admin`, `is_super_admin` → `role`
2. **Neue Tabellen**: TaskMessage, TaskChatRead, UntisCredential
3. **Neue Spalten**: chat_enabled, parent_id, notify_chat_message

---

## ⚙️ Nach dem Upgrade

### 1. WebUntis neu konfigurieren

Passwörter werden jetzt verschlüsselt → Neu eingeben

### 2. Push-Benachrichtigungen neu aktivieren

Benutzer müssen sich neu anmelden

---

## 🔙 Rollback

Falls Probleme auftreten:

```bash
# Backup wiederherstellen
cp instance/l8testudy.db.backup instance/l8testudy.db

# Alte Version
git checkout v1.1.170
pip install -r requirements.txt
python run.py
```

---

## 📚 Weitere Ressourcen

- [CHANGELOG.md](../CHANGELOG.md)
- [Troubleshooting](Troubleshooting)
- [Installation](Installation)

---
