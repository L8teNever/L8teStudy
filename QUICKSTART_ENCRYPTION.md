# 🚀 Quick Start - AES-Verschlüsselung

## 1. Setup (Einmalig)

### Schritt 1: Generiere einen Encryption Key

```bash
py encryption_examples.py
# Wähle Option 1: "Neuen Encryption Key generieren"
```

### Schritt 2: Speichere den Key in .env

Füge die generierte Zeile zu deiner `.env` Datei hinzu:

```bash
ENCRYPTION_KEY=<dein_generierter_key>
```

**⚠️ WICHTIG:** Committe die `.env` Datei NICHT in Git!

## 2. Verwendung in der App

### In `app/__init__.py`:

```python
from app.encryption import AESEncryption
import os

# Initialisiere Encryption
encryption_key = os.getenv('ENCRYPTION_KEY')
if encryption_key:
    encryption = AESEncryption.from_b64_key(encryption_key)
else:
    raise ValueError("ENCRYPTION_KEY nicht in .env gefunden!")
```

### In `app/routes.py`:

```python
from app import encryption
import json

# Datei verschlüsseln
@app.route('/upload', methods=['POST'])
def upload():
    file_data = request.files['file'].read()
    
    metadata = {
        "filename": "example.pdf",
        "user_id": current_user.id
    }
    
    aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
    encrypted = encryption.encrypt(file_data, associated_data=aad)
    
    # Speichere encrypted in Datenbank
    return jsonify({"status": "success"})

# Datei entschlüsseln
@app.route('/download/<file_id>')
def download(file_id):
    # Lade encrypted_data und metadata aus Datenbank
    
    aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
    decrypted = encryption.decrypt(encrypted_data, associated_data=aad)
    
    return send_file(io.BytesIO(decrypted), ...)
```

## 3. Tests ausführen

```bash
py test_encryption.py
```

Alle 9 Tests sollten erfolgreich sein! ✓

## 4. Beispiele ansehen

```bash
py encryption_examples.py
```

Interaktives Menü mit verschiedenen Beispielen.

## Fertig! 🎉

Deine App verwendet jetzt **AES-256-GCM** Verschlüsselung für maximale Sicherheit!
