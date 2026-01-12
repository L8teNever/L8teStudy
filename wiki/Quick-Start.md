# Quick Start

Schnelleinstieg in L8teStudy - in 5 Minuten startklar!

---

## 🚀 Für Benutzer

### 1. Einloggen (1 Min)

1. Öffne L8teStudy im Browser
2. Gib ein:
   - **Klassencode** (von deinem Admin)
   - **Benutzername** (von deinem Admin)
   - **Passwort** (von deinem Admin)
3. **Anmelden**

### 2. Passwort ändern (1 Min)

Beim ersten Login musst du dein Passwort ändern:
- Neues Passwort eingeben (min. 7 Zeichen, A-Z, a-z, 0-9)
- Wiederholen
- **Speichern**

### 3. Tutorial ansehen (2 Min)

Das Tutorial zeigt dir die wichtigsten Funktionen. Folge einfach den Schritten!

### 4. Erste Aufgabe erstellen (1 Min)

1. **Aufgaben** → **+**
2. Titel eingeben (z.B. "Mathe S. 42")
3. Fach und Datum wählen
4. **Speichern**

**Fertig!** Du kannst jetzt L8teStudy nutzen! 🎉

---

## 👨‍💼 Für Admins

### 1. Installation (2 Min)

```bash
git clone <repo-url>
cd L8teStudy-4
pip install -r requirements.txt
python create_admin.py admin IhrPasswort superadmin
python run.py
```

### 2. Klasse erstellen (1 Min)

1. Login als Super Admin
2. **Admin** → **Superadmin Dashboard**
3. **Klassen verwalten** → **+**
4. Name und Code eingeben → **Erstellen**

### 3. Benutzer erstellen (1 Min)

1. **Admin Center** → **Benutzerverwaltung** → **+**
2. Benutzername, Passwort, Rolle
3. **Erstellen**

### 4. Fächer einrichten (1 Min)

**Option A**: Manuell
- **Fächer verwalten** → Fach eingeben → **Hinzufügen**

**Option B**: Von WebUntis
- WebUntis konfigurieren → **Von WebUntis importieren**

**Fertig!** Deine Klasse ist einsatzbereit! 🎉

---

## 🐳 Docker Quick Start

```bash
docker-compose up -d
docker exec -it l8testudy python create_admin.py admin IhrPasswort superadmin
```

Öffne `http://localhost:5000` → **Fertig!**

---

## 📚 Nächste Schritte

- [Erste Schritte](Erste-Schritte) - Ausführliches Tutorial
- [Konfiguration](Konfiguration) - Erweiterte Einstellungen
- [WebUntis Integration](WebUntis-Integration) - Stundenplan einrichten

---

**Los geht's!** 🚀
