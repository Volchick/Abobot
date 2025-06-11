from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base
from .config_reader import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

Base = declarative_base()
DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL, echo=True)