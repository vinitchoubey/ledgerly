from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text
from sqlalchemy.orm import sessionmaker, relationship, declarative_base

# DATABASE_URL = "sqlite:///./smartbudget.db"

DATABASE_URL = "sqlite:///./data/smartbudget.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    monthly_budget = Column(Float, default=3000.0)
    days_in_month = Column(Integer, default=30)

    expenses = relationship("Expense", back_populates="owner")


class Expense(Base):
    __tablename__ = "expenses"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    shop = Column(String, default="Entry")
    date = Column(String)
    total = Column(Float)
    items_json = Column(Text)  # stores the items list as a JSON string

    owner = relationship("User", back_populates="expenses")


def init_db():
    Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()





# from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, Text
# from sqlalchemy.orm import sessionmaker, relationship, declarative_base
# import os

# # Reads the database connection string from an environment variable.
# # Locally (no env var set) it falls back to a SQLite file for easy testing.
# # In production (Render), set DATABASE_URL to your Neon Postgres connection string.
# DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///./data/smartbudget.db")

# # SQLite needs this extra arg; Postgres does not
# connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

# engine = create_engine(DATABASE_URL, connect_args=connect_args)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
# Base = declarative_base()


# class User(Base):
#     __tablename__ = "users"

#     id = Column(Integer, primary_key=True, index=True)
#     email = Column(String, unique=True, index=True, nullable=False)
#     hashed_password = Column(String, nullable=False)
#     monthly_budget = Column(Float, default=3000.0)
#     days_in_month = Column(Integer, default=30)

#     expenses = relationship("Expense", back_populates="owner")


# class Expense(Base):
#     __tablename__ = "expenses"

#     id = Column(Integer, primary_key=True, index=True)
#     user_id = Column(Integer, ForeignKey("users.id"))
#     shop = Column(String, default="Entry")
#     date = Column(String)
#     total = Column(Float)
#     items_json = Column(Text)  # stores the items list as a JSON string

#     owner = relationship("User", back_populates="expenses")


# def init_db():
#     Base.metadata.create_all(bind=engine)


# def get_db():
#     db = SessionLocal()
#     try:
#         yield db
#     finally:
#         db.close()