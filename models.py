from sqlalchemy import Column, Integer, ForeignKey, DateTime, String
from sqlalchemy.orm import relationship
from database import Base  
from datetime import datetime 

class User(Base):
   __tablename__ = "users"
   id = Column(Integer, primary_key=True, index=True)
   name = Column(String, index=True)
   email = Column(String, unique=True, index=True)
   age = Column(Integer) # New column added
   
   

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)


class UserRole(Base):
    __tablename__ = "user_roles"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    role_id = Column(Integer, ForeignKey('roles.id'), nullable=False)
    assigned_at = Column(DateTime, default=datetime.utcnow)  # Example additional column



class Location(Base):
    __tablename__ = "locations"
    id = Column(Integer, primary_key=True, index=True)
    location = Column(String, unique=True, index=True)
