# 🔒 AES-Verschlüsselung für L8teStudy

## Übersicht

Das Encryption-Modul implementiert **AES-256-GCM** Verschlüsselung für maximale Sicherheit in L8teStudy. Es bietet:

- ✅ **AES-256-GCM** (Authenticated Encryption with Associated Data)
- ✅ **Automatische Nonce-Generierung** für jede Verschlüsselung
- ✅ **PBKDF2 Key Derivation** aus Passwörtern
- ✅ **Manipulations-Erkennung** durch Authentication Tags
- ✅ **Metadaten-Support** (AAD - Associated Authenticated Data)
- ✅ **Datei- und String-Verschlüsselung**

## Sicherheits-Features

### 1. AES-256-GCM
- **256-bit Schlüssel** für maximale Sicherheit
- **GCM-Modus** (Galois/Counter Mode) für authentifizierte Verschlüsselung
- **Integrität garantiert**: Manipulierte Daten werden automatisch erkannt

### 2. Sichere Schlüsselverwaltung
- **Kryptographisch sichere Zufallszahlen** (os.urandom)
- **PBKDF2** mit 100.000 Iterationen für Passwort-basierte Schlüssel
- **Base64-Kodierung** für sichere Speicherung

### 3. Metadaten-Authentifizierung
- **AAD (Associated Authenticated Data)** schützt Metadaten
- Beispiel: Dateiname, Besitzer, Zeitstempel werden mit-authentifiziert
- Änderungen an Metadaten werden erkannt

## Installation

Die `cryptography` Library ist bereits in `requirements.txt` enthalten:

```bash
pip install -r requirements.txt
```

## Schnellstart

### Basis-Verschlüsselung

```python
from app.encryption import AESEncryption

# Erstelle Encryption-Instanz (generiert automatisch einen Schlüssel)
enc = AESEncryption()

# Verschlüssele Daten
data = b"Geheime Notizen"
encrypted = enc.encrypt(data)

# Entschlüssele Daten
decrypted = enc.decrypt(encrypted)
print(decrypted)  # b"Geheime Notizen"
```

### String-Verschlüsselung

```python
from app.encryption import AESEncryption

enc = AESEncryption()

# Verschlüssele String (Base64-kodiert)
text = "Geheimer Text 🔒"
encrypted_text = enc.encrypt_string(text)

# Entschlüssele String
decrypted_text = enc.decrypt_string(encrypted_text)
print(decrypted_text)  # "Geheimer Text 🔒"
```

### Passwort-basierte Verschlüsselung

```python
from app.encryption import AESEncryption

# Leite Schlüssel aus Passwort ab
password = "MeinSicheresPasswort123!"
key, salt = AESEncryption.derive_key_from_password(password)

# Erstelle Encryption mit abgeleitetem Schlüssel
enc = AESEncryption(master_key=key)

# Verschlüssele Daten
encrypted = enc.encrypt(b"Geschützte Daten")

# Später: Wiederherstellung mit gleichem Passwort und Salt
key2, _ = AESEncryption.derive_key_from_password(password, salt)
enc2 = AESEncryption(master_key=key2)
decrypted = enc2.decrypt(encrypted)
```

### Datei-Verschlüsselung

```python
from app.encryption import AESEncryption

enc = AESEncryption()

# Verschlüssele Datei
enc.encrypt_file("notizen.txt", "notizen.txt.encrypted")

# Entschlüssele Datei
enc.decrypt_file("notizen.txt.encrypted", "notizen_decrypted.txt")
```

### Verschlüsselung mit Metadaten

```python
from app.encryption import AESEncryption, FileEncryptionManager

enc = AESEncryption()
manager = FileEncryptionManager(enc)

# Metadaten definieren
metadata = {
    "filename": "mathe_notizen.pdf",
    "owner": "Lena",
    "subject": "Mathematik",
    "timestamp": "2026-01-21T11:50:00"
}

# Verschlüssele mit Metadaten
encrypted = manager.encrypt_with_metadata("notizen.pdf", metadata)

# Entschlüssele (nur mit korrekten Metadaten möglich!)
decrypted = manager.decrypt_with_metadata(encrypted, metadata)
```

## Utility-Funktionen

Für einfache Verwendung gibt es Utility-Funktionen:

```python
from app.encryption import generate_encryption_key, encrypt_data, decrypt_data

# Generiere neuen Schlüssel
key = generate_encryption_key()

# Verschlüssele
data = b"Test-Daten"
metadata = {"user": "Lena"}
encrypted = encrypt_data(data, key, metadata)

# Entschlüssele
decrypted = decrypt_data(encrypted, key, metadata)
```

## Schlüssel-Persistenz

```python
from app.encryption import AESEncryption

# Erstelle Encryption
enc = AESEncryption()

# Exportiere Schlüssel (z.B. für Speicherung in Umgebungsvariable)
key_b64 = enc.get_master_key_b64()
print(f"Schlüssel: {key_b64}")

# Später: Lade Schlüssel
enc2 = AESEncryption.from_b64_key(key_b64)
```

## Integration in L8teStudy

### 1. Schlüssel-Management in .env

```bash
# .env
ENCRYPTION_KEY=<generierter_base64_schlüssel>
```

### 2. Initialisierung in app/__init__.py

```python
from app.encryption import AESEncryption
import os

# Lade Schlüssel aus Umgebungsvariable
encryption_key = os.getenv('ENCRYPTION_KEY')
if encryption_key:
    encryption = AESEncryption.from_b64_key(encryption_key)
else:
    # Generiere neuen Schlüssel beim ersten Start
    encryption = AESEncryption()
    print(f"Neuer Encryption Key: {encryption.get_master_key_b64()}")
    print("Bitte in .env als ENCRYPTION_KEY speichern!")
```

### 3. Verwendung in routes.py

```python
from app import encryption

@app.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    
    # Lese Datei
    file_data = file.read()
    
    # Metadaten
    metadata = {
        "filename": file.filename,
        "user_id": current_user.id,
        "upload_time": datetime.now().isoformat()
    }
    
    # Verschlüssele mit Metadaten
    import json
    aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
    encrypted_data = encryption.encrypt(file_data, associated_data=aad)
    
    # Speichere verschlüsselte Daten
    # ... (in Datenbank oder Dateisystem)
    
    return jsonify({"status": "success"})

@app.route('/download/<file_id>')
def download_file(file_id):
    # Lade verschlüsselte Daten und Metadaten
    encrypted_data = ...  # aus Datenbank
    metadata = ...  # aus Datenbank
    
    # Entschlüssele
    import json
    aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
    decrypted_data = encryption.decrypt(encrypted_data, associated_data=aad)
    
    # Sende Datei
    return send_file(
        io.BytesIO(decrypted_data),
        download_name=metadata['filename']
    )
```

## Best Practices

### ✅ DO's

1. **Schlüssel sicher speichern**
   - Verwende Umgebungsvariablen (.env)
   - Niemals im Code hardcoden
   - Niemals in Git committen

2. **Metadaten verwenden**
   - Authentifiziere wichtige Metadaten (Dateiname, Besitzer, etc.)
   - Verhindert Metadaten-Manipulation

3. **Passwort-basierte Verschlüsselung**
   - Verwende starke Passwörter (min. 12 Zeichen)
   - Speichere Salt sicher
   - Verwende PBKDF2 mit mindestens 100.000 Iterationen

4. **Fehlerbehandlung**
   ```python
   try:
       decrypted = enc.decrypt(encrypted_data)
   except DecryptionError as e:
       # Daten wurden manipuliert oder falscher Schlüssel
       logger.error(f"Decryption failed: {e}")
   ```

### ❌ DON'Ts

1. **Niemals Schlüssel wiederverwenden** für verschiedene Zwecke
2. **Niemals Nonce manuell setzen** (wird automatisch generiert)
3. **Niemals verschlüsselte Daten ohne Metadaten-Validierung** entschlüsseln
4. **Niemals Schlüssel in Logs ausgeben**

## Sicherheits-Garantien

### Was ist geschützt?

✅ **Vertraulichkeit**: Daten können ohne Schlüssel nicht gelesen werden  
✅ **Integrität**: Manipulationen werden erkannt  
✅ **Authentizität**: Metadaten werden mit-authentifiziert  
✅ **Replay-Schutz**: Jede Verschlüsselung verwendet eine neue Nonce  

### Was ist NICHT geschützt?

❌ **Größe der Daten**: Verschlüsselte Daten haben ähnliche Größe wie Original  
❌ **Existenz der Daten**: Dass Daten existieren, ist sichtbar  
❌ **Zugriffsmuster**: Wann auf Daten zugegriffen wird  

## Performance

- **Verschlüsselung**: ~100 MB/s (abhängig von Hardware)
- **Entschlüsselung**: ~100 MB/s (abhängig von Hardware)
- **Key Derivation**: ~50ms (100.000 PBKDF2-Iterationen)

## Technische Details

### Verschlüsselungs-Format

```
[Nonce (12 bytes)] + [Ciphertext + Auth Tag (variable)]
```

- **Nonce**: 96-bit zufällige Nonce (empfohlen für GCM)
- **Ciphertext**: Verschlüsselte Daten
- **Auth Tag**: 128-bit Authentication Tag (in GCM integriert)

### Algorithmen

- **Verschlüsselung**: AES-256-GCM
- **Key Derivation**: PBKDF2-HMAC-SHA256
- **Zufallszahlen**: os.urandom (kryptographisch sicher)

## Tests

Führe die Test-Suite aus:

```bash
python test_encryption.py
```

Die Tests umfassen:
1. ✅ Basis-Verschlüsselung
2. ✅ String-Verschlüsselung
3. ✅ Passwort-basierte Verschlüsselung
4. ✅ Datei-Verschlüsselung
5. ✅ Authentifizierte Verschlüsselung (AAD)
6. ✅ Datei-Verschlüsselung mit Metadaten
7. ✅ Schlüssel-Persistenz
8. ✅ Utility-Funktionen
9. ✅ Manipulations-Erkennung

## Beispiel: Vollständiger Workflow

```python
from app.encryption import AESEncryption, FileEncryptionManager
import os

# 1. Setup (einmalig)
if not os.getenv('ENCRYPTION_KEY'):
    enc = AESEncryption()
    key = enc.get_master_key_b64()
    print(f"Neuer Schlüssel: {key}")
    print("Bitte in .env speichern!")
else:
    # Lade existierenden Schlüssel
    enc = AESEncryption.from_b64_key(os.getenv('ENCRYPTION_KEY'))

# 2. Datei hochladen und verschlüsseln
manager = FileEncryptionManager(enc)

metadata = {
    "filename": "mathe_klausur.pdf",
    "owner": "Lena",
    "subject": "Mathematik",
    "class": "12a",
    "timestamp": "2026-01-21T11:50:00"
}

# Verschlüssele
encrypted_data = manager.encrypt_with_metadata("mathe_klausur.pdf", metadata)

# Speichere verschlüsselt
with open("storage/encrypted_files/file_123.enc", "wb") as f:
    f.write(encrypted_data)

# Speichere Metadaten separat (unverschlüsselt für Suche)
import json
with open("storage/metadata/file_123.json", "w") as f:
    json.dump(metadata, f)

# 3. Später: Datei abrufen und entschlüsseln
with open("storage/encrypted_files/file_123.enc", "rb") as f:
    encrypted_data = f.read()

with open("storage/metadata/file_123.json", "r") as f:
    metadata = json.load(f)

# Entschlüssele (nur mit korrekten Metadaten!)
decrypted_data = manager.decrypt_with_metadata(encrypted_data, metadata)

# Sende an User
# ...
```

## Troubleshooting

### Problem: "Authentifizierung fehlgeschlagen"

**Ursache**: Daten wurden manipuliert oder falscher Schlüssel/Metadaten

**Lösung**:
- Prüfe, ob der richtige Schlüssel verwendet wird
- Prüfe, ob die Metadaten exakt übereinstimmen
- Prüfe, ob die Daten beschädigt wurden

### Problem: "Schlüssel muss 32 bytes lang sein"

**Ursache**: Ungültiger Schlüssel

**Lösung**:
```python
# Generiere neuen Schlüssel
from app.encryption import generate_encryption_key
key = generate_encryption_key()
```

### Problem: Performance-Probleme bei großen Dateien

**Lösung**: Implementiere Chunk-basierte Verschlüsselung:

```python
def encrypt_large_file(input_path, output_path, chunk_size=1024*1024):
    """Verschlüsselt große Dateien in Chunks"""
    enc = AESEncryption()
    
    with open(input_path, 'rb') as f_in:
        with open(output_path, 'wb') as f_out:
            while True:
                chunk = f_in.read(chunk_size)
                if not chunk:
                    break
                
                encrypted_chunk = enc.encrypt(chunk)
                # Schreibe Chunk-Größe + Chunk
                f_out.write(len(encrypted_chunk).to_bytes(4, 'big'))
                f_out.write(encrypted_chunk)
```

## Support & Fragen

Bei Fragen oder Problemen:
1. Prüfe diese Dokumentation
2. Führe die Tests aus (`python test_encryption.py`)
3. Prüfe die Logs auf Fehlermeldungen

## Lizenz

Teil von L8teStudy - Alle Rechte vorbehalten
