# ❓ FAQ & Troubleshooting

Hier findest du Lösungen zu häufigen Problemen.

## 🔴 Fehlermeldungen beim Start

### `ModuleNotFoundError: No module named '...'`
**Ursache:** Eine erforderliche Python-Bibliothek ist nicht installiert.
**Lösung:**
Stelle sicher, dass du alle Abhängigkeiten installiert hast:
```bash
pip install -r requirements.txt
```
Sollte ein spezifisches Modul fehlen, installiere es manuell:
```bash
pip install <modulname>
```

---

## 📱 PWA & Mobile Nutzung

### Warum kann ich die App nicht installieren?
1.  **HTTPS**: Damit der Browser die Installation erlaubt, muss die App über eine sichere Verbindung (`https://`) laufen oder auf `localhost` aufgerufen werden.
2.  **Browser**: Nutze unter Android **Chrome** und unter iOS **Safari**. Andere Browser (wie In-App-Browser von Instagram) unterstützen PWAs oft nicht.

### Die App lädt keine alten Inhalte, wenn ich offline bin.
Stelle sicher, dass du die App mindestens einmal mit Internetverbindung geöffnet hast, damit der **Service Worker** alle Dateien in den Cache laden kann.

---

## 🖼️ Bilder & Uploads

### Warum werden meine Bilder nicht angezeigt?
Prüfe, ob der Ordner `static/uploads` existiert und Schreibrechte hat. In Docker-Umgebungen stelle sicher, dass das **Volume** korrekt gemappt ist (siehe [Installation](Installation)).

---

## 🔐 Login-Probleme

### Ich habe mein Passwort vergessen und bin kein Admin.
Wende dich an den Administrator deines Systems. Er kann dein Passwort in der **Benutzerverwaltung** zurücksetzen.

### Ich habe mein Admin-Passwort vergessen.
Keine Sorge! Du kannst einfach über die Konsole (CLI) einen neuen Admin-Account erstellen:
```bash
python create_admin.py NeuerAdmin MeinSicheresPasswort
```
Nutze danach diesen Account, um dich einzuloggen.
