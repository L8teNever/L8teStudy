# 🔄 Datenbank-Migration & Troubleshooting

## Problem: 400 Fehler nach Update

Wenn du nach einem Update 400 BAD REQUEST Fehler bekommst, liegt das meist daran, dass neue Datenbank-Tabellen fehlen.

### Lösung 1: Automatische Migration (empfohlen)

Das neue Docker-Image führt die Migration automatisch beim Start aus. Einfach Container neu starten:

**Docker Compose:**
```bash
docker-compose down
docker-compose up -d
```

**Dockge/Portainer:**
- Container stoppen
- Container löschen
- Stack neu deployen

### Lösung 2: Manuelle Migration

Falls die automatische Migration nicht funktioniert:

**Lokal (Python):**
```bash
python migrate_db.py
```

**Docker (laufender Container):**
```bash
docker-compose exec web python migrate_db.py
```

**Dockge/Portainer (Container-Konsole):**
```bash
python migrate_db.py
```

### Lösung 3: Datenbank neu erstellen (⚠️ Datenverlust!)

**Nur als letzte Option!** Dies löscht alle Daten.

1. Container stoppen
2. Datenbank-Datei löschen:
   ```bash
   rm ./data/l8testudy.db
   ```
3. Container neu starten

## Was wurde geändert?

### Version 1.1.25+ (TaskCompletion)

- **Neue Tabelle**: `TaskCompletion` für benutzerspezifische Task-Status
- **Grund**: Ermöglicht gemeinsame Hausaufgaben, bei denen jeder Benutzer seinen eigenen Erledigungsstatus hat
- **Migration**: Alte `Task.is_done` Werte werden automatisch migriert

### Überprüfung

Nach der Migration solltest du sehen:
```
✓ All database tables created/verified successfully
✓ TaskCompletion table exists with X entries
Database migration completed successfully!
```

## Häufige Fehler

### "Table already exists"
- **Ursache**: Tabelle existiert bereits
- **Lösung**: Kein Problem, ignorieren

### "No such column: task_completion.is_done"
- **Ursache**: Tabelle fehlt
- **Lösung**: Migration ausführen (siehe oben)

### "UNIQUE constraint failed"
- **Ursache**: Doppelte Einträge
- **Lösung**: Datenbank-Datei löschen und neu starten (Datenverlust!)

## Support

Bei weiteren Problemen:
1. Logs überprüfen: `docker-compose logs -f`
2. Issue auf GitHub öffnen
3. Logs und Fehlermeldung mitschicken
