# Testing

Anleitung zum Testen von L8teStudy.

---

## 🧪 Test-Suite

L8teStudy enthält ein umfassendes Test-Script: `test_everything.py`

### Tests ausführen

```bash
python test_everything.py
```

**Testet**:
- ✅ Alle API-Endpunkte
- ✅ Authentifizierung
- ✅ CRUD-Operationen
- ✅ Berechtigungen
- ✅ Datenintegrität

---

## 📊 Test-Ausgabe

```
Testing L8teStudy Application
=============================

✓ Login successful
✓ Tasks API working
✓ Events API working
✓ Grades API working
✓ Permissions correct
...

All tests passed! ✓
```

---

## 🔧 Manuelle Tests

### API testen

```bash
# Login
curl -X POST http://localhost:5000/auth/login \
  -d "class_code=CLASS1&username=admin&password=test"

# Tasks abrufen
curl http://localhost:5000/api/tasks \
  -H "Cookie: session=..."
```

---

## 📚 Weitere Ressourcen

- [Entwicklung](Entwicklung)
- [API-Dokumentation](API-Dokumentation)

---
