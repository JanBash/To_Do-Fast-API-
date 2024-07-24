from fastapi import (
    FastAPI,
    Depends,
    HTTPException,
    status,
    Request,
    APIRouter
)
from fastapi.security import (
    OAuth2PasswordBearer,
)
from sqlalchemy.orm import Session
from jose import (
    JWTError,
    jwt
)
from datetime import (
    datetime,
    timedelta
)
from typing import (
    Optional,
    List
)

import crud
import models
import schemas

from database import (
    SessionLocal,
    engine
)

models.Base.metadata.create_all(bind = engine)

app = FastAPI()
tasks = APIRouter()

app.include_router(tasks, prefix="/tasks", tags=["tasks"])

SECRET_KEY = 'JanBash'
ALGORITHM = 'HS256'
ACCESS_TOKEN_EXPIRE_MINUTE = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl = 'token')

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes = 15)
    to_encode.update({'exp': expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm = ALGORITHM)
    return encoded_jwt

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Not Authorized",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        
        if email is None:
            raise credentials_exception
        
        user = crud.get_user_by_email(db, email=email)
        if user is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return user

def get_current_user_id(request: Request, db: Session = Depends(SessionLocal)) -> int:
    token = request.headers.get("Authorization")
    if token is None:
        raise HTTPException(status_code=401, detail="Not authenticated")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user_id

@app.post('/token/', response_model = schemas.Token)
async def login_for_access_token(request: schemas.TokenRequest, db: Session = Depends(get_db)):
    user = crud.authenticate_user(db, request.email, request.password)
    if not user:
        raise HTTPException(
            status_code = status.HTTP_401_UNAUTHORIZED,
            detail = 'Incorrect username or password',
            headers = {'WWW-Authenticate': 'Bearer'},
        )
    access_token_expires = timedelta(minutes = ACCESS_TOKEN_EXPIRE_MINUTE)
    access_token = create_access_token(
        data = {'sub': user.email}, expires_delta = access_token_expires
    )
    return {'access_token': access_token, 'token_type': 'bearer'}

@app.post('/register/', response_model = schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email = user.email)
    if db_user:
        raise HTTPException(status_code = 400, detail = 'Email already registered')
    return crud.create_user(db = db, user = user)

@app.get('/user/me/', response_model = schemas.User)
async def read_user_me(current_user: schemas.User = Depends(get_current_user)):
    return current_user

@app.post('/tasks/', response_model = schemas.TaskBase)
async def create_task(task: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_task = models.Task(title = task.title, user_id=current_user.id)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)
    return new_task

@app.get('/', response_model = List[schemas.Task])
async def read_tasks(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    tasks = db.query(models.Task).filter(models.Task.user_id == current_user.id)
    
    return tasks

@app.get('/{task_id}/', response_model = schemas.Task)
async def task_detail(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = crud.find_task(db, task_id, current_user)
    
    if db_task is None:
        raise HTTPException(status_code = 404, detail = 'Task not found')
    
    return db_task

@app.patch('/{task_id}/done/', response_model = schemas.Task)
async def task_done(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = crud.find_task(db, task_id, current_user)
    
    if db_task is None:
        raise HTTPException(status_code = 404, detail = 'Task not found')
    
    db_task.is_done = True
    db.commit()
    db.refresh(db_task)
    
    return db_task

@app.delete('/{task_id}/', response_model = schemas.Task)
async def delete_task(task_id: int, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = crud.find_task(db, task_id, current_user)
    
    if db_task is None:
        raise HTTPException(status_code = 404, detail = 'Task not found')
    
    db.delete(db_task)
    db.commit()
    
    return db_task

@app.put('/{task_id}/update/', response_model = schemas.Task)
async def update_task(task_id: int, user_update: schemas.TaskCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    db_task = crud.update_task(db, task_id, user_update, current_user)
    
    if db_task is None:
        raise HTTPException(status_code = 404, detail = 'Task not found')
    
    return db_task
