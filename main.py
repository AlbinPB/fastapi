from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import engine, Base, SessionLocal
from models import User, Role, UserRole
from typing import Optional
from datetime import datetime 
from database import get_db

# Initialize FastAPI app
app = FastAPI()






# Pydantic models for validation
class UserCreate(BaseModel):
    name: str
    email: str
    age: int

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    age:  Optional[int]

    class Config:
        from_attributes = True

class RoleCreate(BaseModel):
    name: str

class RoleResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class UserRoleCreate(BaseModel):
    user_id: int
    role_id: int

class UserRoleResponse(BaseModel):
    id: int
    user_id: int
    role_id: int
    assigned_at: datetime

    class Config:
        from_attributes = True


class UserRoleResponsejoin(BaseModel):
    assignment_id: int
    user_id: int
    user_name: str
    role_id: int
    role_name: str
    assigned_at: datetime

    class Config:
        from_attributes = True

# Create a new user
@app.post("/users", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    # Check if email exists
    existing_user = db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    
    new_user = User(name=user.name, email=user.email,age = user.age)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@app.put("/users/{user_id}",response_model=UserResponse)
def insert_users(user_id: int,user: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    existing_user.name = user.name
    existing_user.email = user.email
    existing_user.age = user.age
    db.commit()
    db.refresh(existing_user)
    return existing_user

@app.delete("/users/{user_id}")
def insert_users(user_id: int,db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.id == user_id).first()
    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(existing_user)
    db.commit()
    return {"message": "User deleted successfully"}

# Get all users
@app.get("/users", response_model=list[UserResponse])
def get_users(db: Session = Depends(get_db)):
    return db.query(User).all()

# Get a user by ID
@app.get("/users/{user_id}", response_model=UserResponse)
def get_user(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.post("/roles", response_model= RoleResponse)
def post_role(role: RoleCreate, db: Session = Depends(get_db)):
    existing_role = db.query(Role).filter(Role.name == role.name).first()
    if  existing_role:
        raise HTTPException(status_code=404, detail="role exists")
    
    new_role = Role(name = role.name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

@app.get("/roles", response_model=list[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()

@app.get("/roles/{role_id}", response_model=RoleResponse)
def get_role(role_id: int, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")
    return role

@app.put("/roles/{role_id}",response_model=RoleResponse)
def update_role(role_id : int, role : RoleCreate, db: Session = Depends(get_db)):
    existing_role = db.query(Role).filter(Role.id == role_id).first()
    if not existing_role:
        raise HTTPException(status_code=404, detail="Role not found")
    
    existing_role.name = role.name
    db.commit()
    db.refresh(existing_role)
    return existing_role

@app.delete("/roles/{role_id}")
def delete_role(role_id: int, db: Session = Depends(get_db)):
    existing_role = db.query(Role).filter(Role.id == role_id).first()
    if not existing_role:
        raise HTTPException(status_code=404, detail="Role not found")
    db.delete(existing_role)
    db.commit()
    return {"message": "Role deleted successfully"}


@app.post("/user_roles", response_model=UserRoleResponse)
def assign_role_to_user(user_role: UserRoleCreate, db: Session = Depends(get_db)):
    new_user_role = UserRole(user_id=user_role.user_id, role_id=user_role.role_id)
    db.add(new_user_role)
    db.commit()
    db.refresh(new_user_role)
    return new_user_role

@app.get("/user_roles", response_model=list[UserRoleResponse])
def get_user_roles(db: Session = Depends(get_db)):
    return db.query(UserRole).all()

@app.get("/user_roles/{user_id}", response_model=list[UserRoleResponsejoin])

def get_roles_for_user(user_id: int, db: Session = Depends(get_db)):
    user_roles = db.query(UserRole).filter(UserRole.user_id == user_id).all()
    response = []
    for ur in user_roles:
        role = db.query(Role).filter(Role.id == ur.role_id).first()
        user = db.query(User).filter(User.id == ur.user_id).first()
        response.append(
            UserRoleResponsejoin(
                assignment_id=ur.id,
                user_id=user.id,
                user_name=user.name,
                role_id=role.id,
                role_name=role.name,
                assigned_at = ur.assigned_at
            )
        )
    return response
