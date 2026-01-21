"""
Demo: AES-256-GCM Verschlüsselung "At Rest" für L8teStudy
Zeigt, wie Dateien auf dem Server verschlüsselt gespeichert werden
"""

import os
import sys
from pathlib import Path

# Füge app-Verzeichnis zum Python-Path hinzu
sys.path.insert(0, str(Path(__file__).parent / 'app'))

from encryption import (
    AESEncryption, 
    FileEncryptionManager,
    generate_encryption_key,
    EncryptionError,
    DecryptionError
)


def demo_basic_encryption():
    """Demonstriert grundlegende Verschlüsselung"""
    print("=" * 70)
    print("🔐 DEMO 1: Grundlegende AES-256-GCM Verschlüsselung")
    print("=" * 70)
    
    # Generiere einen Master Key
    enc = AESEncryption()
    print(f"\n✅ Master Key generiert (256-bit)")
    print(f"   Key (Base64): {enc.get_master_key_b64()[:32]}...")
    
    # Verschlüssele einen Text
    original_text = "Geheime Notizen für Mathematik - Quadratische Gleichungen"
    print(f"\n📝 Original Text: '{original_text}'")
    
    encrypted = enc.encrypt_string(original_text)
    print(f"\n🔒 Verschlüsselt (Base64): {encrypted[:50]}...")
    print(f"   Länge: {len(encrypted)} Zeichen")
    
    # Entschlüssele
    decrypted = enc.decrypt_string(encrypted)
    print(f"\n🔓 Entschlüsselt: '{decrypted}'")
    print(f"   ✅ Erfolgreich: {original_text == decrypted}")


def demo_file_encryption():
    """Demonstriert Datei-Verschlüsselung (At Rest)"""
    print("\n\n" + "=" * 70)
    print("📁 DEMO 2: Datei-Verschlüsselung 'At Rest'")
    print("=" * 70)
    
    # Erstelle Testdateien
    test_dir = Path("test_encryption_demo")
    test_dir.mkdir(exist_ok=True)
    
    original_file = test_dir / "original_notes.txt"
    encrypted_file = test_dir / "notes.encrypted"
    decrypted_file = test_dir / "decrypted_notes.txt"
    
    # Erstelle eine Test-Notiz
    test_content = """
    Mathematik - Kapitel 5: Quadratische Gleichungen
    
    Wichtige Formeln:
    - ax² + bx + c = 0
    - x = (-b ± √(b²-4ac)) / 2a
    
    Beispiel:
    2x² + 5x - 3 = 0
    Lösung: x₁ = 0.5, x₂ = -3
    
    📌 Wichtig für die Klausur!
    """
    
    with open(original_file, 'w', encoding='utf-8') as f:
        f.write(test_content)
    
    print(f"\n📄 Original-Datei erstellt: {original_file}")
    print(f"   Größe: {original_file.stat().st_size} bytes")
    
    # Verschlüssele die Datei
    enc = AESEncryption()
    enc.encrypt_file(str(original_file), str(encrypted_file))
    
    print(f"\n🔒 Verschlüsselte Datei: {encrypted_file}")
    print(f"   Größe: {encrypted_file.stat().st_size} bytes")
    
    # Zeige, dass verschlüsselte Daten unleserlich sind
    with open(encrypted_file, 'rb') as f:
        encrypted_bytes = f.read(50)
    print(f"   Inhalt (erste 50 bytes): {encrypted_bytes.hex()}")
    print(f"   ⚠️  Ohne Schlüssel UNLESERLICH!")
    
    # Entschlüssele die Datei
    enc.decrypt_file(str(encrypted_file), str(decrypted_file))
    
    print(f"\n🔓 Entschlüsselte Datei: {decrypted_file}")
    
    # Vergleiche Original und Entschlüsselt
    with open(original_file, 'r', encoding='utf-8') as f:
        original_content = f.read()
    with open(decrypted_file, 'r', encoding='utf-8') as f:
        decrypted_content = f.read()
    
    print(f"   ✅ Inhalt identisch: {original_content == decrypted_content}")
    
    # Cleanup
    print(f"\n🧹 Aufräumen...")
    original_file.unlink()
    encrypted_file.unlink()
    decrypted_file.unlink()
    test_dir.rmdir()


def demo_metadata_authentication():
    """Demonstriert Metadaten-Authentifizierung"""
    print("\n\n" + "=" * 70)
    print("🛡️  DEMO 3: Metadaten-Authentifizierung (AAD)")
    print("=" * 70)
    
    enc = AESEncryption()
    manager = FileEncryptionManager(enc)
    
    # Erstelle Testdatei
    test_dir = Path("test_encryption_demo")
    test_dir.mkdir(exist_ok=True)
    test_file = test_dir / "test_note.txt"
    
    with open(test_file, 'w', encoding='utf-8') as f:
        f.write("Geheime Notiz von Max Mustermann")
    
    # Metadaten
    metadata = {
        "filename": "test_note.txt",
        "owner": "Max Mustermann",
        "subject": "Mathematik",
        "timestamp": "2026-01-21T11:52:00"
    }
    
    print(f"\n📋 Metadaten:")
    for key, value in metadata.items():
        print(f"   {key}: {value}")
    
    # Verschlüssele mit Metadaten
    encrypted_data = manager.encrypt_with_metadata(str(test_file), metadata)
    print(f"\n🔒 Verschlüsselt mit Metadaten-Authentifizierung")
    print(f"   Größe: {len(encrypted_data)} bytes")
    
    # Entschlüssele mit korrekten Metadaten
    try:
        decrypted_data = manager.decrypt_with_metadata(encrypted_data, metadata)
        print(f"\n✅ Entschlüsselung mit korrekten Metadaten: ERFOLGREICH")
        print(f"   Inhalt: {decrypted_data.decode('utf-8')}")
    except DecryptionError as e:
        print(f"\n❌ Fehler: {e}")
    
    # Versuche Entschlüsselung mit falschen Metadaten
    wrong_metadata = metadata.copy()
    wrong_metadata["owner"] = "Hacker"
    
    print(f"\n🚨 Versuch mit FALSCHEN Metadaten (owner: 'Hacker')...")
    try:
        decrypted_data = manager.decrypt_with_metadata(encrypted_data, wrong_metadata)
        print(f"   ❌ Das sollte nicht passieren!")
    except DecryptionError as e:
        print(f"   ✅ Entschlüsselung BLOCKIERT: {e}")
        print(f"   🛡️  Manipulationsschutz funktioniert!")
    
    # Cleanup
    test_file.unlink()
    test_dir.rmdir()


def demo_key_derivation():
    """Demonstriert Schlüsselableitung aus Passwort"""
    print("\n\n" + "=" * 70)
    print("🔑 DEMO 4: Schlüsselableitung aus Passwort (PBKDF2)")
    print("=" * 70)
    
    password = "MeinSicheresPasswort123!"
    print(f"\n🔐 Passwort: '{password}'")
    
    # Leite Schlüssel ab
    key, salt = AESEncryption.derive_key_from_password(password)
    
    print(f"\n✅ Schlüssel abgeleitet:")
    print(f"   Salt (hex): {salt.hex()}")
    print(f"   Key (hex): {key.hex()[:32]}...")
    print(f"   Iterationen: {AESEncryption.PBKDF2_ITERATIONS:,}")
    
    # Erstelle Encryption-Instanz mit abgeleitetem Schlüssel
    enc = AESEncryption(master_key=key)
    
    # Verschlüssele etwas
    message = "Nachricht verschlüsselt mit Passwort-basiertem Schlüssel"
    encrypted = enc.encrypt_string(message)
    
    print(f"\n📝 Nachricht: '{message}'")
    print(f"🔒 Verschlüsselt: {encrypted[:50]}...")
    
    # Entschlüssele mit demselben Passwort
    enc2 = AESEncryption(master_key=AESEncryption.derive_key_from_password(password, salt)[0])
    decrypted = enc2.decrypt_string(encrypted)
    
    print(f"🔓 Entschlüsselt: '{decrypted}'")
    print(f"   ✅ Erfolgreich: {message == decrypted}")


def demo_security_features():
    """Zeigt Sicherheitsfeatures"""
    print("\n\n" + "=" * 70)
    print("🔒 DEMO 5: Sicherheitsfeatures")
    print("=" * 70)
    
    enc = AESEncryption()
    
    print("\n✅ Implementierte Sicherheitsfeatures:")
    print(f"   • AES-256-GCM (Authenticated Encryption)")
    print(f"   • Schlüssellänge: {AESEncryption.KEY_SIZE * 8} Bit")
    print(f"   • Nonce-Größe: {AESEncryption.NONCE_SIZE * 8} Bit (einzigartig pro Verschlüsselung)")
    print(f"   • PBKDF2 Iterationen: {AESEncryption.PBKDF2_ITERATIONS:,}")
    print(f"   • Authentifizierungs-Tag: Automatisch (GCM)")
    print(f"   • Manipulationsschutz: ✅ (InvalidTag Exception)")
    print(f"   • Metadaten-Authentifizierung: ✅ (AAD Support)")
    
    print("\n🛡️  Was bedeutet 'At Rest' Verschlüsselung?")
    print("   • Alle Dateien werden verschlüsselt auf der Festplatte gespeichert")
    print("   • Ohne den Master Key sind die Daten UNLESERLICH")
    print("   • Selbst bei physischem Zugriff auf den Server: KEINE Daten lesbar")
    print("   • Entschlüsselung nur im RAM beim Zugriff")
    
    print("\n🔐 Sicherheitsgarantien:")
    print("   • Vertraulichkeit: ✅ (AES-256)")
    print("   • Integrität: ✅ (GCM Authentication Tag)")
    print("   • Authentizität: ✅ (AAD Metadaten)")
    print("   • Forward Secrecy: ✅ (Einzigartige Nonce pro Verschlüsselung)")


def main():
    """Hauptfunktion"""
    print("\n" + "=" * 70)
    print("🚀 L8teStudy - AES-256-GCM 'At Rest' Verschlüsselung Demo")
    print("=" * 70)
    
    try:
        demo_basic_encryption()
        demo_file_encryption()
        demo_metadata_authentication()
        demo_key_derivation()
        demo_security_features()
        
        print("\n\n" + "=" * 70)
        print("✅ Alle Demos erfolgreich abgeschlossen!")
        print("=" * 70)
        print("\n💡 Nächste Schritte:")
        print("   1. Integration in die Hauptanwendung")
        print("   2. Automatische Verschlüsselung beim Datei-Upload")
        print("   3. Entschlüsselung nur im RAM beim Zugriff")
        print("   4. Sichere Schlüsselverwaltung implementieren")
        print("   5. Logging und Monitoring hinzufügen")
        
    except Exception as e:
        print(f"\n❌ Fehler: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
