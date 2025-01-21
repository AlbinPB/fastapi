from sqlalchemy.orm import Session
from database import SessionLocal, engine
from models import User,UserRole


# Create a session
db = SessionLocal()

# Query all rows from the 'users' table
users = db.query(User).all()

# Print the rows
for user in users:
    print(f"ID: {user.id}, user_id: {user.user_id}, role_id: {user.role_id}, date: {user.assigned_at}")
