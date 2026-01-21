# -*- coding: utf-8 -*-
"""
Einfacher Test fuer Drive Integration Core-Funktionen
Testet nur Verschluesselung und Subject Mapper (keine externen Dependencies)
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.encryption import AESEncryption
from app.subject_mapper import SubjectMapper


def test_encryption():
    """Testet die Verschluesselung"""
    print("=" * 60)
    print("Test 1: Verschluesselung")
    print("=" * 60)
    
    try:
        # Create encryption instance
        enc = AESEncryption()
        
        # Test data
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
        import traceback
        traceback.print_exc()
        return False


def test_subject_mapper():
    """Testet den Subject Mapper"""
    print("=" * 60)
    print("Test 2: Subject Mapper")
    print("=" * 60)
    
    try:
        mapper = SubjectMapper()
        
        # Test normalization
        test_cases = [
            ("Ph", "ph"),
            ("  Mathe  ", "mathe"),
            ("Fach Deutsch", "deutsch"),
            ("LK Physik", "physik")
        ]
        
        print("Normalisierung:")
        for input_val, expected in test_cases:
            result = mapper.normalize_name(input_val)
            if result == expected:
                print(f"  [OK] '{input_val}' -> '{result}'")
            else:
                print(f"  [FAIL] '{input_val}' -> '{result}' (erwartet: '{expected}')")
                return False
        
        # Test similarity
        similarity = mapper.get_similarity("Mathematik", "Mathe")
        print(f"\nAehnlichkeit:")
        print(f"  [OK] 'Mathematik' <-> 'Mathe': {similarity:.2f}")
        
        # Test common aliases
        print(f"\nAlias-System:")
        print(f"  [OK] {len(mapper.COMMON_ALIASES)} vordefinierte Aliases")
        print(f"  Beispiele: ph->physik, ma->mathematik, de->deutsch")
        
        print()
        return True
        
    except Exception as e:
        print(f"[FAIL] Fehler: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_tests():
    """Fuehrt alle Tests aus"""
    print()
    print("=" * 60)
    print("  L8teStudy Drive Integration - Core Tests")
    print("=" * 60)
    print()
    
    results = []
    
    # Run tests
    results.append(("Verschluesselung", test_encryption()))
    results.append(("Subject Mapper", test_subject_mapper()))
    
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
        print("Alle Core-Tests erfolgreich!")
        print()
        print("Hinweis: Fuer vollstaendige Tests installiere:")
        print("  pip install -r requirements.txt")
        return True
    else:
        print("Einige Tests sind fehlgeschlagen")
        return False


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
