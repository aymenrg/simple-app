from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from sqlalchemy import create_engine

# Keep your existing connection string
SQLALCHEMY_DATABASE_URL = "postgresql://postgres:123@database:5432/postgres"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# --- NEW: The User Table ---
class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True) # unique=True prevents duplicate usernames
    hashed_password = Column(String)

    # This creates a virtual link to the records they own
    records = relationship("Record", back_populates="owner")

# --- UPDATED: The Record Table ---
class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, index=True)
    metric = Column(Float)
    
    # NEW: The Foreign Key that maps this exact record to a specific user's ID
    user_id = Column(Integer, ForeignKey("users.id"))

    # This creates the virtual link back to the User table
    owner = relationship("User", back_populates="records")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()