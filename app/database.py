from sqlalchemy import create_engine
from config_reader import POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB

DATABASE_URL = f"postgresql+psycopg2://{POSTGRES_USER}:{POSTGRES_PASSWORD}@db:5432/{POSTGRES_DB}"
engine = create_engine(DATABASE_URL, echo=True)