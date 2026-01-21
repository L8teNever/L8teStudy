"""
Drive Integration Initialisierung
Dieses Skript initialisiert die Drive Integration für L8teStudy
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.encryption import generate_encryption_key


def init_drive_integration():
    """Initialisiert die Drive Integration"""
    
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("L8teStudy Drive Integration - Initialisierung")
        print("=" * 60)
        print()
        
        # 1. Check if encryption key exists
        print("1. Überprüfe Verschlüsselungsschlüssel...")
        drive_key = app.config.get('DRIVE_ENCRYPTION_KEY')
        
        if not drive_key:
            print("   ⚠️  DRIVE_ENCRYPTION_KEY nicht in .env gefunden!")
            print("   Generiere neuen Schlüssel...")
            new_key = generate_encryption_key()
            print()
            print("   ✅ Neuer Verschlüsselungsschlüssel generiert!")
            print()
            print("   Füge folgende Zeile zu deiner .env Datei hinzu:")
            print(f"   DRIVE_ENCRYPTION_KEY={new_key}")
            print()
        else:
            print("   ✅ DRIVE_ENCRYPTION_KEY gefunden")
        
        # 2. Check Google Service Account
        print()
        print("2. Überprüfe Google Service Account...")
        service_account_file = app.config.get('GOOGLE_SERVICE_ACCOUNT_FILE')
        
        if not service_account_file:
            print("   ⚠️  GOOGLE_SERVICE_ACCOUNT_FILE nicht in .env gefunden!")
            print()
            print("   Füge folgende Zeile zu deiner .env Datei hinzu:")
            print("   GOOGLE_SERVICE_ACCOUNT_FILE=instance/service-account.json")
            print()
        elif not os.path.exists(service_account_file):
            print(f"   ⚠️  Service Account Datei nicht gefunden: {service_account_file}")
            print()
            print("   Lade die JSON-Datei von Google Cloud Console herunter")
            print("   und speichere sie unter dem angegebenen Pfad.")
            print()
        else:
            print(f"   ✅ Service Account Datei gefunden: {service_account_file}")
        
        # 3. Check encrypted files directory
        print()
        print("3. Überprüfe Speicherverzeichnis...")
        encrypted_path = app.config.get('ENCRYPTED_FILES_PATH', 'instance/encrypted_files')
        
        if not os.path.exists(encrypted_path):
            print(f"   📁 Erstelle Verzeichnis: {encrypted_path}")
            os.makedirs(encrypted_path, exist_ok=True)
            print("   ✅ Verzeichnis erstellt")
        else:
            print(f"   ✅ Verzeichnis existiert: {encrypted_path}")
        
        # 4. Initialize FTS5 table
        print()
        print("4. Initialisiere FTS5-Suchtabelle...")
        
        try:
            from app.drive_search import get_drive_search_service
            
            search_service = get_drive_search_service()
            search_service.ensure_fts_table()
            
            print("   ✅ FTS5-Tabelle erstellt/verifiziert")
            
        except Exception as e:
            print(f"   ⚠️  Fehler beim Erstellen der FTS5-Tabelle: {e}")
            print()
            print("   Hinweis: FTS5-Tabelle wird automatisch beim ersten Sync erstellt")
        
        # 5. Summary
        print()
        print("=" * 60)
        print("Initialisierung abgeschlossen!")
        print("=" * 60)
        print()
        print("Nächste Schritte:")
        print()
        print("1. Stelle sicher, dass alle Konfigurationswerte in .env gesetzt sind")
        print("2. Führe die Datenbank-Migration aus:")
        print("   flask db migrate -m 'Add Drive Integration models'")
        print("   flask db upgrade")
        print()
        print("3. Starte den Server:")
        print("   py run.py")
        print()
        print("4. Füge einen Ordner hinzu:")
        print("   - Gehe zur Drive-Seite")
        print("   - Klicke auf 'Ordner hinzufügen'")
        print("   - Gib die Google Drive Ordner-ID ein")
        print()
        print("Dokumentation: DRIVE_INTEGRATION_README.md")
        print()


if __name__ == '__main__':
    init_drive_integration()
