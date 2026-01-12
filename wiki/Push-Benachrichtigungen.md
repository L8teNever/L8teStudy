# Push-Benachrichtigungen

Anleitung zur Konfiguration von Push-Benachrichtigungen in L8teStudy.

---

## 🔔 Überblick

L8teStudy unterstützt Browser-Push-Benachrichtigungen für:
- Neue Aufgaben (von anderen)
- Neue Termine (von anderen)
- Chat-Nachrichten
- Tägliche Erinnerungen

---

## ⚙️ Aktivierung

### Schritt 1: Push erlauben

1. **Account** → **Einstellungen** → **Benachrichtigungen**
2. Klicke auf **"Push erlauben"**
3. **Browser-Berechtigung erteilen** (Popup bestätigen)
4. Fertig! ✅

**Wichtig**: HTTPS erforderlich (außer localhost)

### Schritt 2: Benachrichtigungstypen wählen

**Verfügbare Optionen**:
- ☑️ Neue Aufgaben (von anderen)
- ☑️ Neue Termine (von anderen)
- ☑️ Neue Chat-Nachrichten
- ☑️ Tägliche Erinnerung: Hausaufgaben
- ☑️ Tägliche Erinnerung: Termine

Aktiviere/deaktiviere nach Bedarf.

---

## ⏰ Erinnerungen konfigurieren

### Hausaufgaben-Erinnerung

**Funktion**: Tägliche Übersicht über offene Aufgaben für morgen

**Konfiguration**:
1. Wähle eine Uhrzeit (z.B. 17:00)
2. Speichern
3. Du erhältst täglich zur gewählten Zeit eine Benachrichtigung

**Deaktivieren**: Feld leer lassen

### Termin-Erinnerung

**Funktion**: Tägliche Übersicht über morgige Termine

**Konfiguration**:
1. Wähle eine Uhrzeit (z.B. 19:00)
2. Speichern
3. Du erhältst täglich zur gewählten Zeit eine Benachrichtigung

**Deaktivieren**: Feld leer lassen

---

## 🧪 Test-Benachrichtigung

**Funktion testen**:
1. Einstellungen → Benachrichtigungen
2. Klicke auf **"Test-Benachrichtigung senden"**
3. Du solltest sofort eine Benachrichtigung erhalten

**Keine Benachrichtigung?** Siehe [Troubleshooting](#troubleshooting)

---

## 📱 Unterstützte Browser

| Browser | Desktop | Mobile |
|---------|---------|--------|
| Chrome | ✅ | ✅ |
| Edge | ✅ | ✅ |
| Firefox | ✅ | ✅ |
| Safari | ✅ (macOS 16.4+) | ✅ (iOS 16.4+) |
| Opera | ✅ | ✅ |

---

## 🔕 Deaktivierung

### In L8teStudy

1. **Account** → **Einstellungen** → **Benachrichtigungen**
2. Klicke auf **"Benachrichtigungen deaktivieren"**
3. Bestätige

### Im Browser

**Chrome**:
1. Einstellungen → Datenschutz und Sicherheit → Website-Einstellungen
2. Benachrichtigungen
3. L8teStudy blockieren

**Firefox**:
1. Einstellungen → Datenschutz & Sicherheit
2. Berechtigungen → Benachrichtigungen
3. L8teStudy entfernen

---

## 🆘 Troubleshooting

### Keine Benachrichtigungen

**Lösungen**:

1. **HTTPS erforderlich**: Push funktioniert nur über HTTPS (außer localhost)

2. **Browser-Berechtigung**:
   - Chrome: `chrome://settings/content/notifications`
   - Firefox: `about:preferences#privacy`
   - Prüfe ob L8teStudy erlaubt ist

3. **Service Worker**:
   - F12 → Application → Service Workers
   - Sollte "activated and running" sein

4. **Neu anmelden**:
   - Deaktiviere Push
   - Aktiviere Push neu
   - Browser-Berechtigung neu erteilen

### Test-Benachrichtigung kommt nicht

**Lösungen**:

1. **Tab schließen**: Schließe den L8teStudy-Tab nach dem Test
2. **Browser-Fokus**: Wechsle zu anderem Tab/Fenster
3. **Warten**: Manchmal dauert es 5-10 Sekunden

### "Push subscription failed"

**Lösungen**:

1. **Service Worker neu registrieren**:
   - F12 → Application → Service Workers
   - "Unregister" → Seite neu laden

2. **Browser-Cache leeren**: Ctrl+Shift+Delete

3. **Anderen Browser testen**

---

## 💡 Tipps

### Benachrichtigungen anpassen

**Nur wichtige Benachrichtigungen**:
- Deaktiviere "Neue Aufgaben" wenn zu viele
- Behalte Chat-Nachrichten aktiviert
- Nutze nur eine Erinnerung (Hausaufgaben ODER Termine)

### Zeitpunkt der Erinnerungen

**Empfehlungen**:
- **Hausaufgaben**: 17:00-18:00 (nach der Schule)
- **Termine**: 19:00-20:00 (abends)
- **Wochenende**: Deaktivieren oder später

### Mehrere Geräte

**Push auf mehreren Geräten**:
- Aktiviere Push auf jedem Gerät separat
- Jedes Gerät erhält Benachrichtigungen
- Deaktiviere auf Geräten, die du nicht nutzt

---

## 🔒 Datenschutz

**Was wird gespeichert**:
- Push-Subscription (Endpoint, Keys)
- Benachrichtigungs-Einstellungen
- Zeitpunkt der letzten Erinnerung

**Was wird NICHT gespeichert**:
- Keine persönlichen Daten in der Benachrichtigung selbst
- Benachrichtigungen werden nicht protokolliert

**Wer hat Zugriff**:
- Nur du siehst deine Benachrichtigungen
- Server sendet nur, speichert nicht

---

## 📚 Weitere Ressourcen

- [Erste Schritte](Erste-Schritte)
- [Chat-System](Chat-System)
- [Troubleshooting](Troubleshooting)

---

**Bleib auf dem Laufenden!** 🔔
