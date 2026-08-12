from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# The exact connection string to reach the PostgreSQL container
SQLALCHEMY_DATABASE_URL = "postgresql://admin:123@database:5432/app_db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Define the schema for your database table
class Record(Base):
    __tablename__ = "records"

    id = Column(Integer, primary_key=True, index=True)
    status = Column(String, index=True)
    metric = Column(Float)
