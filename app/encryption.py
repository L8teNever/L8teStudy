"""
Encryption Module für L8teStudy
Implementiert AES-256-GCM Verschlüsselung für sichere Datenspeicherung
"""

import os
import base64
from typing import Tuple, Optional
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidTag


class EncryptionError(Exception):
    """Custom exception für Verschlüsselungsfehler"""
    pass


class DecryptionError(Exception):
    """Custom exception für Entschlüsselungsfehler"""
    pass


class AESEncryption:
    """
    AES-256-GCM Verschlüsselung für L8teStudy
    
    Features:
    - AES-256-GCM (Authenticated Encryption)
    - Automatische Nonce-Generierung
    - PBKDF2 Key Derivation
    - Sichere Schlüsselverwaltung
    """
    
    # Konstanten für die Verschlüsselung
    KEY_SIZE = 32  # 256 bits
    NONCE_SIZE = 12  # 96 bits (empfohlen für GCM)
    SALT_SIZE = 16  # 128 bits
    PBKDF2_ITERATIONS = 100000  # Anzahl der Iterationen für Key Derivation
    
    def __init__(self, master_key: Optional[bytes] = None):
        """
        Initialisiert das Verschlüsselungssystem
        
        Args:
            master_key: Optional - Master Key als bytes. Wenn None, wird ein neuer generiert.
        """
        if master_key is None:
            self.master_key = self._generate_key()
        else:
            if len(master_key) != self.KEY_SIZE:
                raise EncryptionError(f"Master Key muss {self.KEY_SIZE} bytes lang sein")
            self.master_key = master_key
    
    @staticmethod
    def _generate_key() -> bytes:
        """
        Generiert einen kryptographisch sicheren zufälligen Schlüssel
        
        Returns:
            bytes: 256-bit Schlüssel
        """
        return os.urandom(AESEncryption.KEY_SIZE)
    
    @staticmethod
    def derive_key_from_password(password: str, salt: Optional[bytes] = None) -> Tuple[bytes, bytes]:
        """
        Leitet einen Verschlüsselungsschlüssel aus einem Passwort ab
        
        Args:
            password: Das Benutzerpasswort
            salt: Optional - Salt für die Key Derivation. Wenn None, wird ein neuer generiert.
        
        Returns:
            Tuple[bytes, bytes]: (abgeleiteter Schlüssel, verwendetes Salt)
        """
        if salt is None:
            salt = os.urandom(AESEncryption.SALT_SIZE)
        
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=AESEncryption.KEY_SIZE,
            salt=salt,
            iterations=AESEncryption.PBKDF2_ITERATIONS,
            backend=default_backend()
        )
        
        key = kdf.derive(password.encode('utf-8'))
        return key, salt
    
    def encrypt(self, plaintext: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """
        Verschlüsselt Daten mit AES-256-GCM
        
        Args:
            plaintext: Die zu verschlüsselnden Daten
            associated_data: Optional - Zusätzliche authentifizierte Daten (AAD)
        
        Returns:
            bytes: Verschlüsselte Daten im Format: nonce + ciphertext + tag
        
        Raises:
            EncryptionError: Bei Verschlüsselungsfehlern
        """
        try:
            # Generiere eine zufällige Nonce
            nonce = os.urandom(self.NONCE_SIZE)
            
            # Erstelle AESGCM Cipher
            aesgcm = AESGCM(self.master_key)
            
            # Verschlüssele die Daten
            ciphertext = aesgcm.encrypt(nonce, plaintext, associated_data)
            
            # Format: nonce + ciphertext (enthält bereits den Auth-Tag)
            return nonce + ciphertext
            
        except Exception as e:
            raise EncryptionError(f"Verschlüsselung fehlgeschlagen: {str(e)}")
    
    def decrypt(self, encrypted_data: bytes, associated_data: Optional[bytes] = None) -> bytes:
        """
        Entschlüsselt AES-256-GCM verschlüsselte Daten
        
        Args:
            encrypted_data: Die verschlüsselten Daten (nonce + ciphertext + tag)
            associated_data: Optional - Zusätzliche authentifizierte Daten (AAD)
        
        Returns:
            bytes: Entschlüsselte Daten
        
        Raises:
            DecryptionError: Bei Entschlüsselungsfehlern oder Authentifizierungsfehlern
        """
        try:
            # Extrahiere Nonce und Ciphertext
            nonce = encrypted_data[:self.NONCE_SIZE]
            ciphertext = encrypted_data[self.NONCE_SIZE:]
            
            # Erstelle AESGCM Cipher
            aesgcm = AESGCM(self.master_key)
            
            # Entschlüssele die Daten
            plaintext = aesgcm.decrypt(nonce, ciphertext, associated_data)
            
            return plaintext
            
        except InvalidTag:
            raise DecryptionError("Authentifizierung fehlgeschlagen - Daten wurden möglicherweise manipuliert")
        except Exception as e:
            raise DecryptionError(f"Entschlüsselung fehlgeschlagen: {str(e)}")
    
    def encrypt_file(self, input_path: str, output_path: str, 
                     associated_data: Optional[bytes] = None) -> None:
        """
        Verschlüsselt eine Datei
        
        Args:
            input_path: Pfad zur Eingabedatei
            output_path: Pfad zur verschlüsselten Ausgabedatei
            associated_data: Optional - Zusätzliche authentifizierte Daten
        
        Raises:
            EncryptionError: Bei Verschlüsselungsfehlern
        """
        try:
            # Lese die Datei
            with open(input_path, 'rb') as f:
                plaintext = f.read()
            
            # Verschlüssele die Daten
            encrypted_data = self.encrypt(plaintext, associated_data)
            
            # Schreibe die verschlüsselten Daten
            with open(output_path, 'wb') as f:
                f.write(encrypted_data)
                
        except EncryptionError:
            raise
        except Exception as e:
            raise EncryptionError(f"Datei-Verschlüsselung fehlgeschlagen: {str(e)}")
    
    def decrypt_file(self, input_path: str, output_path: str,
                     associated_data: Optional[bytes] = None) -> None:
        """
        Entschlüsselt eine Datei
        
        Args:
            input_path: Pfad zur verschlüsselten Datei
            output_path: Pfad zur entschlüsselten Ausgabedatei
            associated_data: Optional - Zusätzliche authentifizierte Daten
        
        Raises:
            DecryptionError: Bei Entschlüsselungsfehlern
        """
        try:
            # Lese die verschlüsselte Datei
            with open(input_path, 'rb') as f:
                encrypted_data = f.read()
            
            # Entschlüssele die Daten
            plaintext = self.decrypt(encrypted_data, associated_data)
            
            # Schreibe die entschlüsselten Daten
            with open(output_path, 'wb') as f:
                f.write(plaintext)
                
        except DecryptionError:
            raise
        except Exception as e:
            raise DecryptionError(f"Datei-Entschlüsselung fehlgeschlagen: {str(e)}")
    
    def encrypt_string(self, text: str, associated_data: Optional[bytes] = None) -> str:
        """
        Verschlüsselt einen String und gibt ihn Base64-kodiert zurück
        
        Args:
            text: Der zu verschlüsselnde Text
            associated_data: Optional - Zusätzliche authentifizierte Daten
        
        Returns:
            str: Base64-kodierter verschlüsselter Text
        """
        plaintext = text.encode('utf-8')
        encrypted_data = self.encrypt(plaintext, associated_data)
        return base64.b64encode(encrypted_data).decode('utf-8')
    
    def decrypt_string(self, encrypted_text: str, associated_data: Optional[bytes] = None) -> str:
        """
        Entschlüsselt einen Base64-kodierten verschlüsselten String
        
        Args:
            encrypted_text: Base64-kodierter verschlüsselter Text
            associated_data: Optional - Zusätzliche authentifizierte Daten
        
        Returns:
            str: Entschlüsselter Text
        """
        encrypted_data = base64.b64decode(encrypted_text.encode('utf-8'))
        plaintext = self.decrypt(encrypted_data, associated_data)
        return plaintext.decode('utf-8')
    
    def get_master_key_b64(self) -> str:
        """
        Gibt den Master Key Base64-kodiert zurück (für sichere Speicherung)
        
        Returns:
            str: Base64-kodierter Master Key
        """
        return base64.b64encode(self.master_key).decode('utf-8')
    
    @classmethod
    def from_b64_key(cls, b64_key: str) -> 'AESEncryption':
        """
        Erstellt eine AESEncryption-Instanz aus einem Base64-kodierten Schlüssel
        
        Args:
            b64_key: Base64-kodierter Schlüssel
        
        Returns:
            AESEncryption: Neue Instanz mit dem gegebenen Schlüssel
        """
        master_key = base64.b64decode(b64_key.encode('utf-8'))
        return cls(master_key=master_key)


class FileEncryptionManager:
    """
    Manager für die Verschlüsselung von Dateien mit Metadaten
    """
    
    def __init__(self, encryption: AESEncryption):
        """
        Initialisiert den FileEncryptionManager
        
        Args:
            encryption: AESEncryption-Instanz
        """
        self.encryption = encryption
    
    def encrypt_with_metadata(self, file_path: str, metadata: dict) -> bytes:
        """
        Verschlüsselt eine Datei mit Metadaten als AAD
        
        Args:
            file_path: Pfad zur Datei
            metadata: Metadaten (z.B. Dateiname, Besitzer, Zeitstempel)
        
        Returns:
            bytes: Verschlüsselte Daten
        """
        # Konvertiere Metadaten zu bytes für AAD
        import json
        aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
        
        with open(file_path, 'rb') as f:
            plaintext = f.read()
        
        return self.encryption.encrypt(plaintext, associated_data=aad)
    
    def decrypt_with_metadata(self, encrypted_data: bytes, metadata: dict) -> bytes:
        """
        Entschlüsselt Daten mit Metadaten-Validierung
        
        Args:
            encrypted_data: Verschlüsselte Daten
            metadata: Erwartete Metadaten
        
        Returns:
            bytes: Entschlüsselte Daten
        
        Raises:
            DecryptionError: Wenn Metadaten nicht übereinstimmen
        """
        import json
        aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
        
        return self.encryption.decrypt(encrypted_data, associated_data=aad)


# Utility-Funktionen für einfache Verwendung

def generate_encryption_key() -> str:
    """
    Generiert einen neuen Verschlüsselungsschlüssel
    
    Returns:
        str: Base64-kodierter Schlüssel
    """
    enc = AESEncryption()
    return enc.get_master_key_b64()


def encrypt_data(data: bytes, key: str, metadata: Optional[dict] = None) -> bytes:
    """
    Verschlüsselt Daten mit einem gegebenen Schlüssel
    
    Args:
        data: Zu verschlüsselnde Daten
        key: Base64-kodierter Schlüssel
        metadata: Optional - Metadaten für AAD
    
    Returns:
        bytes: Verschlüsselte Daten
    """
    enc = AESEncryption.from_b64_key(key)
    
    if metadata:
        import json
        aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
        return enc.encrypt(data, associated_data=aad)
    
    return enc.encrypt(data)


def decrypt_data(encrypted_data: bytes, key: str, metadata: Optional[dict] = None) -> bytes:
    """
    Entschlüsselt Daten mit einem gegebenen Schlüssel
    
    Args:
        encrypted_data: Verschlüsselte Daten
        key: Base64-kodierter Schlüssel
        metadata: Optional - Metadaten für AAD
    
    Returns:
        bytes: Entschlüsselte Daten
    """
    enc = AESEncryption.from_b64_key(key)
    
    if metadata:
        import json
        aad = json.dumps(metadata, sort_keys=True).encode('utf-8')
        return enc.decrypt(encrypted_data, associated_data=aad)
    
    return enc.decrypt(encrypted_data)
