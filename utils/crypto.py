import os
import base64
from typing import Optional, Union
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# Constants aligned with the TypeScript code.
PBKDF2_ITERATIONS: int = 100000
PBKDF2_KEY_LENGTH: int = 32
PBKDF2_HASH_ALGORITHM = hashes.SHA256()
AES_KEY_LENGTH: int = PBKDF2_KEY_LENGTH
AES_IV_LENGTH: int = 16
AES_BLOCK_SIZE_BITS: int = algorithms.AES.block_size  # type: ignore
SALT_LENGTH: int = 16


def derive_key(password: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    kdf = PBKDF2HMAC(
        algorithm=PBKDF2_HASH_ALGORITHM,
        length=PBKDF2_KEY_LENGTH,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )
    return kdf.derive(password.encode('utf-8'))


def encrypt(data: Union[bytes, str], password: Optional[str] = None) -> bytes:
    if password is None:
        password = os.environ.get("APP_CRYPTO_PASSWORD", None)

    if password is None:
        raise Exception(
            "Encryption password not provided and APP_CRYPTO_PASSWORD environment variable not set."
        )

    if isinstance(data, str):
        data = data.encode('utf-8')

    salt = os.urandom(SALT_LENGTH)
    key = derive_key(password, salt)
    iv = os.urandom(AES_IV_LENGTH)

    aes_algorithm = algorithms.AES(key)
    cipher = Cipher(aes_algorithm, modes.CBC(iv),
                    backend=default_backend())
    encryptor = cipher.encryptor()

    padder = padding.PKCS7(AES_BLOCK_SIZE_BITS).padder()
    padded_data = padder.update(data) + padder.finalize()

    encrypted = encryptor.update(padded_data) + encryptor.finalize()

    # Concatenate salt, IV and encrypted data, then encode in Base64
    return base64.b64encode(salt + iv + encrypted)


def decrypt(token: Union[bytes, str], password: Optional[str] = None) -> bytes:
    if password is None:
        password = os.environ.get("APP_CRYPTO_PASSWORD", None)

    if password is None:
        raise Exception(
            "Decryption password not provided and APP_CRYPTO_PASSWORD environment variable not set."
        )

    decoded_payload = base64.b64decode(token)

    salt = decoded_payload[:SALT_LENGTH]
    iv = decoded_payload[SALT_LENGTH: SALT_LENGTH + AES_IV_LENGTH]
    encrypted_data = decoded_payload[SALT_LENGTH + AES_IV_LENGTH:]

    key = derive_key(password, salt)

    aes_algorithm = algorithms.AES(key)
    cipher = Cipher(aes_algorithm, modes.CBC(iv),
                    backend=default_backend())
    decryptor = cipher.decryptor()

    decrypted_padded = decryptor.update(encrypted_data) + decryptor.finalize()

    unpadder = padding.PKCS7(AES_BLOCK_SIZE_BITS).unpadder()
    decrypted = unpadder.update(decrypted_padded) + unpadder.finalize()

    return decrypted
