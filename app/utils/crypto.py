import os
from cryptography .fernet import Fernet
ENCRYPTION_KEY =os .getenv ('ENCRYPTION_KEY')
fernet =Fernet (ENCRYPTION_KEY .encode ())
def encrypt_password (password :str )->str :
    encrypted_password =fernet .encrypt (password .encode ())
    return encrypted_password .decode ()
def decrypt_password (encrypted_password :str )->str :
    decrypted_password =fernet .decrypt (encrypted_password .encode ())
    return decrypted_password .decode ()