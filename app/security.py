from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

password_hasher = PasswordHasher()

def password_hash(mdp:str)->str:
    return password_hasher.hash(mdp)

def verify_password(mdp:str, mdp_hash:str)->bool:
    try:
        password_hasher.verify(mdp_hash, mdp)
        return True
    except VerifyMismatchError:
        return False