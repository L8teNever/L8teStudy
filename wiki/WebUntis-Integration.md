# WebUntis Integration

Detaillierte Anleitung zur WebUntis-Integration für automatischen Stundenplan-Import.

---

## 🕐 Überblick

Die WebUntis-Integration ermöglicht:
- ✅ Automatischer Stundenplan-Import
- ✅ Vertretungsplan-Anzeige
- ✅ Automatischer Fächer-Import
- ✅ Fachvorschläge beim Erstellen von Aufgaben
- ✅ Aktuelle Woche auf einen Blick

---

## ⚙️ Einrichtung (Admin)

### Voraussetzungen

- WebUntis-Zugang (Schüler-Account)
- Admin- oder Super-Admin-Rechte in L8teStudy
- Klassenname in WebUntis bekannt

---

### Schritt 1: Zugangsdaten eingeben

1. **Als Admin einloggen**
2. **Admin** → **Admin Center**
3. **Klassen-Einstellungen**
4. Scrolle zu **"WebUntis Integration"**

---

### Schritt 2: Formular ausfüllen

**Server**:
- Format: `server.webuntis.com` (OHNE `https://`)
- Beispiele:
  - `mese.webuntis.com`
  - `herakles.webuntis.com`
  - `thalia.webuntis.com`

**Schule**:
- Der Schulname in WebUntis
- Beispiel: `gymnasium-musterstadt`
- Zu finden in der WebUntis-URL: `https://server.webuntis.com/WebUntis/?school=gymnasium-musterstadt`

**Benutzername**:
- Dein WebUntis-Benutzername
- Meist: Vorname.Nachname oder Schüler-ID

**Passwort**:
- Dein WebUntis-Passwort
- Wird verschlüsselt gespeichert (Fernet-Verschlüsselung)

**Klassenname**:
- Exakter Name deiner Klasse in WebUntis
- Beispiele: `10a`, `10A`, `EF`, `Q1`
- **Wichtig**: Groß-/Kleinschreibung beachten!

---

### Schritt 3: Speichern und Testen

1. **Klicke auf "Speichern"**
2. **Gehe zu "Stundenplan"** (Hauptmenü)
3. **Prüfe**: Wird der Stundenplan angezeigt?

**Bei Erfolg**: Stundenplan wird geladen
**Bei Fehler**: Siehe [Troubleshooting](#troubleshooting)

---

## 📅 Stundenplan verwenden

### Ansicht

**Wochenübersicht**:
- Montag bis Freitag (oder Samstag)
- Alle Stunden des Tages
- Fach, Lehrer, Raum

**Farbcodierung**:
- **Normal**: Regulärer Unterricht (blau/grau)
- **Vertretung**: Gelb/Orange
- **Ausfall**: Rot durchgestrichen

---

### Informationen pro Stunde

**Anzeige**:
- **Zeit**: z.B. "08:00 - 08:45"
- **Fach**: z.B. "Mathematik"
- **Lehrer**: z.B. "Müller"
- **Raum**: z.B. "R101"
- **Status**: Normal, Vertretung, Ausfall

**Vertretung**:
- Ursprüngliches Fach durchgestrichen
- Neues Fach/Lehrer angezeigt
- Gelbe Markierung

**Ausfall**:
- Rote Markierung
- "Entfällt" oder "Ausfall"

---

### Aktualisierung

**Automatisch**:
- Beim Öffnen der Stundenplan-Seite
- Alle 5 Minuten (wenn Seite offen)

**Manuell**:
- Seite neu laden (F5)
- Oder: Swipe-Down auf Mobile

---

## 📚 Fächer importieren

### Automatischer Import

1. **Admin Center** → **Fächer verwalten**
2. **Klicke auf "Von WebUntis importieren"**
3. **Warte**: Fächer werden geladen
4. **Fertig**: Alle Fächer aus dem Stundenplan sind jetzt verfügbar

**Vorteile**:
- Keine manuelle Eingabe
- Immer aktuell
- Korrekte Schreibweise

---

### Fachvorschläge

Wenn WebUntis konfiguriert ist:

**Beim Erstellen einer Aufgabe**:
1. Öffne "Neue Aufgabe"
2. Das Fach-Feld zeigt automatisch das **aktuelle oder letzte Fach** aus dem Stundenplan
3. Du kannst es übernehmen oder ändern

**Beispiel**:
- Es ist gerade Mathe-Unterricht
- Du erstellst eine Aufgabe
- "Mathematik" ist automatisch vorausgewählt

---

## 🔒 Sicherheit

### Passwort-Verschlüsselung

**Fernet-Verschlüsselung**:
- WebUntis-Passwörter werden NICHT im Klartext gespeichert
- Verschlüsselung mit `UNTIS_FERNET_KEY`
- Nur die App kann das Passwort entschlüsseln

**Wichtig**:
- Ändere niemals den `UNTIS_FERNET_KEY` nach der ersten Konfiguration
- Sonst können gespeicherte Passwörter nicht mehr entschlüsselt werden

---

### Zugriffsrechte

**Wer kann konfigurieren**:
- Admins (für ihre eigene Klasse)
- Super Admins (für alle Klassen)

**Wer sieht den Stundenplan**:
- Alle Benutzer der Klasse
- Passwort wird NICHT angezeigt

---

## 🔄 Aktualisierung

### Zugangsdaten ändern

**Wenn sich dein WebUntis-Passwort ändert**:

1. **Admin Center** → **Klassen-Einstellungen**
2. **WebUntis Integration**
3. **Gib das neue Passwort ein**
4. **Speichern**

**Hinweis**: Alle anderen Felder bleiben gleich.

---

### Klassenname ändern

**Wenn deine Klasse umbenannt wird** (z.B. von 10a zu 11a):

1. **Admin Center** → **Klassen-Einstellungen**
2. **WebUntis Integration**
3. **Ändere "Klassenname"**
4. **Speichern**

---

## 🆘 Troubleshooting

### "Invalid credentials"

**Problem**: WebUntis-Login schlägt fehl.

**Lösungen**:

1. **Zugangsdaten testen**:
   - Gehe zu https://webuntis.com
   - Logge dich mit denselben Daten ein
   - Funktioniert es dort?

2. **Server-URL prüfen**:
   - OHNE `https://`
   - OHNE `/WebUntis`
   - Nur: `server.webuntis.com`

3. **Schulname prüfen**:
   - Exakt wie in WebUntis-URL
   - Meist kleingeschrieben
   - Bindestriche beachten

4. **Klassenname prüfen**:
   - Exakt wie in WebUntis
   - Groß-/Kleinschreibung wichtig!
   - Beispiel: `10a` ≠ `10A`

---

### Stundenplan lädt nicht

**Problem**: Seite bleibt leer oder zeigt Fehler.

**Lösungen**:

1. **Zugangsdaten neu eingeben**:
   - Manchmal hilft es, alles neu einzugeben
   - Besonders nach Updates

2. **Firewall prüfen**:
   - Server muss WebUntis erreichen können
   - Ausgehende Verbindungen erlauben

3. **Logs prüfen**:
   ```bash
   # Lokale Installation
   python run.py
   
   # Docker
   docker-compose logs -f
   ```

4. **Browser-Console**:
   - F12 → Console
   - Fehler anzeigen?

---

### Vertretungen werden nicht angezeigt

**Problem**: Vertretungsplan ist nicht aktuell.

**Lösungen**:

1. **Seite neu laden**: F5 oder Swipe-Down
2. **WebUntis prüfen**: Sind Vertretungen dort sichtbar?
3. **Zeitzone**: Ist die Server-Zeit korrekt?

---

### Fächer-Import funktioniert nicht

**Problem**: "Von WebUntis importieren" zeigt Fehler.

**Lösungen**:

1. **Stundenplan prüfen**: Wird der Stundenplan angezeigt?
2. **Zugangsdaten**: Sind sie korrekt?
3. **Neu versuchen**: Manchmal temporäres Problem

---

### "Connection timeout"

**Problem**: Verbindung zu WebUntis schlägt fehl.

**Lösungen**:

1. **Internet-Verbindung**: Ist der Server online?
2. **WebUntis-Status**: Ist WebUntis erreichbar?
3. **Firewall**: Blockiert die Firewall WebUntis?
4. **Proxy**: Nutzt du einen Proxy?

---

## 💡 Tipps & Tricks

### Mehrere Klassen

**Wenn du mehrere Klassen hast** (z.B. Kurssystem):

**Problem**: WebUntis zeigt nur eine Klasse.

**Lösung**: 
- Nutze den Klassennamen, der die meisten Stunden abdeckt
- Oder: Erstelle mehrere L8teStudy-Klassen (eine pro WebUntis-Klasse)

---

### Ferien und Feiertage

**WebUntis zeigt Ferien**:
- L8teStudy zeigt "Keine Stunden" an
- Normal und kein Fehler

---

### Stundenplan als Backup

**Empfehlung**:
- Mache Screenshots deines Stundenplans
- Falls WebUntis nicht erreichbar ist
- Oder: Drucke ihn aus

---

### Datenschutz

**Was wird gespeichert**:
- Server, Schule, Benutzername, Klassenname (Klartext)
- Passwort (verschlüsselt)

**Was wird NICHT gespeichert**:
- Dein Stundenplan (wird jedes Mal neu geladen)
- Vertretungen (live von WebUntis)

**Wer hat Zugriff**:
- Admins sehen die Konfiguration (ohne Passwort)
- Super Admins können Konfiguration ändern
- Datenbank-Backups enthalten verschlüsselte Passwörter

---

## 🔗 WebUntis-Ressourcen

**Offizielle Website**: https://webuntis.com

**Support**:
- WebUntis-Support für Login-Probleme
- L8teStudy-Support für Integrations-Probleme

**API-Dokumentation**: 
- Für Entwickler: https://github.com/python-webuntis/python-webuntis

---

## 📚 Weitere Ressourcen

- **[Erste Schritte](Erste-Schritte)** - Grundlagen
- **[Aufgaben und Termine](Aufgaben-und-Termine)** - Fachvorschläge nutzen
- **[Klassenverwaltung](Klassenverwaltung)** - Klassen konfigurieren
- **[Troubleshooting](Troubleshooting)** - Allgemeine Probleme

---

**Viel Erfolg mit der WebUntis-Integration!** 🕐
