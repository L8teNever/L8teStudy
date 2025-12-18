# 🔒 Datenschutz & Sicherheit - L8teStudy

## Keine Datenübertragung nach außen! ✅

**L8teStudy ist eine vollständig lokale, selbst-gehostete Anwendung.**

### Was bedeutet das?

1. **Alle Daten bleiben bei dir**
   - Deine Datenbank wird lokal gespeichert (SQLite in `/data/l8testudy.db`)
   - Hochgeladene Bilder bleiben auf deinem Server (`/data/uploads`)
   - Keine Cloud-Synchronisation
   - Keine externen API-Aufrufe

2. **Kein Tracking oder Analytics**
   - Keine Google Analytics
   - Keine Telemetrie
   - Keine Fehlerberichterstattung an externe Server
   - Keine Cookies von Drittanbietern

3. **Keine externen Abhängigkeiten zur Laufzeit**
   - Die App funktioniert komplett offline
   - Keine Verbindung zu externen Servern erforderlich
   - Alle Ressourcen (CSS, JavaScript, Icons) sind lokal

4. **Open Source**
   - Der gesamte Quellcode ist auf GitHub einsehbar
   - Du kannst selbst überprüfen, was die App macht
   - Keine versteckten Funktionen

### Was wird übertragen?

**Nur beim Docker-Image-Download:**
- Wenn du das Docker-Image von Docker Hub herunterlädst (`L8teNever/l8testudy:latest`), wird das Image von Docker Hub heruntergeladen
- Das ist ein einmaliger Download beim ersten Start oder Update
- **Keine Daten von dir werden dabei hochgeladen!**

**Danach:**
- Absolut nichts! Die App läuft komplett lokal auf deinem Server
- Alle Anfragen gehen nur zwischen deinem Browser und deinem Server hin und her
- Keine Verbindung nach außen

### Wie kann ich das überprüfen?

1. **Netzwerk-Monitoring**: 
   - Nutze die Browser-Entwicklertools (F12 → Network Tab)
   - Du wirst sehen, dass alle Anfragen nur an `localhost` oder deine Server-IP gehen

2. **Quellcode-Prüfung**:
   - Schau dir den Code auf GitHub an: https://github.com/L8teNever/L8teStudy
   - Suche nach `requests`, `http://`, `https://` - du wirst keine externen API-Aufrufe finden

3. **Docker-Container-Logs**:
   - Überwache die Container-Logs - keine ausgehenden Verbindungen

### Technische Details

**Verwendete Technologien:**
- **Backend**: Flask (Python) - nur lokale Verarbeitung
- **Datenbank**: SQLite - Datei-basiert, lokal
- **Frontend**: Vanilla HTML/CSS/JavaScript - keine externen Frameworks von CDNs
- **Icons**: Lucide Icons - lokal eingebunden

**Keine der folgenden Bibliotheken wird verwendet:**
- ❌ `requests` (für HTTP-Anfragen)
- ❌ `urllib` (für externe Verbindungen)
- ❌ Google Analytics
- ❌ Facebook Pixel
- ❌ Sentry oder andere Fehler-Tracking-Dienste

### Zusammenfassung

✅ **100% lokal**  
✅ **Keine Datenübertragung nach außen**  
✅ **Volle Kontrolle über deine Daten**  
✅ **Open Source & überprüfbar**  
✅ **DSGVO-konform** (da keine Daten das System verlassen)

---

**Fragen oder Bedenken?**  
Schau dir den Quellcode an oder öffne ein Issue auf GitHub!
