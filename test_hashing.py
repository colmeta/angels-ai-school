import hashlib
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    # SHA-256 hexdigest is always 64 chars, bypassing bcrypt's 72-byte limit
    pre_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
    print(f"Pre-hash length: {len(pre_hash)}")
    return pwd_context.hash(pre_hash)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    # 1. Try SHA-256 pre-hash
    try:
        pre_hash = hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
        if pwd_context.verify(pre_hash, hashed_password):
            return True
    except Exception as e:
        print(f"SHA-256 verification failed: {e}")
    
    # 2. Try Raw Password (Legacy)
    try:
        # This will fail with ValueError if len(plain_password) > 72
        if pwd_context.verify(plain_password, hashed_password):
            return True
    except ValueError as e:
        print(f"Raw password verification caught ValueError (Expected if > 72 chars): {e}")
    except Exception as e:
        print(f"Raw password verification failed with unexpected error: {e}")
        
    return False

# Test with a very long password
long_password = "a" * 1000
print(f"Testing with password length: {len(long_password)}")

hashed = hash_password(long_password)
print(f"Hashed password: {hashed}")

is_valid = verify_password(long_password, hashed)
print(f"Verification successful: {is_valid}")

# Test with 80 character password
med_password = "b" * 80
hashed_med = hash_password(med_password)
is_valid_med = verify_password(med_password, hashed_med)
print(f"Verification (80 chars) successful: {is_valid_med}")
