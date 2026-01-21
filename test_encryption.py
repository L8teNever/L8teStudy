"""
Test-Suite für das Encryption-Modul
Demonstriert alle Funktionen der AES-Verschlüsselung
"""

import os
import sys
import tempfile
from pathlib import Path

# UTF-8 Encoding für Windows-Konsole
if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

# Füge das app-Verzeichnis zum Python-Pfad hinzu
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from encryption import (
    AESEncryption, 
    FileEncryptionManager,
    EncryptionError, 
    DecryptionError,
    generate_encryption_key,
    encrypt_data,
    decrypt_data
)


def test_basic_encryption():
    """Test 1: Basis-Verschlüsselung von Bytes"""
    print("\n=== Test 1: Basis-Verschlüsselung ===")
    
    # Erstelle Encryption-Instanz
    enc = AESEncryption()
    
    # Testdaten
    original_data = "Geheime Notizen aus dem Mathe-Unterricht!".encode('utf-8')
    print(f"Original: {original_data.decode('utf-8')}")
    
    # Verschlüsseln
    encrypted = enc.encrypt(original_data)
    print(f"Verschlüsselt (Länge): {len(encrypted)} bytes")
    print(f"Verschlüsselt (Hex): {encrypted[:32].hex()}...")
    
    # Entschlüsseln
    decrypted = enc.decrypt(encrypted)
    print(f"Entschlüsselt: {decrypted.decode('utf-8')}")
    
    # Validierung
    assert original_data == decrypted, "Entschlüsselung fehlgeschlagen!"
    print("✓ Test erfolgreich!")


def test_string_encryption():
    """Test 2: String-Verschlüsselung mit Base64"""
    print("\n=== Test 2: String-Verschlüsselung ===")
    
    enc = AESEncryption()
    
    original_text = "Dies ist ein geheimer Text für L8teStudy! 🔒"
    print(f"Original: {original_text}")
    
    # Verschlüsseln
    encrypted_text = enc.encrypt_string(original_text)
    print(f"Verschlüsselt (Base64): {encrypted_text[:50]}...")
    
    # Entschlüsseln
    decrypted_text = enc.decrypt_string(encrypted_text)
    print(f"Entschlüsselt: {decrypted_text}")
    
    assert original_text == decrypted_text, "String-Entschlüsselung fehlgeschlagen!"
    print("✓ Test erfolgreich!")


def test_password_based_encryption():
    """Test 3: Passwort-basierte Verschlüsselung"""
    print("\n=== Test 3: Passwort-basierte Verschlüsselung ===")
    
    password = "MeinSuperSicheresPasswort123!"
    print(f"Passwort: {password}")
    
    # Schlüssel aus Passwort ableiten
    key, salt = AESEncryption.derive_key_from_password(password)
    print(f"Salt (Hex): {salt.hex()}")
    print(f"Abgeleiteter Schlüssel (Hex): {key[:16].hex()}...")
    
    # Verschlüsselung mit abgeleitetem Schlüssel
    enc = AESEncryption(master_key=key)
    
    original_data = "Passwort-geschuetzte Daten!".encode('utf-8')
    encrypted = enc.encrypt(original_data)
    decrypted = enc.decrypt(encrypted)
    
    assert original_data == decrypted, "Passwort-basierte Verschlüsselung fehlgeschlagen!"
    
    # Teste mit gleichem Passwort und Salt
    key2, _ = AESEncryption.derive_key_from_password(password, salt)
    enc2 = AESEncryption(master_key=key2)
    decrypted2 = enc2.decrypt(encrypted)
    
    assert original_data == decrypted2, "Wiederherstellung mit gleichem Passwort fehlgeschlagen!"
    print("✓ Test erfolgreich!")


def test_file_encryption():
    """Test 4: Datei-Verschlüsselung"""
    print("\n=== Test 4: Datei-Verschlüsselung ===")
    
    enc = AESEncryption()
    
    # Erstelle temporäre Dateien
    with tempfile.TemporaryDirectory() as tmpdir:
        original_file = os.path.join(tmpdir, "original.txt")
        encrypted_file = os.path.join(tmpdir, "encrypted.bin")
        decrypted_file = os.path.join(tmpdir, "decrypted.txt")
        
        # Schreibe Testdaten
        test_content = "Dies ist eine Test-Datei für L8teStudy!\nZeile 2\nZeile 3"
        with open(original_file, 'w', encoding='utf-8') as f:
            f.write(test_content)
        
        print(f"Original-Datei: {original_file}")
        print(f"Inhalt: {test_content[:50]}...")
        
        # Verschlüssele Datei
        enc.encrypt_file(original_file, encrypted_file)
        print(f"Verschlüsselte Datei: {encrypted_file}")
        print(f"Größe: {os.path.getsize(encrypted_file)} bytes")
        
        # Entschlüssele Datei
        enc.decrypt_file(encrypted_file, decrypted_file)
        print(f"Entschlüsselte Datei: {decrypted_file}")
        
        # Validierung
        with open(decrypted_file, 'r', encoding='utf-8') as f:
            decrypted_content = f.read()
        
        assert test_content == decrypted_content, "Datei-Entschlüsselung fehlgeschlagen!"
        print("✓ Test erfolgreich!")


def test_authenticated_encryption():
    """Test 5: Authentifizierte Verschlüsselung mit AAD"""
    print("\n=== Test 5: Authentifizierte Verschlüsselung (AAD) ===")
    
    enc = AESEncryption()
    
    # Daten und Metadaten
    data = "Wichtige Notizen".encode('utf-8')
    metadata = "user_id=123, file=mathe.pdf".encode('utf-8')
    
    print(f"Daten: {data.decode('utf-8')}")
    print(f"Metadaten (AAD): {metadata.decode('utf-8')}")
    
    # Verschlüsseln mit AAD
    encrypted = enc.encrypt(data, associated_data=metadata)
    
    # Entschlüsseln mit korrekten Metadaten
    decrypted = enc.decrypt(encrypted, associated_data=metadata)
    assert data == decrypted, "Entschlüsselung mit AAD fehlgeschlagen!"
    print("✓ Entschlüsselung mit korrekten Metadaten erfolgreich!")
    
    # Versuche Entschlüsselung mit falschen Metadaten
    try:
        wrong_metadata = "user_id=999, file=fake.pdf".encode('utf-8')
        enc.decrypt(encrypted, associated_data=wrong_metadata)
        print("✗ FEHLER: Entschlüsselung mit falschen Metadaten sollte fehlschlagen!")
    except DecryptionError as e:
        print(f"✓ Entschlüsselung mit falschen Metadaten korrekt abgelehnt: {e}")


def test_file_encryption_with_metadata():
    """Test 6: Datei-Verschlüsselung mit Metadaten"""
    print("\n=== Test 6: Datei-Verschlüsselung mit Metadaten ===")
    
    enc = AESEncryption()
    manager = FileEncryptionManager(enc)
    
    with tempfile.TemporaryDirectory() as tmpdir:
        test_file = os.path.join(tmpdir, "test.txt")
        
        # Erstelle Testdatei
        with open(test_file, 'w', encoding='utf-8') as f:
            f.write("Geheime Notizen von Lena - Mathe Klausur")
        
        # Metadaten
        metadata = {
            "filename": "mathe_notizen.txt",
            "owner": "Lena",
            "subject": "Mathematik",
            "timestamp": "2026-01-21T11:50:00"
        }
        
        print(f"Metadaten: {metadata}")
        
        # Verschlüsseln mit Metadaten
        encrypted = manager.encrypt_with_metadata(test_file, metadata)
        print(f"Verschlüsselt mit Metadaten: {len(encrypted)} bytes")
        
        # Entschlüsseln mit korrekten Metadaten
        decrypted = manager.decrypt_with_metadata(encrypted, metadata)
        print(f"Entschlüsselt: {decrypted.decode('utf-8')}")
        
        # Versuche mit falschen Metadaten
        try:
            wrong_metadata = metadata.copy()
            wrong_metadata["owner"] = "Hacker"
            manager.decrypt_with_metadata(encrypted, wrong_metadata)
            print("✗ FEHLER: Sollte mit falschen Metadaten fehlschlagen!")
        except DecryptionError:
            print("✓ Metadaten-Validierung funktioniert!")


def test_key_persistence():
    """Test 7: Schlüssel-Persistenz (Speichern und Laden)"""
    print("\n=== Test 7: Schlüssel-Persistenz ===")
    
    # Erstelle Verschlüsselung mit neuem Schlüssel
    enc1 = AESEncryption()
    
    # Exportiere Schlüssel
    key_b64 = enc1.get_master_key_b64()
    print(f"Exportierter Schlüssel (Base64): {key_b64[:50]}...")
    
    # Verschlüssele Daten
    data = "Test-Daten fuer Persistenz".encode('utf-8')
    encrypted = enc1.encrypt(data)
    
    # Erstelle neue Instanz mit gleichem Schlüssel
    enc2 = AESEncryption.from_b64_key(key_b64)
    
    # Entschlüssele mit neuer Instanz
    decrypted = enc2.decrypt(encrypted)
    
    assert data == decrypted, "Schlüssel-Persistenz fehlgeschlagen!"
    print("✓ Schlüssel erfolgreich gespeichert und wiederhergestellt!")


def test_utility_functions():
    """Test 8: Utility-Funktionen"""
    print("\n=== Test 8: Utility-Funktionen ===")
    
    # Generiere neuen Schlüssel
    key = generate_encryption_key()
    print(f"Generierter Schlüssel: {key[:50]}...")
    
    # Verschlüssele mit Utility-Funktion
    data = "Test mit Utility-Funktionen".encode('utf-8')
    metadata = {"test": "metadata"}
    
    encrypted = encrypt_data(data, key, metadata)
    print(f"Verschlüsselt: {len(encrypted)} bytes")
    
    # Entschlüssele mit Utility-Funktion
    decrypted = decrypt_data(encrypted, key, metadata)
    print(f"Entschlüsselt: {decrypted.decode('utf-8')}")
    
    assert data == decrypted, "Utility-Funktionen fehlgeschlagen!"
    print("✓ Utility-Funktionen funktionieren!")


def test_tampering_detection():
    """Test 9: Manipulations-Erkennung"""
    print("\n=== Test 9: Manipulations-Erkennung ===")
    
    enc = AESEncryption()
    
    data = "Wichtige Daten".encode('utf-8')
    encrypted = enc.encrypt(data)
    
    # Manipuliere verschlüsselte Daten
    tampered = bytearray(encrypted)
    tampered[-1] ^= 0xFF  # Ändere letztes Byte
    
    try:
        enc.decrypt(bytes(tampered))
        print("✗ FEHLER: Manipulierte Daten sollten erkannt werden!")
    except DecryptionError as e:
        print(f"✓ Manipulation erfolgreich erkannt: {e}")


def run_all_tests():
    """Führt alle Tests aus"""
    print("=" * 70)
    print("L8teStudy - AES-256-GCM Verschlüsselung Test-Suite")
    print("=" * 70)
    
    tests = [
        test_basic_encryption,
        test_string_encryption,
        test_password_based_encryption,
        test_file_encryption,
        test_authenticated_encryption,
        test_file_encryption_with_metadata,
        test_key_persistence,
        test_utility_functions,
        test_tampering_detection
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except Exception as e:
            print(f"\n✗ Test fehlgeschlagen: {test.__name__}")
            print(f"   Fehler: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"Test-Ergebnisse: {passed} erfolgreich, {failed} fehlgeschlagen")
    print("=" * 70)
    
    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
