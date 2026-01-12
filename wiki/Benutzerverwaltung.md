# Benutzerverwaltung

Anleitung zur Verwaltung von Benutzern (für Admins und Super Admins).

---

## 👥 Benutzer erstellen

### Als Admin (eigene Klasse)

1. **Admin** → **Admin Center**
2. **Benutzerverwaltung**
3. **Neuer Benutzer** (+)
4. **Formular ausfüllen**:
   - Benutzername (eindeutig)
   - Passwort (min. 7 Zeichen, A-Z, a-z, 0-9)
   - Rolle: Student oder Admin
5. **Erstellen**

### Als Super Admin (alle Klassen)

1. **Admin** → **Superadmin Dashboard**
2. **Klassen verwalten**
3. Klasse wählen
4. **Benutzer** → **Neuer Benutzer**
5. Rolle wählen: Student, Admin oder **Super Admin**
6. **Erstellen**

---

## 🔑 Login-Informationen teilen

### Klassencode

Jede Klasse hat einen eindeutigen Code (z.B. `CLASS1`).

**Teilen**:
- Gib Benutzern: Klassencode, Benutzername, Passwort
- Sie können sich damit einloggen

### Direkt-Login-Link

**Generieren**:
1. Klassen-Einstellungen
2. **Direkt-Login Link** kopieren
3. Link teilen (z.B. per E-Mail, Chat)

**Vorteil**: Benutzer müssen Klassencode nicht manuell eingeben

---

## ✏️ Benutzer bearbeiten

**Aktuell nicht möglich** über die Oberfläche.

**Passwort zurücksetzen**:
1. Benutzer löschen
2. Neu erstellen mit neuem Passwort

**Oder**: CLI-Tool verwenden:
```bash
python create_admin.py username neuesPasswort student
```

---

## 🗑️ Benutzer löschen

1. **Benutzerverwaltung**
2. Benutzer in der Liste finden
3. **Papierkorb-Symbol**
4. **Bestätigen**

**Wichtig**: 
- Alle Daten des Benutzers bleiben erhalten (Aufgaben, Termine)
- Noten werden gelöscht (privat)
- Kann nicht rückgängig gemacht werden

---

## 🔒 Sicherheit

### Passwort-Anforderungen

- Mindestens 7 Zeichen
- Groß- und Kleinbuchstaben
- Mindestens eine Zahl

### Erzwungener Passwortwechsel

Neue Benutzer müssen beim ersten Login ihr Passwort ändern.

**Deaktivieren**: Nur bei CLI-erstellten Benutzern möglich

---

## 💡 Best Practices

- **Sichere Passwörter**: Generiere zufällige Passwörter
- **Dokumentation**: Notiere Benutzernamen und initiale Passwörter
- **Regelmäßige Prüfung**: Lösche inaktive Benutzer
- **Rollen**: Vergib Admin-Rechte sparsam

---

## 📚 Weitere Ressourcen

- [Benutzerrollen](Benutzerrollen)
- [Klassenverwaltung](Klassenverwaltung)
- [Erste Schritte](Erste-Schritte)

---
