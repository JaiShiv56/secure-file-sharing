from sqlalchemy import Column, Integer, String
from .database import Base
from sqlalchemy import Boolean

# User table: handles both ops and client users
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String, default="client")  # 'client' or 'ops'
    is_verified = Column(Boolean, default=False)

# File table: uploaded files with filename and owner
class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, index=True)
    uploaded_by = Column(String)  # email of uploader (Ops user)


