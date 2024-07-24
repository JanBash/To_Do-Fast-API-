from sqlalchemy import (
    Boolean, 
    Column, 
    Integer,
    String,
    ForeignKey,
    DateTime
)
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.sql import func

class User(Base):
    __tablename__ = 'users'
    
    id = Column(
        Integer, 
        primary_key = True,
    )
    username = Column(
        String
    )
    email = Column(
        String,
        unique = True,
    )
    full_name = Column(
        String,
    )
    hashed_password = Column(
        String
    )
    is_active = Column(
        Boolean,
        default = True
    )

    tasks = relationship(
        'Task', 
        back_populates = 'user'
    )


class Task(Base):
    __tablename__ = 'tasks'
    
    id = Column(
        Integer, 
        primary_key = True
    )
    user_id = Column(
        Integer,
        ForeignKey('users.id')
    )
    title = Column(
        String
    )
    created_date = Column(
        DateTime(
            timezone = True
        ), 
        server_default = func.now()
    )
    updated_date = Column(
        DateTime(
            timezone = True
        ),
        onupdate = func.now()
    )
    is_done = Column(
        Boolean,
        default = False
    )

    user = relationship(
        'User',
        back_populates = 'tasks'
    )
