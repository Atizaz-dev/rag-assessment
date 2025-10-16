from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

plain_password = "admin123"  # Replace with your actual password if different
hashed_password = pwd_context.hash(plain_password)

print("Hashed password:")
print(hashed_password)
