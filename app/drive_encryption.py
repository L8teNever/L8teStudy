"""
Drive Encryption Manager für L8teStudy
Erweitert das Encryption-Modul für Drive-spezifische Funktionen
"""

import os
import hashlib
from typing import Tuple, Optional
from flask import current_app
from .encryption import AESEncryption, EncryptionError, DecryptionError


class DriveEncryptionManager:
    """
    Manager für die Verschlüsselung von Drive-Dateien
    
    Features:
    - Verschlüsselte Speicherung von PDF-Dateien
    - Live-Entschlüsselung im RAM
    - SHA-256 Hash-Berechnung für Change Detection
    - Sichere Dateiverwaltung
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialisiert den Drive Encryption Manager
        
        Args:
            encryption_key: Optional - Base64-kodierter Verschlüsselungsschlüssel
        """
        if encryption_key is None:
            encryption_key = current_app.config.get('DRIVE_ENCRYPTION_KEY')
        
        if not encryption_key:
            raise EncryptionError("DRIVE_ENCRYPTION_KEY not configured")
        
        self.encryption = AESEncryption.from_b64_key(encryption_key)
        self.storage_path = current_app.config.get(
            'ENCRYPTED_FILES_PATH',
            'instance/encrypted_files'
        )
        
        # Ensure storage directory exists
        os.makedirs(self.storage_path, exist_ok=True)
    
    def calculate_file_hash(self, file_path: str) -> str:
        """
        Berechnet SHA-256 Hash einer Datei
        
        Args:
            file_path: Pfad zur Datei
        
        Returns:
            Hex-String des SHA-256 Hashes
        """
        sha256_hash = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            # Read in chunks to handle large files
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        
        return sha256_hash.hexdigest()
    
    def calculate_bytes_hash(self, data: bytes) -> str:
        """
        Berechnet SHA-256 Hash von Bytes
        
        Args:
            data: Daten als bytes
        
        Returns:
            Hex-String des SHA-256 Hashes
        """
        return hashlib.sha256(data).hexdigest()
    
    def encrypt_and_store_file(
        self,
        source_path: str,
        file_id: str,
        metadata: Optional[dict] = None
    ) -> Tuple[str, str, int]:
        """
        Verschlüsselt eine Datei und speichert sie
        
        Args:
            source_path: Pfad zur Quelldatei
            file_id: Eindeutige ID für die Datei (z.B. Google Drive File ID)
            metadata: Optional - Metadaten für AAD
        
        Returns:
            Tuple of (encrypted_path, file_hash, file_size)
        
        Raises:
            EncryptionError: Bei Verschlüsselungsfehlern
        """
        try:
            # Read source file
            with open(source_path, 'rb') as f:
                plaintext = f.read()
            
            # Calculate hash of original file
            file_hash = self.calculate_bytes_hash(plaintext)
            file_size = len(plaintext)
            
            # Prepare metadata for AAD
            if metadata is None:
                metadata = {}
            metadata['file_id'] = file_id
            metadata['file_hash'] = file_hash
            
            # Encrypt
            import json
            aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
            encrypted_data = self.encryption.encrypt(plaintext, associated_data=aad)
            
            # Generate encrypted file path
            encrypted_filename = f"{file_id}.enc"
            encrypted_path = os.path.join(self.storage_path, encrypted_filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(encrypted_path), exist_ok=True)
            
            # Write encrypted file
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            return encrypted_path, file_hash, file_size
            
        except EncryptionError:
            raise
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt and store file: {str(e)}")
    
    def encrypt_and_store_bytes(
        self,
        data: bytes,
        file_id: str,
        metadata: Optional[dict] = None
    ) -> Tuple[str, str, int]:
        """
        Verschlüsselt Bytes und speichert sie
        
        Args:
            data: Daten als bytes
            file_id: Eindeutige ID für die Datei
            metadata: Optional - Metadaten für AAD
        
        Returns:
            Tuple of (encrypted_path, file_hash, file_size)
        
        Raises:
            EncryptionError: Bei Verschlüsselungsfehlern
        """
        try:
            # Calculate hash
            file_hash = self.calculate_bytes_hash(data)
            file_size = len(data)
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
            metadata['file_id'] = file_id
            metadata['file_hash'] = file_hash
            
            # Encrypt
            import json
            aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
            encrypted_data = self.encryption.encrypt(data, associated_data=aad)
            
            # Generate path
            encrypted_filename = f"{file_id}.enc"
            encrypted_path = os.path.join(self.storage_path, encrypted_filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(encrypted_path), exist_ok=True)
            
            # Write
            with open(encrypted_path, 'wb') as f:
                f.write(encrypted_data)
            
            return encrypted_path, file_hash, file_size
            
        except EncryptionError:
            raise
        except Exception as e:
            raise EncryptionError(f"Failed to encrypt and store bytes: {str(e)}")
    
    def decrypt_file_to_memory(
        self,
        encrypted_path: str,
        metadata: Optional[dict] = None
    ) -> bytes:
        """
        Entschlüsselt eine Datei direkt in den RAM (Live-Entschlüsselung)
        
        Args:
            encrypted_path: Pfad zur verschlüsselten Datei
            metadata: Optional - Metadaten für AAD-Validierung
        
        Returns:
            Entschlüsselte Daten als bytes
        
        Raises:
            DecryptionError: Bei Entschlüsselungsfehlern
        """
        try:
            # Read encrypted file
            with open(encrypted_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Prepare AAD if metadata provided
            aad = None
            if metadata:
                import json
                aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
            
            # Decrypt
            plaintext = self.encryption.decrypt(encrypted_data, associated_data=aad)
            
            return plaintext
            
        except DecryptionError:
            raise
        except Exception as e:
            raise DecryptionError(f"Failed to decrypt file to memory: {str(e)}")
    
    def decrypt_file_to_path(
        self,
        encrypted_path: str,
        output_path: str,
        metadata: Optional[dict] = None
    ) -> None:
        """
        Entschlüsselt eine Datei und speichert sie temporär
        
        Args:
            encrypted_path: Pfad zur verschlüsselten Datei
            output_path: Pfad für die entschlüsselte Datei
            metadata: Optional - Metadaten für AAD-Validierung
        
        Raises:
            DecryptionError: Bei Entschlüsselungsfehlern
        """
        try:
            plaintext = self.decrypt_file_to_memory(encrypted_path, metadata)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # Write decrypted file
            with open(output_path, 'wb') as f:
                f.write(plaintext)
                
        except DecryptionError:
            raise
        except Exception as e:
            raise DecryptionError(f"Failed to decrypt file to path: {str(e)}")
    
    def delete_encrypted_file(self, encrypted_path: str) -> None:
        """
        Löscht eine verschlüsselte Datei sicher
        
        Args:
            encrypted_path: Pfad zur verschlüsselten Datei
        """
        try:
            if os.path.exists(encrypted_path):
                os.remove(encrypted_path)
        except Exception as e:
            # Log error but don't raise
            pass
    
    def get_encrypted_file_path(self, file_id: str) -> str:
        """
        Generiert den Pfad für eine verschlüsselte Datei
        
        Args:
            file_id: Datei-ID
        
        Returns:
            Pfad zur verschlüsselten Datei
        """
        encrypted_filename = f"{file_id}.enc"
        return os.path.join(self.storage_path, encrypted_filename)
    
    def file_exists(self, file_id: str) -> bool:
        """
        Prüft, ob eine verschlüsselte Datei existiert
        
        Args:
            file_id: Datei-ID
        
        Returns:
            True wenn die Datei existiert
        """
        path = self.get_encrypted_file_path(file_id)
        return os.path.exists(path)


# Utility function
def get_drive_encryption_manager() -> DriveEncryptionManager:
    """
    Get a Drive Encryption Manager instance
    
    Returns:
        DriveEncryptionManager instance
    """
    return DriveEncryptionManager()
