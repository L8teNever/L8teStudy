# Benutzerrollen

Übersicht über die Benutzerrollen in L8teStudy.

---

## 👤 Rollen-Übersicht

L8teStudy hat drei Benutzerrollen:

| Rolle | Beschreibung | Anzahl |
|-------|--------------|--------|
| **Student** | Normaler Benutzer | Unbegrenzt |
| **Admin** | Klassenadministrator | Mehrere pro Klasse |
| **Super Admin** | Systemadministrator | Wenige |

---

## 🎓 Student

### Berechtigungen

**Kann**:
- ✅ Aufgaben erstellen, bearbeiten, löschen (eigene)
- ✅ Termine erstellen, bearbeiten, löschen (eigene)
- ✅ Noten verwalten (nur eigene, privat)
- ✅ Chat-Nachrichten senden
- ✅ Stundenplan ansehen
- ✅ Benachrichtigungen konfigurieren
- ✅ Eigenes Profil bearbeiten

**Kann NICHT**:
- ❌ Andere Benutzer verwalten
- ❌ Klasseneinstellungen ändern
- ❌ Fächer verwalten
- ❌ WebUntis konfigurieren
- ❌ Inhalte anderer löschen
- ❌ Aufgaben/Termine teilen (klassenübergreifend)

### Anwendungsfall

- Schüler in einer Klasse
- Normale Nutzung der App
- Keine administrativen Aufgaben

---

## 👨‍💼 Admin

### Berechtigungen

**Alle Student-Rechte PLUS**:
- ✅ Benutzer erstellen/löschen (eigene Klasse)
- ✅ Klasseneinstellungen bearbeiten
- ✅ Fächer verwalten
- ✅ WebUntis konfigurieren
- ✅ Aufgaben/Termine teilen (klassenübergreifend)
- ✅ Audit-Log einsehen (eigene Klasse)
- ✅ Alle Aufgaben/Termine der Klasse bearbeiten/löschen

**Kann NICHT**:
- ❌ Andere Klassen verwalten
- ❌ Klassen erstellen/löschen
- ❌ Globale Fächer erstellen
- ❌ System-Backups erstellen
- ❌ Noten anderer Benutzer sehen

### Anwendungsfall

- Klassenlehrer
- Klassensprecher
- Vertrauensschüler mit erweiterten Rechten

---

## 👑 Super Admin

### Berechtigungen

**Alle Admin-Rechte PLUS**:
- ✅ Klassen erstellen/bearbeiten/löschen
- ✅ Alle Klassen verwalten
- ✅ Globale Fächer erstellen
- ✅ Klassenübergreifende Statistiken
- ✅ System-Backups erstellen/wiederherstellen
- ✅ Audit-Log aller Klassen
- ✅ Geteilte Inhalte verwalten

**Kann NICHT**:
- ❌ Noten anderer Benutzer sehen (Datenschutz!)

### Anwendungsfall

- Schuladministrator
- IT-Verantwortlicher
- Systemverwalter

---

## 🔄 Rollen zuweisen

### Bei Benutzererstellung

**Als Admin** (eigene Klasse):
1. Admin Center → Benutzerverwaltung
2. Neuer Benutzer
3. Rolle wählen: Student oder Admin
4. Erstellen

**Als Super Admin** (alle Klassen):
1. Superadmin Dashboard → Klassen verwalten
2. Klasse wählen → Benutzer
3. Rolle wählen: Student, Admin oder Super Admin
4. Erstellen

### Rolle ändern

**Aktuell nicht möglich** über die Oberfläche.

**Workaround**:
1. Benutzer löschen
2. Neu erstellen mit gewünschter Rolle

**Oder**: Datenbank direkt bearbeiten (nur für Experten)

---

## 🔒 Sicherheit

### Passwort-Richtlinien

**Für alle Rollen**:
- Mindestens 7 Zeichen
- Groß- und Kleinbuchstaben
- Mindestens eine Zahl

**Empfehlung für Admins**:
- Mindestens 12 Zeichen
- Sonderzeichen verwenden
- Nicht mit anderen Accounts teilen

### Erzwungener Passwortwechsel

**Neue Benutzer**:
- Müssen beim ersten Login Passwort ändern
- Gilt für alle Rollen

**Ausnahme**:
- Per CLI erstellte Benutzer (`create_admin.py`)

---

## 💡 Best Practices

### Student-Accounts

- Standard-Rolle für die meisten Benutzer
- Keine erweiterten Rechte nötig
- Einfache Verwaltung

### Admin-Accounts

**Wann Admin-Rechte vergeben**:
- Vertrauenswürdige Personen
- Technisch versiert
- Verantwortungsbewusst

**Wie viele Admins**:
- 2-3 pro Klasse empfohlen
- Mindestens 1 Backup-Admin
- Nicht zu viele (Sicherheit)

### Super Admin-Accounts

**Wann Super Admin**:
- Nur für Systemverwalter
- Sehr restriktiv vergeben
- Maximal 2-3 Accounts

**Sicherheit**:
- Starke Passwörter
- Regelmäßig ändern
- Nicht teilen

---

## 📊 Rollen-Vergleich

| Feature | Student | Admin | Super Admin |
|---------|---------|-------|-------------|
| Aufgaben/Termine (eigene) | ✅ | ✅ | ✅ |
| Noten (eigene) | ✅ | ✅ | ✅ |
| Chat | ✅ | ✅ | ✅ |
| Stundenplan | ✅ | ✅ | ✅ |
| Benutzer verwalten (Klasse) | ❌ | ✅ | ✅ |
| Klasseneinstellungen | ❌ | ✅ | ✅ |
| Fächer verwalten | ❌ | ✅ | ✅ |
| WebUntis konfigurieren | ❌ | ✅ | ✅ |
| Inhalte teilen | ❌ | ✅ | ✅ |
| Klassen erstellen | ❌ | ❌ | ✅ |
| Globale Fächer | ❌ | ❌ | ✅ |
| System-Backup | ❌ | ❌ | ✅ |
| Alle Klassen sehen | ❌ | ❌ | ✅ |

---

## 📚 Weitere Ressourcen

- [Benutzerverwaltung](Benutzerverwaltung)
- [Klassenverwaltung](Klassenverwaltung)
- [Erste Schritte](Erste-Schritte)

---

**Rollen richtig nutzen!** 👥
