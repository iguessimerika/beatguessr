import hashlib

def hash_password(password):
    hashed = hashlib.sha256(password.encode()).hexdigest()
    
    return hashed

def check_password(user_entry, db_entry):
    hashed_user_entry = hash_password(user_entry)
    
    print(f"user pw hash: {hashed_user_entry}")
    print(f"db pw hash: {db_entry}")
    
    return db_entry == hashed_user_entry