"""
Data Encryption Service for Production
Encrypts sensitive health data, payment info, and personal details
"""
import os
import base64
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2


class EncryptionService:
    """
    Production-ready encryption for sensitive data
    Uses Fernet (symmetric encryption) with PBKDF2 key derivation
    """
    
    def __init__(self):
        self.encryption_key = self._get_or_generate_key()
        self.cipher = Fernet(self.encryption_key)
    
    def _get_or_generate_key(self) -> bytes:
        """Get encryption key from env or generate for development"""
        key_str = os.getenv('ENCRYPTION_KEY')
        
        if key_str:
            # Production: Use provided key
            return key_str.encode()
        else:
            # Development: Generate temporary key (NOT for production!)
            print("⚠️  WARNING: No ENCRYPTION_KEY set. Using temporary key.")
            print("⚠️  Generate key with: python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'")
            
            # Derive key from a default password (INSECURE - for dev only)
            password = b"angels_ai_dev_key_CHANGE_IN_PRODUCTION"
            salt = b"angels_ai_salt"  # In prod, store salt separately
            kdf = PBKDF2(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(password))
            return key
    
    def encrypt(self, plaintext: str) -> str:
        """
        Encrypt sensitive data
        
        Args:
            plaintext: Data to encrypt (e.g., "Blood type: O+")
        
        Returns:
            Base64-encoded encrypted string
        """
        if not plaintext:
            return ""
        
        try:
            encrypted_bytes = self.cipher.encrypt(plaintext.encode('utf-8'))
            return base64.urlsafe_b64encode(encrypted_bytes).decode('utf-8')
        except Exception as e:
            print(f"❌ Encryption error: {e}")
            raise
    
    def decrypt(self, encrypted_text: str) -> str:
        """
        Decrypt sensitive data
        
        Args:
            encrypted_text: Base64-encoded encrypted string
        
        Returns:
            Original plaintext
        """
        if not encrypted_text:
            return ""
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_text.encode('utf-8'))
            decrypted_bytes = self.cipher.decrypt(encrypted_bytes)
            return decrypted_bytes.decode('utf-8')
        except Exception as e:
            print(f"❌ Decryption error: {e}")
            raise
    
    def encrypt_dict(self, data: dict, fields_to_encrypt: list) -> dict:
        """
        Encrypt specific fields in a dictionary
        
        Args:
            data: Dictionary with sensitive fields
            fields_to_encrypt: List of field names to encrypt
        
        Returns:
            Dictionary with encrypted fields
        """
        encrypted_data = data.copy()
        
        for field in fields_to_encrypt:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))
        
        return encrypted_data
    
    def decrypt_dict(self, data: dict, fields_to_decrypt: list) -> dict:
        """
        Decrypt specific fields in a dictionary
        
        Args:
            data: Dictionary with encrypted fields
            fields_to_decrypt: List of field names to decrypt
        
        Returns:
            Dictionary with decrypted fields
        """
        decrypted_data = data.copy()
        
        for field in fields_to_decrypt:
            if field in decrypted_data and decrypted_data[field]:
                try:
                    decrypted_data[field] = self.decrypt(decrypted_data[field])
                except Exception:
                    # If decryption fails, field might not be encrypted
                    pass
        
        return decrypted_data
    
    @staticmethod
    def generate_new_key() -> str:
        """Generate a new encryption key for production"""
        return Fernet.generate_key().decode()


# Singleton instance
_encryption_service: Optional[EncryptionService] = None


def get_encryption_service() -> EncryptionService:
    """Get or create encryption service instance"""
    global _encryption_service
    if _encryption_service is None:
        _encryption_service = EncryptionService()
    return _encryption_service


# Fields that should be encrypted
SENSITIVE_FIELDS = {
    'student_health': ['blood_type', 'allergies', 'medical_conditions', 'medications'],
    'parent': ['national_id', 'tax_id'],
    'payment': ['card_last_4', 'mobile_money_number'],
    'teacher': ['national_id', 'bank_account']
}


def encrypt_student_health(health_data: dict) -> dict:
    """Encrypt student health record"""
    service = get_encryption_service()
    return service.encrypt_dict(health_data, SENSITIVE_FIELDS['student_health'])


def decrypt_student_health(health_data: dict) -> dict:
    """Decrypt student health record"""
    service = get_encryption_service()
    return service.decrypt_dict(health_data, SENSITIVE_FIELDS['student_health'])
