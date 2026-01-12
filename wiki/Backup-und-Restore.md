# Backup und Restore

Anleitung zur Datensicherung und Wiederherstellung (nur Super Admin).

---

## 💾 Datenbank exportieren

1. **Admin** → **Superadmin Dashboard**
2. **Backup & Restore**
3. **Daten exportieren**
4. JSON-Datei wird heruntergeladen

**Enthält**:
- Alle Klassen
- Alle Benutzer (mit verschlüsselten Passwörtern)
- Alle Aufgaben, Termine, Noten
- Alle Einstellungen
- Audit-Logs

---

## 📥 Datenbank importieren

**⚠️ WARNUNG**: Überschreibt ALLE aktuellen Daten!

1. **Backup & Restore**
2. **Daten importieren**
3. **JSON-Datei auswählen**
4. **Bestätigen**
5. **Warten**: App wird neu geladen

---

## 🔄 Regelmäßige Backups

**Empfehlung**:
- Täglich: Automatisches Backup (Cron-Job)
- Wöchentlich: Manuelles Backup
- Vor Updates: Immer Backup erstellen

**Automatisierung** (Linux):
```bash
# Crontab
0 2 * * * curl -o /backup/l8testudy-$(date +\%Y\%m\%d).json https://your-domain.com/api/backup/export
```

---

## 📚 Weitere Ressourcen

- [Deployment](Deployment)
- [Troubleshooting](Troubleshooting)

---
