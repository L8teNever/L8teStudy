# Performance

Optimierung und Skalierung von L8teStudy.

---

## ⚡ Performance-Optimierungen

### Datenbank

**SQLite** (Standard):
- Gut für kleine/mittlere Installationen
- Bis ~100 Benutzer

**PostgreSQL** (Empfohlen für Produktion):
```env
DATABASE_URL=postgresql://user:password@localhost/l8testudy
```

**Vorteile**:
- Bessere Concurrent-Performance
- Mehr Features
- Skalierbar

---

### Gunicorn Workers

**Formel**: `(2 × CPU-Kerne) + 1`

```bash
# 4 CPU-Kerne → 9 Workers
gunicorn -w 9 -b 0.0.0.0:5000 run:app
```

---

### Caching

**Redis für Sessions** (optional):
```python
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_REDIS'] = redis.from_url('redis://localhost:6379')
```

---

## 📊 Monitoring

### Logs analysieren

```bash
# Langsame Requests finden
grep "slow" /var/log/l8testudy/access.log

# Fehler zählen
grep "ERROR" /var/log/l8testudy/error.log | wc -l
```

---

## 🔧 Skalierung

### Horizontal (mehrere Server)

**Load Balancer** (Nginx):
```nginx
upstream l8testudy {
    server 192.168.1.10:5000;
    server 192.168.1.11:5000;
    server 192.168.1.12:5000;
}

server {
    location / {
        proxy_pass http://l8testudy;
    }
}
```

---

## 📚 Weitere Ressourcen

- [Deployment](Deployment)
- [Docker](Docker)
- [Konfiguration](Konfiguration)

---
