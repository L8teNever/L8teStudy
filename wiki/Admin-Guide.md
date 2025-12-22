# 🛡️ Admin-Guide

Als Administrator hast du zusätzliche Rechte, um das System zu verwalten. Diese Funktionen sind im **Account Hub** (Profil-Icon oben rechts) sichtbar, wenn dein Account als Admin markiert ist.

## 👥 Benutzerverwaltung & Fächer
Diese Funktionen findest du jetzt unter **"Admin Einstellungen"** im Account Hub.

### 1. Benutzerverwaltung
- **Neue Benutzer anlegen**: Erstelle Accounts für Freunde oder Mitschüler.
- **Passwörter zurücksetzen**: Fall jemand sein Passwort vergessen hat.
- **Benutzer löschen**: Entferne Accounts aus dem System.

### 2. Fächerverwaltung (Neu)
Da jede Schule andere Fächer hat, kannst du diese hier zentral verwalten:
- **Hinzufügen**: Trage den Namen des Fachs ein (z.B. "Informatik" oder "Wirtschaft").
- **Löschen**: Entferne Fächer, die nicht benötigt werden. 
  *(Achtung: Dies kann Auswirkungen auf bestehende Aufgaben haben, die dieses Fach nutzen)*.

---

## 💾 Datensicherung (Backup)
Alle deine Daten liegen in einer SQLite-Datenbank. 
- **Speicherort**: `instance/l8testudy.db` (Lokal) oder `/data/l8testudy.db` (Docker).
- **Strategie**: Es wird empfohlen, diesen Ordner regelmäßig zu sichern. Da es sich um eine einzelne Datei handelt, kannst du sie einfach kopieren.
- **Bilder**: Hochgeladene Bilder befinden sich in `static/uploads/`. Auch dieser Ordner sollte gesichert werden.

---

## 🛠️ CLI-Tools
Es gibt hilfreiche Scripte im Hauptverzeichnis:

### 1. `create_admin.py`
Erstellt einen neuen Benutzer direkt über die Konsole.
```bash
python create_admin.py Name Passwort
```

### 2. `migrate_uploads.py`
Falls du die Speicherstruktur deiner Bilder aktualisieren musst, hilft dieses Script dabei, die Datenbank mit dem Dateisystem abzugleichen.

---

## 🛑 Fehlerbehebung für Admins
Falls die App nicht startet:
1. Prüfe, ob alle Module installiert sind: `pip install -r requirements.txt`.
2. Schau in die Logs: In Docker mit `docker logs l8testudy`.
3. Stelle sicher, dass der Ordner `instance` Schreibrechte hat.
