import bcrypt

def hash_password() -> str:
    """Hash a password for storing."""
    password = input("Enter password to hash: ")
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

password = hash_password()
print("Password hashed successfully.", password)