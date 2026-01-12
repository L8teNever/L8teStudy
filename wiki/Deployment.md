# Deployment

Anleitung für Produktions-Deployment von L8teStudy.

---

## 🚀 Produktions-Checkliste

- [ ] `FLASK_ENV=production`
- [ ] Starker `SECRET_KEY`
- [ ] `UNTIS_FERNET_KEY` gesetzt
- [ ] HTTPS konfiguriert
- [ ] Firewall eingerichtet
- [ ] Backups konfiguriert
- [ ] Monitoring eingerichtet

---

## 🐧 Linux-Server

### Mit Gunicorn & Systemd

**1. Gunicorn installieren**:
```bash
pip install gunicorn
```

**2. Systemd Service** (`/etc/systemd/system/l8testudy.service`):
```ini
[Unit]
Description=L8teStudy
After=network.target

[Service]
User=www-data
WorkingDirectory=/var/www/l8testudy
Environment="PATH=/var/www/l8testudy/venv/bin"
ExecStart=/var/www/l8testudy/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 run:app

[Install]
WantedBy=multi-user.target
```

**3. Service starten**:
```bash
sudo systemctl enable l8testudy
sudo systemctl start l8testudy
```

---

## 🌐 Nginx Reverse Proxy

**Konfiguration** (`/etc/nginx/sites-available/l8testudy`):
```nginx
server {
    listen 80;
    server_name your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;

    client_max_body_size 16M;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

---

## 🐳 Docker Deployment

Siehe [Docker](Docker)

---

## 🔒 SSL/TLS (Let's Encrypt)

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 📊 Monitoring

**Logs**:
```bash
# Systemd
sudo journalctl -u l8testudy -f

# Nginx
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

---

## 📚 Weitere Ressourcen

- [Docker](Docker)
- [Sicherheit](Sicherheit)
- [Performance](Performance)

---
