"""
Beispiel-Integration der AES-Verschlüsselung in L8teStudy
Zeigt, wie man das Encryption-Modul in der Flask-App verwendet
"""

import os
import sys
from datetime import datetime

# UTF-8 Encoding für Windows-Konsole
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Füge das app-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from encryption import AESEncryption, FileEncryptionManager


def setup_encryption_key():
    """
    Setup-Funktion: Generiert einen neuen Verschlüsselungsschlüssel
    Dieser sollte einmalig ausgeführt und dann in .env gespeichert werden
    """
    print("=" * 70)
    print("L8teStudy - Encryption Key Setup")
    print("=" * 70)
    print()
    
    # Generiere neuen Schlüssel
    enc = AESEncryption()
    key = enc.get_master_key_b64()
    
    print("Neuer Verschlüsselungsschlüssel wurde generiert!")
    print()
    print("Füge folgende Zeile zu deiner .env Datei hinzu:")
    print("-" * 70)
    print(f"ENCRYPTION_KEY={key}")
    print("-" * 70)
    print()
    print("⚠️  WICHTIG:")
    print("  - Speichere diesen Schlüssel sicher!")
    print("  - Committe die .env Datei NICHT in Git!")
    print("  - Ohne diesen Schlüssel können verschlüsselte Daten nicht wiederhergestellt werden!")
    print()


def example_file_encryption():
    """
    Beispiel 1: Datei-Verschlüsselung für hochgeladene Notizen
    """
    print("\n" + "=" * 70)
    print("Beispiel 1: Datei-Verschlüsselung")
    print("=" * 70)
    
    # Simuliere Schlüssel aus .env
    enc = AESEncryption()
    manager = FileEncryptionManager(enc)
    
    # Simuliere hochgeladene Datei
    import tempfile
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt', encoding='utf-8') as f:
        f.write("Mathe-Klausur Notizen\n")
        f.write("Thema: Integralrechnung\n")
        f.write("Wichtig: Substitutionsregel nicht vergessen!")
        temp_file = f.name
    
    print(f"\n📄 Original-Datei: {os.path.basename(temp_file)}")
    
    # Metadaten (wie sie in der Datenbank gespeichert würden)
    metadata = {
        "filename": "mathe_klausur.txt",
        "user_id": 123,
        "owner": "Lena",
        "subject": "Mathematik",
        "class": "12a",
        "upload_time": datetime.now().isoformat(),
        "file_type": "text/plain"
    }
    
    print(f"📋 Metadaten: {metadata['filename']} von {metadata['owner']}")
    
    # Verschlüssele Datei
    encrypted_data = manager.encrypt_with_metadata(temp_file, metadata)
    print(f"🔒 Verschlüsselt: {len(encrypted_data)} bytes")
    
    # Speichere verschlüsselte Daten (simuliert)
    encrypted_file = temp_file + '.encrypted'
    with open(encrypted_file, 'wb') as f:
        f.write(encrypted_data)
    
    print(f"💾 Gespeichert: {os.path.basename(encrypted_file)}")
    
    # Später: Entschlüssele Datei
    with open(encrypted_file, 'rb') as f:
        encrypted_data = f.read()
    
    decrypted_data = manager.decrypt_with_metadata(encrypted_data, metadata)
    print(f"🔓 Entschlüsselt: {len(decrypted_data)} bytes")
    print(f"📝 Inhalt: {decrypted_data.decode('utf-8')[:50]}...")
    
    # Cleanup
    os.unlink(temp_file)
    os.unlink(encrypted_file)
    
    print("✓ Beispiel erfolgreich!")


def example_database_encryption():
    """
    Beispiel 2: Verschlüsselung sensibler Daten in der Datenbank
    """
    print("\n" + "=" * 70)
    print("Beispiel 2: Datenbank-Verschlüsselung")
    print("=" * 70)
    
    enc = AESEncryption()
    
    # Simuliere sensible Benutzerdaten
    sensitive_data = {
        "email": "lena@example.com",
        "phone": "+49 123 456789",
        "address": "Musterstraße 123, 12345 Musterstadt"
    }
    
    print(f"\n📊 Original-Daten:")
    for key, value in sensitive_data.items():
        print(f"  {key}: {value}")
    
    # Verschlüssele jedes Feld einzeln
    encrypted_data = {}
    for key, value in sensitive_data.items():
        encrypted_data[key] = enc.encrypt_string(value)
    
    print(f"\n🔒 Verschlüsselte Daten:")
    for key, value in encrypted_data.items():
        print(f"  {key}: {value[:30]}...")
    
    # Entschlüssele Daten
    decrypted_data = {}
    for key, value in encrypted_data.items():
        decrypted_data[key] = enc.decrypt_string(value)
    
    print(f"\n🔓 Entschlüsselte Daten:")
    for key, value in decrypted_data.items():
        print(f"  {key}: {value}")
    
    print("\n✓ Beispiel erfolgreich!")


def example_password_protection():
    """
    Beispiel 3: Passwort-geschützte Verschlüsselung
    """
    print("\n" + "=" * 70)
    print("Beispiel 3: Passwort-geschützte Verschlüsselung")
    print("=" * 70)
    
    # Benutzer-Passwort (würde normalerweise vom User eingegeben)
    password = "MeinSicheresPasswort123!"
    print(f"\n🔑 Passwort: {password}")
    
    # Leite Schlüssel aus Passwort ab
    key, salt = AESEncryption.derive_key_from_password(password)
    print(f"🧂 Salt (Hex): {salt.hex()}")
    
    # Erstelle Encryption mit abgeleitetem Schlüssel
    enc = AESEncryption(master_key=key)
    
    # Verschlüssele private Notizen
    private_notes = "Meine geheimen Gedanken zum Projekt..."
    encrypted = enc.encrypt_string(private_notes)
    print(f"\n🔒 Verschlüsselt: {encrypted[:50]}...")
    
    # Simuliere: Benutzer gibt Passwort erneut ein
    print("\n🔄 Benutzer gibt Passwort erneut ein...")
    
    # Leite Schlüssel mit gleichem Salt ab
    key2, _ = AESEncryption.derive_key_from_password(password, salt)
    enc2 = AESEncryption(master_key=key2)
    
    # Entschlüssele
    decrypted = enc2.decrypt_string(encrypted)
    print(f"🔓 Entschlüsselt: {decrypted}")
    
    print("\n✓ Beispiel erfolgreich!")


def example_flask_integration():
    """
    Beispiel 4: Integration in Flask-Routes
    """
    print("\n" + "=" * 70)
    print("Beispiel 4: Flask-Integration (Code-Beispiel)")
    print("=" * 70)
    
    code = '''
# In app/__init__.py:
from app.encryption import AESEncryption
import os

# Initialisiere Encryption
encryption_key = os.getenv('ENCRYPTION_KEY')
if encryption_key:
    encryption = AESEncryption.from_b64_key(encryption_key)
else:
    raise ValueError("ENCRYPTION_KEY nicht in .env gefunden!")

# In app/routes.py:
from app import encryption
import json

@app.route('/upload_note', methods=['POST'])
@login_required
def upload_note():
    """Upload und verschlüssele eine Notiz"""
    file = request.files['file']
    
    # Lese Datei
    file_data = file.read()
    
    # Metadaten für AAD
    metadata = {
        "filename": file.filename,
        "user_id": current_user.id,
        "upload_time": datetime.now().isoformat()
    }
    
    # Verschlüssele mit Metadaten
    aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
    encrypted_data = encryption.encrypt(file_data, associated_data=aad)
    
    # Speichere in Datenbank
    note = Note(
        user_id=current_user.id,
        filename=file.filename,
        encrypted_data=encrypted_data,
        metadata=json.dumps(metadata)
    )
    db.session.add(note)
    db.session.commit()
    
    return jsonify({"status": "success", "note_id": note.id})

@app.route('/download_note/<int:note_id>')
@login_required
def download_note(note_id):
    """Entschlüssele und sende eine Notiz"""
    note = Note.query.get_or_404(note_id)
    
    # Prüfe Berechtigung
    if note.user_id != current_user.id:
        abort(403)
    
    # Lade Metadaten
    metadata = json.loads(note.metadata)
    
    # Entschlüssele
    aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
    decrypted_data = encryption.decrypt(note.encrypted_data, associated_data=aad)
    
    # Sende Datei
    return send_file(
        io.BytesIO(decrypted_data),
        download_name=metadata['filename'],
        as_attachment=True
    )
'''
    
    print(code)
    print("\n✓ Code-Beispiel angezeigt!")


def main():
    """Hauptfunktion"""
    print("\n" + "=" * 70)
    print("L8teStudy - AES-Verschlüsselung Integration Beispiele")
    print("=" * 70)
    
    while True:
        print("\nWas möchtest du tun?")
        print("1. Neuen Encryption Key generieren")
        print("2. Beispiel: Datei-Verschlüsselung")
        print("3. Beispiel: Datenbank-Verschlüsselung")
        print("4. Beispiel: Passwort-geschützte Verschlüsselung")
        print("5. Beispiel: Flask-Integration (Code)")
        print("6. Alle Beispiele ausführen")
        print("0. Beenden")
        
        choice = input("\nDeine Wahl (0-6): ").strip()
        
        if choice == "1":
            setup_encryption_key()
        elif choice == "2":
            example_file_encryption()
        elif choice == "3":
            example_database_encryption()
        elif choice == "4":
            example_password_protection()
        elif choice == "5":
            example_flask_integration()
        elif choice == "6":
            example_file_encryption()
            example_database_encryption()
            example_password_protection()
            example_flask_integration()
        elif choice == "0":
            print("\nAuf Wiedersehen! 👋")
            break
        else:
            print("\n❌ Ungültige Eingabe!")


if __name__ == "__main__":
    main()
