"""
Integration Example: AES-256-GCM Verschlüsselung in L8teStudy
Zeigt, wie die Verschlüsselung in die Hauptanwendung integriert wird
"""

import os
import io
from pathlib import Path
from flask import Flask, request, send_file, jsonify
from werkzeug.utils import secure_filename
from app.encryption import AESEncryption, FileEncryptionManager, EncryptionError, DecryptionError


# ============================================================================
# KONFIGURATION
# ============================================================================

class Config:
    """Verschlüsselungs-Konfiguration"""
    
    # Master Key aus Umgebungsvariable laden
    ENCRYPTION_MASTER_KEY = os.getenv('ENCRYPTION_MASTER_KEY')
    
    # Wenn kein Key vorhanden, generiere einen neuen (nur für Development!)
    if not ENCRYPTION_MASTER_KEY:
        print("⚠️  WARNUNG: Kein ENCRYPTION_MASTER_KEY gefunden!")
        print("   Generiere temporären Schlüssel für Development...")
        from app.encryption import generate_encryption_key
        ENCRYPTION_MASTER_KEY = generate_encryption_key()
        print(f"   Temporärer Key: {ENCRYPTION_MASTER_KEY}")
        print("   ⚠️  In Produktion MUSS ein permanenter Key verwendet werden!")
    
    # Upload-Verzeichnis
    UPLOAD_FOLDER = Path('uploads_encrypted')
    UPLOAD_FOLDER.mkdir(exist_ok=True)
    
    # Erlaubte Dateitypen
    ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg', 'txt', 'docx'}


# ============================================================================
# HELPER FUNKTIONEN
# ============================================================================

def get_encryption_instance() -> AESEncryption:
    """
    Gibt eine AESEncryption-Instanz mit dem Master Key zurück
    
    Returns:
        AESEncryption: Konfigurierte Encryption-Instanz
    """
    return AESEncryption.from_b64_key(Config.ENCRYPTION_MASTER_KEY)


def allowed_file(filename: str) -> bool:
    """
    Prüft, ob Dateityp erlaubt ist
    
    Args:
        filename: Dateiname
    
    Returns:
        bool: True wenn erlaubt
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS


def get_encrypted_filepath(filename: str) -> Path:
    """
    Gibt den Pfad zur verschlüsselten Datei zurück
    
    Args:
        filename: Original-Dateiname
    
    Returns:
        Path: Pfad zur verschlüsselten Datei
    """
    safe_filename = secure_filename(filename)
    return Config.UPLOAD_FOLDER / f"{safe_filename}.encrypted"


# ============================================================================
# DATEI-VERSCHLÜSSELUNG
# ============================================================================

def encrypt_and_store_file(file_data: bytes, filename: str, metadata: dict = None) -> dict:
    """
    Verschlüsselt eine Datei und speichert sie
    
    Args:
        file_data: Datei-Daten (bytes)
        filename: Original-Dateiname
        metadata: Optional - Metadaten für AAD
    
    Returns:
        dict: Informationen über die gespeicherte Datei
    
    Raises:
        EncryptionError: Bei Verschlüsselungsfehlern
    """
    try:
        # Encryption-Instanz
        enc = get_encryption_instance()
        
        # Metadaten vorbereiten
        if metadata is None:
            metadata = {}
        
        metadata.update({
            'filename': filename,
            'size': len(file_data),
            'encrypted': True
        })
        
        # Verschlüssele mit Metadaten
        if metadata:
            manager = FileEncryptionManager(enc)
            import json
            aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
            encrypted_data = enc.encrypt(file_data, associated_data=aad)
        else:
            encrypted_data = enc.encrypt(file_data)
        
        # Speichere verschlüsselte Datei
        encrypted_path = get_encrypted_filepath(filename)
        with open(encrypted_path, 'wb') as f:
            f.write(encrypted_data)
        
        return {
            'success': True,
            'filename': filename,
            'encrypted_path': str(encrypted_path),
            'original_size': len(file_data),
            'encrypted_size': len(encrypted_data),
            'metadata': metadata
        }
        
    except Exception as e:
        raise EncryptionError(f"Fehler beim Verschlüsseln von {filename}: {str(e)}")


def decrypt_and_retrieve_file(filename: str, metadata: dict = None) -> bytes:
    """
    Entschlüsselt eine gespeicherte Datei
    
    Args:
        filename: Original-Dateiname
        metadata: Optional - Erwartete Metadaten für AAD
    
    Returns:
        bytes: Entschlüsselte Datei-Daten
    
    Raises:
        DecryptionError: Bei Entschlüsselungsfehlern
    """
    try:
        # Lese verschlüsselte Datei
        encrypted_path = get_encrypted_filepath(filename)
        
        if not encrypted_path.exists():
            raise DecryptionError(f"Datei nicht gefunden: {filename}")
        
        with open(encrypted_path, 'rb') as f:
            encrypted_data = f.read()
        
        # Encryption-Instanz
        enc = get_encryption_instance()
        
        # Entschlüssele mit Metadaten
        if metadata:
            import json
            aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
            decrypted_data = enc.decrypt(encrypted_data, associated_data=aad)
        else:
            decrypted_data = enc.decrypt(encrypted_data)
        
        return decrypted_data
        
    except Exception as e:
        raise DecryptionError(f"Fehler beim Entschlüsseln von {filename}: {str(e)}")


# ============================================================================
# FLASK ROUTES (Beispiel-Integration)
# ============================================================================

def create_app():
    """Erstellt Flask-App mit Verschlüsselung"""
    app = Flask(__name__)
    app.config.from_object(Config)
    
    @app.route('/api/upload', methods=['POST'])
    def upload_file():
        """
        Datei-Upload mit automatischer Verschlüsselung
        
        POST /api/upload
        Body: multipart/form-data mit 'file' und optionalen Metadaten
        """
        try:
            # Prüfe, ob Datei vorhanden
            if 'file' not in request.files:
                return jsonify({'error': 'Keine Datei hochgeladen'}), 400
            
            file = request.files['file']
            
            if file.filename == '':
                return jsonify({'error': 'Kein Dateiname'}), 400
            
            if not allowed_file(file.filename):
                return jsonify({'error': 'Dateityp nicht erlaubt'}), 400
            
            # Lese Datei-Daten
            file_data = file.read()
            
            # Metadaten aus Request
            metadata = {
                'owner': request.form.get('owner', 'unknown'),
                'subject': request.form.get('subject', 'general'),
                'filename': file.filename
            }
            
            # Verschlüssele und speichere
            result = encrypt_and_store_file(file_data, file.filename, metadata)
            
            return jsonify({
                'success': True,
                'message': 'Datei erfolgreich verschlüsselt und gespeichert',
                'filename': result['filename'],
                'size': result['original_size'],
                'encrypted_size': result['encrypted_size']
            }), 200
            
        except EncryptionError as e:
            return jsonify({'error': f'Verschlüsselungsfehler: {str(e)}'}), 500
        except Exception as e:
            return jsonify({'error': f'Unerwarteter Fehler: {str(e)}'}), 500
    
    
    @app.route('/api/download/<filename>', methods=['GET'])
    def download_file(filename):
        """
        Datei-Download mit automatischer Entschlüsselung
        
        GET /api/download/<filename>
        Query-Parameter: owner, subject (für Metadaten-Validierung)
        """
        try:
            # Metadaten aus Query-Parametern
            metadata = None
            if request.args.get('validate_metadata') == 'true':
                metadata = {
                    'owner': request.args.get('owner'),
                    'subject': request.args.get('subject'),
                    'filename': filename
                }
            
            # Entschlüssele Datei
            decrypted_data = decrypt_and_retrieve_file(filename, metadata)
            
            # Sende Datei an Benutzer
            return send_file(
                io.BytesIO(decrypted_data),
                download_name=filename,
                as_attachment=True
            )
            
        except DecryptionError as e:
            return jsonify({'error': f'Entschlüsselungsfehler: {str(e)}'}), 500
        except Exception as e:
            return jsonify({'error': f'Unerwarteter Fehler: {str(e)}'}), 500
    
    
    @app.route('/api/files', methods=['GET'])
    def list_files():
        """
        Liste alle verschlüsselten Dateien
        
        GET /api/files
        """
        try:
            files = []
            
            for encrypted_file in Config.UPLOAD_FOLDER.glob('*.encrypted'):
                # Extrahiere Original-Dateiname
                original_name = encrypted_file.stem
                
                files.append({
                    'filename': original_name,
                    'encrypted_path': str(encrypted_file),
                    'size': encrypted_file.stat().st_size
                })
            
            return jsonify({
                'success': True,
                'count': len(files),
                'files': files
            }), 200
            
        except Exception as e:
            return jsonify({'error': f'Fehler: {str(e)}'}), 500
    
    
    @app.route('/api/encryption/status', methods=['GET'])
    def encryption_status():
        """
        Zeigt Verschlüsselungs-Status
        
        GET /api/encryption/status
        """
        enc = get_encryption_instance()
        
        return jsonify({
            'encryption_enabled': True,
            'algorithm': 'AES-256-GCM',
            'key_size': AESEncryption.KEY_SIZE * 8,
            'nonce_size': AESEncryption.NONCE_SIZE * 8,
            'pbkdf2_iterations': AESEncryption.PBKDF2_ITERATIONS,
            'master_key_set': bool(Config.ENCRYPTION_MASTER_KEY),
            'upload_folder': str(Config.UPLOAD_FOLDER),
            'allowed_extensions': list(Config.ALLOWED_EXTENSIONS)
        }), 200
    
    
    return app


# ============================================================================
# COMMAND-LINE TOOLS
# ============================================================================

def cli_encrypt_file(input_path: str, output_path: str = None):
    """
    CLI: Verschlüssele eine Datei
    
    Args:
        input_path: Pfad zur Eingabedatei
        output_path: Optional - Pfad zur Ausgabedatei
    """
    if output_path is None:
        output_path = f"{input_path}.encrypted"
    
    print(f"🔒 Verschlüssele: {input_path}")
    
    try:
        enc = get_encryption_instance()
        enc.encrypt_file(input_path, output_path)
        
        original_size = Path(input_path).stat().st_size
        encrypted_size = Path(output_path).stat().st_size
        
        print(f"✅ Erfolgreich verschlüsselt!")
        print(f"   Original: {original_size:,} bytes")
        print(f"   Verschlüsselt: {encrypted_size:,} bytes")
        print(f"   Gespeichert: {output_path}")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")


def cli_decrypt_file(input_path: str, output_path: str = None):
    """
    CLI: Entschlüssele eine Datei
    
    Args:
        input_path: Pfad zur verschlüsselten Datei
        output_path: Optional - Pfad zur Ausgabedatei
    """
    if output_path is None:
        output_path = input_path.replace('.encrypted', '.decrypted')
    
    print(f"🔓 Entschlüssele: {input_path}")
    
    try:
        enc = get_encryption_instance()
        enc.decrypt_file(input_path, output_path)
        
        decrypted_size = Path(output_path).stat().st_size
        
        print(f"✅ Erfolgreich entschlüsselt!")
        print(f"   Größe: {decrypted_size:,} bytes")
        print(f"   Gespeichert: {output_path}")
        
    except Exception as e:
        print(f"❌ Fehler: {e}")


# ============================================================================
# MAIN
# ============================================================================

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        # CLI-Modus
        command = sys.argv[1]
        
        if command == 'encrypt' and len(sys.argv) >= 3:
            input_file = sys.argv[2]
            output_file = sys.argv[3] if len(sys.argv) > 3 else None
            cli_encrypt_file(input_file, output_file)
        
        elif command == 'decrypt' and len(sys.argv) >= 3:
            input_file = sys.argv[2]
            output_file = sys.argv[3] if len(sys.argv) > 3 else None
            cli_decrypt_file(input_file, output_file)
        
        else:
            print("Usage:")
            print("  python integration_example.py encrypt <input_file> [output_file]")
            print("  python integration_example.py decrypt <input_file> [output_file]")
    
    else:
        # Flask-Server-Modus
        print("=" * 70)
        print("🚀 L8teStudy - Verschlüsselungs-Server")
        print("=" * 70)
        print(f"\n🔐 Verschlüsselung: AES-256-GCM")
        print(f"📁 Upload-Ordner: {Config.UPLOAD_FOLDER}")
        print(f"🔑 Master Key: {'✅ Gesetzt' if Config.ENCRYPTION_MASTER_KEY else '❌ Nicht gesetzt'}")
        print("\n" + "=" * 70)
        
        app = create_app()
        app.run(debug=True, host='0.0.0.0', port=5000)
