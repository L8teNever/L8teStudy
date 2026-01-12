# Sicherheit

Sicherheits-Best-Practices für L8teStudy.

---

## 🔒 Implementierte Sicherheitsmaßnahmen

### Authentifizierung

- ✅ Passwort-Hashing (PBKDF2)
- ✅ Session-basiert (Flask-Login)
- ✅ Secure Cookies (HttpOnly, Secure, SameSite)
- ✅ Erzwungener Passwortwechsel

### CSRF-Schutz

- ✅ Flask-WTF CSRF-Tokens
- ✅ SameSite Cookies (Strict)

### Content Security Policy

- ✅ Strikte CSP-Header
- ✅ Nur selbst-gehostete Ressourcen
- ✅ Frame-Ancestors: none

### HTTPS & Transport

- ✅ HTTPS-Erzwingung (Produktion)
- ✅ HSTS (1 Jahr)
- ✅ Secure Cookies

### Rate Limiting

- ✅ Flask-Limiter
- ✅ Schutz vor Brute-Force

### Datenverschlüsselung

- ✅ WebUntis-Passwörter (Fernet)
- ✅ Sichere Schlüsselverwaltung

---

## 🛡️ Best Practices

### Passwörter

**Anforderungen**:
- Mindestens 7 Zeichen
- Groß- und Kleinbuchstaben
- Zahlen

**Empfehlung**:
- Mindestens 12 Zeichen
- Sonderzeichen
- Passwort-Manager nutzen

### Secret Keys

**SECRET_KEY**:
```python
import secrets
print(secrets.token_hex(32))
```

**UNTIS_FERNET_KEY**:
```python
from cryptography.fernet import Fernet
print(Fernet.generate_key().decode())
```

**Wichtig**: Niemals im Code oder Git!

### HTTPS

**Immer in Produktion**:
- Let's Encrypt (kostenlos)
- Nginx/Apache als Reverse Proxy
- HSTS aktiviert

---

## 🔍 Sicherheits-Audit

### Regelmäßig prüfen

- [ ] Dependencies aktuell? (`pip list --outdated`)
- [ ] Backups funktionieren?
- [ ] Logs auf Anomalien prüfen
- [ ] Inaktive Benutzer löschen
- [ ] Admin-Rechte minimal halten

---

## 📚 Weitere Ressourcen

- [Konfiguration](Konfiguration)
- [Deployment](Deployment)
- [Audit-Log](Audit-Log)

---
