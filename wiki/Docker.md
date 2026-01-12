# Docker

Anleitung für Docker-Installation und -Konfiguration.

---

## 🐳 Docker Installation

### Mit docker-compose.yml

**1. Repository klonen**:
```bash
git clone <repo-url>
cd L8teStudy-4
```

**2. .env erstellen**:
```env
SECRET_KEY=your-secret-key-here
FLASK_ENV=production
UNTIS_FERNET_KEY=your-fernet-key-here
```

**3. Container starten**:
```bash
docker-compose up -d
```

**4. Admin erstellen**:
```bash
docker exec -it l8testudy python create_admin.py admin IhrPasswort superadmin
```

---

## 📋 docker-compose.yml

```yaml
version: '3.8'

services:
  l8testudy:
    build: .
    ports:
      - "5000:5000"
    volumes:
      - l8testudy-data:/app/instance
    environment:
      - SECRET_KEY=${SECRET_KEY}
      - FLASK_ENV=production
      - UNTIS_FERNET_KEY=${UNTIS_FERNET_KEY}
    restart: unless-stopped

volumes:
  l8testudy-data:
```

---

## 🔧 Verwaltung

### Container-Status

```bash
docker-compose ps
```

### Logs anzeigen

```bash
docker-compose logs -f
```

### Container neu starten

```bash
docker-compose restart
```

### Container stoppen

```bash
docker-compose down
```

---

## 💾 Daten-Persistenz

**Volume**: `l8testudy-data`
- Enthält: Datenbank, Uploads
- Bleibt bei Container-Neustart erhalten

**Backup**:
```bash
docker run --rm -v l8testudy-data:/data -v $(pwd):/backup alpine tar czf /backup/backup.tar.gz /data
```

**Restore**:
```bash
docker run --rm -v l8testudy-data:/data -v $(pwd):/backup alpine tar xzf /backup/backup.tar.gz -C /
```

---

## 🔄 Updates

```bash
# Code aktualisieren
git pull

# Image neu bauen
docker-compose build

# Container neu starten
docker-compose up -d
```

---

## 📚 Weitere Ressourcen

- [Deployment](Deployment)
- [Installation](Installation)

---
