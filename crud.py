from sqlalchemy.orm import Session
from models import User, Task
from schemas import UserBase, TaskBase, TaskCreate
from passlib.context import CryptContext

pwd_context = CryptContext(schemes = ['bcrypt'], deprecated = 'auto')


def get_user_by_email(db: Session, email: str):
    user = db.query(User).filter(User.email == email).first()
    
    return user

def create_user(db: Session, user: UserBase):
    hashed_password = pwd_context.hash(user.password)
    db_user = User(username = user.username, email = user.email, full_name = user.full_name, hashed_password = hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_task(db: Session, task: TaskBase):
    db_task = Task(title = task.title, user_id = task.user_id)
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

def authenticate_user(db: Session, username: str, password: str):
    user = get_user_by_email(db, username)
    if not user:
        return False
    if not pwd_context.verify(password, user.hashed_password):
        return False
    return user

def update_task(db: Session, task_id: int, task_update: TaskCreate, current_user: User):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    if db_task:
        db_task.title = task_update.title
        db.commit()
        db.refresh(db_task)
    
    return db_task

def find_task(db: Session, task_id: int, current_user: User):
    db_task = db.query(Task).filter(Task.id == task_id, Task.user_id == current_user.id).first()
    
    return db_task