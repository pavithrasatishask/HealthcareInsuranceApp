"""
Helper script to generate bcrypt password hashes for testing.
Usage: python generate_password_hash.py
"""
import bcrypt
from config import Config

if __name__ == '__main__':
    print("Password Hash Generator")
    print("=" * 50)
    
    password = input("Enter password to hash: ")
    
    if not password:
        print("Password cannot be empty!")
        exit(1)
    
    # Generate hash with same rounds as configured
    salt = bcrypt.gensalt(rounds=Config.BCRYPT_ROUNDS)
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    print("\nGenerated hash:")
    print(hashed.decode('utf-8'))
    print("\nYou can use this hash in SQL INSERT statements for testing.")
    print("\nExample SQL:")
    print(f"INSERT INTO users (email, password_hash, full_name, role) VALUES")
    print(f"('test@example.com', '{hashed.decode('utf-8')}', 'Test User', 'patient');")

