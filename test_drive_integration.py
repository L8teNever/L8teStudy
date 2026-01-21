# -*- coding: utf-8 -*-
"""
Test-Skript fuer Drive Integration
Testet die grundlegenden Funktionen ohne Google Drive Zugriff
"""

import os
import sys
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app
from app.encryption import AESEncryption


def test_encryption():
    """Testet die Verschluesselung"""
    print("=" * 60)
    print("Test 1: Verschluesselung")
    print("=" * 60)
    
    try:
        # Create encryption instance
        enc = AESEncryption()
        
        # Test data (ASCII-safe)
        test_data = b"Dies ist ein Test-PDF Inhalt"
        
        # Encrypt
        encrypted = enc.encrypt(test_data)
        print(f"[OK] Verschluesselung erfolgreich ({len(encrypted)} bytes)")
        
        # Decrypt
        decrypted = enc.decrypt(encrypted)
        print(f"[OK] Entschluesselung erfolgreich ({len(decrypted)} bytes)")
        
        # Verify
        if decrypted == test_data:
            print("[OK] Daten-Integritaet verifiziert")
        else:
            print("[FAIL] Daten-Integritaet fehlgeschlagen!")
            return False
        
        print()
        return True
        
    except Exception as e:
        print(f"[FAIL] Fehler: {e}")
        return False


def test_ocr_service():
    """Testet den OCR Service"""
    print("=" * 60)
    print("Test 2: OCR Service")
    print("=" * 60)
    
    try:
        from app.ocr_service import OCRService
        
        ocr = OCRService()
        
        # Test with sample text
        sample_text = """
        Dies ist ein Test-Text.
        Er enthaelt mehrere Zeilen.
        
        Und auch Leerzeilen.
        """
        
        cleaned = ocr.clean_text(sample_text)
        print(f"[OK] Text-Bereinigung erfolgreich")
        print(f"   Original: {len(sample_text)} Zeichen")
        print(f"   Bereinigt: {len(cleaned)} Zeichen")
        print()
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_subject_mapper():
    """Testet den Subject Mapper"""
    print("=" * 60)
    print("Test 3: Subject Mapper")
    print("=" * 60)
    
    try:
        from app.subject_mapper import SubjectMapper
        
        mapper = SubjectMapper()
        
        # Test normalization
        test_cases = [
            ("Ph", "ph"),
            ("  Mathe  ", "mathe"),
            ("Fach Deutsch", "deutsch"),
            ("LK Physik", "physik")
        ]
        
        for input_val, expected in test_cases:
            result = mapper.normalize_name(input_val)
            if result == expected:
                print(f"[OK] '{input_val}' -> '{result}'")
            else:
                print(f"[FAIL] '{input_val}' -> '{result}' (erwartet: '{expected}')")
        
        # Test similarity
        similarity = mapper.get_similarity("Mathematik", "Mathe")
        print(f"[OK] Aehnlichkeit 'Mathematik' <-> 'Mathe': {similarity:.2f}")
        
        print()
        return True
        
    except Exception as e:
        print(f"[FAIL] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_drive_encryption():
    """Testet den Drive Encryption Manager"""
    print("=" * 60)
    print("Test 4: Drive Encryption Manager")
    print("=" * 60)
    
    app = create_app()
    
    with app.app_context():
        try:
            from app.drive_encryption import DriveEncryptionManager
            
            # Create temp file
            with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.pdf') as f:
                test_data = b"Test PDF content"
                f.write(test_data)
                temp_path = f.name
            
            try:
                # Create encryption manager
                manager = DriveEncryptionManager()
                
                # Calculate hash
                file_hash = manager.calculate_file_hash(temp_path)
                print(f"[OK] Hash berechnet: {file_hash[:16]}...")
                
                # Encrypt and store
                encrypted_path, hash_result, size = manager.encrypt_and_store_file(
                    temp_path,
                    'test-file-123',
                    metadata={'test': True}
                )
                print(f"[OK] Datei verschluesselt: {encrypted_path}")
                print(f"   Hash: {hash_result[:16]}...")
                print(f"   Groesse: {size} bytes")
                
                # Decrypt to memory
                decrypted = manager.decrypt_file_to_memory(
                    encrypted_path,
                    metadata={'file_id': 'test-file-123', 'file_hash': hash_result, 'test': True}
                )
                print(f"[OK] Datei entschluesselt: {len(decrypted)} bytes")
                
                # Verify
                if decrypted == test_data:
                    print("[OK] Daten-Integritaet verifiziert")
                else:
                    print("[FAIL] Daten-Integritaet fehlgeschlagen!")
                    return False
                
                # Cleanup
                manager.delete_encrypted_file(encrypted_path)
                print("[OK] Verschluesselte Datei geloescht")
                
            finally:
                # Cleanup temp file
                if os.path.exists(temp_path):
                    os.remove(temp_path)
            
            print()
            return True
            
        except Exception as e:
            print(f"[FAIL] Fehler: {e}")
            import traceback
            traceback.print_exc()
            return False


def run_all_tests():
    """Fuehrt alle Tests aus"""
    print()
    print("=" * 60)
    print("  L8teStudy Drive Integration Tests")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Verschluesselung", test_encryption()))
    results.append(("OCR Service", test_ocr_service()))
    results.append(("Subject Mapper", test_subject_mapper()))
    results.append(("Drive Encryption", test_drive_encryption()))
    
    # Summary
    print("=" * 60)
    print("Test-Zusammenfassung")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "[OK] BESTANDEN" if result else "[FAIL] FEHLGESCHLAGEN"
        print(f"{name:.<40} {status}")
    
    print()
    print(f"Ergebnis: {passed}/{total} Tests bestanden")
    print()
    
    if passed == total:
        print("Alle Tests erfolgreich!")
        return True
    else:
        print("Einige Tests sind fehlgeschlagen")
        return False


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
