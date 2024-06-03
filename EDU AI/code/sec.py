import secrets

# Generate a random 32-byte secret key (suitable for many applications)
secret_key = secrets.token_bytes(32)

# Generate a URL-safe random string for session management
