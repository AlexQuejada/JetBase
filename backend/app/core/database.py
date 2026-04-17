from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import psycopg2

load_dotenv()

DATABASE_URL = "postgresql://user:password@localhost:5432/jetbase"

# 🔥 función que fuerza encoding en psycopg2
def get_connection():
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_client_encoding('UTF8')  # 💥 CLAVE
    return conn

engine = create_engine(
    DATABASE_URL,
    creator=get_connection  # 👈 usamos nuestra conexión custom
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()